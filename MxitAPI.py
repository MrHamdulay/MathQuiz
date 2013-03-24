import requests
from requests.auth import HTTPBasicAuth
import json
from time import time
import urllib

authUrl = 'https://auth.mxit.com'
apiUrl = 'http://api.mxit.com'

class ForbiddenException(Exception): pass

class MxitAPI:
    scopes = []
    access_token = None
    expiration_time = None

    def __init__(self, client_id, secret_id, appName):
        self.client_id = client_id
        self.secret_id = secret_id
        self.appName = appName

    def auth(self, scopes, grant_type='client_credentials'):
        auth = HTTPBasicAuth(self.client_id, self.secret_id)
        path='/token'

        postData = 'grant_type=%s&scope=%s' % (grant_type, ' '.join(scopes))

        response = requests.post(authUrl+path, auth=auth, data=postData)

        if not response.ok:
            raise ForbiddenException(response.text)

        auth_info = json.loads(response.text)

        self.token_type = auth_info['token_type']
        self.access_token = auth_info['access_token']
        self.scopes = auth_info['scope'].split(',')
        self.expiration_time = time()+int(auth_info['expires_in'])

    def _api_call(self, resource, body=None):
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

if __name__== '__main__':
    import config
    api=MxitApi(config.client_id, config.secret_id, 'mathchallenge')
    api.auth(('message/send', ))

    r=api.send_message('m47692421002', 'ola amigo')
    print r
