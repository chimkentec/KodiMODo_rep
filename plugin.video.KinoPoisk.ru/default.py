#!/usr/bin/python
# -*- coding: utf-8 -*-

# *      Copyright (C) 2011 TDW

import xbmc, xbmcgui, xbmcplugin, xbmcaddon, os, urllib, time, codecs, httplib
import SelectBox
from KPmenu import *

PLUGIN_NAME   = 'KinoPoisk.ru'
siteUrl = 'www.KinoPoisk.ru'
httpSiteUrl = 'http://' + siteUrl
handle = int(sys.argv[1])
addon = xbmcaddon.Addon(id='plugin.video.KinoPoisk.ru')
__settings__ = xbmcaddon.Addon(id='plugin.video.KinoPoisk.ru')
xbmcplugin.setContent(int(sys.argv[1]), 'movies')

icon  = os.path.join( addon.getAddonInfo('path'), 'icon.png')
dbDir = os.path.join( addon.getAddonInfo('path'), "db" )
LstDir = addon.getAddonInfo('path')

headers  = {
	'User-Agent' : 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00',
	'Accept'     :' text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*',
	'Accept-Language':'ru-RU,ru;q=0.9,en;q=0.8',
	'Accept-Charset' :'utf-8, utf-16, *;q=0.1',
	'Accept-Encoding':'identity, *;q=0'
}

# -------- Torrent2Http---by-Anteo---
try:
	import tthp
except:
	print "Error import t2http"

def t2http_list(url, info={}):
		L=tthp.list(url)
	#if len (L)<2:
	#	tthp.play(url, handle, 0, __settings__.getSetting("DownloadDirectory"))
	#else:
		for i in L:
			#print i
			listitem = xbmcgui.ListItem(i.name)
			purl = sys.argv[0] + '?mode=t2http_play'\
				+ '&url=' + urllib.quote_plus(url)\
				+ '&ind=' + urllib.quote_plus(str(i.index))
			
			try:title=info['originaltitle']+' ('+str(info['year'])+')'
			except:
				try:title=info['namef']
				except:title="error"

			uri2 = construct_request({
				't': url,
				'tt': i.name,
				'title': title,
				'i':str(i.index),
				'ii':"",
				'mode': 'save_strm'
				})
			listitem.addContextMenuItems([('[B]Сохранить фильм(STRM)[/B]', 'XBMC.RunPlugin(%s)' % uri2),])
			
			xbmcplugin.addDirectoryItem(handle, purl, listitem, False)
			

		xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
		xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL)
		xbmcplugin.endOfDirectory(handle)

def t2http_play(uri, id):
	tthp.play(uri, handle, id, __settings__.getSetting("DownloadDirectory"))



#---------asengine----by-nuismons-----

from ASCore import TSengine,_TSPlayer

def play_url(torr_link,img, info={}):
    #print torr_link

    TSplayer=TSengine()
    out=TSplayer.load_torrent(torr_link,'TORRENT')
    if out=='Ok':
        for k,v in TSplayer.files.iteritems():
            li = xbmcgui.ListItem(urllib.unquote(k))
            #fokus(urllib.unquote(k))# -----------------========================:::::::::::::::::: ТУТ
            uri = construct_request({
                't': torr_link,
                'tt': k.encode('utf-8'),
                'i':v,
                'ii':urllib.quote(img),
                'mode': 'addplist'
            })
            li.setProperty('IsPlayable', 'true')
            
            #li.addContextMenuItems([('Добавить в плейлист', 'XBMC.RunPlugin(%s)' % uri),])
            try:title=info['originaltitle']+' ('+str(info['year'])+')'
            except:
                try:title=info['namef']
                except:title="error"
                print "----------title------------"
                print title
            uri2 = construct_request({
                't': torr_link,
                'tt': k.encode('utf-8'),
                'title': title,
                'i':v,
                'ii':img,
                'mode': 'save_strm'
            })
            li.addContextMenuItems([('[B]Сохранить фильм(STRM)[/B]', 'XBMC.RunPlugin(%s)' % uri2),('Добавить в плейлист', 'XBMC.RunPlugin(%s)' % uri)])
            uri = construct_request({
                'torr_url': torr_link,
                'title': k,
                'ind':v,
                'img':img,
                'func': 'play_url2',
                'mode': 'play_url2'
            })
            #li.addContextMenuItems([('Добавить в плейлист', 'XBMC.RunPlugin(%s?func=addplist&torr_url=%s&title=%s&ind=%s&img=%s&func=play_url2)' % (sys.argv[0],urllib.quote(torr_link),k,v,img  )),])
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), uri, li)
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    TSplayer.end()

def play_url2(params):
    #print 'play'
    torr_link=urllib.unquote(params["torr_url"]).replace("www.rutor.org","open-tor.org")
    
    Engine = __settings__.getSetting("Engine")
    if Engine=="2":
        tthp.play(torr_link, handle, int(params['ind']), __settings__.getSetting("DownloadDirectory"))
        return False
    
    img=urllib.unquote_plus(params["img"])
    title=urllib.unquote_plus(params["title"])
    #showMessage('heading', torr_link, 10000)
    TSplayer=TSengine()
    out=TSplayer.load_torrent(torr_link,'TORRENT')
    if out=='Ok':
        lnk=TSplayer.get_link(int(params['ind']),title, img, img)
        if lnk:
           
            item = xbmcgui.ListItem(path=lnk, thumbnailImage=img, iconImage=img)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)  

            while not xbmc.Player().isPlaying:
                xbmc.sleep(300)
            while TSplayer.player.active and not TSplayer.local: 
                TSplayer.loop()
                xbmc.sleep(300)
                if xbmc.abortRequested:
                    TSplayer.log.out("XBMC is shutting down")
                    break
            if TSplayer.local and xbmc.Player().isPlaying: 
                try: time1=TSplayer.player.getTime()
                except: time1=0
                
                i = xbmcgui.ListItem("***%s"%title)
                i.setProperty('StartOffset', str(time1))
                xbmc.Player().play(TSplayer.filename.decode('utf-8'),i)

        else:
            item = xbmcgui.ListItem(path='')
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, item) 
    else:
        try:    xbmc.executebuiltin('Container.Update("plugin://plugin.video.KinoPoisk.ru/?mode=alter&title="'+urllib.unquote_plus(get_params()["title2"])+'")')
        except: xbmc.executebuiltin('Container.Update("plugin://plugin.video.KinoPoisk.ru/?mode=alter&title="'+urllib.unquote_plus(get_params()["title"])+'")')
    TSplayer.end()
    xbmc.Player().stop



#--------------tsengine----by-nuismons--------------


def alter(text):
		info={"title":text}
		print text
		rutor(text, info)
		dugtor(text, info)
		fileek(text, info)
		s2kp(text, info)
		xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
		xbmcplugin.endOfDirectory(handle)
		xbmc.sleep(300)
		xbmc.executebuiltin("Container.SetViewMode(51)")




def addplist(params):
    li = xbmcgui.ListItem(params['tt'])
    uri = construct_request({
        'torr_url': params['t'],
        'title': params['tt'].decode('utf-8'),
        'ind':urllib.unquote_plus(params['i']),
        'img':urllib.unquote_plus(params['ii']),
        'mode': 'play_url2'
    })
    xbmc.PlayList(xbmc.PLAYLIST_VIDEO).add(uri,li)

def save_strm(params):
		SaveDirectory = __settings__.getSetting("SaveDirectory")#[:-1]
		if SaveDirectory=="":SaveDirectory=LstDir
		name=urllib.unquote_plus(params['title']).decode('utf-8').replace("\\","").replace("?","").replace(":","")
		uri = construct_request({
			'torr_url': urllib.unquote_plus(params['t']),
			'title': params['tt'].decode('utf-8'),
			'title2': name,
			'ind':urllib.unquote_plus(params['i']),
			'img':urllib.unquote_plus(urllib.unquote_plus(params['ii'])),
			'func': 'play_url2',
			'mode': 'play_url2'
		})
		fl = open(os.path.join(ru(SaveDirectory),name+".strm"), "w")
		fl.write(uri)
		fl.close()
		xbmc.executebuiltin('UpdateLibrary("video")')
		

def save_tvshow_nfo(tts,img, info={}):
		title=info['title']
		cn=title.find(" (")
		title=title[:cn]
		name=ru(info['originaltitle'])#.replace(" (сериал)","")
		cn=name.find(" (")
		if cn>0:
			name=name[:cn]
			rus=1
		else: rus=0

		fanart=info['fanart']
		cover=info['cover']
		year=info['year']
		plot=info['plot']
		
		SaveDirectory = os.path.join(ru(__settings__.getSetting("SaveDirectory2")), name)
		if os.path.isdir(SaveDirectory)==0: os.mkdir(SaveDirectory)
		if SaveDirectory=="":SaveDirectory=LstDir
		nfo='<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>'+chr(10)
		nfo='<tvshow>'+chr(10)
		
		nfo+="	<title>"+title+"</title>"+chr(10)
		nfo+="	<showtitle>"+title+"</showtitle>"+chr(10)
		nfo+="	<year>"+str(year)+"</year>"+chr(10)
		nfo+="	<season>-1</season>"+chr(10)
		nfo+="	<plot>"+plot+"</plot>"+chr(10)
		nfo+="	<fanart>"+fanart+"</fanart>"+chr(10)
		nfo+="	<thumb>"+cover+"</thumb>"+chr(10)
		nfo+="</tvshow>"+chr(10)
		
		nf=__settings__.getSetting("NFO")
		nfowr="no"
		if nf=="0" and rus==1: nfowr="ok"
		if nf=="1": nfowr="ok"
		
		if nfowr=="ok":
			fl = open(os.path.join(SaveDirectory, "tvshow.nfo"), "w")
			fl.write(nfo)
			fl.close()


