#!env/bin/python
#coding: utf-8

from login import login, headers
import re
import json
from bs4 import BeautifulSoup

def get_msg(s, my_uid, friend_uid):
    print('Getting all messages with uid = %s' % friend_uid)
    url = 'http://api.weibo.com/webim/2/direct_messages/conversation.json'
    data = {
        'source': my_uid,
        'callback': 'angular.callbacks._5',
        'convert_emoji': 1,
        'count': 20,
        'is_include_group': 0,
        'max_id': 0,
        'uid': friend_uid
    }
    msg = []

    # First fetch
    t = s.get(url, headers = headers, params = data).text[25:-13]
    t = json.loads(t)
    if t['code'] != 1:
        print('Error occured!')
        return None
    t = t['data']
    total_cnt = t['total_number']
    print('  %d messages in total' % total_cnt)
    while True:
        total_cnt -= 20
        min_mid = 10 ** 20
        for m in t['direct_messages']:
            tmp = {
                'time': m['created_at'],
                'sender': m['sender']['name'],
                'recipient': m['recipient']['name']
            }
            if m['media_type'] == 0:
                tmp['type'] = 'text'
                tmp['text'] = m['text']
            elif m['media_type'] == 1:
                tmp['type'] = 'picture'
                tmp['img'] = 'http://upload.api.weibo.com/2/mss/msget?source=%s&fid=%s' % (my_uid, m['att_ids'][0])
            else:
                tmp['type'] = m['media_type']
            msg.append(tmp)
            min_mid = min(min_mid, m['id'])
        print('  %d messages finished' % len(msg))
        if total_cnt < 0:
            break
        data['max_id'] = min_mid - 1
        data['callback'] = 'angular.callbacks._7'
        t = s.get(url, headers = headers, params = data).text[25:-13]
        t = json.loads(t)
        if t['code'] != 1:
            print('Error occured!')
            break
        t = t['data']

    with open('debug.json', 'w') as f:
        f.write(json.dumps(msg, indent = 2))

    return msg

from config import username, password
print('Logging in to %s' % username)
s = login(username, password)
headers['Referer'] = 'http://api.weibo.com/chat/'
get_msg(s, '209678993', '2287739035')
