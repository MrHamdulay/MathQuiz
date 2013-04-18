import requests
from datetime import date
import json
import logging

from flask import request

from MxitAPI import User
from . import APP_NAME
from analytics import stats

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
            'X-Forwarded-For': request.headers.get('X-Forwarded-For', '41.132.228.92'),
            'Referer': APP_NAME
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
        stats.incr("mathchallenge.ads.shinka-zerocount")
        return ''

    ad = responseData['ads']['ad'][0]

    creative = ad['creative'][0]
    beacon = creative['tracking']['impression']
    r = requests.get(beacon, headers=headers)
    r.raise_for_status()

    stats.incr('mathchallenge.ads.shinka')

    if ad['type'] == 'image':
        stats.incr('mathchallenge.ads.shinka.image')
        mediaUrl = creative['media']
        clickUrl = creative['tracking']['click']
        height, width = creative['height'], creative['width']

        return '<a href="%s"><img src="%s" align="middle"></a>' % (clickUrl, mediaUrl)

    if ad['type'] == 'html':
        stats.incr('mathchallenge.ads.shinka.html')
        return ad['html']



if __name__ == '__main__':
    print generate_ad(1)