def save_nfo(tts,img, info={}):
		sts,ste=find_se(tts)
		try: s=int(sts.replace("s",""))
		except: s=0
		try: e=int(ste.replace("e",""))
		except: e=0
		
		title="season "+str(s)+" episode "+str(e)
		name=ru(info['originaltitle'])#.replace(" (сериал)","")
		cn=name.find(" (")
		rus=0
		if cn>0:
			name=name[:cn]
			rus=1
		
		plot=xt(tts)
		cover=info['cover']
		fanart=info['fanart']
		if s>0:
			if s<10: ss=".S0"+str(s)
			else:ss=".S"+str(s)
		else: ss=".0"
		
		if e>0:
			if e<10: es=".E0"+str(e)
			else:es=".E"+str(e)
		else: es=""

		if es!="":tts=name+ss+es
		
		SaveDirectory = os.path.join(ru(__settings__.getSetting("SaveDirectory2")), name)
		if os.path.isdir(SaveDirectory)==0: os.mkdir(SaveDirectory)
		if SaveDirectory=="":SaveDirectory=LstDir
		nfo="<episodedetails>"+chr(10)
		nfo+="	<title>"+title+"</title>"+chr(10)
		nfo+="	<season>"+str(s)+"</season>"+chr(10)
		nfo+="	<episode>"+str(e)+"</episode>"+chr(10)
		nfo+="	<plot>"+plot+"</plot>"+chr(10)
		nfo+="	<fanart>"+fanart+"</fanart>"+chr(10)
		nfo+="	<thumb>"+cover+"</thumb>"+chr(10)
		nfo+="</episodedetails>"+chr(10)
		
		nfo=__settings__.getSetting("NFO")
		nfowr="no"
		if nfo=="0" and rus==1: nfowr="ok"
		if nfo=="1": nfowr="ok"
		
		if nfowr=="ok":
			fl = open(os.path.join(SaveDirectory, tts+".nfo"), "w")
			fl.write(nfo)
			fl.close()
		return tts

def fokus(txt):
	pass

def find_se(txt):
	txt=txt.lower()
	
	txt=txt.replace(".","")
	LE=mfindal(txt,"s","e")
	s=-1
	e=-1
	for i in LE:
		print i
		if len(i)<4:
			try: 
				s=int(i[1:])
				ss=i
			except: pass
	if s>0:
		n=txt.find(ss)
		try: e=int(txt[n+len(ss)+1:n+len(ss)+3])
		except: e=-1
			
	if e<0: e=find_e(txt)
	if s<0: s=find_s(txt)
			
	return (s,e)
	
def find_se(txt):
	txt=txt.lower()
	for i in range (2000,2020):
		txt=txt.replace(str(i),"")

	F=["480","720","1080",".mp4",".ts","5.1","264"]
	for i in F:
		txt=txt.replace(i,"")

	SL=['.sezon','.Сезон','.сезон',  'sezon','Сезон','сезон']
	for i in SL:
		try:txt=txt.replace(i,"^")
		except: pass

	EL=['seriya','serija','Серия','серия','vypusk']
	for i in EL:
		try:txt=txt.replace(i,"#")
		except: pass
			
	EL2=['.e',' e','e','x']
	for i in EL2:
		for j in range (0,9):
			r=i+str(j)
			try:txt=txt.replace(r,"@"+str(j))
			except: pass

	SL2=['.s',' s','s']
	for i in SL2:
		for j in range (0,9):
			r=i+str(j)
			try:txt=txt.replace(r,"*"+str(j))
			except: pass


	T=["0","1","2","3","4","5","6","7","8","9",".","-","\\",  "#","@","^","*"]#,"x","s","e"
	L=tuple(txt)
	nst=""
	for i in L:
		if i in T: nst+=i
			
	nst=nst.replace("-",".")
	nst=nst.replace("#.","#").replace(".#","#")
	nst=nst.replace("@.","@").replace(".@","@")
	nst=nst.replace("^.","^").replace(".^","^")
	nst=nst.replace("*.","*").replace(".*","*")
	nst=nst.replace("......",".").replace(".....",".").replace("....",".").replace("...",".").replace("..",".")
	if nst[:1]==".": nst=nst[1:]
	if nst[-1:]==".": nst=nst[:-1]
	nc=nst.find("\\")
	if nc>0: 
		nst1=nst[:nc]
		nst2=nst[nc+1:]
		n1=nst2.find("*")
		n2=nst2.find("^")
		if n1>-1 or n2>-1:nst=nst2
		else:
			#print nst1
			try:nst1="^"+str(int(nst1.replace(".","").replace("^","").replace("*","")))
			except:
				nss=nst1.find("^")
				if nss>-1:nst1=nst1[:nss+2]
				else:nst1=""
			try:nst2="@"+str(int(nst2))
			except:nst2=">"+nst2
			nst=nst1+nst2
	sez="!?!"
	if 1==1:
		ns=nst.find("*")
		if ns>-1:
			try: sez="s"+str(int(nst[ns+1:ns+3]))
			except:
				try:sez="s"+str(int(nst[ns+1:ns+2]))
				except:sez="!*!"
			#print sez
			
	if sez=="!?!" or sez=="!*!":
		ns=nst.find("^")
		if ns>-1:
			try: sez="s"+str(int(nst[ns-2:ns]))
			except:
				try:sez="s"+str(int(nst[ns-1:ns]))
				except:
					try: sez="s"+str(int(nst[ns+1:ns+3]))
					except:
						try:sez="s"+str(int(nst[ns+1:ns+2]))
						except:sez="!^!"

	epd="!?!"
	if 1==1:
		ns=nst.find("@")
		if ns>-1:
			try: epd="e"+str(int(nst[ns+1:ns+4]))
			except:
				try:epd="e"+str(int(nst[ns+1:ns+3]))
				except:
					try:epd="e"+str(int(nst[ns+1:ns+2]))
					except:epd="!@!"
			
			if sez=="!?!":
					try: sez="s"+str(int(nst[ns-2:ns]))
					except:
						try:sez="s"+str(int(nst[ns-1:ns]))
						except:sez=="!?@!"
			#print sez
			
	if epd=="!?!" or epd=="!@!":
		ns=nst.find("#")
		if ns>-1:
			try: epd="e"+str(int(nst[ns-3:ns]))
			except:
				try:epd="e"+str(int(nst[ns-2:ns]))
				except:
					try:epd="e"+str(int(nst[ns-1:ns]))
					except:
						try: epd="e"+str(int(nst[ns+1:ns+4]))
						except:
							try:epd="e"+str(int(nst[ns+1:ns+3]))
							except:
								try:epd="e"+str(int(nst[ns+1:ns+2]))
								except:epd="!#!"
	
	if sez=="!?!" and epd!="!?!":
		if ns>3:
					try: sez="s"+str(int(nst[:2]))
					except:
						try:sez="s"+str(int(nst[:1]))
						except:sez=="!?!"

	if sez=="!?!" and epd=="!?!":
					try:epd="e"+str(int(nst))
					except:
						try:
							tmp=float(nst)
							sez="s"+str(int(tmp))
							sss,eee=divmod(tmp, 1)
							epd="e"+str(eee*100).replace(".0","")
						except: pass

	if sez!="!?!" and epd=="!?!":
			ns=nst.find(">")
			if ns>0:
					try:epd="e"+str(int(nst[ns+1:].replace(".","")))
					except:epd=="!?!"

	print sez+"\t:\t"+epd+"\t:\t"+nst
	return (sez,epd)



