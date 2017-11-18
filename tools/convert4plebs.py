#!/usr/bin/env python
# ---------------------------------------------------------
# built for Q
# version: 0.0.6
# ---------------------------------------------------------
# code quality: none
# code level: below normie, i dont like python
# ---------------------------------------------------------
# dependencies:
#  - python 2.7.14+ (linux, mac)
#  - see imports (pip install ... or apt install ...)
# ---------------------------------------------------------
# quick rundown:
# - ugly compiled with stackoverflow copy paste
# - requires servistat formatted json/project file
# - import servistate-current.json (symlink!) into your chrome (extension needed)
# - clone a request if new Q posts appear with specific userID
# - test api request and export servistate file, remove & create symlink pointing to new file
# - execute tools/convert4plebs.py data/servistate-current.json and look for errors or something
# - update timeline_daily.html's for new content if wanted
# - q.json is pretty large, rendering could take a while, mozilla quantum (Q!!!) is pretty neat
# ---------------------------------------------------------
# offline browsing
# - fagfox is fine
# - chrome (macos) eg. start with open /Applications/Google\ Chrome.app --args --allow-file-access-from-files
# - linux same
# - idK about windoze
# ---------------------------------------------------------

import json
import sys
import re      # venti b00bs
import urllib
import datetime
import os
import time
import urllib2,cookielib
import pytz
from HTMLParser import HTMLParser
from urlparse import urlparse
from os.path import splitext, basename

# commandline brabb
if len(sys.argv) != 2:
    print "Usage: %s [file.json]" % sys.argv[0]
    sys.exit(0)

# unicode
def __unicode__(self):
   return unicode(self.some_field) or u''

# fetch image/media to filecache
def process_4plebs_media(s):
    disassembled = urlparse(s)
    filename, file_ext = splitext(basename(disassembled.path))
    cachefile =  "imgcache/" + filename + file_ext
    d={"file": "compiled/" + cachefile, "url": s}
    process_4plebs_api(d)
    return cachefile

# fetch from archive 4plebs
def process_4plebs_api(s,force=False):
    my_file = s['file']
    fexists = False
    if os.path.exists(my_file):
        print "file:",my_file," already exists, ignoring"
        fexists = True

    if force:
        fexists = False

    if not fexists:
        print "fetching data for file:",my_file
        # sleep for plebs!
        time.sleep(1)
        hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
               'Accept-Encoding': 'none',
               'Accept-Language': 'en-US,en;q=0.8',
               'Connection': 'keep-alive'}
        req = urllib2.Request(s['url'], headers=hdr)
        try:
            page = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            print e.fp.read()
        content = page.read()
        fh = open(my_file, 'w')
        fh.write(content)
        fh.close()
        # sleep again to avoid ban
        time.sleep(8)

def process_4plebs_timestamp(t):
    # get time in UTC
    utc_dt = datetime.datetime.utcfromtimestamp(t).replace(tzinfo=pytz.utc)

    # convert it to tz
    tz = pytz.timezone('America/New_York')
    dt = utc_dt.astimezone(tz)
    raw_utc_timestamp = dt.strftime('%Y-%m-%d %H:%M:%S %Z%z')

    # create dates
    sdate               = { "year": "", "month": "", "day": "", "hour": "", "minute": "", "second": "", "millisecond": "", "format": "" }
    sdate['year']       = dt.strftime('%Y')
    sdate['month']      = dt.strftime('%m')
    sdate['day']        = dt.strftime('%d')
    sdate['hour']       = dt.strftime('%H')
    sdate['minute']     = dt.strftime('%M')
    sdate['second']     = dt.strftime('%S')
    sdate['_identdate'] = dt.strftime('%Y%m%d')
    #sdate['millisecond'] = ""
    sdate['format']     = "'<small>'mmmm d',' yyyy'</small>' - HH:MM:ss TT"
    sdate['raw_utc']    = raw_utc_timestamp

    return sdate


