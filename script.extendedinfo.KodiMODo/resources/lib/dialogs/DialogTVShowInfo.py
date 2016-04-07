# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcgui
import ast
import urllib
from xbmcgui import Dialog
from ..Utils import *
from ..ImageTools import *
from ..TheMovieDB import *
from DialogBaseInfo import DialogBaseInfo
from ..WindowManager import wm
from ..OnClickHandler import OnClickHandler
from .. import VideoPlayer

PLAYER = VideoPlayer.VideoPlayer()
ch = OnClickHandler()


def get_tvshow_window(window_type):

    class DialogTVShowInfo(DialogBaseInfo, window_type):

        def __init__(self, *args, **kwargs):
            super(DialogTVShowInfo, self).__init__(*args, **kwargs)
            self.type = "TVShow"
            data = extended_tvshow_info(tvshow_id=kwargs.get('tmdb_id', False),
                                        dbid=self.dbid)
            if not data:
                return None
            self.info, self.data, self.account_states = data
            if "dbid" not in self.info:
                self.info['poster'] = get_file(self.info.get("poster", ""))
            self.info['ImageFilter'], self.info['ImageColor'] = filter_image(input_img=self.info.get("poster", ""),
                                                                             radius=25)
            self.listitems = [(150, self.data["similar"]),
                              (250, self.data["seasons"]),
                              (1450, self.data["networks"]),
                              (550, self.data["studios"]),
                              (650, merge_with_cert_desc(self.data["certifications"], "tv")),
                              (750, self.data["crew"]),
                              (850, self.data["genres"]),
                              (950, self.data["keywords"]),
                              (1000, self.data["actors"]),
                              (1150, self.data["videos"]),
                              (1250, self.data["images"]),
                              (1350, self.data["backdrops"])]

        def onInit(self):
            self.get_youtube_vids("%s tv" % (self.info['title']))
            super(DialogTVShowInfo, self).onInit()
            pass_dict_to_skin(data=self.info,
                              prefix="movie.",
                              window_id=self.window_id)
            super(DialogTVShowInfo, self).update_states()
            self.fill_lists()

        def onClick(self, control_id):
            super(DialogTVShowInfo, self).onClick(control_id)
            ch.serve(control_id, self)

        @ch.click(120)
        def browse_tvshow(self):
            self.close()
            xbmc.executebuiltin("ActivateWindow(videos,videodb://tvshows/titles/%s/)" % (self.dbid))

        @ch.click(750)
        @ch.click(1000)
        def credit_dialog(self):
            selection = xbmcgui.Dialog().select(heading=LANG(32151),
                                                list=[LANG(32009), LANG(32147)])
            if selection == 0:
                wm.open_actor_info(prev_window=self,
                                   actor_id=self.listitem.getProperty("id"))
            if selection == 1:
                self.open_credit_dialog(self.listitem.getProperty("credit_id"))

        @ch.click(150)
        def open_tvshow_dialog(self):
            wm.open_tvshow_info(prev_window=self,
                                tvshow_id=self.listitem.getProperty("id"),
                                dbid=self.listitem.getProperty("dbid"))

        @ch.click(250)
        def open_season_dialog(self):
            wm.open_season_info(prev_window=self,
                                tvshow_id=self.info["id"],
                                season=self.listitem.getProperty("season"),
                                tvshow=self.info['title'])

        @ch.click(550)
        def open_company_info(self):
            filters = [{"id": self.listitem.getProperty("id"),
                        "type": "with_companies",
                        "typelabel": LANG(20388),
                        "label": self.listitem.getLabel().decode("utf-8")}]
            wm.open_video_list(prev_window=self,
                               filters=filters)

        @ch.click(950)
        def open_keyword_info(self):
            filters = [{"id": self.listitem.getProperty("id"),
                        "type": "with_keywords",
                        "typelabel": LANG(32114),
                        "label": self.listitem.getLabel().decode("utf-8")}]
            wm.open_video_list(prev_window=self,
                               filters=filters)

        @ch.click(850)
        def open_genre_info(self):
            filters = [{"id": self.listitem.getProperty("id"),
                        "type": "with_genres",
                        "typelabel": LANG(135),
                        "label": self.listitem.getLabel().decode("utf-8")}]
            wm.open_video_list(prev_window=self,
                               filters=filters,
                               media_type="tv")

        @ch.click(1450)
        def open_network_info(self):
            filters = [{"id": self.listitem.getProperty("id"),
                        "type": "with_networks",
                        "typelabel": LANG(32152),
                        "label": self.listitem.getLabel().decode("utf-8")}]
            wm.open_video_list(prev_window=self,
                               filters=filters,
                               media_type="tv")

        @ch.click(445)
        def show_manage_dialog(self):
            manage_list = []
            manage_list.append(["Extended Info Settings", "Addon.OpenSettings(script.extendedinfo)"])
            if xbmc.getCondVisibility("system.hasaddon(plugin.video.genesis)"):
                manage_list.append(["Genesis Settings", "Addon.OpenSettings(plugin.video.genesis)"])
            if xbmc.getCondVisibility("system.hasaddon(plugin.video.salts)"):
                manage_list.append(["SALTS Settings", "Addon.OpenSettings(plugin.video.salts)"])
            if xbmc.getCondVisibility("system.hasaddon(script.icechannel)"):
                manage_list.append(["iStream Settings", "Addon.OpenSettings(script.icechannel)"])
            if xbmc.getCondVisibility("system.hasaddon(plugin.video.mutttsnutz)"):
                manage_list.append(["MuttsNutz Settings", "Addon.OpenSettings(plugin.video.mutttsnutz)"])
            if xbmc.getCondVisibility("system.hasaddon(plugin.video.phstreams)"):
                manage_list.append(["Phoenix Settings", "Addon.OpenSettings(plugin.video.phstreams)"])
            if xbmc.getCondVisibility("system.hasaddon(plugin.program.super.favourites)"):
                manage_list.append(["iSearch Settings", "Addon.OpenSettings(plugin.program.super.favourites)"])
            if xbmc.getCondVisibility("system.hasaddon(script.search.play2kd)"):
                manage_list.append(["[COLOR FFF35C9F]Search+Play[/COLOR]2KD Settings", "Addon.OpenSettings(script.search.play2kd)"])
            if xbmc.getCondVisibility("system.hasaddon(plugin.video.pulsar)"):
                manage_list.append(["Pulsar Settings", "Addon.OpenSettings(plugin.video.pulsar)"])
            title = self.info.get("TVShowTitle", "")
            if self.dbid:
                artwork_call = "RunScript(script.artwork.downloader,%s)"
                manage_list += [[LANG(413), artwork_call % ("mode=gui,mediatype=tv,dbid=" + self.dbid)],
                                [LANG(14061), artwork_call % ("mediatype=tv, dbid=" + self.dbid)],
                                [LANG(32101), artwork_call % ("mode=custom,mediatype=tv,dbid=" + self.dbid + ",extrathumbs")],
                                [LANG(32100), artwork_call % ("mode=custom,mediatype=tv,dbid=" + self.dbid)]]
            else:
                manage_list += [[LANG(32166), "RunPlugin(plugin://plugin.video.sickrage?action=addshow&show_name=%s)" % title]]
            # if xbmc.getCondVisibility("system.hasaddon(script.tvtunes)") and self.dbid:
            #     manage_list.append([LANG(32102), "RunScript(script.tvtunes,mode=solo&amp;tvpath=$ESCINFO[Window.Property(movie.FilenameAndPath)]&amp;tvname=$INFO[Window.Property(movie.TVShowTitle)])"])
            if xbmc.getCondVisibility("system.hasaddon(script.libraryeditor)") and self.dbid:
                manage_list.append([LANG(32103), "RunScript(script.libraryeditor,DBID=" + self.dbid + ")"])
            selection = xbmcgui.Dialog().select(heading=LANG(32133),
                                                list=[item[0] for item in manage_list])
            if selection == -1:
                return None
            for item in manage_list[selection][1].split("||"):
                xbmc.executebuiltin(item)

        @ch.click(446)
        def play_tvshow_not_in_library(self):
            themoviedb_id = str(self.info.get("id", ""))
            tvshow_dbid = str(self.info.get("dbid", ""))
            year = str(self.info.get("year", ""))
            premocktitle = self.info.get("TVShowTitle", "")
            mocktitle = premocktitle.replace("&", "%26")
            title = mocktitle.encode('utf-8')
            lowertitle = title.lower()
            slug = lowertitle.replace(" ", "-")
            imdbfind = 'http://www.imdb.com/xml/find?json=1&nr=1&tt=on&q='
            urltitle = urllib.quote_plus(title)
            imdburl = imdbfind+urltitle.replace(" ", "%20")
            imdbreq = urllib2.Request(imdburl)
            imdbresponse = urllib2.urlopen(imdbreq)
            imdblink = imdbresponse.read()
            imdbresponse.close()
            imdblink = imdblink.split('id":"tt', 1)
            imdblink = str(imdblink[1])
            imdblink = imdblink.split('"', 1)
            imdb_id = str(imdblink[0])
            tvdbfind = 'http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=tt'
            tvdburl = tvdbfind+imdb_id
            tvdbreq = urllib2.Request(tvdburl)
            tvdbresponse = urllib2.urlopen(tvdbreq)
            tvdblink = tvdbresponse.read()
            tvdbresponse.close()
            tvdblink = tvdblink.split('<seriesid>', 1)
            tvdblink = tvdblink[1]
            tvdblink = tvdblink.split('<', 1)
            tvdb_id = tvdblink[0]
            addon = xbmcaddon.Addon()
            maintvshowaddon = addon.getSetting('MainTVShowAddon')
            addplay = addon.getSetting('AddOrPlayTVShows')
            autoaddtvshow = addon.getSetting('AutoAddTVShow')
            language = xbmc.getLanguage()
            dialog = xbmcgui.Dialog()
            if xbmc.getCondVisibility("system.hasaddon(plugin.video.genesis)") and maintvshowaddon == 'Genesis' and addplay == 'Play':
                if autoaddtvshow == 'true':
                    xbmc.executebuiltin("RunPlugin(plugin://plugin.video.genesis/?action=tvshowToLibrary&tvshowtitle="+title+"&year="+year+"&imdb="+imdb_id+"&tvdb="+tvdb_id+")")
                preseason = dialog.numeric(0, 'Season?')
                if preseason == '' or preseason == 0:
                    preseason = "1"
                preepisode = dialog.numeric(0, 'Episode?')
                if preepisode == '' or preepisode == 0:
                    preepisode = "1"
                season = preseason.zfill(2)
                episode = preepisode.zfill(2)
                xbmc.executebuiltin("PlayMedia(plugin://plugin.video.genesis/?action=play&name="+title+" S"+season+"E"+episode+"&year="+year+"&imdb="+imdb_id+"&tvdb="+tvdb_id+"&season="+preseason+"&episode="+preepisode+"&show="+title+"&show_alt="+title+"&url=http://www.imdb.com/title/"+imdb_id+")")
                xbmc.executebuiltin("Notification("+maintvshowaddon+",Playing "+premocktitle+" S"+season+"E"+episode+",5000,special://home/addons/plugin.video.genesis/icon.png)")
                self.close()
            elif xbmc.getCondVisibility("system.hasaddon(plugin.video.genesis)") and maintvshowaddon == 'Genesis' and addplay == 'Add':
                xbmc.executebuiltin("RunPlugin(plugin://plugin.video.genesis/?action=tvshowToLibrary&tvshowtitle="+title+"&year="+year+"&imdb="+imdb_id+"&tvdb="+tvdb_id+")")
                xbmc.executebuiltin("Notification("+maintvshowaddon+",Adding "+premocktitle+" to Library,5000,special://home/addons/plugin.video.genesis/icon.png)")
            elif xbmc.getCondVisibility("system.hasaddon(plugin.video.salts)") and maintvshowaddon == 'SALTS' and addplay == 'Play':
                if autoaddtvshow == 'true':
                    xbmc.executebuiltin("RunPlugin(plugin://plugin.video.salts/?mode=add_to_library&title="+title+"&slug="+slug+"&video_type=TV Show&year="+year+")")
                preseason = dialog.numeric(0, 'Season?')
                if preseason == '' or preseason == 0:
                    preseason = "1"
                preepisode = dialog.numeric(0, 'Episode?')
                if preepisode == '' or preepisode == 0:
                    preepisode = "1"
                season = preseason.zfill(2)
                episode = preepisode.zfill(2)
                xbmc.executebuiltin("PlayMedia(plugin://plugin.video.salts/?episode="+preepisode+"&title="+title+"&season="+preseason+"&video_type=Episode&mode=get_sources&dialog=True&year="+year+"&slug="+slug+")")
                xbmc.executebuiltin("Notification("+maintvshowaddon+",Playing "+premocktitle+" S"+season+"E"+episode+",5000,special://home/addons/plugin.video.salts/icon.png)")
                self.close()
            elif xbmc.getCondVisibility("system.hasaddon(plugin.video.salts)") and maintvshowaddon == 'Salts' and addplay == 'Add':
                xbmc.executebuiltin("RunPlugin(plugin://plugin.video.salts/?mode=add_to_library&title="+title+"&slug="+slug+"&video_type=TV Show&year="+year+")")
                xbmc.executebuiltin("Notification("+maintvshowaddon+",Adding "+premocktitle+" to Library,5000,special://home/addons/plugin.video.salts/icon.png)")
            elif xbmc.getCondVisibility("system.hasaddon(script.icechannel)") and maintvshowaddon == 'iStream' and addplay == 'Play':
                if autoaddtvshow == 'true':
                    xbmc.executebuiltin("RunPlugin(plugin://script.icechannel/?indexer_id=IMDb&episode=&name="+title+"&title="+title+" %28"+year+"%29&item_title="+title+" %28"+year+"%29&season=&section=&video_type=tvshow&indexer=tv_shows&imdb_id=tt"+imdb_id+"&url=http%3A%2F%2Fimdb.com%2Ftitle%2Ftt"+imdb_id+"%2F&urls=&year="+year+"&item_mode=content&type=tv_seasons&mode=add_to_library)")
                preseason = dialog.numeric(0, 'Season?')
                if preseason == '' or preseason == 0:
                    preseason = "1"
                preepisode = dialog.numeric(0, 'Episode?')
                if preepisode == '' or preepisode == 0:
                    preepisode = "1"
                season = preseason.zfill(2)
                episode = preepisode.zfill(2)
                xbmc.executebuiltin("PlayMedia(plugin://script.icechannel/?episode="+preepisode+"&name="+title+"&season="+preseason+"&section=&indexer=tv_shows&library=true&imdb_id=tt"+imdb_id+"&video_type=episode&year="+year+"&type=tv_episodes&mode=file_hosts)")
                xbmc.executebuiltin("Notification("+maintvshowaddon+",Playing "+premocktitle+" S"+season+"E"+episode+",5000,special://home/addons/plugin.video.salts/icon.png)")
                self.close()
            elif xbmc.getCondVisibility("system.hasaddon(script.icechannel)") and maintvshowaddon == 'iStream' and addplay == 'Add':
                xbmc.executebuiltin("RunPlugin(plugin://script.icechannel/?indexer_id=IMDb&episode=&name="+title+"&title="+title+" %28"+year+"%29&item_title="+title+" %28"+year+"%29&season=&section=&video_type=tvshow&indexer=tv_shows&imdb_id=tt"+imdb_id+"&url=http%3A%2F%2Fimdb.com%2Ftitle%2Ftt"+imdb_id+"%2F&urls=&year="+year+"&item_mode=content&type=tv_seasons&mode=add_to_library)")
                xbmc.executebuiltin("Notification("+maintvshowaddon+",Adding "+premocktitle+" to Library,5000,special://home/addons/script.icechannel/icon.png)")
            elif xbmc.getCondVisibility("system.hasaddon(plugin.video.pulsar)") and xbmc.getCondVisibility("system.hasaddon(script.search.play2kd)") and maintvshowaddon == 'Search+Play2KD' and addplay == 'Play':
                preseason = dialog.numeric(0, 'Season?')
                if preseason == '' or preseason == 0:
                    preseason = "1"
                preepisode = dialog.numeric(0, 'Episode?')
                if preepisode == '' or preepisode == 0:
                    preepisode = "1"
                season = preseason.zfill(2)
                episode = preepisode.zfill(2)
                xbmc.executebuiltin("RunScript(script.search.play2kd,type=2,query="+title+" S"+season+"E"+episode+")")
                xbmc.executebuiltin("Notification("+maintvshowaddon+",Playing "+premocktitle+" S"+season+"E"+episode+",5000,special://home/addons/script.search.play2kd/icon.png)")
                self.close()
            elif xbmc.getCondVisibility("system.hasaddon(plugin.video.pulsar)") and xbmc.getCondVisibility("system.hasaddon(script.search.play2kd)") and maintvshowaddon == 'Search+Play2KD' and addplay == 'Add':
                if dialog.yesno('Add not (yet) available','Play Instead?'):
                    preseason = dialog.numeric(0, 'Season?')
                    if preseason == '' or preseason == 0:
                        preseason = "1"
                    preepisode = dialog.numeric(0, 'Episode?')
                    if preepisode == '' or preepisode == 0:
                        preepisode = "1"
                    season = preseason.zfill(2)
                    episode = preepisode.zfill(2)
                    xbmc.executebuiltin("RunScript(script.search.play2kd,type=2,query="+title+" S"+season+"E"+episode+")")
                    xbmc.executebuiltin("Notification("+maintvshowaddon+",Playing "+premocktitle+" S"+season+"E"+episode+",5000,special://home/addons/script.search.play2kd/icon.png)")
                    self.close()
            elif xbmc.getCondVisibility("system.hasaddon(plugin.program.super.favourites)") and maintvshowaddon == 'iSearch':
                if dialog.yesno('Add/Play not available for iSearch','Search Instead?'):
                    xbmc.executebuiltin("ActivateWindow(10025,plugin://plugin.program.super.favourites/?mode=0&keyword="+title+",return)")
                    xbmc.executebuiltin("Notification("+maintvshowaddon+","+premocktitle+",5000,special://home/addons/script.search.play2kd/icon.png)")
                    self.close()

        @ch.click(447)
        def show_appintegration_dialog(self):
            premocktitle = self.info.get("TVShowTitle", "")
            mocktitle = premocktitle.replace("&", "%26")
            title = mocktitle.encode('utf-8')
            manage_list = []
            manage_list.append(["Extended Info Settings", "Addon.OpenSettings(script.extendedinfo)"])
            if xbmc.getCondVisibility("system.hasaddon(plugin.program.super.favourites)"):
                manage_list.append(["iSearch", "ActivateWindow(10025,plugin://plugin.program.super.favourites/?mode=0&keyword="+title+",return)||Notification(iSearch:,"+premocktitle+",5000,special://home/addons/plugin.program.super.favourites/icon.png)"])
            if xbmc.getCondVisibility("system.hasaddon(plugin.video.genesis)"):
                manage_list.append(["GeneSearch", "ActivateWindow(10025,plugin://plugin.video.genesis/?action=tvSearch&query="+title+",return)||Notification(GeneSearch:,"+premocktitle+",5000,special://home/addons/plugin.video.genesis/icon.png)"])
            if xbmc.getCondVisibility("system.hasaddon(plugin.video.kmediatorrent)"):
                manage_list.append(["K-Search ExtraTorrent", "ActivateWindow(10025,plugin://plugin.video.kmediatorrent/extratorrent/search/?query="+title+",return)||Notification(K-Search ExtraTorrent:,"+premocktitle+",5000,special://home/addons/plugin.video.kmediatorrent/icon.png)"])
            if xbmc.getCondVisibility("system.hasaddon(plugin.video.phstreams)"):
                manage_list.append(["PhoenixFind", "ActivateWindow(10025,plugin://plugin.video.phstreams/?audio=0&content=0&mode=savedsearch&playable=false&url="+title+",return)||Notification(PhoenixFind:,"+premocktitle+",5000,special://home/addons/plugin.video.phstreams/icon.png)"])
            if xbmc.getCondVisibility("system.hasaddon(script.icechannel)"):
                manage_list.append(["iStreamSearch", "ActivateWindow(10025,plugin://script.icechannel/?indexer=tv_shows&indexer_id&mode=search&search_term="+title+"&section=search&type=tv_shows)||Notification(iStreamSearch:,"+premocktitle+",5000,special://home/addons/script.icechannel/icon.png)"])
            selection = xbmcgui.Dialog().select(heading=LANG(32133),
                                                list=[item[0] for item in manage_list])
            if selection == -1:
                return None
            for item in manage_list[selection][1].split("||"):
                xbmc.executebuiltin("Dialog.Close(all,true)")
                xbmc.executebuiltin(item)

        @ch.click(6001)
        def set_rating(self):
            if set_rating_prompt(media_type="tv",
                                 media_id=self.info["id"]):
                self.update_states()

        @ch.click(6002)
        def open_list(self):
            index = xbmcgui.Dialog().select(heading=LANG(32136),
                                            list=[LANG(32144), LANG(32145)])
            if index == 0:
                wm.open_video_list(prev_window=self,
                                   media_type="tv",
                                   mode="favorites")
            elif index == 1:
                wm.open_video_list(prev_window=self,
                                   mode="rating",
                                   media_type="tv")

        @ch.click(6003)
        def toggle_fav_status(self):
            change_fav_status(media_id=self.info["id"],
                              media_type="tv",
                              status=str(not bool(self.account_states["favorite"])).lower())
            self.update_states()

        @ch.click(6006)
        def open_rated_items(self):
            wm.open_video_list(prev_window=self,
                               mode="rating",
                               media_type="tv")

        @ch.click(132)
        def open_text(self):
            wm.open_textviewer(header=LANG(32037),
                               text=self.info["Plot"],
                               color=self.info['ImageColor'])

        def update_states(self):
            xbmc.sleep(2000)  # delay because MovieDB takes some time to update
            _, __, self.account_states = extended_tvshow_info(tvshow_id=self.info["id"],
                                                              cache_time=0,
                                                              dbid=self.dbid)
            super(DialogTVShowInfo, self).update_states()

    return DialogTVShowInfo