def find_se(txt):
	txt=txt.lower()
	for i in range (2000,2020):
		txt=txt.replace(str(i),"")

	F=["480","720","1080",".mp4",".ts","5.1","264"]
	for i in F:
		txt=txt.replace(i,"")

	SL=['.sezon','.Сезон','.сезон',  'sezon','Сезон','сезон']
	for i in SL:
		try:txt=txt.replace(i,"^")
		except: pass

	EL=['seriya','serija','Серия','серия','vypusk']
	for i in EL:
		try:txt=txt.replace(i,"#")
		except: pass
			
	EL2=['.e',' e','e','x']
	for i in EL2:
		for j in range (0,9):
			r=i+str(j)
			try:txt=txt.replace(r,"@"+str(j))
			except: pass

	SL2=['.s',' s','s']
	for i in SL2:
		for j in range (0,9):
			r=i+str(j)
			try:txt=txt.replace(r,"*"+str(j))
			except: pass


	T=["0","1","2","3","4","5","6","7","8","9",".","-","\\",  "#","@","^","*"]#,"x","s","e"
	L=tuple(txt)
	nst=""
	for i in L:
		if i in T: nst+=i
			
	nst=nst.replace("-",".")
	nst=nst.replace("#.","#").replace(".#","#")
	nst=nst.replace("@.","@").replace(".@","@")
	nst=nst.replace("^.","^").replace(".^","^")
	nst=nst.replace("*.","*").replace(".*","*")
	nst=nst.replace("......",".").replace(".....",".").replace("....",".").replace("...",".").replace("..",".")
	if nst[:1]==".": nst=nst[1:]
	if nst[-1:]==".": nst=nst[:-1]
	nc=nst.find("\\")
	if nc>0: 
		nst1=nst[:nc]
		nst2=nst[nc+1:]
		n1=nst2.find("*")
		n2=nst2.find("^")
		if n1>-1 or n2>-1:nst=nst2
		else:
			#print nst1
			try:nst1="^"+str(int(nst1.replace(".","").replace("^","").replace("*","")))
			except:
				nss=nst1.find("^")
				if nss>-1:nst1=nst1[:nss+2]
				else:nst1=""
			try:nst2="@"+str(int(nst2))
			except:nst2=">"+nst2
			nst=nst1+nst2
	sez="!?!"
	if 1==1:
		ns=nst.find("*")
		if ns>-1:
			try: sez="s"+str(int(nst[ns+1:ns+3]))
			except:
				try:sez="s"+str(int(nst[ns+1:ns+2]))
				except:sez="!*!"
			#print sez
			
	if sez=="!?!" or sez=="!*!":
		ns=nst.find("^")
		if ns>-1:
			try: sez="s"+str(int(nst[ns-2:ns]))
			except:
				try:sez="s"+str(int(nst[ns-1:ns]))
				except:
					try: sez="s"+str(int(nst[ns+1:ns+3]))
					except:
						try:sez="s"+str(int(nst[ns+1:ns+2]))
						except:sez="!^!"

	epd="!?!"
	if 1==1:
		ns=nst.find("@")
		if ns>-1:
			try: epd="e"+str(int(nst[ns+1:ns+4]))
			except:
				try:epd="e"+str(int(nst[ns+1:ns+3]))
				except:
					try:epd="e"+str(int(nst[ns+1:ns+2]))
					except:epd="!@!"
			
			if sez=="!?!":
					try: sez="s"+str(int(nst[ns-2:ns]))
					except:
						try:sez="s"+str(int(nst[ns-1:ns]))
						except:sez=="!?@!"
			#print sez
			
	if epd=="!?!" or epd=="!@!":
		
		ns=nst.find("#")
		if ns>-1:
			try: epd="e"+str(int(nst[ns-3:ns]))
			except:
				try:epd="e"+str(int(nst[ns-2:ns]))
				except:
					try:epd="e"+str(int(nst[ns-1:ns]))
					except:epd=="!?!"

		if ns>-1 and ns<len(nst)-2:
				pb=0
				try:
					epd="e"+str(int(nst[ns+1:ns+4]))
					pb=1
				except:
							try:
								epd="e"+str(int(nst[ns+1:ns+3]))
								pb=1
							except:
								try:
									epd="e"+str(int(nst[ns+1:ns+2]))
									pb=1
								except:epd="!#!"
	
				if sez=="!?!" and epd!="!?!" and pb==1:
					try:sez="s"+str(int(nst[ns-2:ns]))
					except:
						try:sez="s"+str(int(nst[ns-1:ns]))
						except:pass

	if sez=="!?!" and epd!="!?!":
		if ns>3:
					try: sez="s"+str(int(nst[:2]))
					except:
						try:sez="s"+str(int(nst[:1]))
						except:sez=="!?!"

	if sez=="!?!" and epd=="!?!":
					try:epd="e"+str(int(nst))
					except:
						try:
							tmp=float(nst)
							sez="s"+str(int(tmp))
							sss,eee=divmod(tmp, 1)
							epd="e"+str(eee*100).replace(".0","")
						except: pass

	if sez!="!?!" and epd=="!?!":
			ns=nst.find(">")
			if ns>0:
					try:epd="e"+str(int(nst[ns+1:].replace(".","")))
					except:epd=="!?!"


	if sez=="!?!" and epd!="!?!":
						try:
							e1=epd.replace("e","")+"#"
							tmp=float(nst.replace(e1,"0"))
							sez="s"+str(int(tmp))
						except: pass


	print sez+"\t:\t"+epd+"\t:\t"+nst
	return (sez,epd)



def find_e(txt):
	txt=txt.replace(" ","")
	L=['seriya#','#seriya','serija#','#serija', 'e#']
	for i in L:
		for i1 in range (0,200):
					n=200-i1
					sn1='00'+str(n)
					sn2='0'+str(n)
					sn3=str(n)
					n1=txt.find(i.replace("#",sn1))
					n2=txt.find(i.replace("#",sn2))
					n3=txt.find(i.replace("#",sn3))
					if n1>-1: return n
					if n2>-1: return n
					if n3>-1: return n
	if txt.find("sezon")<0 and txt.find("сезон")<0:
		for i in range (2000,2020):
			txt=txt.replace(str(i),"")
		txt=txt[:-3]
		for i in range (0,300):
			n=300-i
			n1=txt.find(str(n))
			if n1>-1: return n

	return -1
	

def find_s(txt):
	txt=txt.replace(" ","")
	
	L=['#sezon','sezon#','s#',eval(repr("#Сезон"))]#'#Сезон',u'Сезон#',u'#сезон',u'сезон#',
	for i in L:
		for i1 in range (0,20):
					n=20-i1
					sn1='0'+str(n)
					sn2=str(n)
					n1=txt.find(i.replace("#",sn1))
					n2=txt.find(i.replace("#",sn2))
					#print i.replace("#",sn2)
					if n1>-1: return n
					if n2>-1: return n
	return -1
	

def save_all(torr_link,img, info={}):
	TSplayer=TSengine()
	out=TSplayer.load_torrent(torr_link,'TORRENT')
	if out=='Ok':
		name=ru(info['originaltitle'])
		cn=name.find(" (")
		if cn>0:name=name[:cn]
		#+' ('+str(info['year'])+')'ru(urllib.unquote_plus(info['title']))#.decode('utf-8')
		SaveDirectory = os.path.join(ru(__settings__.getSetting("SaveDirectory2")), name)
		if os.path.isdir(SaveDirectory)==0: os.mkdir(SaveDirectory)
		if SaveDirectory=="":SaveDirectory=LstDir
		for k,v in TSplayer.files.iteritems():
			li = xbmcgui.ListItem(urllib.unquote(k))
			uri = construct_request({
				'torr_url': torr_link,
				'title': k.encode('utf-8'),
				'ind':v,
				'img':img,
				'func': 'play_url2',
				'mode': 'play_url2'
			})
			tts=urllib.unquote_plus(k)#.encode('utf-8')
			tts=tts.replace("\\",' ')
			try:tts=ru(os.path.basename(tts))#[nf+1:]
			except: tts=xt(os.path.basename(tts))
			tts=save_nfo(tts,img, info)
			fl = open(os.path.join(SaveDirectory, tts+".strm"), "w")
			fl.write(uri)
			fl.close()
			
		save_tvshow_nfo(tts,img, info)
	TSplayer.end()
	xbmc.executebuiltin('UpdateLibrary("video")')



from TSCore import TSengine as tsengine

def construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))

def play_url_old(params):
	torr_link=params['file']
	img=urllib.unquote_plus(params["img"])
	#showMessage('heading', torr_link, 10000)
	TSplayer=tsengine()
	out=TSplayer.load_torrent(torr_link,'TORRENT')
	if out=='Ok':
		for k,v in TSplayer.files.iteritems():
			li = xbmcgui.ListItem(urllib.unquote(k))
			uri = construct_request({
				'torr_url': torr_link,
				'title': k,
				'ind':v,
				'img':img,
				'mode': 'play_url2'
			})
			xbmcplugin.addDirectoryItem(handle, uri, li, False)
	xbmcplugin.endOfDirectory(handle)
	TSplayer.end()
	
def play_url2_old(params):
	#torr_link=params['torr_url']
	torr_link=urllib.unquote_plus(params["torr_url"])
	img=urllib.unquote_plus(params["img"])
	title=urllib.unquote_plus(params["title"])
	#showMessage('heading', torr_link, 10000)
	TSplayer=tsengine()
	out=TSplayer.load_torrent(torr_link,'TORRENT')
	if out=='Ok':
		TSplayer.play_url_ind(int(params['ind']),title, icon, img)
	TSplayer.end()

#-----------------------libtorrents-torrenter-by-slng--------------------------------
import Downloader
try:import Downloader
except: pass
def playTorrent(url, StorageDirectory):
		torrentUrl = url#__settings__.getSetting("lastTorrent")
		if 0 != len(torrentUrl):
			contentId = 0#int(urllib.unquote_plus(url))
			torrent = Downloader.Torrent(torrentUrl, StorageDirectory)
			torrent.startSession(contentId)
			iterator = 0
			progressBar = xbmcgui.DialogProgress()
			progressBar.create('Подождите', 'Идёт поиск сидов.')
			downloadedSize = 0
			while downloadedSize < (44 * 1024 * 1024): #not torrent.canPlay:
				time.sleep(0.1)
				progressBar.update(iterator)
				iterator += 1
				if iterator == 100:
					iterator = 0
				downloadedSize = torrent.torrentHandle.file_progress()[contentId]
				dialogText = 'Preloaded: ' + str(downloadedSize / 1024 / 1024) + ' MB / ' + str(torrent.getContentList()[contentId].size / 1024 / 1024) + ' MB'
				peersText = ' [%s: %s; %s: %s]' % ('Seeds', str(torrent.torrentHandle.status().num_seeds), 'Peers', str(torrent.torrentHandle.status().num_peers))
				speedsText = '%s: %s Mbit/s; %s: %s Mbit/s' % ('Downloading', str(torrent.torrentHandle.status().download_payload_rate * 8/ 1000000), 'Uploading', str(torrent.torrentHandle.status().upload_payload_rate * 8 / 1000000))
				progressBar.update(iterator, 'Seeds searching.' + peersText, dialogText, speedsText)
				if progressBar.iscanceled():
					progressBar.update(0)
					progressBar.close()
					torrent.threadComplete = True
					return
			progressBar.update(0)
			progressBar.close()
			playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
			playlist.clear()
			listitem = xbmcgui.ListItem(torrent.getContentList()[contentId].path)
			playlist.add('file:///' + torrent.getFilePath(contentId), listitem)
			progressBar.close()
			xbmc.Player().play(playlist)
			progressBar.close()
			time.sleep(15)
			while 1 == xbmc.Player().isPlayingVideo():
				torrent.fetchParts()
				torrent.checkThread()
				time.sleep(1)
			xbmc.executebuiltin("Notification(%s, %s)" % ('Информация', 'Загрузка торрента прекращена.'))
			torrent.threadComplete = True
		else:
			print " Unexpected access to method playTorrent() without torrent content"

