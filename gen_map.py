# coding=utf8
"""
Generate an SVG map with avatars on it.
"""

import urllib, urllib2
import base64
import json
import re
import sys

client_key = ''
client_secret = ''
image_template = """
<a xlink:href="{link}">
    <title>{nick}</title>
    <image width="{width}" height="{height}" xlink:href="{avatar-url}" x="{x}" y="{y}">
        <title>{nick}</title>
    </image>
</a>
"""

def get_twitter_oauth():
    url = 'https://api.twitter.com/oauth2/token'
    # print url
    data = urllib.urlencode({'grant_type': 'client_credentials'})
    request = urllib2.Request(url, data) 
    base64string = base64.encodestring('%s:%s' % (client_key, client_secret)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string) 
    return json.loads(urllib2.urlopen(request).read())

def get_user_data(users):
    url = 'https://api.twitter.com/1.1/users/lookup.json?screen_name={}'.format(','.join(users))
    # print url
    request = urllib2.Request(url) 
    token = get_twitter_oauth()['access_token']
    #print token
    request.add_header('Authorization', 'Bearer %s' % token)
    try:
        #print request.headers
        result = urllib2.urlopen(request)
        return json.loads(result.read())
    except urllib2.HTTPError, error:
        return json.loads(error.read())

def get_avatars(data):
    users=[]
    for member in data:
        handled = re.match('^\{twitter:(.+?)\}$', member['avatar-url'], re.I)
        if not handled:
            continue
        member['handle'] = handled.group(1)
        users.append(handled.group(1))
    twit_data = get_user_data(users)
    if 'errors' in twit_data:
        return False
    for user in twit_data:
        #print user
        #exit(0)
        for member in data:
            #print str(member)
            handle = member['nick']
            if 'handle' in member:
                handle = member['handle']
            if user['screen_name'].lower() == handle.lower():
                member['avatar-url'] = user['profile_image_url'].replace('_normal', '')
    return data

def gen_map():
    with open('members.json') as data_file:    
        data = json.load(data_file)

    data = get_avatars(data)
    
    if not data:
        return False

    with open('map_template.svg', 'r+b') as tmpl_map:
        output = tmpl_map.read()

    members = []
    for member in data:
        members.append(image_template.format(**member))
        
    output = output.replace('{wamm}', '\n'.join(members))
    print output
    return True


if __name__ == "__main__":
    client_key = sys.argv[1]
    client_secret = sys.argv[2]
    if not gen_map():
        print 'Error!'