#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import re
import sys
import os
import gc
import socket
import threading
import random
import json
import xbmcgui
import xbmc
import xbmcaddon
import xbmcplugin
import BaseHTTPServer
import SocketServer
from datetime import datetime

Addon = xbmcaddon.Addon(id='script.module.torrent.ts')
Debug = xbmcaddon.Addon(id='script.module.torrent.ts').getSetting('debug')
ServerAddress = Addon.getSetting('address') if Addon.getSetting('address').strip() != '' else '127.0.0.1'

MIME_TYPES = {'webm': 'video/webm', 'mkv': 'video/x-matroska ', 'flv': 'video/x-flv', 'mp4': 'video/mp4',
              'm4v': 'video/x-m4v', 'mpeg': 'video/mpg', 'mpg': 'video/mpg', 'mts': 'video/mpg', 'm2v': 'video/mpg',
              'm2ts': 'video/m2ts', 'ogm': 'video/ogg', 'ogv': 'video/ogg', 'vob': 'video/dvd', 'avi': 'video/avi',
              'mov': 'video/quicktime', 'qt': 'video/quicktime', 'wmv': 'video/x-ms-wmv', '3gp': 'video/3gpp',
              'rm': 'application/vnd.rn-realmedia', 'asf': 'video/x-ms-asf', 'divx': 'video/x-divx',
              'bdmv': 'video/x-bdmv', 'ts': 'video/mp2t'}

if sys.platform == 'win32' or sys.platform == 'win64':
    pwin = True
else:
    pwin = False


def fs_enc(path):
    sys_enc = sys.getfilesystemencoding() if sys.getfilesystemencoding() else 'utf-8'
    return path.decode('utf-8').encode(sys_enc)


def fs_dec(path):
    sys_enc = sys.getfilesystemencoding() if sys.getfilesystemencoding() else 'utf-8'
    return path.decode(sys_enc).encode('utf-8')


def debug(s):
    if Debug == 'true':
        log = open(os.path.join(fs_enc(xbmc.translatePath('special://home')), 'ASCore.log'), 'a')
        log.write('%s: %s\r\n' % (str(datetime.utcnow().strftime('%H:%M:%S.%f')[:-3]), str(s)))
        log.close()


class Logger:
    def __init__(self):
        pass

    def out(self, txt):
        pass


class StreamReader(object):
    chunk_size = 256 * 1024

    def __init__(self, uri):
        self.headers = {'User-Agent': 'VLC 2.0.5', 'Accept': '*/*', 'Accept-Charset': 'utf-8, *;q=0.1',
                        'Accept-Encoding': 'none', 'Connection': 'keep-alive'}
        self.uri = uri
        self.opened = False
        self.r = None

    def __del__(self):
        self.close()

    def set_range(self, r):
        self.headers['Range'] = r

    def start_stream(self):
        bo = urllib2.build_opener()
        try:
            self.r = bo.open(urllib2.Request(url=self.uri, data=None, headers=self.headers))
            self.opened = True
            debug('HTTPD: Stream started')
        except:
            self.opened = False

    def is_opened(self):
        return self.opened

    def close(self):
        if self.opened:
            self.r.close()
            self.opened = False
            debug('HTTPD: Stream closed')

    def read(self):
        if self.opened:
            return self.r.read(self.chunk_size)
        return None

    def get_content_range_header(self):
        if self.opened:
            return self.r.info().getheader('Content-Range')

    def get_content_length_header(self):
        if self.opened:
            return self.r.info().getheader('Content-Length')


class StreamManager(object):
    def __init__(self):
        self.stream_list = list()

    def open(self, uri):
        for s in self.stream_list:
            s[1].close()
        self.stream_list = list()
        sr = StreamReader(uri)
        self.stream_list.append([uri, sr])
        print repr(self.stream_list)
        return sr


class ThreadingHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    def handle_error(self, *args, **kwargs):
        pass


class HttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def log_request(self, *args, **kwargs):
        pass

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        if self.server.file_name == urllib2.unquote(self.path[1:]):
            st = self.server.stream_manager.open(self.server.ace_stream_uri)
            if "range" in self.headers:
                self.send_response(206, 'Partial Content')
                st.set_range(self.headers['range'])
            else:
                self.send_response(200)
            st.start_stream()
            if st.is_opened():
                _, ext = os.path.splitext(self.server.file_name)
                ext = ext[1:]
                if ext == '' or ext not in MIME_TYPES:
                    self.send_header("Content-type", "application/octet-stream")
                else:
                    self.send_header("Content-type", MIME_TYPES[ext])
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Content-Range", st.get_content_range_header())
                self.send_header("Content-Length", st.get_content_length_header())
                self.end_headers()
                while True:
                    try:
                        readed = st.read()
                        if not readed:
                            break
                        self.wfile.write(readed)
                    except socket.timeout:
                        debug('HTTPD: Timeout reached')
                    except:
                        break
                st.close()
        else:
            self.send_response(404, 'not found')
            self.end_headers()


class _TSPlayer(xbmc.Player):
    def __init__(self):
        self.active = True
        self.started = False
        self.ended = False
        self.tsserv = None
        self.paused = False
        self.buffering = False
        width, height = self._get_skin_resolution()
        w = width
        h = int(0.14 * height)
        x = 0
        y = (height - h) / 2
        self.ov_window = xbmcgui.Window(12005)
        self.ov_label = xbmcgui.ControlLabel(x, y, w, h, '', alignment=6)
        self.ov_background = xbmcgui.ControlImage(x, y, w, h, os.path.join(Addon.getAddonInfo('path'), r'resources\bg.png'))
        self.ov_background.setColorDiffuse("0xD0000000")
        self.ov_visible = False
        xbmc.Player.__init__(self)

    def __del__(self):
        self.ov_hide()

    def ov_show(self):
        if not self.ov_visible:
            self.ov_window.addControls([self.ov_background, self.ov_label])
            self.ov_visible = True

    def ov_hide(self):
        if self.ov_visible:
            self.ov_window.removeControls([self.ov_background, self.ov_label])
            self.ov_visible = False

    def ov_update(self):
        if self.ov_visible:
            if int(self.tsserv.status[0]) == 100 and self.tsserv.status[1] == 'Загрузка файла':
                self.ov_label.setLabel('Загрузка завершена.\n[B]Пауза.[/B]')
            else:
                self.ov_label.setLabel('%s\nЗавершено: [B]%d%%[/B]\n%s' %
                                       (self.tsserv.status[1], int(self.tsserv.status[0]), self.tsserv.status[2]))

    def _get_skin_resolution(self):
        import xml.etree.ElementTree as ET
        skin_path = fs_enc(xbmc.translatePath("special://skin/"))
        tree = ET.parse(os.path.join(skin_path, "addon.xml"))
        res = tree.findall("./extension/res")[0]
        return int(res.attrib["width"]), int(res.attrib["height"])

    def onPlayBackPaused(self):
        self.ov_show()
        if not self.buffering:
            self.paused = True
        self.tsserv.push('EVENT pause position=%d' % int(self.getTime()))

    def onPlayBackStarted(self):
        xbmc.executebuiltin('XBMC.ActivateWindow(12005)')
        try:
            if self.tsserv.vod:
                self.tsserv.push('DUR %s %d' % (self.tsserv.stream_url, int(xbmc.Player().getTotalTime() * 1000)))
        except:
            self.started = False
            return
        self.tsserv.push('EVENT play')
        self.tsserv.push('PLAYBACK %s 0' % self.tsserv.stream_url)
        self.started = True
        xbmc.sleep(1000)

    def onPlayBackResumed(self):
        self.ov_hide()
        self.paused = False
        self.tsserv.push('EVENT play')

    def onPlayBackEnded(self):
        self.active = False
        self.ended = True

    def onPlayBackStopped(self):
        self.ov_hide()
        self.tsserv.push('STOP')
        self.tsserv.push('EVENT stop')
        self.active = False

    def onPlayBackSeek(self, time, seekOffset):
        self.tsserv.push('EVENT seek position=%d' % int(time / 1000))


