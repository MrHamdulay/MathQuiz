#!/usr/bin/python
#coding=UTF-8
"""
Python server-side google analytics tracking (or, simply, pyGA)

It's an adpatation of a script  from
https://github.com/b1tr0t/Google-Analytics-for-Mobile--python-/blob/master/ga.py
(Python implementation of ga.php.)
(See also https://github.com/singhj/Google-Analytics-for-Mobile--Google-App-Engine)

The goal is to make the code cleaner, pythonic and more usable.

Original Google Analytics Reference:
http://code.google.com/mobile/analytics/docs/web/

Cookies Reference:
On http://www.google.com/support/conversionuniversity/bin/static.py?hl=en&page=iq_learning_center.cs&rd=1,
(watch the Cookies and Google Analytics presentation)


#Generic usage:

from pyga import GATracker

ga = GATracker('domain.com', 'UA-xxxx') #your domain and google analytics key
ga.track('/api/news/', user_session_id, ip_address, useragent)

#Django Basic Usage:

#in you views.py
from pyga import DjangoGATracker

def some_view(request):

    ga = FlaskGATracker('domain.com', 'UA-xxxx')
    ga.track(request)

    #<...>

#Flask basic usage:

import flask
from flask import request, session #secret_key must be set to use session, see flask docs

from pyga import FlaskGATracker

#<...>

ga = FlaskGATracker('domain.com', 'UA-xxxx')
ga.track(request, session)

@requires: httplib2
@author: Alexey "DataGreed" Strelkov
@since: 2012
"""

import re
import os
from hashlib import md5
from random import randint
import struct
import httplib2
import time
from urllib import unquote, quote
from Cookie import SimpleCookie, CookieError
#from messaging import stdMsg, dbgMsg, errMsg, setDebugging
import uuid

try:
    # The mod_python version is more efficient, so try importing it first.
    from mod_python.util import parse_qsl
except ImportError:
    from cgi import parse_qsl

GA_VERSION = "4.4sh"
COOKIE_NAME = "__utmmobile"
COOKIE_PATH = "/"
COOKIE_USER_PERSISTENCE = 63072000

GIF_DATA = reduce(lambda x,y: x + struct.pack('B', y),
                  [0x47,0x49,0x46,0x38,0x39,0x61,
                   0x01,0x00,0x01,0x00,0x80,0x00,
                   0x00,0x00,0x00,0x00,0xff,0xff,
                   0xff,0x21,0xf9,0x04,0x01,0x00,
                   0x00,0x00,0x00,0x2c,0x00,0x00,
                   0x00,0x00,0x01,0x00,0x01,0x00,
                   0x00,0x02,0x01,0x44,0x00,0x3b], '')

# WHITE GIF:
# 47 49 46 38 39 61
# 01 00 01 00 80 ff
# 00 ff ff ff 00 00
# 00 2c 00 00 00 00
# 01 00 01 00 00 02
# 02 44 01 00 3b

# TRANSPARENT GIF:
# 47 49 46 38 39 61
# 01 00 01 00 80 00
# 00 00 00 00 ff ff
# ff 21 f9 04 01 00
# 00 00 00 2c 00 00
# 00 00 01 00 01 00
# 00 02 01 44 00 3b

