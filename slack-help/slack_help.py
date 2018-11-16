#!/usr/bin/python

import requests
import json
import pprint

get_users_url = 'https://slack.com/api/users.list?token=xoxp-2714696934-7680422917-179161854261-98a886a8248c2e50e25f67e195fc3f3f&pretty=1'
get_channels_url = 'https://slack.com/api/channels.list?token=xoxp-2714696934-7680422917-179161854261-98a886a8248c2e50e25f67e195fc3f3f&pretty=1'

target_member_name = 'jimmy-fei'
target_tz_offset = 28800
member_hits = []

s = requests.session()

resp = s.get(get_users_url)
assert resp.ok
members = resp.json()['members']

for m in members:
	if 'tz_offset' in m and m['tz_offset'] == target_tz_offset:
		print 'Member: {:>10s}, {:>14s}, {:26s}, restricted={}'.format(m['id'], m['name'], m['profile']['email'], m['is_restricted'])
		member_hits.append({'id' : m['id'], 'name' : m['name'], 'email' : m['profile']['email'], 'restricted' : m['is_restricted']})  
		#pprint.pprint(m, depth=2)
	
	if 'profile' in m and 'email' in m['profile'] and 'jauntvr.cn' in m['profile']['email']:
		#pprint.pprint(m, depth=2)
		None

	if m['name'] == target_member_name:
		#pprint.pprint(m, depth=2)
		None

#print member_hits

channel_to_member_map = {}
member_to_channel_map = {}

resp = s.get(get_channels_url)
assert resp.ok
#pprint.pprint(resp.json()['channels'], depth=2)
for c in resp.json()['channels']:
	channel_members = []
	for m in member_hits:
		if (m['id'] in c['members']):
			channel_members.append(m)
	if (len(channel_members) > 0):
		print 'Channel: {}, {:20s}: {}'.format(c['id'], c['name'], [str(x['name']) for x in channel_members])
		channel_to_member_map[c['name']] = channel_to_member_map.get(c['name'], []) + [str(x['name']) for x in channel_members]
		for m in channel_members:
			member_to_channel_map[m['name']] = member_to_channel_map.get(x['name'], []) + [c['name']]

#channels = resp.json()['members']


#print member_hits
#print channel_to_member_map
#print member_to_channel_map

for m in sorted(member_to_channel_map.keys()):
	print 'Member: {:10s}: {}'.format(m, member_to_channel_map[m])