# process single post
def process_4plebs_post(p):
    # init
    r               = { "headline": "", "text": "" }
    post_num        = p['num']
    post_timestamp  = int(p['timestamp'])
    post_excerpt    = ""
    post_trip       = ""
    post_title      = ""
    post_media      = ""

    # get time in UTC
    post_startDate    = process_4plebs_timestamp(post_timestamp)
    raw_utc_timestamp = post_startDate['raw_utc']

    # use raw comment
    post_comment_raw = p['comment']


    # is comment?
    if post_comment_raw and len(post_comment_raw) >= 1:
        post_comment  = htmlparser.unescape(post_comment_raw)
        # build excerpt (not used now)
        if len(post_comment_raw) >= 20:
            post_excerpt     = post_comment[:20]
        else:
            post_excerpt     = post_comment[:len(post_comment_raw)-1]
        # html linebreaks
        post_comment     = post_comment.replace("\n","<br>")
    else:
        post_comment     = ""

    # post tripper
    if p['trip']:
        post_trip = ' ' +  p['trip']

    # post title
    if p['title']:
        post_title = p['title'] # op faggot
    else:
        post_title = p['name']  # user faggot

    # build some html
    #post_headline    = '<div class="4plebs_headline">'
    #post_headline   += p['name'] + ' ' + post_trip + '(ID: ' + p['poster_hash'] + ') ' + p['fourchan_date'] + ' No.' + post_num
    #post_headline   += '</div>'
    # add to html return
    r['headline'] = post_title + ' ' + post_trip + p['fourchan_date']

    # process media if set
    if p['media']:
        media           = p['media']
        media_link      = urllib.unquote(urllib.unquote(media['media_link']))
        thumb_link      = urllib.unquote(urllib.unquote(media['thumb_link']))
        preview_w       = urllib.unquote(urllib.unquote(media['preview_w']))
        preview_h       = urllib.unquote(urllib.unquote(media['preview_h']))
        media_filename  = urllib.unquote(urllib.unquote(media['media_filename']))
        # grab files for offline caching
        cachefile_url   = process_4plebs_media(media_link)
        cachethumb_url  = process_4plebs_media(thumb_link)
        # html (inline)
        post_media_inl  = '<a href="'+cachefile_url+'" target="_blank"><img src="'+cachethumb_url+'" width="'+preview_w+'" height="'+preview_h+'" title="'+media_filename+'"></a><br>'
        # event media
        post_media      = { "url": "", "caption": "", "thumbnail": "", "link": "", "link_target": "_blank", "credit": "" }
        post_media['url'] = cachethumb_url
        post_media['thumbnail'] = cachethumb_url
        post_media['link'] = cachefile_url
        post_media['caption'] = media_filename

    # build context
    urL_archive_thread  = "http://archive.4plebs.org/pol/thread/" + p['thread_num']
    url_archive_post    = "http://archive.4plebs.org/pol/thread/" + p['thread_num'] + "/#" + post_num
    url_json_call       = "http://archive.4plebs.org/_/api/chan/post/?board=pol&num=" + post_num
    post_srccontext     = '<div class="4plebs_context_' + post_num + ' ">'
    post_srccontext    += '<strong>Archive-Info:</strong><br>'
    post_srccontext    += '  &nbsp;' + p['name'] + ' ' + post_trip + '(ID: ' + p['poster_hash'] + ') ' + p['fourchan_date'] + ' No.' + post_num + '<br>'
    post_srccontext    += '  &nbsp;Unix Timestamp: '+ str(post_timestamp) +'<br>'
    post_srccontext    += '  &nbsp;DateTime: '+ raw_utc_timestamp +'<br>'
    post_srccontext    += '<strong>Online:</strong><br>'
    post_srccontext    += '  &nbsp;Post:   <a class="tl-makelink" onclick="void(0)" target="_blank" href="' + url_archive_post + '">' + url_archive_post + '</a><br>'
    post_srccontext    += '  &nbsp;Thread: <a class="tl-makelink" onclick="void(0)" target="_blank" href="' + urL_archive_thread + '">' + urL_archive_thread + '</a><br>'
    post_srccontext    += '  &nbsp;JSON:   <a class="tl-makelink" onclick="void(0)" target="_blank" href="' + url_json_call + '">' + url_json_call + '</a><br>'
    post_srccontext    += '</div>'

    # build html body
    post_commentbody   = '<div class="4plebs_contentbody_' + post_num + ' ">'
    post_commentbody  += post_comment
    post_commentbody  += '</div>'
    # post_media_inl +
    r['text'] = post_commentbody + "<br>" + post_srccontext

    # create dates
    #
    #post_startDate              = { "year": "", "month": "", "day": "", "hour": "", "minute": "", "second": "", "millisecond": "", "format": "" }
    #post_startDate['year']      = dt.strftime('%Y')
    #post_startDate['month']     = dt.strftime('%m')
    #post_startDate['day']       = dt.strftime('%d')
    #post_startDate['hour']      = dt.strftime('%H')
    #post_startDate['minute']    = dt.strftime('%M')
    #post_startDate['second']    = dt.strftime('%S')
    ##post_startDate['millisecond'] = ""
    #post_startDate['format']    = "'<small>'mmmm d',' yyyy'</small>' - HH:MM:ss TT"
    #*/

    # build return data
    rd = {"start_date": {}, "text": {}, "media": {} }
    rd['text']          = r
    rd['start_date']    = post_startDate
    rd['media']         = post_media
    rd['_identdate']    = post_startDate['_identdate']
    #d['background'] = {
    #                "color": "#202020",
    #                "opacity": 100,
    #                "url": ""
    #            }
    #d['end_date'] = post_endDate
    return rd