#===========================================================

def ru(x):return unicode(x,'utf8', 'ignore')
def xt(x):return xbmc.translatePath(x)
def rt(x):
	L=[('&#39;','’'), ('&#145;','‘'), ('&#146;','’'), ('&#147;','“'), ('&#148;','”'), ('&#149;','•'), ('&#150;','–'), ('&#151;','—'), ('&#152;','?'), ('&#153;','™'), ('&#154;','s'), ('&#155;','›'), ('&#156;','?'), ('&#157;',''), ('&#158;','z'), ('&#159;','Y'), ('&#160;',''), ('&#161;','?'), ('&#162;','?'), ('&#163;','?'), ('&#164;','¤'), ('&#165;','?'), ('&#166;','¦'), ('&#167;','§'), ('&#168;','?'), ('&#169;','©'), ('&#170;','?'), ('&#171;','«'), ('&#172;','¬'), ('&#173;',''), ('&#174;','®'), ('&#175;','?'), ('&#176;','°'), ('&#177;','±'), ('&#178;','?'), ('&#179;','?'), ('&#180;','?'), ('&#181;','µ'), ('&#182;','¶'), ('&#183;','·'), ('&#184;','?'), ('&#185;','?'), ('&#186;','?'), ('&#187;','»'), ('&#188;','?'), ('&#189;','?'), ('&#190;','?'), ('&#191;','?'), ('&#192;','A'), ('&#193;','A'), ('&#194;','A'), ('&#195;','A'), ('&#196;','A'), ('&#197;','A'), ('&#198;','?'), ('&#199;','C'), ('&#200;','E'), ('&#201;','E'), ('&#202;','E'), ('&#203;','E'), ('&#204;','I'), ('&#205;','I'), ('&#206;','I'), ('&#207;','I'), ('&#208;','?'), ('&#209;','N'), ('&#210;','O'), ('&#211;','O'), ('&#212;','O'), ('&#213;','O'), ('&#214;','O'), ('&#215;','?'), ('&#216;','O'), ('&#217;','U'), ('&#218;','U'), ('&#219;','U'), ('&#220;','U'), ('&#221;','Y'), ('&#222;','?'), ('&#223;','?'), ('&#224;','a'), ('&#225;','a'), ('&#226;','a'), ('&#227;','a'), ('&#228;','a'), ('&#229;','a'), ('&#230;','?'), ('&#231;','c'), ('&#232;','e'), ('&#233;','e'), ('&#234;','e'), ('&#235;','e'), ('&#236;','i'), ('&#237;','i'), ('&#238;','i'), ('&#239;','i'), ('&#240;','?'), ('&#241;','n'), ('&#242;','o'), ('&#243;','o'), ('&#244;','o'), ('&#245;','o'), ('&#246;','o'), ('&#247;','?'), ('&#248;','o'), ('&#249;','u'), ('&#250;','u'), ('&#251;','u'), ('&#252;','u'), ('&#253;','y'), ('&#254;','?'), ('&#255;','y')]
	for i in L:
		x=x.replace(i[0], i[1])
	return x

def mfindal(http, ss, es):
	L=[]
	while http.find(es)>0:
		s=http.find(ss)
		e=http.find(es)
		i=http[s:e]
		L.append(i)
		http=http[e+2:]
	return L
def debug(s):
	fl = open(ru(os.path.join( addon.getAddonInfo('path'),"test.txt")), "w")
	fl.write(s)
	fl.close()

def inputbox():
	skbd = xbmc.Keyboard()
	skbd.setHeading('Поиск:')
	skbd.doModal()
	if skbd.isConfirmed():
		SearchStr = skbd.getText()
		return SearchStr
	else:
		return ""

def showMessage(heading, message, times = 3000):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))


def GET(target, referer, post_params = None, accept_redirect = True, get_redirect_url = False, siteUrl='www.KinoPoisk.ru'):
	try:
		connection = httplib.HTTPConnection(siteUrl)

		if post_params == None:
			method = 'GET'
			post = None
		else:
			method = 'POST'
			post = urllib.urlencode(post_params)
			headers['Content-Type'] = 'application/x-www-form-urlencoded'
		
		sid_file = os.path.join(xbmc.translatePath('special://temp/'), 'plugin.video.KinoPoisk.ru.cookies.sid')
		if os.path.isfile(sid_file):
			fh = open(sid_file, 'r')
			csid = fh.read()
			fh.close()
			headers['Cookie'] = 'session=%s' % csid

		headers['Referer'] = referer
		connection.request(method, target, post, headers = headers)
		response = connection.getresponse()

		if response.status == 403:
			raise Exception("Forbidden, check credentials")
		if response.status == 404:
			raise Exception("File not found")
		if accept_redirect and response.status in (301, 302):
			target = response.getheader('location', '')
			if target.find("://") < 0:
				target = httpSiteUrl + target
			if get_redirect_url:
				return target
			else:
				return GET(target, referer, post_params, False)

		try:
			sc = Cookie.SimpleCookie()
			sc.load(response.msg.getheader('Set-Cookie'))
			fh = open(sid_file, 'w')
			fh.write(sc['session'].value)
			fh.close()
		except: pass

		if get_redirect_url:
			return False
		else:
			http = response.read()
			return http

	except Exception, e:
		showMessage('Error', e, 5000)
		return None


def fs(s):
	s=str(repr(s))[1:-1]
	s=s.replace('\\xb8','ё')
	s=s.replace('\\xe0','a')
	s=s.replace('\\xe1','б')
	s=s.replace('\\xe2','в')
	s=s.replace('\\xe3','г')
	s=s.replace('\\xe4','д')
	s=s.replace('\\xe5','е')
	s=s.replace('\\xe6','ж')
	s=s.replace('\\xe7','з')
	s=s.replace('\\xe8','и')
	s=s.replace('\\xe9','й')
	s=s.replace('\\xea','к')
	s=s.replace('\\xeb','л')
	s=s.replace('\\xec','м')
	s=s.replace('\\xed','н')
	s=s.replace('\\xee','о')
	s=s.replace('\\xef','п')
	s=s.replace('\\xf0','р')
	s=s.replace('\\xf1','с')
	s=s.replace('\\xf2','т')
	s=s.replace('\\xf3','у')
	s=s.replace('\\xf4','ф')
	s=s.replace('\\xf5','х')
	s=s.replace('\\xf6','ц')
	s=s.replace('\\xf7','ч')
	s=s.replace('\\xf8','ш')
	s=s.replace('\\xf9','щ')
	s=s.replace('\\xfa','ъ')
	s=s.replace('\\xfb','ы')
	s=s.replace('\\xfc','ь')
	s=s.replace('\\xfd','э')
	s=s.replace('\\xfe','ю')
	s=s.replace('\\xff','я')
	
	s=s.replace('\\xa8','Ё')
	s=s.replace('\\xc0','А')
	s=s.replace('\\xc1','Б')
	s=s.replace('\\xc2','В')
	s=s.replace('\\xc3','Г')
	s=s.replace('\\xc4','Д')
	s=s.replace('\\xc5','Е')
	s=s.replace('\\xc6','Ж')
	s=s.replace('\\xc7','З')
	s=s.replace('\\xc8','И')
	s=s.replace('\\xc9','Й')
	s=s.replace('\\xca','К')
	s=s.replace('\\xcb','Л')
	s=s.replace('\\xcc','М')
	s=s.replace('\\xcd','Н')
	s=s.replace('\\xce','О')
	s=s.replace('\\xcf','П')
	s=s.replace('\\xd0','Р')
	s=s.replace('\\xd1','С')
	s=s.replace('\\xd2','Т')
	s=s.replace('\\xd3','У')
	s=s.replace('\\xd4','Ф')
	s=s.replace('\\xd5','Х')
	s=s.replace('\\xd6','Ц')
	s=s.replace('\\xd7','Ч')
	s=s.replace('\\xd8','Ш')
	s=s.replace('\\xd9','Щ')
	s=s.replace('\\xda','Ъ')
	s=s.replace('\\xdb','Ы')
	s=s.replace('\\xdc','Ь')
	s=s.replace('\\xdd','Э')
	s=s.replace('\\xde','Ю')
	s=s.replace('\\xdf','Я')
	
	s=s.replace('\\xab','"')
	s=s.replace('\\xbb','"')
	s=s.replace('\\r','')
	s=s.replace('\\n','\n')
	s=s.replace('\\t','\t')
	s=s.replace("\\x85",'...')
	s=s.replace("\\x97",'-')
	s=s.replace("\\xb7","·")
	s=s.replace("\\x96",'-')
	s=s.replace("\\x92",'')
	s=s.replace("\\xb9",'№')
	s=s.replace("\\xa0",' ')
	s=s.replace('&laquo;','"')
	s=s.replace('&raquo;','"')
	s=s.replace('&#38;','&')
	s=s.replace('&#233;','é')
	s=s.replace('&#232;','è')
	s=s.replace('&#224;','à')
	s=s.replace('&#244;','ô')
	s=s.replace('&#246;','ö')
	return s

