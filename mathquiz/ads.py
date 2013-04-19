import requests
from datetime import date
import json
import logging
from time import time

from flask import request

from MxitAPI import User
from . import APP_NAME, config
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
            'X-Forwarded-For': request.headers['X-Forwarded-For'],
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
    print r
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

def buzz_city_ad():
    width, height = map(int, request.headers.get('Ua-Pixels', '240x320').split('x'))
    adwidth = width
    adheight = width*20/120
    ad = '''
    <a href="http://click.buzzcity.net/click.php?partnerid={partnerid}&ts={time}" style="display: block; width: {width}px; height: {height}px;">
  <img width="{width}" height="{height}" src="http://show.buzzcity.net/show.php?partnerid={partnerid}&get=image&imgsize=120x20&ts={time}" alt="" />
</a>'''.format(partnerid=config.buzzcity_partnerid, time=time(), width=adwidth, height=adheight)
    print ad

    return ad



if __name__ == '__main__':
    print generate_ad(1)