# =======================
# Main
# =======================
htmlparser = HTMLParser()

# read given servistate file (see chrome plugin how to)
data = json.load(open(sys.argv[1]))

# check if servistate file
try:
    check = data["servistate"]
except KeyError:
    sys.exit("error, json not servistate format")

# init
plebsUrls   = data["stores"]
threads     = []  # just bunch of ints
threads_info= []
threads_daily= []
events      = []
eras        = []
plebFiles   = []
# some title json
desciption  = """1. The purpose is to log events as they happen over the coming days. All of the shit going down in the last week is connected, the sealed indictments, the KSA purge and Lebanon tension, Trump donning a bomber jacket in the Pacific. We are here to record and analyze because no one else will be able to do a better job than /us/.<br>
              2. Everyone is aware of the presence of b0ts and derailers in these threads. Focus, Believe, and make a choice right now: Do you Trust Trump?<br>
              3. How would *you* succinctly break all this news to your blue-pilled friend? Does the initial message need to answer every detail? Bring them along for the ride and celebrations lads.<br>
              4. Stick to the graphic and produce infographics for redpilling<br>
              5. Shill are now trying to bake fake breads with dead link. REMEMBER to check for mold in new breads<br>
              6. Get Comfy, Believe in your bones that we're riding the greatest timeline in existence.</p>"""
newtitle    = { "text": { "headline": "The Q Chronicles", "text": desciption },"media": {"url": "img/cbts.jpg","thumb":   "img/cbts.jpg" }}
newdata     = { "events": events, "title": newtitle, "eras": eras }
newdailyindex = {}

# iterate plebs urls and call api if no file(s)
for plebs in plebsUrls:
    if plebs["name"] == "requests":
        for fetch in plebs["data"]:
            s           = { "url": '', "file": '' }
            s['url']    = fetch["url"]
            s['file']   = "4plebs/" + fetch["name"] + ".json"
            # call api
            process_4plebs_api(s)
            # build timeline data
            plebFiles.append({ "name": fetch["name"], "file": s['file'] })

# iterate plebs and process
for plebs in plebFiles:
    print "processing: ",plebs["name"]
    data = json.load(open(plebs['file']))
    # parse complete timeline
    for npost in data['0']['posts']:
        r = process_4plebs_post(npost)
        r['group'] = "QAnon"
        # add to global timeline
        events.append(r)
        # add threads
        if npost['thread_num']:
            item = int(npost['thread_num'])
            if item not in threads:
                threads.append(item)

# build index before adding thread infos to events (identdate gets lost)
for npost in events:
    identdate = npost['_identdate']
    newdailyindex[identdate] = {}