def formatKP(str):
	str=str.strip()
	str=str.replace('%','%25')
	str=str.replace('&','%26')
	str=str.replace('?','%3F')
	str=str.replace('&','%26')
	str=str.replace('!','%21')
	str=str.replace(':','%3A')
	str=str.replace('#','%23')
	str=str.replace(',','%2C')
	str=str.replace(';','%3B')
	str=str.replace('@','%40')
	str=str.replace('(','%28')
	str=str.replace(')','%29')
	str=str.replace('"','%22')
	
	str=str.replace('а','%E0')
	str=str.replace('б','%E1')
	str=str.replace('в','%E2')
	str=str.replace('г','%E3')
	str=str.replace('д','%E4')
	str=str.replace('е','%E5')
	str=str.replace('ё','%b8')
	str=str.replace('ж','%E6')
	str=str.replace('з','%E7')
	str=str.replace('и','%E8')
	str=str.replace('й','%E9')
	str=str.replace('к','%EA')
	str=str.replace('л','%EB')
	str=str.replace('м','%EC')
	str=str.replace('н','%ED')
	str=str.replace('о','%EE')
	str=str.replace('п','%EF')
	str=str.replace('р','%F0')
	str=str.replace('с','%F1')
	str=str.replace('т','%F2')
	str=str.replace('у','%F3')
	str=str.replace('ф','%F4')
	str=str.replace('х','%F5')
	str=str.replace('ц','%F6')
	str=str.replace('ч','%F7')
	str=str.replace('ш','%F8')
	str=str.replace('щ','%F9')
	str=str.replace('ъ','%FA')
	str=str.replace('ы','%FB')
	str=str.replace('ь','%FC')
	str=str.replace('э','%FD')
	str=str.replace('ю','%FE')
	str=str.replace('я','%FF')
	
	str=str.replace('А','%C0')
	str=str.replace('Б','%C1')
	str=str.replace('В','%C2')
	str=str.replace('Г','%C3')
	str=str.replace('Д','%C4')
	str=str.replace('Е','%C5')
	str=str.replace('Ё','%A8')
	str=str.replace('Ж','%C6')
	str=str.replace('З','%C7')
	str=str.replace('И','%C8')
	str=str.replace('Й','%C9')
	str=str.replace('К','%CA')
	str=str.replace('Л','%CB')
	str=str.replace('М','%CC')
	str=str.replace('Н','%CD')
	str=str.replace('О','%CE')
	str=str.replace('П','%CF')
	str=str.replace('Р','%D0')
	str=str.replace('С','%D1')
	str=str.replace('Т','%D2')
	str=str.replace('У','%D3')
	str=str.replace('Ф','%D4')
	str=str.replace('Х','%D5')
	str=str.replace('Ц','%D6')
	str=str.replace('Ч','%D7')
	str=str.replace('Ш','%D8')
	str=str.replace('Щ','%D9')
	str=str.replace('Ь','%DA')
	str=str.replace('Ы','%DB')
	str=str.replace('Ъ','%DC')
	str=str.replace('Э','%DD')
	str=str.replace('Ю','%DE')
	str=str.replace('Я','%DF')

	str=str.replace(' ','+')
	return str

def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
	return param



import sqlite3 as db
db_name = os.path.join( addon.getAddonInfo('path'), "move_info.db" )
c = db.connect(database=db_name)
cu = c.cursor()
def add_to_db(n, item):
		item=item.replace("'","XXCC").replace('"',"XXDD")
		err=0
		tor_id="n"+n
		litm=str(len(item))
		try:
			cu.execute("CREATE TABLE "+tor_id+" (db_item VARCHAR("+litm+"), i VARCHAR(1));")
			c.commit()
		except: 
			err=1
			print "Ошибка БД"
		if err==0:
			cu.execute('INSERT INTO '+tor_id+' (db_item, i) VALUES ("'+item+'", "1");')
			c.commit()
			#c.close()

def get_inf_db(n):
		tor_id="n"+n
		cu.execute(str('SELECT db_item FROM '+tor_id+';'))
		c.commit()
		Linfo = cu.fetchall()
		info=Linfo[0][0].replace("XXCC","'").replace("XXDD",'"')
		return info


def s2kp(id, info):
	try:
		
		import tokp
		skp=tokp.Tracker()
		RL = skp.Search(id)
		if len(RL)>0:
			Title = "[COLOR F050F050]"+"[--------------  «Tracker.ru»  "+id+" --------------]"+"[/COLOR]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
			
			for itm in RL:
				Title = "|"+itm[0]+"|"+itm[1]+"|  "+itm[2]
				row_url = itm[3]
				#print row_url
				cover=""
				dict={}
				listitem = xbmcgui.ListItem(Title, thumbnailImage=cover, iconImage=cover)
				try:listitem.setInfo(type = "Video", infoLabels = dict)
				except: pass
				listitem.setProperty('fanart_image', cover)
				purl = sys.argv[0] + '?mode=OpenTorrent'\
					+ '&url=' + urllib.quote_plus(row_url)\
					+ '&title=' + urllib.quote_plus(info['title'])\
					+ '&info=' + urllib.quote_plus(repr(info))
				xbmcplugin.addDirectoryItem(handle, purl, listitem, True, len(RL))
		return len(RL)
	except:
		return 0


def fileek(qury, info):
	try:
		
		import fileek
		skp=fileek.Tracker()
		RL = skp.Search(qury)
		if len(RL)>0:
			Title = "[COLOR F050F050]"+"[--------------  «Fileek.com»  "+qury+" --------------]"+"[/COLOR]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
			
			for itm in RL:
				Title = "|"+itm[0]+"|"+itm[1]+"|  "+itm[2]
				row_url = itm[3]
				#print row_url
				cover=""
				dict={}
				info['url']=row_url
				listitem = xbmcgui.ListItem(Title, thumbnailImage=cover, iconImage=cover)
				try:listitem.setInfo(type = "Video", infoLabels = dict)
				except: pass
				listitem.setProperty('fanart_image', cover)
				purl = sys.argv[0] + '?mode=OpenTorrent'\
					+ '&url=' + urllib.quote_plus(row_url)\
					+ '&title=' + urllib.quote_plus(info['title'])\
					+ '&info=' + urllib.quote_plus(repr(info))
				
				listitem.addContextMenuItems([('[B]Сохранить сериал[/B]', 'Container.Update("plugin://plugin.video.KinoPoisk.ru/?mode=save_all&url='+row_url+'&info='+urllib.quote_plus(repr(info))+'")'),])
				xbmcplugin.addDirectoryItem(handle, purl, listitem, True, len(RL))
		return len(RL)
	except:
		return 0



def srr(text, info={}):
	import RuTrackerOrg
	rtr=RuTrackerOrg.RuTrackerOrg()
	
	RL=rtr.search(text)
	if len(RL)>0:
		Title = "[COLOR F050F050]"+"[------- «RuTracker.Org»  "+text+" ---------]"+"[/COLOR]"
		row_url = Title
		listitem = xbmcgui.ListItem(Title)
		listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
		purl = sys.argv[0] + '?mode=Search'\
			+ '&url=' + urllib.quote_plus(row_url)\
			+ '&title=' + urllib.quote_plus(Title)\
			+ '&text=' + urllib.quote_plus('0')
		xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
		
	for itm in RL:
				Title = "|"+str(itm[0])+"|  "+itm[2]
				row_url = itm[3]
				cover=""
				dict={}
				listitem = xbmcgui.ListItem(Title, thumbnailImage=cover, iconImage=cover)
				try:listitem.setInfo(type = "Video", infoLabels = dict)
				except: pass
				listitem.setProperty('fanart_image', cover)
				purl = sys.argv[0] + '?mode=OpenTorrent'\
					+ '&url=' + urllib.quote_plus(row_url)\
					+ '&title=' + urllib.quote_plus(info['title'])\
					+ '&info=' + urllib.quote_plus(repr(info))
				xbmcplugin.addDirectoryItem(handle, purl, listitem, True, len(RL))

	return len(RL)

def rutor(text, info={}):
	#try:
	import rutors
	rtr=rutors.Tracker()
	#except: pass
	
	RL=rtr.Search(text, "0")
	if len(RL)>0:
		Title = "[COLOR F050F050]"+"[------- «Rutor»  "+text+" ---------]"+"[/COLOR]"
		row_url = Title
		listitem = xbmcgui.ListItem(Title)
		listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
		purl = sys.argv[0] + '?mode=Search'\
			+ '&url=' + urllib.quote_plus(row_url)\
			+ '&title=' + urllib.quote_plus(Title)\
			+ '&text=' + urllib.quote_plus('0')
		xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
		
	for y in range (1970, 2018):
		sy=" "+str(y)
		text=text.replace(sy,"")

	for itm in RL:
		if itm[2].find(text)>=0:
				Title = "|"+itm[0]+"|"+itm[1]+"|  "+itm[2]
				row_url = itm[3]
				cover=""
				dict={}
				listitem = xbmcgui.ListItem(Title, thumbnailImage=cover, iconImage=cover)
				try:listitem.setInfo(type = "Video", infoLabels = dict)
				except: pass
				listitem.setProperty('fanart_image', cover)
				purl = sys.argv[0] + '?mode=OpenTorrent'\
					+ '&url=' + urllib.quote_plus(row_url)\
					+ '&title=' + urllib.quote_plus(info['title'])\
					+ '&info=' + urllib.quote_plus(repr(info))
				listitem.addContextMenuItems([('[B]Сохранить сериал[/B]', 'Container.Update("plugin://plugin.video.KinoPoisk.ru/?mode=save_all&url='+row_url+'&info='+urllib.quote_plus(repr(info))+'")'),])
				xbmcplugin.addDirectoryItem(handle, purl, listitem, True, len(RL))
	return len(RL)

