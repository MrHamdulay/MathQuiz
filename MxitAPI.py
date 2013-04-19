import requests
from requests.auth import HTTPBasicAuth
import json
from time import time
import datetime
import time

from flask import request

authUrl = 'https://auth.mxit.com'
apiUrl = 'http://api.mxit.com'


class ForbiddenException(Exception):
    pass


class MxitAPI:
    scopes = []
    grant_type = 'client_credentials'
    access_token = None
    expiration_time = None

    def __init__(self, client_id, secret_id, appName):
        self.client_id = client_id
        self.secret_id = secret_id
        self.appName = appName

    def auth(self, scopes, grant_type='client_credentials'):
        auth = HTTPBasicAuth(self.client_id, self.secret_id)
        path = '/token'

        postData = 'grant_type=%s&scope=%s' % (grant_type, ' '.join(scopes))

        response = requests.post(authUrl+path, auth=auth, data=postData)

        if not response.ok:
            raise ForbiddenException(response.text)

        auth_info = json.loads(response.text)

        self.grant_type = grant_type
        self.token_type = auth_info['token_type']
        self.access_token = auth_info['access_token']
        self.scopes = auth_info['scope'].split(',')
        self.expiration_time = time()+int(auth_info['expires_in'])-1000

    def _api_call(self, resource, body=None):
        if time() > self.expiration_time:
            self.auth(self.scopes, self.grant_type)

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': '%s %s' % (self.token_type.title(), self.access_token)
        }
        function = requests.post if body is not None else requests.get
        print resource, body, headers, function
        return function(apiUrl+resource, data=body, headers=headers)

    def send_message(self, to, body, spool=True):
        self.validate('message/send')
        if not isinstance(to, basestring):
            to = ','.join(to)

        message = json.dumps({
            'Body': body,
            'From': self.appName,
            'To': to,
            'ContainsMarkup': True,
            'Spool': True
        })

        response = self._api_call('/message/send/', message)
        return response

    def get_profile(self):
        return self._api_call('/user/profile')


    def get_version(self):
        return self._api_call('/message/version/')

    def validate(self, scope=None):
        if self.access_token is None:
            raise ForbiddenException('Not authed')
        if scope and scope not in self.scopes:
            raise ForbiddenException('Not authed for requested scope')
        if time() > self.expiration_time:
            raise ForbiddenException('Token expired')

class User:
    @property
    def age(self):
        today = datetime.date.today()
        print type(self.dob)
        years = today.year - self.dob.year
        birthday = datetime.date(today.year, self.dob.month, self.dob.day)
        if today < birthday:
            years -= 1

        return years

    @staticmethod
    def current():
        if 'X-Mxit-Location' not in request.headers:
            location_info = 'ZA,,06,,,Johannesburg,33170,2026338302,'.split(',')
            profile_info = 'en,ZA,1995-02-14,Female,1'.split(',')
            user_id = '1'
            nick = 'Yaseen'
        else:
            location_info = request.headers['X-Mxit-Location'].split(',')
            profile_info = request.headers['X-Mxit-Profile'].split(',')
            user_id = request.headers['X-Mxit-Userid-R']
            nick = request.headers['X-Mxit-Nick']

        country = location_info[0]
        city = location_info[5]
        language = profile_info[0]
        dob = datetime.datetime.strptime(profile_info[2], '%Y-%m-%d')
        gender = profile_info[3]

        u = User()
        u.user_id = user_id
        u.username = nick
        u.country = country
        u.city = city
        u.language = language
        u.dob = dob
        u.gender = gender

        return u

if __name__ == '__main__':
    import config
    api = MxitAPI(config.client_id, config.secret_id, 'mathchallenge')
    api.auth(('message/send', ))

    r = api.send_message('m47692421002', 'ola amigo')
    print r
    ck