class TSengine():
    def __init__(self):
        self.log = Logger()
        self.saving_folder = None
        self.progress = xbmcgui.DialogProgress()
        self.player = None
        self.files = dict()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(3)
        self.tsserv = None
        self.connected = False
        self.media_info = dict()
        self.filename = None
        self.mode = None
        self.url = None
        self.local = False
        self.saved = False
        self.pos = [25, 50, 75, 100]
        self.aceport = 62062
        self.progress.create("AceStream", "Инициализация")
        self._httpd = None
        self._httpd_thread = None
        self.save = True if Addon.getSetting('save') == 'true' and Addon.getSetting('folder') else False
        self.resume_saved = True if Addon.getSetting('switch_playback') == 'true' else False
        self.buf_pause = True if Addon.getSetting('auto_pause_buf') == 'true' else False
        self.use_httpd = True if Addon.getSetting('httpd') == 'true' else False
        if xbmc.Player().isPlaying():
            xbmc.Player().stop()
        Addon.setSetting('active', 'true')


    def _ts_init(self):
        self.tsserv = _TSServ(self._sock)
        self.tsserv.start()
        self.tsserv.push("HELLOBG version=6")
        self.progress.update(10, "Ждем ответа", " ")
        while not self.tsserv.version:
            if xbmc.abortRequested or self.progress.iscanceled():
                return False
            xbmc.sleep(200)
        if self.tsserv.err:
            return False
        import hashlib
        sha1 = hashlib.sha1()
        pkey = self.tsserv.pkey
        sha1.update(self.tsserv.key + pkey)
        key = sha1.hexdigest()
        pk = pkey.split('-')[0]
        ready_key = 'READY key=%s-%s' % (pk, key)
        self.tsserv.push(ready_key)
        self.progress.update(30, "Авторизиция", " ")
        while not self.tsserv.auth_ok:
            if xbmc.abortRequested or self.progress.iscanceled():
                return True
            xbmc.sleep(200)
        return True

    def sm(self, msg):
        xbmc.executebuiltin('XBMC.Notification("AceStream", "%s", 2000, "")' % msg)
    
    def _connect(self):
        self.progress.update(0, 'Пробуем подключиться', ' ')
        if pwin:
            if not self._start_windows():
                return False
        else:
            try:
                self._sock.connect((ServerAddress, 62062))
                self._sock.settimeout(None)
                return True
            except:
                if not self._start_linux():
                    return False

        for i in range(1, 100, 1):
            self.progress.update(i, 'Пробуем подключиться', '')
            try:
                if pwin:
                    self.aceport = self._get_aceport_windows()
                if self.aceport:
                    self._sock.connect((ServerAddress, self.aceport))
                    self._sock.settimeout(None)
                    self.connected = True
                    return True
            except:
                pass
            if self.progress.iscanceled():
                return False
            xbmc.sleep(500)
        return False

    def _start_linux(self):
        import subprocess
        try:
            proc = subprocess.Popen(["acestreamengine","--client-console"])
        except:
            try:  proc = subprocess.Popen('acestreamengine-client-console')
            except: 
                try: 
                    subprocess.Popen(Addon.getSetting('prog'), shell=True)
                except:
                    try:
                        xbmc.executebuiltin('XBMC.StartAndroidActivity("org.acestream.engine")')
                    except:
                        self.sm('Not Installed')
                        self.progress.update(0,'AceStream not installed','')
                        return False
        return True
    
    def _start_windows(self):
        try:
            import _winreg
            t = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 'Software\AceStream')
            needed_value =  _winreg.QueryValueEx(t , 'EnginePath')[0]
            path= needed_value.replace('ace_engine.exe','')
            self.progress.update(0,'Starting ASEngine','')
            os.startfile(needed_value)
        except:
            self.sm('Not Installed')
            self.progress.update(0,'AceStream not installed','')
            return False
        return True

    def _get_aceport_windows(self):
        try:
            import _winreg
            t = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 'Software\\AceStream')
            needed_value =  _winreg.QueryValueEx(t , 'EnginePath')[0]
            path= needed_value.replace('ace_engine.exe','')
            pfile= os.path.join( path,'acestream.port')
            gf = open(pfile, 'r')
            self.aceport = int(gf.read())
        except:
            return False
        return self.aceport

    def _get_local_file(self, index):
        if not self.save:
            return False
        for k, v in self.files.iteritems():
            if v == index:
                self.filename = k.replace('/', '_').replace('\\', '_')
        if not self.saving_folder:
            self.saving_folder = fs_enc(Addon.getSetting('folder'))
        self.filename = os.path.join(self.saving_folder, fs_enc(self.filename))
        if os.path.exists(self.filename):
            return fs_dec(self.filename)
        return False

    def _start_stream(self, index):
        self.tsserv.index = index
        self.tsserv.push('START %s %s %s 0 0 0' % (self.mode, self.url, str(index)))
        while not self.tsserv.state == 2:
            self.progress.update(int(self.tsserv.status[0]), self.tsserv.status[1], self.tsserv.status[2])
            if xbmc.abortRequested or self.progress.iscanceled() or self.tsserv.err:
                return False
            xbmc.sleep(200)
        return True

    def _save_file(self):
        if self.tsserv.can_save and self.save:
            if not os.path.exists(self.filename):
                self.progress.update(0, 'Сохраняю файл на диск', '')
                save_name = urllib.quote(fs_dec(self.filename))
                self.tsserv.push('SAVE %s path=%s' % (self.tsserv.save_info[0] + ' ' + self.tsserv.save_info[1], save_name))
                self.tsserv.can_save = None
                while not os.path.exists(self.filename):
                    if xbmc.abortRequested or self.progress.iscanceled():
                        return False
                    xbmc.sleep(200)
                return fs_dec(self.filename)
        return False

    def _start_httpd(self, uri, file_name):
        port = self._get_random_open_port()
        self._httpd = ThreadingHTTPServer(('127.0.0.1', port), HttpHandler)
        self._httpd.stream_manager = StreamManager()
        self._httpd.ace_stream_uri = uri
        self._httpd.file_name = file_name
        self._httpd_thread = threading.Thread(target=self._httpd.serve_forever)
        self._httpd_thread.start()
        debug('HTTPD: started at http://127.0.0.1:%d/' % port)
        return 'http://127.0.0.1:%d/%s' % (port, urllib2.quote(file_name))

    def _get_random_open_port(self):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(("", 0))
            s.listen(1)
            port = s.getsockname()[1]
            s.close()
            return int(port)

    def play_url_ind(self, index=0, title='', icon='', thumb='', use_resolved_url=False):
        self.progress.update(50, 'Загрузка', '')
        self.media_info = {'title': title, 'icon': icon, 'thumb': thumb}
        if len(self.files) == 1 and int(index) != 0:
            index = 0
        local_file = self._get_local_file(index)
        if not local_file:
            self.progress.update(70, 'Ожидание воспроизведения', '')
            if not self._start_stream(index):
                return False
            xbmc.sleep(700)
            self.progress.update(100, 'Запускается воспроизведение', '')
            local_file = self._save_file()
            if not local_file:
                if self.use_httpd:
                    self.tsserv.stream_url = self._start_httpd(self.tsserv.stream_url, title)
                self.player = _TSPlayer()
                self.player.tsserv = self.tsserv
                self.progress.close()
                item = xbmcgui.ListItem(title, thumb, icon, path=self.tsserv.stream_url)
                if use_resolved_url:
                    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
                else:
                    self.player.play(self.tsserv.stream_url, item)
                while self.player.active:
                    xbmc.sleep(200)
                    self.loop()
                    if xbmc.abortRequested:
                        break
                return self.player.started
        if local_file:
            self.progress.update(100, 'Запускается воспроизведение', '')
            xbmc.sleep(700)
            item = xbmcgui.ListItem(title, thumb, icon, path=local_file)
            self.progress.close()
            if use_resolved_url:
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
            else:
                xbmc.Player().play(local_file, item)
            return True

    def get_link(self, index=0, title='', icon='', thumb=''):
        self.progress.close()
        self.player = _TSPlayer()
        self.player.tsserv = self.tsserv
        local_file = self._get_local_file(index)
        if local_file:
            self.local = True
            return local_file
        if not self._start_stream(index):
            return False
        xbmc.sleep(500)
        local_file = self._save_file()
        if local_file:
            self.local = True
            return local_file
        else:
            if self.use_httpd:
                self.tsserv.stream_url = self._start_httpd(self.tsserv.stream_url, title)
            return self.tsserv.stream_url

    def loop(self):
        if self.player.isPlaying():
            pos = self.pos
            if self.player.getTotalTime() > 0:
                cpos = int((1-(self.player.getTotalTime()-self.player.getTime())/self.player.getTotalTime())*100) + 1
            else:
                cpos = 0
            if cpos in pos:
                pos.remove(cpos)
                self.tsserv.push('PLAYBACK %s %d' % (self.tsserv.stream_url, cpos))
        if self.tsserv.can_save and self.save:
            save_name = urllib.quote(fs_dec(self.filename))
            self.tsserv.push('SAVE %s path=%s' % (self.tsserv.save_info[0] + ' ' + self.tsserv.save_info[1], save_name))
            self.tsserv.can_save = None
            self.saved = True
        if self.resume_saved and self.saved and self.player.started:
            if self.player.isPlaying() and os.path.exists(self.filename) and not self.player.paused:
                xbmc.sleep(2000)
                local_file = fs_dec(self.filename)
                time1 = self.player.getTime()
                item = xbmcgui.ListItem(self.media_info['title'], self.media_info['thumb'], self.media_info['icon'], path=local_file)
                item.setProperty('StartOffset', str(time1))
                self.tsserv.push('STOP')
                self.player.ov_hide()
                xbmc.Player().play(local_file, item)
                self.player.active = False
                self.local = True
        if self.buf_pause:
            if self.tsserv.state == 3 and self.tsserv.pause:
                self.player.buffering = True
                if not self.player.ov_visible:
                    self.player.pause()
            if self.tsserv.state == 2 and self.player.buffering:
                if not self.player.paused:
                    self.player.pause()
                self.player.buffering = False
        if self.player.ov_visible and self.player.started:
            self.player.ov_update()

    def load_torrent(self, torrent, mode, host='127.0.0.1', port=62062):
        self.mode = mode
        self.url = torrent
        if not self._connect():
            self.sm('Connection Failed')
            return False
        if not self._ts_init():
            self.sm('Initialization Failed')
            return False
        self.progress.update(10, "Загрузка торрента", "")
        self.tsserv.push('LOADASYNC %s %s %s 0 0 0' % (str(random.randint(0, 0x7fffffff)), mode, torrent))
        while not self.tsserv.files:
            if xbmc.abortRequested or self.progress.iscanceled() or self.tsserv.err:
                return False
            xbmc.sleep(200)
        self.progress.update(50, 'Загрузка файлов', '')
        if not self.tsserv.files:
            return False
        file_list = json.loads(self.tsserv.files)
        try:
            for l in file_list['files']:
                self.files[urllib.unquote_plus(l[0].encode('utf-8'))] = l[1]
            self.progress.update(100, 'Загрузка данных завершена', '')
        except:
            self.sm('Ошибка загрузки файла')
            return False
        return "Ok"

    def set_saving_settings(self, save=False, saving_folder=None, resume_saved=False):
        self.save = save
        self.resume_saved = resume_saved
        if save and saving_folder:
            self.saving_folder = fs_enc(saving_folder)

    def end(self):
        if self._httpd:
            self._httpd.shutdown()
            self._httpd.server_close()
        if self._httpd_thread:
            self._httpd_thread.join()
        if self.progress:
            self.progress.close()
        if self.connected:
            self.connected = False
            self.tsserv.push('SHUTDOWN')
        if self.tsserv:
            self.tsserv.active = False
            self.tsserv.join()
        try:
            self._sock.shutdown(socket.SHUT_RDWR)
        except:
            pass
        self._sock.close()
        Addon.setSetting('active', 'false')

    def __del__(self):
        self.end()
        gc.collect()


