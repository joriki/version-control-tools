# Copyright (C) 2010 Mozilla Foundation
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os
import platform
import time
import tempfile
import shutil
import urlparse
import urllib
import urllib2
import json
from mercurial import config, util
from mercurial.i18n import _
try:
    import cPickle as pickle
except:
    import pickle
import bz

from mozhg.auth import (
    find_profiles_path,
    get_bugzilla_login_cookie_from_profile,
    get_profiles,
    win_get_folder_path,
)

global_cache = None


class bzAuth:
    """
    A helper class to abstract away authentication details.  There are two
    allowable types of authentication: userid/cookie and username/password.
    We encapsulate it here so that functions that interact with bugzilla
    need only call the 'auth' method on the token to get a correct URL.
    """
    typeCookie = 1
    typeExplicit = 2

    def __init__(self, userid=None, cookie=None, username=None, password=None):
        assert (userid and cookie) or (username and password)
        assert not ((userid or cookie) and (username or password))
        if userid:
            self._type = self.typeCookie
            self._userid = userid
            self._cookie = cookie
            self._username = None
        else:
            self._type = self.typeExplicit
            self._username = username
            self._password = password

    def auth(self):
        if self._type == self.typeCookie:
            return "userid=%s&cookie=%s" % (self._userid, self._cookie)
        else:
            return "username=%s&password=%s" % (urllib.quote(self._username), urllib.quote(self._password))

    def username(self, api_server):
        # This returns and caches the email-address-like username of the user's ID
        if self._type == self.typeCookie and self._username is None:
            return get_username(api_server, self)
        else:
            return self._username


def get_global_path(filename):
    path = None
    if platform.system() == "Windows":
        # The Windows user profile directory, eg: C:\Users\username
        # From http://msdn.microsoft.com/en-us/library/windows/desktop/bb762494%28v=vs.85%29.aspx
        CSIDL_PROFILE = 40
        path = win_get_folder_path(CSIDL_PROFILE)
    else:
        path = os.path.expanduser("~")
    if path:
        path = os.path.join(path, filename)
    return path


def store_global_cache(filename):
    fp = open(get_global_path(filename), "wb")
    pickle.dump(global_cache, fp)
    fp.close()


def load_global_cache(ui, api_server, filename):
    global global_cache
    if global_cache:
        return global_cache

    cache_file = get_global_path(filename)

    try:
        fp = open(cache_file, "rb")
        global_cache = pickle.load(fp)
    except IOError, e:
        global_cache = {api_server: {'real_names': {}}}
    except Exception, e:
        raise util.Abort("Error loading user cache: " + str(e))

    return global_cache


def store_user_cache(cache, filename):
    user_cache = get_global_path(filename)
    fp = open(user_cache, "wb")
    for section in cache.sections():
        fp.write("[" + section + "]\n")
        for (user, name) in cache.items(section):
            fp.write(user + " = " + name + "\n")
        fp.write("\n")
    fp.close()


def load_user_cache(ui, api_server, filename):
    user_cache = get_global_path(filename)

    # Ensure that the cache exists before attempting to use it
    fp = open(user_cache, "a")
    fp.close()

    c = config.config()
    c.read(user_cache)
    return c


def load_configuration(ui, api_server, filename):
    global_cache = load_global_cache(ui, api_server, filename)
    cache = {}
    try:
        cache = global_cache[api_server]
    except:
        global_cache[api_server] = cache
    now = time.time()
    if cache.get('configuration', None) and now - cache['configuration_timestamp'] < 24*60*60*7:
        return cache['configuration']

    ui.write("Refreshing configuration cache for " + api_server + "\n")
    try:
        cache['configuration'] = json.load(urllib2.urlopen(bz.get_configuration(api_server), timeout=30))
    except Exception, e:
        raise util.Abort("Error loading bugzilla configuration: " + str(e))

    cache['configuration_timestamp'] = now
    store_global_cache(filename)
    return cache['configuration']


def find_profile(ui, profileName):
    """
    Find the default Firefox profile location. Returns None
    if no profile could be located.

    """
    path = find_profiles_path()
    if not path:
        raise util.Abort(_("Could not find a Firefox profile"))

    profiles = get_profiles(path)
    if not profiles:
        raise util.Abort(_('Could not find a Firefox profile'))

    return profiles[0]


def get_auth(ui, bugzilla, profile, username, password):
    if not password:
        # If the password wasn't specified in the hgrc, then see if the
        # credentials can be retrieved from Bugzilla cookies
        userid = None
        cookie = None
        profile = find_profile(ui, profile)
        if profile:
            try:
                userid, cookie = get_bugzilla_login_cookie_from_profile(profile, bugzilla)
            except Exception as e:
                print("Warning: " + str(e))
        if userid and cookie:
            return bzAuth(userid=userid, cookie=cookie)
        ui.write("Credentials not found in .hgrc & unable to retrieve bugzilla login cookies.\n")

    if not username:
        username = ui.prompt("Enter username for %s:" % bugzilla, default='')
    if not password:
        password = ui.getpass("Enter password for %s: " % username)

    return bzAuth(username=username, password=password)


def get_username(api_server, token):
    req = bz.get_user(api_server, token)
    try:
        user = json.load(urllib2.urlopen(req, timeout=30))
        return user["name"]
    except urllib2.HTTPError, e:
        msg = ''
        try:
            err = json.load(e)
            msg = err['message']
        except:
            msg = e
            pass

        if msg:
            raise util.Abort('Unable to get username: %s\n' % msg)
        raise
    except Exception, e:
        raise util.Abort(_("Unable to get username: %s") % str(e))