class GATracker(object):

    def __init__(self, domain, account):
        u'''
        @id - id in Google Analytics
        '''
        self.domain = domain
        self.account = account

    def get_ip(self, remote_address):
        # dbgMsg("remote_address: " + str(remote_address))
        if not remote_address:
            return ""
        matches = re.match('^([^.]+\.[^.]+\.[^.]+\.).*', remote_address)
        if matches:
            return matches.groups()[0] + "0"
        else:
            return ""

    def get_visitor_id(self, guid, account, user_agent, cookie):
        """
         // Generate a visitor id for this hit.
         // If there is a visitor id in the cookie, use that, otherwise
         // use the guid if we have one, otherwise use a random number.
        """
        if cookie:
            return cookie
        message = ""
        if guid:
            # Create the visitor id using the guid.
            message = guid + account
        else:
            # otherwise this is a new user, create a new random id.
            message = user_agent + str(uuid.uuid4())
        md5String = md5(message).hexdigest()
        return "0x" + md5String[:16]

    def get_random_number(self):
        """
        // Get a random number string.
        """
        return str(randint(0, 0x7fffffff))

    def write_gif_data(self):
        """
        // Writes the bytes of a 1x1 transparent gif into the response.

        Returns a dictionary with the following values:

        { 'response_code': '200 OK',
          'response_headers': [(Header_key, Header_value), ...]
          'response_body': 'binary data'
        }
        """
        response = {'response_code': '204 No Content',
                    'response_headers': [('Content-Type', 'image/gif'),
                                         ('Cache-Control', 'private, no-cache, no-cache=Set-Cookie, proxy-revalidate'),
                                         ('Pragma', 'no-cache'),
                                         ('Expires', 'Wed, 17 Sep 1975 21:32:10 GMT'),
                                         ],
                    # 'response_body': GIF_DATA,
                    'response_body': '',
                    }
        return response

    def send_request_to_google_analytics(self, utm_url, useragent='Unknown'):
        """
      // Make a tracking request to Google Analytics from this server.
      // Copies the headers from the original request to the new one.
      // If request containg utmdebug parameter, exceptions encountered
      // communicating with Google Analytics are thown.
        """
        http = httplib2.Http()
        try:
            resp, content = http.request(utm_url,
                                         "GET",
                                         headers={'User-Agent': useragent,
                                                  'Accepts-Language:': os.environ.get("HTTP_ACCEPT_LANGUAGE",'')}
                                         )
            # dbgMsg("success")
            return resp
            #print content
        except httplib2.HttpLib2Error, e:
            errMsg("fail: %s" % utm_url)
            if environ['GET'].get('utmdebug'):
                raise Exception("Error opening: %s" % utm_url)
            else:
                pass


    def parse_cookie(self, cookie):
        """ borrowed from django.http """
        if cookie == '':
            return {}
        try:
            c = SimpleCookie()
            c.load(cookie)
        except CookieError:
            # Invalid cookie
            return {}

        cookiedict = {}
        for key in c.keys():
            cookiedict[key] = c.get(key).value
        return cookiedict

    def track(self, *args, **kwargs):
        u"""
        A short synonym for track_page_view
        """
        return self.track_page_view(*args, **kwargs)

    def track_page_view(self, path, visitor_id, ip_address, useragent='Unknown'):
        """
        // Track a page view, updates all the cookies and campaign tracker,
        // makes a server side request to Google Analytics and writes the transparent
        // gif byte data to the response.
        """
        time_tup = time.localtime(time.time() + COOKIE_USER_PERSISTENCE)

        domain = self.domain

        # Get the referrer from the utmr parameter, this is the referrer to the
        # page that contains the tracking pixel, not the referrer for tracking
        # pixel.
        document_referer = "-"
        document_path = path

        # // Always try and add the cookie to the response.
        cookie = SimpleCookie()
        cookie[COOKIE_NAME] = visitor_id
        morsel = cookie[COOKIE_NAME]
        morsel['expires'] = time.strftime('%a, %d-%b-%Y %H:%M:%S %Z', time_tup)
        morsel['path'] = COOKIE_PATH

        utm_gif_location = "http://www.google-analytics.com/__utm.gif"

        utm_url = utm_gif_location + "?" + \
                "utmwv=" + GA_VERSION + \
                "&utmn=" + self.get_random_number() + \
                "&utmhn=" + quote(domain) + \
                "&utmsr=" + '-' + \
                "&utme=" + '-' + \
                "&utmr=" + quote(document_referer) + \
                "&utmp=" + quote(document_path) + \
                "&utmac=" + self.account + \
                "&utmcc=__utma%3D999.999.999.999.999.1%3B" + \
                "&utmvid=" + visitor_id + \
                "&utmip=" + str(ip_address)
        # dbgMsg("utm_url: " + utm_url)
        return self.send_request_to_google_analytics(utm_url,useragent)


class DjangoGATracker(GATracker):

    def __init__(self, domain, account):
        super(DjangoGATracker, self).__init__(domain, account)


    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_session_id(self, request):

        #fix for django 1.4
        if hasattr(request, 'session') and hasattr(request.session, 'session_key') and getattr(request.session, 'session_key') is None:
            logging.debug("Creating a session key since there is none..")
            request.session.create()

        try:
            return request.session.session_key
        except AttributeError:
            return None

    def track_page_view(self, request, path = None):

        #getting path from request
        if not path:
            path = request.path
            #add args if any
            if request.META.get("QUERY_STRING",None):
                path+='?' + request.META.get("QUERY_STRING",None)

        super(DjangoGATracker, self).track_page_view(
                                path = path,
                                visitor_id = self.get_session_id,
                                ip_address = self.get_client_ip(request),
                                useragent = request.META.get('HTTP_USER_AGENT', 'Unknown')
                                )


class FlaskGATracker(GATracker):

    def __init__(self, domain, account, user_id_key="tr_user_id"):
        import uuid
        self.user_id_key = user_id_key
        super(FlaskGATracker, self).__init__(domain, account)

    def track_page_view(self, request, session, user_id=None, path = None):

        #getting path from request
        if not path:
            path = request.path
            #add args if any
            try:
                path +='?' + request.url.split('?')[1]
            except Exception, e:
                pass

        #if no user id is specified, try to get one from session
        if not user_id:
            user_id = session.get(self.user_id_key, None)
            #or create and save a new one
            if not user_id:
                session[self.user_id_key] = str(uuid.uuid4())
                user_id = session[self.user_id_key]

        super(FlaskGATracker, self).track_page_view(
                                path = path,
                                visitor_id = user_id,
                                ip_address = request.remote_addr,
                                useragent = request.user_agent.string
                                )