# fetch threads
for thread in threads:
    print "processing: thread", thread
    s         = { "url": '', "file": '' }
    s['url']  = "http://archive.4plebs.org/_/api/chan/thread/?board=pol&num=" + str(thread)
    s['file'] = "4plebs_threads/thread_" + str(thread) + ".json"
    # call api
    process_4plebs_api(s)
    # reload from local and process thread from to information
    data = json.load(open(s['file']))
    te   = { "start_date": {}, "end_date": {}, "media": "", "text": {} , "group": "CBTS"}
    re   = { "headline": "", "text": "" }
    # ...
    op = ""

    thread_start = ''
    thread_end   = ''
    # get op
    if data[str(thread)]["op"]:
        print "thread OP okay ..."
        op = data[str(thread)]["op"]
        thread_start = op["timestamp"]
        # process t
        te['start_date'] = process_4plebs_timestamp(int(thread_start))
    else:
        print "thread OP NOT okay!"

    # find last post entry timestamp
    if data[str(thread)]["posts"]:
        posts = data[str(thread)]["posts"]
        posts_last = sorted(posts.keys())[-1]
        print "last entry: ",posts_last
        thread_end = data[str(thread)]["posts"][str(posts_last)]["timestamp"]
        te['end_date'] = process_4plebs_timestamp(int(thread_end))

    # build some event entry context
    te_headline = ""
    if op["title"]:
        te_headline = htmlparser.unescape(op["title"])
    else:
        # faggot op set no title!
        te_headline = "Thread: " + str(thread)

    # process media if set
    op_media = ""
    if op["media"]:
        media           = op['media']
        media_link      = urllib.unquote(urllib.unquote(media['media_link']))
        thumb_link      = urllib.unquote(urllib.unquote(media['thumb_link']))
        preview_w       = urllib.unquote(urllib.unquote(media['preview_w']))
        preview_h       = urllib.unquote(urllib.unquote(media['preview_h']))
        media_filename  = urllib.unquote(urllib.unquote(media['media_filename']))
        # grab files for offline caching
        cachefile_url   = process_4plebs_media(media_link)
        cachethumb_url  = process_4plebs_media(thumb_link)
        # event media
        op_media      = { "url": "", "caption": "", "thumbnail": "", "link": "", "link_target": "_blank", "credit": "" }
        op_media['url'] = cachethumb_url
        op_media['thumbnail'] = cachethumb_url
        op_media['link'] = cachefile_url
        op_media['caption'] = media_filename

    # build context
    # post tripper
    op_trip = ''
    if op['trip']:
        op_trip = op['trip']
    urL_archive_thread  = "http://archive.4plebs.org/pol/thread/" + str(thread)
    url_json_call       = "http://archive.4plebs.org/_/api/chan/thread/?board=pol&num=" + str(thread)
    post_srccontext     = '<div class="tl-media"><div class="tl-media-content-container tl-media-content-container-text"><div class="tl-media-content">'
    post_srccontext    += '<div class="tl-media-item tl-media-wikipedia 4plebs_threadcontext_' + str(thread) + ' ">'
    post_srccontext    += '<strong>Archive-Info:</strong><br>'
    post_srccontext    += '  &nbsp;' + op['name'] + ' ' + op_trip + '(ID: ' + op['poster_hash'] + ') ' + op['fourchan_date'] + ' No.' + op['thread_num'] + '<br>'
    post_srccontext    += '  &nbsp;Unix Timestamp: '+ str(thread_start) +'<br>'
    post_srccontext    += '  &nbsp;DateTime: '+ te['start_date']['raw_utc'] +'<br>'
    post_srccontext    += '<strong>Online:</strong><br>'
    post_srccontext    += '  &nbsp;Thread: <a class="tl-makelink" onclick="void(0)" target="_blank" href="' + urL_archive_thread + '">' + urL_archive_thread + '</a><br>'
    post_srccontext    += '  &nbsp;JSON:   <a class="tl-makelink" onclick="void(0)" target="_blank" href="' + url_json_call + '">' + url_json_call + '</a><br>'
    post_srccontext    += '</div></div></div></div>'


    # text object in text
    re['headline']  = te_headline
    re['text']      = post_srccontext

    # add to event
    te['background']= {
                    #"color": "#d0d0d5",
                    #"opacity": 50,
                    "url": "img/cbts2.jpg"
    }
    te['media']     = op_media
    te['text']      = re
    te['_identdate']= te['start_date']['_identdate']
    # add to global timeline
    events.append(te)
    # test
    if te['start_date']['_identdate']:
        idkey = te['start_date']['_identdate']
        if idkey not in threads_info:
            threads_info.append(te)


# reparse result and sort per day
for key,value in newdailyindex.iteritems():
    f = "compiled/json/q_day_"+key+".json"
    # stupid iterate to events again
    events_per_day = []
    newdata_per_day = { "events": events_per_day}
    # iterate posts again
    for npost in events:
        identdate = npost['_identdate']
        if identdate == key:
            events_per_day.append(npost)

    # iterate ctbs eras again
    for nthread in threads:
        print nthread
        for ndata in threads_info:
            thidentdate = ndata['_identdate']
            print thidentdate
            if thidentdate == key:
                if ndata not in events_per_day:
                    print "appending thread identdate ",thidentdate
                    events_per_day.append(ndata)

    # write to daily json
    rd = json.dumps(newdata_per_day,indent=2)
    fh = open(f, 'w')
    fh.write(rd)
    fh.close()
    print "wrote:",f

# save complete timeline
f  = "compiled/json/q.json"
rd = json.dumps(newdata,indent=2)
fh = open(f, 'w')
fh.write(rd)
fh.close()
print "wrote:",f

# kek
