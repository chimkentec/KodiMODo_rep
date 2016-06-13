# -*- coding: utf-8 -*-

import pickle, re
import xbmcup.app, xbmcup.system, xbmcup.net
from defines import *

class Auth:
    def __init__(self):
        self.success = '"ok"'
        self.cookie_file = xbmcup.system.fs('sandbox://'+COOKIE_FILE)
        self.login = xbmcup.app.setting['username']
        self.password = xbmcup.app.setting['password']
        #xbmcup.system.fs.delete('sandbox://'+COOKIE_FILE)

    def autorize(self):
        try:
            if(self.login == '' or  self.password == ''):
                self.reset_auth()
                return False
            url = '%s/users/index/auth?mail=%s&pass=%s&social=0&_=1422391861285' % (SITE_URL, self.login, self.password)
            response = xbmcup.net.http.get(url)
        except xbmcup.net.http.exceptions.RequestException:
            return False
        else:
            return self._check_response(response)


    def _check_response(self, response):
        is_logged = response.text == self.success
        if(is_logged):
            self.save_cookies(response.cookies)
            xbmcup.app.setting['is_logged'] = 'true'
        else:
            xbmcup.system.fs.delete('sandbox://'+COOKIE_FILE)
        return is_logged


    def save_cookies(self, cookiejar):
        with open(self.cookie_file, 'wb') as f:
            pickle.dump(cookiejar, f)


    def get_cookies(self):
        if(xbmcup.system.fs.exists('sandbox://'+COOKIE_FILE)):
            with open(self.cookie_file, 'rb') as f:
                return pickle.load(f)
        return {}


    def reset_auth(self, reset_settings=False):
        xbmcup.app.setting['is_logged'] = 'false'
        if reset_settings == True:
            xbmcup.app.setting['username'] = ''
            xbmcup.app.setting['password'] = ''
        xbmcup.system.fs.delete('sandbox://'+COOKIE_FILE)


    def check_auth(self, page):
        reg = re.compile('/users/index/logout', re.S).findall(page)
        return len(reg) > 0