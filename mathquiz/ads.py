import requests
from datetime import date
import json
import logging

from flask import request

from MxitAPI import User
from . import APP_NAME

API_SERVER = 'http://ox-d.shinka.sh/ma/1.0/arj'


def generate_ad(auid):
    user = User.current()

    params = {
            'c.age': user.age,
            'c.gender': user.gender,
            'c.country': user.country,
            'xid': user.user_id,
            'auid': auid
    }

    headers = {
            'X-Forwarded-For': request.headers.get('X-Forwarded-For', '41.132.228.92')
            }


    response = requests.get(API_SERVER, params=params, headers=headers)
    if not response.ok:
        raise Exception('Ad request exception: %s' % response.text)

    responseData = json.loads(response.text)
    print responseData
    if responseData['ads']['version'] != 1:
        logging.error('Ad version not supported %d expected 1' % responseData['ads']['version'])
        return ''

    if int(responseData['ads']['count']) == 0:
        return ''

    ad = responseData['ads']['ad'][0]
    creative = ad['creative']

    if ad['type'] == 'image':
        return '<a href=""><img src=""></a>'

if __name__ == '__main__':
    print generate_ad(1)