def rutoris(text, info={}):
	#try:
	import rutor_is
	rtr=rutor_is.Tracker()
	#except: pass
	
	RL=rtr.Search(text, "0")
	if len(RL)>0:
		Title = "[COLOR F050F050]"+"[------- «Rutor.is»  "+text+" ---------]"+"[/COLOR]"
		row_url = Title
		listitem = xbmcgui.ListItem(Title)
		listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
		purl = sys.argv[0] + '?mode=Search'\
			+ '&url=' + urllib.quote_plus(row_url)\
			+ '&title=' + urllib.quote_plus(Title)\
			+ '&text=' + urllib.quote_plus('0')
		xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

	for itm in RL:
				Title = "|"+itm[0]+"|"+itm[1]+"|  "+itm[2]
				row_url = itm[3]
				cover=""
				dict={}
				listitem = xbmcgui.ListItem(Title, thumbnailImage=cover, iconImage=cover)
				try:listitem.setInfo(type = "Video", infoLabels = dict)
				except: pass
				listitem.setProperty('fanart_image', cover)
				purl = sys.argv[0] + '?mode=OpenTorrent'\
					+ '&url=' + urllib.quote_plus(row_url)\
					+ '&title=' + urllib.quote_plus(info['title'])\
					+ '&info=' + urllib.quote_plus(repr(info))
				listitem.addContextMenuItems([('[B]Сохранить сериал[/B]', 'Container.Update("plugin://plugin.video.KinoPoisk.ru/?mode=save_all&url='+row_url+'&info='+urllib.quote_plus(repr(info))+'")'),])
				xbmcplugin.addDirectoryItem(handle, purl, listitem, True, len(RL))
	return len(RL)


def dugtor(text, info={}):
	#try:
	import dugtor
	rtr=dugtor.Tracker()
	#except: pass
	
	try:RL=rtr.Search(text, "0")
	except: RL=[]
	if len(RL)>0:
		Title = "[COLOR F050F050]"+"[------- «Dugtor.ru»  "+text+" ---------]"+"[/COLOR]"
		row_url = Title
		listitem = xbmcgui.ListItem(Title)
		listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
		purl = sys.argv[0] + '?mode=Search'\
			+ '&url=' + urllib.quote_plus(row_url)\
			+ '&title=' + urllib.quote_plus(Title)\
			+ '&text=' + urllib.quote_plus('0')
		xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
		
	for y in range (1970, 2018):
		sy=" "+str(y)
		text=text.replace(sy,"")

	for itm in RL:
		if xt(itm[2]).find(text)>=0:
				Title = "|"+itm[0]+"|"+itm[1]+"|  "+itm[2]
				row_url = itm[3]
				cover=""
				dict={}
				listitem = xbmcgui.ListItem(Title, thumbnailImage=cover, iconImage=cover)
				try:listitem.setInfo(type = "Video", infoLabels = dict)
				except: pass
				listitem.setProperty('fanart_image', cover)
				purl = sys.argv[0] + '?mode=OpenTorrent'\
					+ '&url=' + urllib.quote_plus(row_url)\
					+ '&title=' + info['title']\
					+ '&info=' + urllib.quote_plus(repr(info))
				listitem.addContextMenuItems([('[B]Сохранить сериал[/B]', 'Container.Update("plugin://plugin.video.KinoPoisk.ru/?mode=save_all&url='+row_url+'&info='+urllib.quote_plus(repr(info))+'")'),])
				xbmcplugin.addDirectoryItem(handle, purl, listitem, True, len(RL))
	return len(RL)



def stft(text, info={}):
	try:
		import krasfs
		tft=krasfs.Tracker()
	
		RL=tft.Search(text, 4)
		if len(RL)>0:
			Title = "[COLOR F050F050]"+"[------- «KrasFS.ru»  "+text+" ---------]"+"[/COLOR]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			for itm in RL:
				Title = "|"+itm[0]+"|"+itm[1]+"|  "+itm[2]
				row_url = itm[3]
				cover=""
				dict={}
				info['url']=itm[3]
				listitem = xbmcgui.ListItem(Title, thumbnailImage=cover, iconImage=cover)
				try:listitem.setInfo(type = "Video", infoLabels = dict)
				except: pass
				listitem.setProperty('fanart_image', cover)
				purl = sys.argv[0] + '?mode=OpenTorrent'\
					+ '&url=' + urllib.quote_plus(row_url)\
					+ '&title=' + urllib.quote_plus(Title)\
					+ '&info=' + urllib.quote_plus(repr(info))
				listitem.addContextMenuItems([('Сохранить все', 'Container.Update("plugin://plugin.video.KinoPoisk.ru/?mode=save_all&url='+itm[3]+'&info='+urllib.quote_plus(repr(info))+'")'),])
				xbmcplugin.addDirectoryItem(handle, purl, listitem, True, len(RL))
		return len(RL)
	except:
		return 0




def AddItem(Title = "", mode = "", info = {"cover":icon}, total=100):
			params["mode"] = mode
			params["info"] = info
			
			cover = info["cover"]
			try:fanart = info["fanart"]
			except: fanart = ''
			try:id = info["id"]
			except: id = ''

			listitem = xbmcgui.ListItem(Title, iconImage=cover)#, thumbnailImage=cover
			listitem.setInfo(type = "Video", infoLabels = info )
			listitem.setProperty('fanart_image', fanart)
			purl = sys.argv[0] + '?mode='+mode+ '&params=' + urllib.quote_plus(repr(params))
			if mode=="Torrents": 
				#listitem.addContextMenuItems([('Hайти похожие', 'SrcNavi("Navigator:'+id+'")')])
				listitem.addContextMenuItems([('Hайти похожие', 'Container.Update("plugin://plugin.video.KinoPoisk.ru/?mode=Recomend&id='+id+'")'), ('Персоны', 'Container.Update("plugin://plugin.video.KinoPoisk.ru/?mode=Person&id='+id+'")')])
				xbmcplugin.addDirectoryItem(handle, purl, listitem, False, total)
			elif mode=="PersonFilm":
				listitem.addContextMenuItems([('Добавить в Персоны', 'Container.Update("plugin://plugin.video.KinoPoisk.ru/?mode=AddPerson&info='+urllib.quote_plus(repr(info))+'")'), ('Удалить из Персоны', 'Container.Update("plugin://plugin.video.KinoPoisk.ru/?mode=RemovePerson&info='+urllib.quote_plus(repr(info))+'")')])
				xbmcplugin.addDirectoryItem(handle, purl, listitem, True, total)
			else:xbmcplugin.addDirectoryItem(handle, purl, listitem, True, total)

def FC(s, color="FFFFFF00"):
	s="[COLOR "+color+"]"+s+"[/COLOR]"
	return s

def AddPerson(info):
		try:PL=eval(__settings__.getSetting("PersonList"))
		except: PL=[]
		if info not in PL: 
			PL.append(info)
			__settings__.setSetting(id="PersonList", value=repr(PL))

def RemovePerson(info):
		try:PL=eval(__settings__.getSetting("PersonList"))
		except: PL=[]
		NL=[]
		for i in PL:
				if i!=info: NL.append(i)
		__settings__.setSetting(id="PersonList", value=repr(NL))

def PersonList():
		try:PL=eval(__settings__.getSetting("PersonList"))
		except: PL=[]
		for i in PL:
			AddItem(fs(i["title"]), "PersonFilm", i, len(PL))

		#__settings__.setSetting(id="PersonList", value=repr(PL))

def Person():
	try:id = urllib.unquote_plus(get_params()["id"])
	except: id = ''
	link="http://m.kinopoisk.ru/cast/"+id+"/"

	ss='<dt>'
	se='</dd><dt>'
	http = GET (link, httpSiteUrl)
	L=mfindal(http, ss, se)
	
	for i in L:
		ss='<dt>'
		se='</dt><dd>'
		tb=mfindal(i, ss, se)[0][4:]
		AddItem(FC(fs(tb)), "", {"cover":icon}, len(L))
		
		ss='/person/'
		se='</a>'
		L2=mfindal(i, ss, se)
		for j in L2:
			n=j.find('/">')
			nm=j[n+3:]
			id=j[8:n]
			cover="http://st.kp.yandex.net/images/sm_actor/"+id+".jpg"
			cover="http://st.kp.yandex.net/images/actor_iphone/iphone360_"+id+".jpg"
			#.replace('sm_film/','film_iphone/iphone360_')+'.jpg'
			info={"cover":cover, "title":nm, "id":id}
			AddItem(fs(nm), "PersonFilm", info, len(L))