class _TSServ(threading.Thread):
    def __init__(self,_socket):
        self.pkey = 'n51LvQoTlJzNGaFxseRK-uvnvX-sD4Vm5Axwmc4UcoD-jruxmKsuJaH0eVgE'
        threading.Thread.__init__(self)
        self._sock = _socket
        self.active = True
        self.err = False
        self.buffer = 65020
        self.last_received = ''
        self.auth_ok = False
        self.version = None
        self.files = None
        self.key = None
        self.index = None
        self.stream_url = None
        self.can_save = False
        self.save_info = None
        self.state = 0
        self.status = [0, '', '']
        self.pause = False
        self.vod = True

    def push(self, command):
        debug('>> ' + command)
        try:
            self._sock.send(command + '\r\n')
        except:
            self.err = True

    def run(self):
        while self.active and not self.err:
            try:
                self.temp = self._sock.recv(self.buffer)
            except:
                self.temp = ''
            self.last_received += self.temp
            ind = self.last_received.find('\r\n')
            if ind != -1:
                fcom = self.last_received
                while ind != -1:
                    self.last_received = fcom[:ind]
                    self.exec_com()
                    fcom = fcom[(ind + 2):]
                    ind = fcom.find('\r\n')
                self.last_received = ''

    def exec_com(self):
        debug('<< ' + self.last_received)
        line = self.last_received
        cmd = self.last_received.split(' ')[0]
        params = self.last_received.split(' ')[1::]
        if cmd == 'HELLOTS':
            try:
                self.version = params[0].split('=')[1]
            except:
                self.version = '1.0.6'
            try:
                if params[2].split('=')[0] == 'key':
                    self.key = params[2].split('=')[1]
            except: 
                try:
                    self.key = params[1].split('=')[1]
                except:
                    self.err = True
        elif cmd == 'AUTH':
            self.auth_ok = True
        elif cmd == 'LOADRESP':
            self.files = line[line.find('{'):len(line)]
        elif cmd == 'EVENT':
            if params[0] == 'cansave':
                if int(self.index) == int(params[1].split('=')[1]):
                    self.can_save = True
                    self.save_info = [params[1], params[2]]
            elif params[0] == 'getuserdata':
                self.push('USERDATA [{"gender": 1}, {"age": 3}]')
        elif cmd == 'START':
            try:
                self.stream_url = urllib.unquote_plus(params[0].split('=')[1]).replace('127.0.0.1', ServerAddress)
            except:
                self.stream_url = params[0].replace('127.0.0.1', ServerAddress)
        elif cmd == 'RESUME':
            self.pause = False
        elif cmd == 'PAUSE':
            self.pause = True
        elif cmd == 'SHUTDOWN':
            self.active = False
        elif cmd == 'STATE':
            self.state = int(params[0])
            if self.state == 6:
                self.err = True
        elif cmd == "STATUS":
            self._get_status(params[0])

    def _get_status(self,params):
        ss = re.compile('main:[a-z]+',re.S)
        s1 = re.findall(ss, params)[0]
        st = s1.split(':')[1]
        if st == 'idle':
            self.status[1] = 'Простаивание'
        elif st == 'starting':
            self.status[1] = 'Запуск'
        elif st == 'check':
            self.status[1] = 'Проверка'
            self.status[0] = int(params.split(';')[1])
        elif st == 'prebuf':
            self.status[0] = int(params.split(';')[1])
            self.status[1] = 'Предварительная буферизация'
            self.status[2] = 'Сиды: [B]%s[/B], скорость: [B]%sKb/s[/B]' % (params.split(';')[8], params.split(';')[5])
        elif st == 'loading':
            self.status[1] = 'Загрузка'
        elif st == 'dl':
            self.status[0] = int(params.split(';')[1])
            self.status[1] = 'Загрузка файла'
            self.status[2] = 'Сиды: [B]%s[/B], скорость: [B]%sKb/s[/B]' % (params.split(';')[6], params.split(';')[3])
        elif st == 'buf':
            self.status[0] = int(params.split(';')[1])
            self.status[1] = 'Буферизация'
            self.status[2] = 'Сиды: [B]%s[/B], скорость: [B]%sKb/s[/B]' % (params.split(';')[8], params.split(';')[5])
        elif st == 'wait':
            self.status[0] = 99
            self.status[1] = 'Ожидание сидов'
            self.status[2] = 'Нет достаточной скорости'

    def end(self):
        self.active = False
        self.daemon = False

