import sys
from urllib.parse import urlencode
import requests
from urllib.parse import urlparse, parse_qs
from random import choice
import re
from datetime import datetime, date, time
import calendar

#settings

#your birthday: datetime(year, month, day[, hour[, minute[, second[, microsecond[, tzinfo]]]]])
bday = datetime(2017, 11, 10, 5, 20, 0)

#access_token: Generate one at https://developers.facebook.com/tools/explorer
access_token = "EAACEdEose0cBAMesDiU4BKp3AjL5iZBOha47ekHKIkvRaZAB2PvEFVXk7JDaqecPnimNWFH8kAvVZBwEv4DKC260Oxq9NghfuL8hwl6gFkOe13ZBRjZBKLBJMsckPdOQvCeVwQZB7NuBBUpZC5wbl8oyJZBx1ZCyiwdD5BZCgpnusVLZC3IogZBXtz6RVD2dISrTjTLem6ApdJNI8chbyZBraCiat"
id = "114348712672298"
#set true to like posts on your wall
like = False;

#set true to comment thank you
comment = True;

#the list of messages from which you want a random message to be selected
message_set = ['Thank you very much', 'Thanks a lot', 'Thank you!']

#if false, repies to every message. Make it false if you are sure every wish posted on your wall is a birthday message
use_filter = True

#keywords to respond to. Comment only on posts containing at lease one of these words
bdaywords = ["Happy", "bday", "b\'day", "birthday","hbd", "wish"]

#proxy settings
http_proxy  = "http://104.32.176.195"
https_proxy = "https://10.10.1.11:1080"
ftp_proxy   = "ftp://10.10.1.10:3128"

#do not change anything beyond this line

#calculate utc timestamp
epoch=datetime(1970,1,1)
td = bday - epoch
utc_bday = int((td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 1e6)

#create proxy dictionary
proxy_dict = {
    "http" : http_proxy,
    "https" : http_proxy,
    "ftp" : ftp_proxy
}

#get birthday wishes
def get_posts(url, wishes=None):
    #check if we are done
    if wishes is None:
        wishes = []
        stop = False
    else:
        until = parse_qs(urlparse(url).query).get('until')
        stop = int(until[0]) < utc_bday

    if stop:
        return wishes
    else:
        print(url)
        req = requests.get(url)
        if req.status_code == 200:
            
            content = req.json()
            length = len(content['feed']['data'])
            #keep only relevant fields from post data
            feed = []
            for data in content['feed']['data']:
                feed.append({'id': data['id'], 'message': data.get('message',''),'from': data['from']['name'], 'type': data['type'] })
            #keep only posts relevant to birthday. Make sure you reply your friends who post happy birthday pictures on your timeline or posts in local language
            for post in feed:
                if post['type']=='status' and is_birthday(post['message'], use_filter) :
                    wishes.append(post)
            
            next_url = content['feed']['paging']['next']
            
            return get_posts(next_url, wishes)
        else:
            print("Unable to connect. Check if session is still valid")

def confirm(prompt=None, resp=False):
    if prompt is None:
        prompt = 'Confirm'
    if resp:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')
    while True:
        ans = input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print('please enter y or n.')
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False

def is_birthday (message, filter):
    if filter == False:
        return True
    for keyword in bdaywords:
        if keyword in message:
            return True
    return False

if __name__ == '__main__':
    
    #get bithday wishes
    base_url = 'https://graph.facebook.com/v2.11/me'
    params = {'fields':"id,name,feed{type,from,name,message}",'access_token': access_token}
    url = '%s?%s' % (base_url, urlencode(params))
    posts = get_posts(url)
    
    #confirm before posting
    usersignal = confirm('Found %s birthday wishes. Ready to thank them?' % (len(posts)))
    
    #post if user said yes
    if usersignal is True:
        for post in posts:

            #thank the user
            if comment:
                reply = choice(message_set)
                print('Replying %s to %s' % (reply, post['from']))
                url = 'https://graph.facebook.com/%s/comments' % post['id']
                response=requests.post(url, data={'access_token': access_token, 'message': reply})


            if like:
                url = 'https://graph.facebook.com/%s/likes?access_token=%s' % (post['id'], access_token)
                requests.post(url, data="", proxies=proxy_dict)