def SrcNavi(md="Navigator"):
	#ss="/level/1/film/"
	ss='id="film_eye_'
	#se='/">'
	se='"></div>'

	if md =="Navigator":
		Cats=getList("CutList")
		#Genres=getList("GenreList")
		Cantrys=getList("CantryList")
		Years=__settings__.getSetting("YearList")
		Old=__settings__.getSetting("OldList")
		Sort=__settings__.getSetting("SortList")
		Rating=__settings__.getSetting("RatingList")

		Cat=getList2("CatList")
		sCat=""
		for i in Cat:
			sCat=sCat+"m_act%5B"+str(CategoryDict[i])+"%5D/on/"
		if sCat == "m_act%5B%5D/on/" or sCat == "m_act%5Ball%5D/on/": sCat =""
	
		Cantry=getList2("CantryList")
		Cantrys=""
		for i in Cantry:
			Cantrys=Cantrys+","+str(CantryDict[i])
		Cantrys=Cantrys[1:]
		if Cantrys == "" or Cantrys == "0": sCantry =""
		else: sCantry = "m_act%5Bcountry%5D/"+ Cantrys+"/"

		Genre=getList2("GenreList")
		Genres=""
		for i in Genre:
			Genres=Genres+","+str(GenreDict[i])
		Genres=Genres[1:]
		if Genres == "" or Genres == "0": sGenre =""
		else: sGenre = "m_act%5Bgenre%5D/"+ Genres+"/"

		try:YearId = YearDict[Years]
		except:YearId="0"
		if YearId == "0": sYear = ""
		else: sYear = "m_act%5Bdecade%5D/"+ YearId+"/"
	
		try:OldId = OldDict[Old]
		except:OldId=""
		if OldId == "": sOld = ""
		else: sOld = "m_act%5Brestriction%5D/"+ OldId+"/"
	
		try:RatingId = RatingDict[Rating]
		except:RatingId=""
		if RatingId == "": sRating = ""
		else: sRating = "m_act%5Brating%5D/"+ RatingId+":/"
	
		try:sSort = SortDict[Sort]
		except:sSort = "order/rating"
		
		if sCat.find("is_serial%5D/on")<0 and sCat!="": sGenre=sGenre+"m_act%5Begenre%5D/999/"
		#print sCat
		#print sGenre
		link=httpSiteUrl+"/top/navigator/"+sGenre+sCantry+sYear+sRating+sOld+sCat+sSort+"/perpage/100/#results"
		
		if link=="http://www.KinoPoisk.ru/top/navigator/order/rating/perpage/100/#results": 
			link="http://www.KinoPoisk.ru/top/navigator/m_act%5Brating%5D/7:/order/rating/perpage/100/#results"
			
			
	elif md=="Popular": link="http://www.kinopoisk.ru/top/lists/186/filtr/all/sort/order/perpage/200/"
	elif md=="New": link="http://www.kinopoisk.ru/top/lists/222/"
	elif md=="Future": 
		#link="http://www.kinopoisk.ru/top/lists/220/"
		link="http://www.kinopoisk.ru/comingsoon/sex/all/sort/date/period/halfyear/"
		ss='id="top_film_'
		se='" class="item" style="z'
	elif md=="Recomend": 
		try:id = urllib.unquote_plus(get_params()["id"])
		except: id = ''
		link="http://www.kinopoisk.ru/film/"+id+"/like/"
		#print link
	elif md=="PersonFilm":
		id = params["info"]["id"]
		#try:id = eval(urllib.unquote_plus(get_params()["info"]))["id"]
		#except: id = ''
		link="http://m.kinopoisk.ru/person/"+id+"/"
		ss="m.kinopoisk.ru/movie/"
		se='/">'
		#print link

	else: 
		link='http://www.kinopoisk.ru/index.php?first=no&what=&kp_query='+formatKP(md)
		ss="/level/1/film/"
		se='/sr/1/">'
	
	http = GET (link, httpSiteUrl)
	#debug (http)
	
	#ss="/level/1/film/"
	#ss='id="film_eye_'
	#se='/">'
	#se='"></div>'
	L=mfindal(http, ss, se)
	#debug (str(L))
	L2=[]
	for i in L:
		if i not in L2 and i<>"": L2.append(i)
	#debug (str(L2))
	for i in L2[:-1]:#
		FilmID=i[len(ss):]
		#info=eval(xt(get_inf_db(FilmID)))
		try:
			info=eval(xt(get_inf_db(FilmID)))
			nru=info["title"]
			rating_kp=info["rating"]
			if rating_kp>0: rkp=str(rating_kp)[:3]
			else: rkp= " - - "
			info["id"] = FilmID
			#AddItem("[ "+rkp+" ] "+nru, "Torrents", info, len(L2)-2)
			#print " OK: "+nru 
		except:
#		if len(i)>10:
			url="http://m.kinopoisk.ru/movie/"+i[len(ss):]
			http = GET (url, httpSiteUrl)
			http = rt(http)
			#debug (http)
			# ------------- ищем описание -----------------
			s='<div id="content">'
			e='<br><div class="city">'
			try: Info=mfindal(http, s, e)[0]
			except: Info=""
			#debug (Info)
			# ------------- название -----------------
			s='<p class="title">'
			e='<img src="http://m.kinopoisk.ru/images/star'
			if Info.find(e)<0: e='<div class="block film">'
			try: 
				nbl=mfindal(Info, s, e)[0][len(s):]
			except:
				nbl=""
			if nbl <> "":
				# ---------------- ru -------------------
				s='<b>'
				e='</b>'
				nru=mfindal(nbl, s, e)[0][len(s):]
				
				# ---------------- en yar time -------------------
				s='<span>'
				e='</span>'
				nen=mfindal(nbl, s, e)[0][len(s):]
				vrn=nen.replace("'","#^").replace(",", "','")
				tmps="['"+vrn+"']"
				Lt=eval(tmps)
				n=len(Lt)
				year=0
				duration=""
				for i in Lt:
					try: year=int(i)
					except: pass
					if i[-1:]==".": duration=i
				if year>0: n2= nen.find(str(year))
				else: n2=-1
				if duration<>"":n3=nen.find(duration)
				else: n3=-1
				if n3>0 and n3<n2: n2=n3
				if n2>1: nen=nen[:n2-2]
				else: nen=nru
				
				# ---------------- жанр  страна ----------
				s='<div class="block film">'
				e='<span class="clear"'
				try:
					b2=mfindal(Info, s, e)[0][len(s):]
					s='<span>'
					e='</span>'
					genre=mfindal(b2, s, e)[0][len(s):]
					studio=mfindal(b2, s, e)[1][len(s):]
				except:
					genre=""
					studio=""
				# ---------------- режисер ----------
				s='<span class="clear">'
				e='</a></span>'
				try:
					directors=mfindal(Info, s, e)[0][len(s):]
					s='/">'
					e='</a>'
					try: 
						director1=mfindal(directors, s, e)[0][len(s):]
						nn=directors.rfind('/">')
						director=director1+", "+directors[nn+3:]
					except:
						nn=directors.rfind('/">')
						director=directors[nn+3:]
				except:
					director=""
					
				# --------------- актеры ------------
				if director!="":
					s=directors#'<span class="clear">'
					e='<p class="descr">'
					if Info.find(e)<0:e='">...</a>'
					
					try:bcast=mfindal(Info, s, e)[0][len(s):]
					except: bcast=""
					s='/">'
					e='</a>,'
					lcast=mfindal(bcast, s, e)
					cast=[]
					for i in lcast:
						cast.append(fs(i[3:]))
				else:
					cast=[]
				# ----------------  описание ----------
				s='<p class="descr">'
				e='<span class="link">'
				if Info.find(e)<0: e='<p class="margin"'
				#debug (Info)
				try:plotand=mfindal(Info, s, e)[0][len(s):]
				except:plotand=""# -----------------------------------------------------------  доделать ----------
				nn=plotand.find("</p>")
				plot=plotand[:nn].replace("<br>","").replace("<br />","")
				# ----------------- оценки ------------
				tale=plotand[nn:]
				s='</b> <i>'
				e='</i> ('
				ratings=mfindal(Info, s, e)
				try:rating_kp=float(ratings[0][len(s):])
				except:rating_kp=0
				try:rating_IMDB=float(ratings[1][len(s):])
				except: rating_IMDB=0
				
				
				# ------------------ обложка ----------
				s='http://st.kp.yandex.net/images/sm_'
				e='.jpg" width="'
				try:cover=mfindal(Info, s, e)[0].replace('sm_film/','film_iphone/iphone360_')+'.jpg'
				except:cover="http://st.kp.yandex.net/images/image_none_no_border.gif"
				# ------------------ фанарт ----------
				s='http://st.kp.yandex.net/images/kadr'
				e='.jpg"/></div>'
				try:fanart=mfindal(Info, s, e)[0].replace('sm_','')+'.jpg'
				except:fanart=""
				
				info = {"title":fs(nru), 
						"originaltitle":fs(nen), 
						"year":year, 
						"duration":duration[:-5], 
						"genre":fs(genre), 
						"studio":fs(studio),
						"director":fs(director),
						"cast":cast,
						"rating":rating_kp,
						"cover":cover,
						"fanart":fanart,
						"plot":fs(plot)
						}
				info["id"] = FilmID
				if rating_kp>0: rkp=str(rating_kp)[:3]
				else: rkp= " - - "
				nru=fs(nru)
				#AddItem("[ "+rkp+" ] "+fs(nru), "Torrents", info, len(L2)-2)
				try:
					if rating_kp>0: add_to_db(FilmID, repr(info))
					#print "ADD: " + FilmID
				except:
					print "ERR: " + FilmID
					#print repr(info)
		try: AddItem("[ "+rkp+" ] "+ nru, "Torrents", info, len(L2)-2)
		except: pass


#==============  Menu  ====================
def Root():
	AddItem("Поиск", "Search")
	AddItem("Навигатор", "Navigator")
	AddItem("Популярные", "Popular")
	AddItem("Недавние премьеры", "New")
	AddItem("Самые ожидаемые", "Future")
	AddItem("Персоны", "PersonList")
	#AddItem("Параметры", "Par")

def Search():
	SrcNavi(inputbox())

def PersonSearch():
	PS=inputbox()
	link='http://www.kinopoisk.ru/index.php?first=no&what=&kp_query='+formatKP(PS)
	http = GET (link, httpSiteUrl)
	ss='http://st.kp.yandex.net/images/sm_actor/'
	es='" title="'
	l1=mfindal(http,ss,es)
	for i in l1:
		if len(i) > 45 and len(i)< 550:
			n=i.find('.jpg" alt="')
			id=i[len(ss):n]
			nm=i[n+11:]
			cover='http://st.kp.yandex.net/images/actor_iphone/iphone360_'+id+".jpg"
			info={"cover":cover, "title":nm, "id":id}
			if len(nm)>0 and len(id)>0 :AddItem(fs(nm), "PersonFilm", info, len(l1))
	#debug (http)


def getList(id):
	try:L = eval(__settings__.getSetting(id))
	except:L =[]
	S=""
	for i in L:
		if i[:1]=="[": S=S+", "+i
	return S[1:]

def getList2(id):
	try:L = eval(__settings__.getSetting(id))
	except:L =[]
	S=[]
	for i in L:
		if i[:1]=="[": S.append(i.replace("[COLOR FFFFFF00]","").replace("[/COLOR]",""))
	return S



