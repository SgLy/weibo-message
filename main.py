#!env/bin/python
#coding: utf-8

from login import login, headers
import re
import json
from bs4 import BeautifulSoup

def get_uid(s):
    re0 = re.compile(r"\$CONFIG\['uid'\]='(\d+)';")
    re1 = re.compile(r'(webchat\.[0-9a-f]{8}\.js)')
    re2 = re.compile(r'source=(\d+)')
    print('Getting uid', end = '')
    t = s.get('https://weibo.com/home', headers = headers)
    uid = re.findall(re0, t.text)[0]
    print(' = %s, getting source' % uid, end = '')
    t = s.get('https://api.weibo.com/chat', headers = headers)
    js = re.findall(re1, t.text)[0]
    t = s.get('https://api.weibo.com/chat/%s' % js, headers = headers)
    sid = re.findall(re2, t.text)[0]
    print(' = %s' % sid)
    return uid, sid

def get_contacts(s):
    print('Getting all contacts')
    url = 'http://api.weibo.com/webim/2/direct_messages/contacts.json'
    data = {
        'source': sid,
        'callback': 'angular.callbacks._1',
        'count': 200,
        'is_include_group': 0,
        'myuid': uid
    }
    contacts = []

    # First fetch
    t = s.get(url, headers = headers, params = data).text[25:-13]
    t = json.loads(t)
    if t['code'] != 1:
        print('Error occured!')
        return contacts
    t = t['data']
    total_cnt = t['totalNumber']
    print('  %d contacts in total' % total_cnt)
    for c in t['contacts']:
        contacts.append({
            'uid': c['user']['id'],
            'name': c['user']['name'],
            'remark': c['user']['remark']
        })
    print('  Get %d contacts' % len(contacts))
    return contacts

def get_msg(s, friend_uid):
    print('Getting all messages with uid = %s' % friend_uid)
    url = 'http://api.weibo.com/webim/2/direct_messages/conversation.json'
    data = {
        'source': sid,
        'callback': 'angular.callbacks._5',
        'convert_emoji': 1,
        'count': 200,
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
        return msg
    t = t['data']
    total_cnt = t['total_number']
    print('  %d messages in total' % total_cnt)
    while True:
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
                tmp['img'] = 'http://upload.api.weibo.com/2/mss/msget?source=%s&fid=%s' % (sid, m['att_ids'][0])
            else:
                print('  [DEBUG] New media type: %s' % str(tmp['type']))
                tmp['type'] = m['media_type']
                tmp['orig'] = m
            msg.append(tmp)
            min_mid = min(min_mid, m['id'])
        print('  %d messages finished' % len(msg))
        if len(msg) >= total_cnt:
            break
        data['max_id'] = min_mid - 1
        data['callback'] = 'angular.callbacks._7'
        t = s.get(url, headers = headers, params = data).text[25:-13]
        t = json.loads(t)
        if t['code'] != 1:
            print('Error occured!')
            break
        t = t['data']

    return msg

from config import username, password
print('Logging in to %s' % username)
s = login(username, password)
headers['Referer'] = 'http://api.weibo.com/chat/'

uid, sid = get_uid(s)
contacts = get_contacts(s)

msg = {}
for i, c in enumerate(contacts):
    print('\n\n#%d in %d' % (i + 1, len(contacts)))
    if c['remark'] == '':
        print('Username = %s' % c['name'])
    else:
        print('Username = %s, Remark = %s' % (c['name'], c['remark']))
    msg[c['uid']] = get_msg(s, c['uid'])

with open('debug.txt', 'w') as f:
    json.dump({'contacts': contacts, 'msg': msg}, f)