def setList(idw, L):
	__settings__.setSetting(id=idw, value=repr(L))

def Navigator():
	Cats=getList("CatList")
	Genres=getList("GenreList")
	Cantrys=getList("CantryList")
	Years=__settings__.getSetting("YearList")
	Old=__settings__.getSetting("OldList")
	Sort=__settings__.getSetting("SortList")
	Rating=__settings__.getSetting("RatingList")
	
	if Cats=="": Cats="[COLOR FFFFFF00] --[/COLOR]"
	if Genres=="": Genres="[COLOR FFFFFF00]  --[/COLOR]"
	if Cantrys=="": Cantrys="[COLOR FFFFFF00] --[/COLOR]"
	if Years=="": Years="--"
	if Old=="": Old="--"
	if Rating=="": Rating="> 7"
	if Sort=="": Sort="рейтингу Кинопоиска"
	
	AddItem("Категории: " +Cats,    "SelCat")
	AddItem("Жанры:      " +Genres,  "SelGenre")
	AddItem("Страны:      " +Cantrys, "SelCantry")
	AddItem("Год:             [COLOR FFFFFF00]" +Years+"[/COLOR]",   "SelYear")
	AddItem("Возраст:      [COLOR FFFFFF00]" +Old+"[/COLOR]",     "SelOld")
	AddItem("Рейтинг:      [COLOR FFFFFF00]" +Rating+"[/COLOR]",  "SelRating")
	AddItem("Порядок:      [COLOR FFFFFF00]по " +Sort+"[/COLOR]",    "SelSort")
	
	AddItem("[B][COLOR FF00FF00][ Искать ][/COLOR][/B]", "SrcNavi")

def Popular():
	AddItem("Популярные", "Popular")

def New():
	AddItem("Недавние премьеры", "New")

def Future():
	AddItem("Самые ожидаемые", "Future")


Category=[]
CategoryDict={}
for i in TypeList:
	Category.append(i[1])
	CategoryDict[i[1]]=i[0]

Genre=[]
GenreDict={}
for i in GenreList:
	Genre.append(i[1])
	GenreDict[i[1]]=i[0]

Cantry=[]
CantryDict={}
for i in CantryList:
	Cantry.append(i[1])
	CantryDict[i[1]]=i[0]

Year=[]
YearDict={}
for i in YearList:
	Year.append(i[1])
	YearDict[i[1]]=i[0]

Old=[]
OldDict={}
for i in OldList:
	Old.append(i[1])
	OldDict[i[1]]=i[0]

Sort=[]
SortDict={}
for i in SortList:
	Sort.append(i[1])
	SortDict[i[1]]=i[0]

Rating=[]
RatingDict={}
for i in RatingList:
	Rating.append(i[1])
	RatingDict[i[1]]=i[0]

try:    url = eval(urllib.unquote_plus(get_params()["url"]))
except: url = ""
try:    info = eval(urllib.unquote_plus(get_params()["info"]))
except: info = {}

try:    params = eval(urllib.unquote_plus(get_params()["params"]))
except: params = {}

try: mode = urllib.unquote_plus(get_params()["mode"])
except: 
	try:mode = params["mode"]
	except:mode = None

try:ind = int(params["ind"])
except:ind = 0


if mode == None:
	setList("CatList", Category)
	setList("GenreList", Genre)
	setList("CantryList", Cantry)
	__settings__.setSetting(id="YearList", value="")
	__settings__.setSetting(id="OldList", value="")
	__settings__.setSetting(id="SortList", value="")
	__settings__.setSetting(id="RatingList", value="")

	Root()
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)
		
if mode == "Search":
	Search()
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)
		
if mode == "Navigator":
	Navigator()
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

if mode == "Popular":
	SrcNavi("Popular")
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

if mode == "New":
	SrcNavi("New")
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

if mode == "Future":
	SrcNavi("Future")
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)
	
if mode == "Recomend":
	#xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	#xbmcplugin.endOfDirectory(handle)
	#xbmc.sleep(1000)
	SrcNavi("Recomend")
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

if mode == "PersonFilm":
	SrcNavi("PersonFilm")#+PeID
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

if mode == "Person":
	Person()
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

if mode == "PersonList":
	AddItem("[ Поиск ]", "PersonSearch")
	PersonList()
	xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

if mode=="PersonSearch": 
	PersonSearch()
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

if mode=="AddPerson": 
	AddPerson(info)


if mode=="RemovePerson": 
	RemovePerson(info)
	xbmc.executebuiltin("Container.Refresh()")
	
if mode == "SrcNavi":
	SrcNavi()
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

if mode == "SelCat":
	SelectBox.run("CatList")

if mode == "SelGenre":
	SelectBox.run("GenreList")
	
if mode == "SelCantry":
	SelectBox.run("CantryList")
	
if mode == "SelYear":
	sel = xbmcgui.Dialog()
	r = sel.select("Десятилетие:", Year)
	__settings__.setSetting(id="YearList", value=Year[r])

if mode == "SelOld":
	sel = xbmcgui.Dialog()
	r = sel.select("Возраст:", Old)
	__settings__.setSetting(id="OldList", value=Old[r])

if mode == "SelSort":
	sel = xbmcgui.Dialog()
	r = sel.select("Десятилетие:", Sort)
	__settings__.setSetting(id="SortList", value=Sort[r])

if mode == "SelRating":
	sel = xbmcgui.Dialog()
	r = sel.select("Десятилетие:", Rating)
	__settings__.setSetting(id="RatingList", value=Rating[r])

if mode == "Torrents":
	gty=sys.argv[0] + '?mode=Torrents2&params='+ urllib.quote_plus(repr(params))
	xbmc.executebuiltin("Container.Update("+gty+", "+gty+")")
	
if mode == "Torrents2":
	info=params["info"]
	id=params["info"]["id"]
	try:rus=params["info"]["title"].encode('utf8')
	except: rus=params["info"]["title"]
	try:en=params["info"]["originaltitle"].encode('utf8')
	except: en=params["info"]["originaltitle"]
	if rus == en:text = rus.replace("a","а")+" "+str(params["info"]["year"])
	else:text = params["info"]["originaltitle"]+" "+str(params["info"]["year"])#+" "+rus.replace("a","а")
	n=text.find("(")
	#if n>0: text = text[:n-1]
	text=rt(text)
	
	ttl=rutor(text, info)
	if ttl<1: ttl=rutoris(text, info)
	if ttl<1: rutor(rus.replace("a","а"), info)
	
	#ttl4=dugtor(text, info)
	try:dugtor(rus.replace("a","а"), info)
	except: pass
	
	ttl3=fileek(text, info)
	ttl2=s2kp(rus.replace("a","а"), info)
	ttl=ttl+ttl2
	#ttl=srr(text, info)+ttl
#	if ttl<15:
#		ttl=stft(text, info)
#	if ttl<6: 
#		n=en.find("(")
#		if n>0: text = en[:n-1]
#		else: text = en
#		ttl=stft(text, info)
#	if ttl<6: 
#		n=rus.find("(")
#		if n>0: text = rus.replace("a","а")[:n-1]
#		else: text = rus.replace("a","а")
#		ttl=stft(text, info)

	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)
	xbmc.sleep(300)
	xbmc.executebuiltin("Container.SetViewMode(51)")
	
if mode == "Par":
	text='Predator'
	text=u'хищник'
	#import rutors
	#rtr=rutors.Tracker()
	import dugtor
	rtr=dugtor.Tracker()

	try:
		L=rtr.Search(text, "0")
	except: 
		L=[]

	for y in range (1970, 2018):
		sy=" "+str(y)
		text=text.replace(sy,"")
	BL=['Трейлер', "Тизер"]
	WL=["DVDRip","bdrip","720р"]#
	for itm in L:
		b=0
		w1=0
		for i in BL:
			if itm[2].find(i)>0:b+=1
		for i in WL:
			if itm[2].lower().find(i)>0:w1+=1
		
		w=w1

		if xt(itm[2]).find(text)>=0 and b == 0 and w > 0:
				Title = "|"+itm[0]+"|"+itm[1]+"|  "+itm[2]
				row_url = itm[3]
				listitem = xbmcgui.ListItem(Title)
				purl = sys.argv[0] + '?mode=OpenTorrent'\
					+ '&url=' + urllib.quote_plus(row_url)\
					+ '&title=' + itm[2]
				xbmcplugin.addDirectoryItem(handle, purl, listitem, True, len(L))
	
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)
	xbmc.sleep(300)
	xbmc.executebuiltin("Container.SetViewMode(51)")

if mode == "OpenTorrent":
	url = urllib.unquote_plus(get_params()["url"])
	try:img=info["cover"]
	except: img=icon
	engine = __settings__.getSetting("Engine")
	#print "engine = "+str(engine)
	if engine==0 or engine=='0':
		info['namef']=urllib.unquote_plus(get_params()["title"])
		play_url(url,img,info)
	elif engine=="2":
		t2http_list(url,info)
	else:
		DownloadDirectory = __settings__.getSetting("DownloadDirectory")[:-1]#.replace("\\\\","\\")
		if DownloadDirectory=="":DownloadDirectory=LstDir
		playTorrent(url, DownloadDirectory)

elif mode == 'alter':
	alter(urllib.unquote_plus(get_params()["title"])[1:])

elif mode == 'play_url2':
	play_url2(get_params())

elif mode == 'save_strm':
	save_strm(get_params())
		
elif mode == 'save_all':
	try:url = urllib.unquote_plus(get_params()["url"])
	except:url = info['url']
	save_all(url,"",info)
		

elif mode == 't2http_play':
	try:url = urllib.unquote_plus(get_params()["url"])
	except:url = info['url']
	tthp.play(url, handle, ind, __settings__.getSetting("DownloadDirectory"))

c.close()