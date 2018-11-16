#!/usr/bin/python

import requests
from requests.auth import HTTPDigestAuth
import json
import re
import csv
import sys, getopt
import os
import collections
import logging
from random import randint

from subtitle_file import SubtitleFile

logging.basicConfig()
logger = logging.getLogger()
#logger.setLevel(logging.DEBUG)

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

link_dev_base_url           = 'https://link-dev.jauntvr.net/'
link_staging_base_url       = 'https://www-staging.jauntvr.net/'
link_live_base_url          = 'https://www.jauntvr.com/'

link_china_staging_base_url = 'http://linkstaging.jauntvr.cn/'
link_china_old_base_url     = 'http://linkstaging-app-116833965.cn-north-1.elb.amazonaws.com.cn/'


linkBaseUrl = link_staging_base_url
amaraBaseUrl = 'https://www.amara.org/api/'

#dictionary mapping video fingerprints to amara records
amara_fingerprint_dict = {}

linkHeaders = { 'Accept' : 'application/json;indent=2' }

amaraHeaders = {
    'X-api-username' : 'olaf.brandt',
    'X-api-key' : '558fc7b79e656543cab091c1cf3509c0b61d02e7',
    'Content-Type' : 'application/json'
    }

amaraUserID = 'VqdH1K8wQmWS-9GvKB2N-X9epdw35zLYadzzFQRLop4'

amaraUrl = ''

unlisted_title_ids = [
    # Unlisted on US Link Live
    'e565aef18e', # Camp Life: Woodward - Trailer
    'db2c11341b', # A Hellmann's Journey in VR
    'f534cbe5ca', # The Tiger Fish
    '2e8e594d57', # The Lightning Strike
    '2c00cd601b', # Inside Jeremy Wade's Shed: Spot the Difference #1
    '5922561582', # Inside Jeremy Wade's Shed: Spot the Difference #2
    '25eecc79d6', # Inside Jeremy Wade's Shed: Spot the Difference #3

    # US Link Staging
    # '8e5bc6e4dd', # Meet Land Rover BAR -- released
    '598a507705', # Above And Beyond
    '8bad9953b8', # Jafri

    # Jaunt China Titles
    # '80c4de6156', # TheTibetanEpisode1
    # 'fd8919cc28', # TheTibetanEpisode2
    # '27ad7b4ba7', # TheStarryNight

    # This is not unlisted.  Perhaps it was at one time.
    # '430426b74d', # Timeless: Continuum Recon VR Experience
    ]

#unlisted_title_ids = [ 'ffffffff' ]

suppressed_title_ids = [ ]

china80_titles = ['0f7ec55ef0', '8877eb4d7d', 'ef1910abff', 'c548c2a1a4', 'd7f694b68f', '2644eb6c3f', '97771336ec', 'JackWhiteInConcert-BallAndBiscuit.v10', '49b325c60e', 'd8820cdf36', '0ed2a6b244', 'ec715db71d', '8617386566', 'a852c86690', '16ffdc9b81', 'a13f813ad8', 'JackWhiteInConcert-DeadLeavesAndTheDirtyGround.v12', 'fb1051a266', '6f1e95b021', '75895af640', '55df9686fa', '63f5552fe1', 'ff623af142', 'c693f43562', '2bcc9fd191', 'b4f85188a2', '0f9930d2cf', 'b4c0c8bb90', '3337d2eac5', '7db2b543cf', '0465c441e7', '9f4c87ae68', '9ea7153c39', '83e9a08fb9', '73298fc244.v03', '71b89e6b93', '066c2eef82', 'f8027cfd2d', 'R5-HeartMadeUpOnYou.v07', 'TheNorthFace-extended.v11', 'JackWhiteInConcert-FreedomAt21.v09', 'R5LA-LetsNotBeAloneTonight.v04', '10ceb63bd4', 'f808adb985', '3ae14c75d0', 'StressLevelZero-EarthEncounter.v02', '7ForAllMankind-VisionsOfCalifornia.v12', '10abf60eb4', '6103bb20b2', '8897fbed6e', 'ee22b98089', 'a7df2def03', 'NewDealStudios-BlackMassExperienceTrailer.2014-10-30_titles', 'CatalinaAB-dip.v05', 'f5214935d2', 'ab5640cd90', 'Elle-VirtualRealityFashionShootJacquieLee.v13', '4d46606f76', 'a69d44aa65', '16f15b29a0', 'CatalinaAB-gat.v05', 'CatalinaAB-par.v03', 'be9ea6ef66', 'c0e3e15b42', '9bd23ba3bb', 'e59fd0c61e', 'dbbc03c3fc', '31670c278c', '28cd99babb', 'a2b3dd2943', 'e2024b5c75', 'e6a64293ee', 'f8f1f76c59', '4755e0ca51', '9fc97fc5e2', '8e52131e76', 'be663b520e', 'def1781343', '3e396098eb', 'b64f4c1e0c']
china65_titles = ['8955b4def9', 'de989fd34d', 'ec41b9c913', '430426b74d', '2a450a64b9', '0947c8c2b6', 'af0e85ea90', '7e5f724107', '82f20ae57b', 'e09d7d4419', '4d2a6db111', '5ba9fcb4a9', 'be11d014d0', 'd96c9f52a6', 'cd566a941f', '40fc20416d', 'c2ffa1a86a', '82f36bd00c', '7e10a10ae04f4ccc', '30c9724237', '6ad2192d68', 'd4d7e158c9', 'fc3813e87e', 'ba35beb249', 'a1ba526ccc', '563aef5f0a', '0c33af36e7', '83c460652a', '6afb6b516a', 'c963c95c5a', '3b0497e21e', '452d091d2b', '06a1a02c41', '1c2704dd21', '65b8587a7b', '5938dbd9ee', 'a2714236c7', '2c5f422b49', '351e58119e', '332bf9a458', 'f380742754', '6fb5c8cb53', '861f680af4', 'cb24689706', '1da8fc417c', 'd861dd4e8b', '07a87b2fd9', 'e32a624d35', '29ad0f3206', 'd8ce48550b', 'fe7f760f7a', 'e565aef18e', '6bea142408', '9e3a9442e1', '083cec5ab1', '9e02137cb1', '8264d81aba', '1eac762887', 'd3828e424d', 'd0eb258fe7', '05e50d6ca9.v05', 'PaulMcCartneyAtCandlestick-LiveAndLetDie.v12', '58e99c3a7b', '4cff11ce0a.v04', '4b2484f251.v04']
batch3_titles = ['c44df32ec3', 'e07e9a84ac', 'c12c65e8fe.v18', '781c9eec6a', 'c2794032e6', 'b9674e5dc0', 'e06ecbab20', '322ee46ba8c349e7', '9c03388c8c', 'aeb085addb', '54e7dac054', 'ac88c437e2', 'ecb0103a4f', 'f230dd2811', '5f6e9bddc5', '7abf747d9b', 'RebeccaMinkoff_Sizzle.v07', '0e0e06cedf', 'd23ebeb93a', 'e7aa5f3114', 'd8735b19df', 'ad5a84cb08', '33fa2bb687', 'a42096f8fd', 'bbe8368e9a', '819743750d', '37d43e6408', '05078eb575', 'NewDealStudios-KaijuFury-SundanceTeaser.v03_10', '5f0a704d1e', 'f81fc63d1d', 'ae9b22a979', '0865783de1', '72762a5aab', '86827a514e', '563aef5f0a', '4cdcd50bfc', '0c6d93dcca', '581d7afb9d', 'bf1248b2e1', '2981572c5e', 'YahooStudios-OtherSpaceVR.v10', 'Revolt-BigSeanLive.L3Dv003', 'dd4805a52a', '7e89113205', '861f680af4', '9412f59e27.v03', '3f38295914', '2507e7288c', '2939c72e97', 'fb0934b1bc', '4185958cb7', '618b242b7a']

china65enzh_titles = ['05e50d6ca9.v05', 'PaulMcCartneyAtCandlestick-LiveAndLetDie.v12', '58e99c3a7b', '4cff11ce0a.v04', '4b2484f251.v04']
china65en_titles = ['8955b4def9', 'de989fd34d', 'ec41b9c913', '430426b74d', '2a450a64b9', '0947c8c2b6', 'af0e85ea90', '7e5f724107', '82f20ae57b', 'e09d7d4419', '4d2a6db111', '5ba9fcb4a9', 'be11d014d0', 'd96c9f52a6', 'cd566a941f', '40fc20416d', 'c2ffa1a86a', '82f36bd00c', '7e10a10ae04f4ccc', '30c9724237', '6ad2192d68', 'd4d7e158c9', 'fc3813e87e', 'ba35beb249', 'a1ba526ccc', '563aef5f0a', '0c33af36e7', '83c460652a', '6afb6b516a', 'c963c95c5a', '3b0497e21e', '452d091d2b', '06a1a02c41', '1c2704dd21', '65b8587a7b', '5938dbd9ee', 'a2714236c7', '2c5f422b49', '351e58119e', '332bf9a458' ]
china65nil_titles = ['f380742754', '6fb5c8cb53', '861f680af4', 'cb24689706', '1da8fc417c', 'd861dd4e8b', '07a87b2fd9', 'e32a624d35', '29ad0f3206', 'd8ce48550b', 'fe7f760f7a', 'e565aef18e', '6bea142408', '9e3a9442e1', '083cec5ab1', '9e02137cb1', '8264d81aba', '1eac762887', 'd3828e424d', 'd0eb258fe7']

root_langs = ['cs', 'da', 'de', 'el', 'en', 'en-gb', 'es', 'es-ar', 'fi', 'fr', 'hu', 'it', 'ja', 'ko', 'meta-geo', 'meta-tw', 'ms', 'nb', 'nl', 'pl', 'pt', 'pt-br', 'ru', 'sr-latn', 'sv', 'th', 'tr', 'uk', 'zh', 'zh-cn', 'zh-hk', 'zh-tw']

tc = 0
uc = 0
verbose = False
inputfile = ""
outputfile = ""
genCsv = False
doLobbies = False
doTitles = False
linkBaseUrl = ""
doBust = False
cdnBust = randint(100,999)
doNotAsk = False

linkTitles = {}

def crawlTitle(session, titleUrl, allow_404=False, unlisted=False):
    global linkTitles
    global uc
    global tc
    global verbose
    global linkHeaders

    titleUrl = titleUrl
    if doBust:
        titleUrl = titleUrl + '&bust=' + str(cdnBust)

    if verbose: print 'TITLE: {}'.format(str(titleUrl))

    myResponse = session.get(titleUrl, headers=linkHeaders)

    # For successful API call, response code will be 200 (OK)
    if (myResponse.ok):

        # Loading the response data into a dict variable
        # json.loads takes in only binary or string variables so using content to fetch binary content
        # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
        jData = myResponse.json()

        tc += 1

        if (jData['id'] in suppressed_title_ids):
            print 'SUPPRESS: {} "{}"'.format(jData['id'], jData['display']['en_US']['title'])
            return

        if not (jData['id'] in linkTitles.keys()):
            uc += 1

            #print "Crawl:", jData['id']

            videoUrl = ""
            videoUrls = {}
            if not videoUrl: videoUrl = jData['formats'].get('web-he')
            if not videoUrl: videoUrl = jData['formats'].get('web-xhe')
            if not videoUrl: videoUrl = jData['formats'].get('mobile-de')
            if not videoUrl: videoUrl = jData['formats'].get('mobile-le')

            display_enus = jData['display']['en_US']
            thumbUrl =display_enus['thumb']
            if (thumbUrl):
                thumbUrl = thumbUrl.replace("cdn-cf", "cdn")
                thumbUrl = thumbUrl.replace("http:", "https:")
            if (videoUrl):
                videoUrl = videoUrl.replace("cdn-cf", "cdn")
                videoUrl = videoUrl.replace("http:", "https:")
            if (not videoUrl):
                print 'SKIPPING: No video URL'
                return

            orig_lang = jData.get('original_language', 'Missing')
            web_dash_subl_ids = []
            mobile_subl_ids = []
            psvr_subl_ids = []
            web_audio_formats = []
            mobile_audio_formats = []
            psvr_audio_formats = []

            if ('formats' in jData and 'web-dash' in jData['formats']):
                getUrl = jData['formats']['web-dash']
                if (doBust):
                    getUrl = getUrl + '?bust=' + str(cdnBust)
                mnfst_web_resp = session.get(getUrl, headers=linkHeaders)
                if not mnfst_web_resp.ok:
                    print 'ERROR: Title {} missing Web manifest. HTTP {}: {}'.format(jData['id'], mnfst_web_resp.status_code, getUrl)
                    web_dash_subl_ids = ['error ' + str(mnfst_web_resp.status_code)]
                    web_audio_formats = ['error ' + str(mnfst_web_resp.status_code)]
                else:
                    assert mnfst_web_resp.ok

                    mnfst_jdata = json.loads(mnfst_web_resp.content)

                    for subl in mnfst_jdata.get(u'subtitles', []):
                        #print 'subl:', subl
                        cc_str = str(subl.get(u'cc','Missing'))
                        subl_cc = str(subl[u'language']) + ('-CC' if cc_str == 'True' else '')
                        web_dash_subl_ids.append (subl_cc)
                        #print 'web_dash_subl_ids:', web_dash_subl_ids

                    for au in mnfst_jdata.get(u'audio', []):
                        web_audio_formats.append (au['layout'])

            if ('formats' in jData and 'manifest-v1' in jData['formats']):
                getUrl = jData['formats']['manifest-v1']
                if (doBust):
                    getUrl = getUrl + '?bust=' + str(cdnBust)
                mnfst_v1_resp = session.get(getUrl, headers=linkHeaders)
                if not mnfst_v1_resp.ok:
                    print 'ERROR: Title {} missing V1 manifest. HTTP {}: {}'.format(jData['id'], mnfst_v1_resp.status_code, getUrl)
                    mobile_subl_ids = ['error' + str(mnfst_v1_resp.status_code)]
                    mobile_audio_formats = ['error' + str(mnfst_v1_resp.status_code)]
                else:
                    assert mnfst_v1_resp.ok

                    mnfst_jdata = json.loads(mnfst_v1_resp.content)

                    for subl in mnfst_jdata.get(u'subtitles', []):
                        #print 'subl:', subl
                        cc_str = str(subl.get(u'cc','Missing'))
                        subl_cc = str(subl[u'language']) + ('-CC' if cc_str == 'True' else '')
                        mobile_subl_ids.append (subl_cc)
                        #print 'mobile_subl_ids:', mobile_subl_ids

                    for au in mnfst_jdata.get(u'audio', []):
                        mobile_audio_formats.append (au['layout'])

            if ('formats' in jData and 'manifestPSVR-v1' in jData['formats']):
                getUrl = jData['formats']['manifestPSVR-v1']
                if (doBust):
                    getUrl = getUrl + '?bust=' + str(cdnBust)
                mnfst_psvr_resp = session.get(getUrl, headers=linkHeaders)
                if not mnfst_psvr_resp.ok:
                    print 'ERROR: Title {} missing V1 manifest. HTTP {}: {}'.format(jData['id'], mnfst_psvr_resp.status_code, getUrl)
                    psvr_subl_ids = ['error' + str(mnfst_psvr_resp.status_code)]
                    psvr_audio_formats = ['error' + str(mnfst_psvr_resp.status_code)]
                else:
                    assert mnfst_psvr_resp.ok

                    mnfst_jdata = json.loads(mnfst_psvr_resp.content)

                    for subl in mnfst_jdata.get(u'subtitles', []):
                        #print 'subl:', subl
                        cc_str = str(subl.get(u'cc','Missing'))
                        subl_cc = str(subl[u'language']) + ('-CC' if cc_str == 'True' else '')
                        psvr_subl_ids.append (subl_cc)

                    for au in mnfst_jdata.get(u'audio', []):
                        psvr_audio_formats.append (au['layout'])

            dls = []
            for dl in jData['display'].keys():
                dls.append(str(dl))

            titleEntry = collections.OrderedDict([
                ("index", uc),
                ("link_id", jData['id']),
                ("duration", jData['duration']),
                ("title", display_enus['title']),   
                ("description", display_enus['description']),
                ("thumb", thumbUrl),
                ("video", videoUrl),
                ("creation_time", jData['creation_time']),
                ("display_langs", str(sorted(dls))),
                ("web_dash_langs", str(sorted(web_dash_subl_ids))),
                ("mobile_langs", str(sorted(mobile_subl_ids))),
                ("psvr_langs", str(sorted(psvr_subl_ids))),
                ("web_audio", str(sorted(web_audio_formats))),
                ("mobile_audio", str(sorted(mobile_audio_formats))),
                ("psvr_audio", str(sorted(psvr_audio_formats))),
                ('orig_lang', orig_lang),
                ('unlisted', 1 if unlisted else 0),
            ])

            linkTitles[jData['id']] = titleEntry
            if verbose:
                None
                print "NEW", titleEntry

        else:
            titleEntry = linkTitles[jData['id']]
            if (titleEntry['unlisted']):
                assert not unlisted
                titleEntry['unlisted'] = 1 if unlisted else 0
                linkTitles[jData['id']] = titleEntry
                display_enus = jData['display']['en_US']
                if verbose: print "DUPLICATE: UNLISTED: \""+display_enus['title']+"\"  "+jData['id']
            else:
                uc += 0
                display_enus = jData['display']['en_US']
                if verbose: print "DUPLICATE: \""+display_enus['title']+"\"  "+jData['id']

    else:
        # If response code is not ok (200), print the resulting http error code with description
        if unlisted:
            print 'Missing Unlisted: "{}" failed: {}, {}'.format(titleUrl, str(myResponse.status_code), myResponse.json()['detail'])
        else:
            print 'MISSING: "{}" failed: {}, {}'.format(titleUrl, str(myResponse.status_code), myResponse.json()['detail'])
            if (myResponse.status_code == 404):
                assert allow_404
            else:
                assert False


def crawlPlaylist(session, playlistUrl): 
    global tc
    global uc
    global linkHeaders

    if verbose: print ("PLAYLIST:", playlistUrl)

    while True:
        # It is a good practice not to hardcode the credentials. So ask the user to enter credentials at runtime
        myResponse = session.get(playlistUrl, headers=linkHeaders)
        #print (myResponse.status_code)

        # For successful API call, response code will be 200 (OK)
        if (myResponse.ok):

            # Loading the response data into a dict variable
            # json.loads takes in only binary or string variables so using content to fetch binary content
            # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
            jData = json.loads(myResponse.content)

            #print("The playlist contains {0} titles".format(len(jData['playlist'])))
            for i in range(len(jData['playlist'])):
                playItem = jData['playlist'][i]
                if re.search("\/title\/", playItem['url']):
                    #tc += 1
                    titleUrl = re.sub("^.*\/title\/(.*)\?.*","\\1",playItem['url'])
                    titleUrl += '?raw=1'
                    if verbose: print '{0:3d}; {2:10s}; {1:s}'.format(tc, playItem['display']['title'], titleUrl)
                    crawlTitle(session, titleUrl)

            if jData.get('next') == None:
                break
            linkUrl = jData['next']
            linkUrl = re.sub("(.*)(\?.*)(\?.*)", "\\1\\3&format=json", linkUrl)
        else:
          # If response code is not ok (200), print the resulting http error code with description
            myResponse.raise_for_status()

def crawlLobby(session, linkBaseUrl, lobbyName):
    global tc
    global linkHeaders

    lobbyUrl = linkBaseUrl + "/lobby/" + lobbyName
    if verbose: print ("LOBBY:", lobbyName)

    # It is a good practice not to hardcode the credentials. So ask the user to enter credentials at runtime
    myResponse = session.get(lobbyUrl, headers=linkHeaders)
    #print (myResponse.status_code)

    # For successful API call, response code will be 200 (OK)
    if(myResponse.ok):

        # Loading the response data into a dict variable
        # json.loads takes in only binary or string variables so using content to fetch binary content
        # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
        jData = json.loads(myResponse.content)

        #print("The lobby contains {0} groups".format(len(jData['lobby_groups'])))
        for i in range(len(jData['lobby_groups'])):
            playlistItem = jData['lobby_groups'][i]
            playlistUrl = playlistItem['playlist']
            if (re.search("HomeNavLink", playlistUrl) == None):
                crawlPlaylist(playlistUrl)
    else:
      # If response code is not ok (200), print the resulting http error code with description
        myResponse.raise_for_status()   

def crawlAllTitles(linkBaseUrl, doUnlisted=True):
    linkUrl = linkBaseUrl + "/title/"
    if doBust:
        linkUrl = linkUrl + '&bust=' + str(cdnBust)
    session = requests.Session()

    # Walk an enumerated list of unlisted titles that will not otherwise appear in a crawl.
    if doUnlisted:
        for tid in unlisted_title_ids:
            unlistedUrl = linkBaseUrl + '/title/' + tid + '?raw=1'
            crawlTitle(session, unlistedUrl, allow_404=True, unlisted=True)

    while True:
        # It is a good practice not to hardcode the credentials. So ask the user to enter credentials at runtime
        myResponse = session.get(linkUrl, headers=linkHeaders)
        print (myResponse.status_code)

        # For successful API call, response code will be 200 (OK)
        if(myResponse.ok):

            # Loading the response data into a dict variable
            # json.loads takes in only binary or string variables so using content to fetch binary content
            # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
            jData = json.loads(myResponse.content)

            #print("The response contains {0} titles".format(len(jData['titles'])))
            #print("\n")

            for title in jData['titles']:
                crawlTitle(session, title['url']+'?raw=1')

            if jData.get('next') == None:
                break
            
            linkUrl = jData['next']
            linkUrl = re.sub("(.*)(\?.*)(\?.*)", "\\1\\3", linkUrl)
        else:
          # If response code is not ok (200), print the resulting http error code with description
            myResponse.raise_for_status()

    print "Title Count:", tc, "Unique:", uc

def writeTitlesToCSV(titles, outfile, colNames = None, exactCols = False, inplaceOrder=False):
    global verbose

    if (len(outfile) <= 0):
        outfile = 'titles.csv'
    csvcols = []
    allcols = titles[titles.keys()[0]].keys()
    if inplaceOrder:
        colNames = titles[titles.keys()[0]].keys()
    prefcols = ["index", "link_id", "amara_id", "amara_team", "amara_project", "title", "duration", "video", "thumb", "description"]
    if (colNames):
        prefcols = colNames
    if (exactCols):
        allcols = colNames
    else:
        for p in prefcols:
            if p in allcols:
                csvcols.append(p)
                allcols.remove(p)
    csvcols.extend(allcols)
    if verbose: print "writeTitlesToCSV(\"" + outfile + "\")"
    csvWriter = csv.writer(open(outfile, 'wb'), delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

    title = titles[titles.keys()[0]]

    #first write column headers
    csvWriter.writerow(csvcols)

    #now data, assuming each column has the same # of values
    for i in range (len(titles.keys())):
        title = titles[titles.keys()[i]]
        [title.setdefault(k, '') for k in csvcols]
        row = [title[k] for k in csvcols]
        row=[s.encode('utf-8') if isinstance(s, basestring) else s for s in row]
        csvWriter.writerow(row)

def crawlAllLobbies(linkBaseUrl):
    lobbies = [
        "veterans", "MusicLobby", "PopularLobby", "invisible", "AdventureLobby",
        "StoryLobby", "MusicLobby", "SportsLobby", "horror", "hometurf", "sky", "ryot",
        "PaulMcCartney", "abcnews"
    ]

    [crawlLobby(linkBaseUrl, lobby) for lobby in lobbies]

    print "Title Count:", tc, "Unique:", uc

def enumAmaraVideosTeamAndProject(amaraVideos, teamName = None, projectName = None):
    amaraUrl = amaraBaseUrl+"videos/"
    separator = '?'
    if teamName: 
        amaraUrl = amaraUrl + separator + "team=" + teamName
        separator = '&'
    if projectName: 
        amaraUrl = amaraUrl + separator + "project=" + projectName

    tc = 0
    uc = 0
    ic = 0
    count = 0

    if verbose: sys.stdout.write('Enum Amara Videos: team={} '.format(teamName))

    while True:
        # It is a good practice not to hardcode the credentials. So ask the user to enter credentials at runtime
        resp = requests.get(amaraUrl, headers=amaraHeaders)
        #print (myResponse.status_code)

        # For successful API call, response code will be 200 (OK)
        if (resp.ok):

            # Loading the response data into a dict variable
            # json.loads takes in only binary or string variables so using content to fetch binary content
            # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
            jData = resp.json()

            #print("The response contains {0} titles".format(len(jData['titles'])))
            #print("\n")
            for video in jData['objects']:
                location = ""

                count += 1
                if verbose and (count % 4 == 0):
                    sys.stdout.write('.')
                    sys.stdout.flush()

                if video['project'] == 'ignore-remove':
                    ic += 1
                    continue

                if ('metadata' in video and 'location' in video['metadata']):
                    location = video['metadata']['location']

                amaraVideo = collections.OrderedDict ([
                    ('id', video['id']),
                    ('title', video['title']),
                    ('description', video['description']),
                    ('link', location),
                    ('team', video['team']),
                    ('project', video['project']),
                    ('duration', video['duration']),
                    ('video_url', video['all_urls'][0]),
                 ])

                fingerprint = None
                for v in video['all_urls']:
                    #print '{}, {}, {}'.format(video['id'], location, v)
                    if 'amara-video.s3.amazonaws.com/uploader' in v:
                        continue
                    matchObj = re.match('.*/(?P<title>[^/]+)-v(?P<version>[^\-]+)-(?P<format>\w+-\w+)-(?P<fingerprint>[^-]+)\.mp4$', v)
                    #print 'title={}, version={}, format={}, fingerprint={}'.format(matchObj.group('title'), matchObj.group('version'), matchObj.group('format'), matchObj.group('fingerprint'))
                    if not fingerprint:
                            fingerprint = matchObj.group('fingerprint')
                    assert fingerprint == matchObj.group('fingerprint')

                for lang in root_langs:
                    amaraVideo[lang] = 0

                for lang in video['languages']:
                    if (lang['published']):
                        amaraVideo[str(lang['code'])] = 1
                    else:
                        print 'enumAmaraVideosTeamAndProject: title {} ignore unpublished language {}'.format(video['id'], lang['code'])

                tc += 1
                if not (amaraVideo['id'] in amaraVideos):
                    amaraVideos[amaraVideo['id']] = amaraVideo
    
                    assert fingerprint not in amara_fingerprint_dict 
                    amara_fingerprint_dict[fingerprint] = amaraVideo

                    uc += 1

            
            amaraUrl = jData['meta']['next']
            #print amaraUrl

            if not amaraUrl:
                break
            
        else:
          # If response code is not ok (200), print the resulting http error code with description
            resp.raise_for_status()

    if verbose: print '\Videos: {}, Uniques: {}, Ignores: {}'.format(tc, uc, ic)

def enumAmaraVideos(write_file=False):
    amaraVideos = {}

    enumAmaraVideosTeamAndProject(amaraVideos, "ondemand637-other-languages")
    enumAmaraVideosTeamAndProject(amaraVideos, "ondemand637-delivery")
    enumAmaraVideosTeamAndProject(amaraVideos, "ondemand637")
    enumAmaraVideosTeamAndProject(amaraVideos, "ondemand578")

    if (write_file):
        #writeTitlesToCSV(amaraVideos, "amara-enum.csv", ['id', 'title', 'link', 'team', 'project'])
        writeTitlesToCSV(amaraVideos, "amara-enum.csv", inplaceOrder=True)


def publishToAmara(infile, doPost, doPut, doExtract):

    global amaraHeaders
    global amaraUrl
    global verbose

    if (len(infile) == 0):
        infile = '80titles.csv'
    if verbose: print "doAmara(\"" + infile + "\")"
    csvfile = open(infile, 'rb')
    dialect = csv.Sniffer().sniff(csvfile.read(40))
    csvfile.seek(0)
    csvDict = csv.DictReader(csvfile, dialect=csv.excel, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

    session = requests.Session()

    amaraTitles = {}

    maxIter = 1000
    for linkTitle in csvDict:
        if (maxIter < 1):
            break
        maxIter -= 1
        linkTitleU = {}
        titleStatus = 'GET'

        for k in linkTitle.keys():
            linkTitleU[k] = linkTitle[k].decode('utf-8') if isinstance(linkTitle[k], basestring) else linkTitle[k]
        linkTitle = {}

        # special case for collisions video URL
        if (linkTitleU['link_id'] == '2981572c5e'):
            linkTitleU['video'] = 'http://amara-video.s3.amazonaws.com/uploader/2016_12_07_14_53_04_collisions-v14-web-he-mp4.mp4'

        if ((len(linkTitleU['video']) < 1) or
            (len(linkTitleU['title']) < 1) or
            (len(linkTitleU['description']) < 1) or
            (len(linkTitleU['thumb']) < 1) or
#            (linkTitleU['duration'] < 1.0) or
            False):
            titleStatus = "SKIP"
            if verbose: print titleStatus, linkTitleU
            amaraTitle = {
                'index' : linkTitleU['index'],
                'title' : linkTitleU['title'],
                'description' : linkTitleU['description'],
                'thumbnail' : linkTitleU['thumb'],
                'duration' : int(float(linkTitleU['duration'])),
                'link_id' : linkTitleU['link_id'],
                'status' : titleStatus,
                'amara_project' : '',
                'amara_team' : '',
                'primary_audio_language_code' : '',
                'amara_id' : '',
                'amara_url' : '',
                'amara_video' : ''
            }
            amaraTitles[amaraTitle['link_id']] = amaraTitle
            continue

        projectName = ''
        teamName = ''
        amaraUrl = ''
        amaraVideoUrl = linkTitleU['video']

        fingerprint = None
        amaraRecord = None
        matchObj = re.match('.*/(?P<title>[^/]+)-v(?P<version>[^\-]+)-(?P<format>\w+-\w+)-(?P<fingerprint>[^-]+)\.mp4$', amaraVideoUrl)
        if matchObj:
            fingerprint = matchObj.group('fingerprint')
            amaraRecord = amara_fingerprint_dict.get(fingerprint, None)

        amaraGet = amaraBaseUrl +'videos/?video_url='+amaraVideoUrl

        print 'HTTP GET ("{}", "{}")'.format(amaraGet, amaraHeaders)
        myResponse = session.get(amaraGet, headers=amaraHeaders)
        if(myResponse.ok):
            jData = myResponse.json()
            if verbose: print "GET", amaraGet, " Count:", jData['meta']['total_count']

            if (jData['meta']['total_count'] == 0) and amaraRecord:
                #raw_input('Video URLs out of date: Continue with PUT?')
                amaraGet = amaraBaseUrl + 'videos/?video_url=' + amaraRecord['video_url']
                print 'HTTP GET ("{}", "{}")'.format(amaraGet, amaraHeaders)
                myResponse = session.get(amaraGet, headers=amaraHeaders)
                assert myResponse.ok
                jData = myResponse.json()
                if verbose: print "GET", amaraGet, " Count:", jData['meta']['total_count']

            if (jData['meta']['total_count'] == 1):
                amaraVideo = jData['objects'][0]
                amaraUrl = jData['objects'][0]['resource_uri']
                link_url = 'https://www.jauntvr.com/title/' + linkTitleU['link_id']
                projectName = amaraVideo['project']
                teamName = amaraVideo['team']
                amara_location = amaraVideo['metadata'].get('location', '')
                if ((amaraVideo['title'] != linkTitleU['title']) or
                    (amaraVideo['description'] != linkTitleU['description']) or
                    (amaraVideoUrl not in amaraVideo['all_urls']) or
                    (amara_location != link_url) or
                    #(linkTitleU['link_id'] in china65nil_titles) or
                    #(linkTitleU['link_id'] in china65en_titles) or
                    #(linkTitleU['link_id'] in china65enzh_titles) or
                    #(linkTitleU['link_id'] in china80_titles) or
                    #(linkTitleU['link_id'] in batch3_titles) or
                    #(amaraVideo['thumbnail'] != linkTitleU['thumb']) or
                    False):
                    
                    if verbose and (amaraVideo['title'] != linkTitleU['title']):
                        print 'title changed: "{}" --> "{}"'.format(amaraVideo['title'], linkTitleU['title'])
                    if verbose and (amaraVideo['description'] != linkTitleU['description']):
                        print 'description changed: "{}" --> "{}"'.format(amaraVideo['description'], linkTitleU['description'])
                    if verbose and (amara_location != link_url):
                        print 'location changed: "{}" --> "{}"'.format(amara_location, link_url)
                    
                    update_video_urls = False
                    if amaraVideoUrl not in amaraVideo['all_urls']:
                        update_video_urls = True
                        if verbose:
                            print 'video URL changed: "{}" --> "{}"'.format(amaraVideo['all_urls'][0], linkTitleU['video'])

                    projectName = 'batch-3'
                    teamName = 'ondemand578'

                    if (linkTitleU['link_id'] in china65nil_titles):
                        teamName = 'ondemand578'
                        projectName = 'china65'
                    if (linkTitleU['link_id'] in china65en_titles):
                        teamName = 'ondemand578'
                        projectName = 'china65en'
                        projectName = 'china65'
                    if (linkTitleU['link_id'] in china65enzh_titles):
                        teamName = 'ondemand578'
                        projectName = 'china65enzh'
                        projectName = 'china65'

                    if (linkTitleU['link_id'] in china80_titles):
                        teamName = 'ondemand578'
                        projectName = 'china80'
                    if (linkTitleU['link_id'] in batch3_titles):
                        teamName = 'ondemand578'
                        projectName = 'batch-3'

                    newData = json.JSONEncoder().encode({
                        'title' : linkTitleU['title'],
                        'description' : linkTitleU['description'],
                        'thumbnail' : linkTitleU['thumb'],
                        'duration' : int(float(linkTitleU['duration'])),
                        'project' : projectName,
                        'team' : teamName,
                        'metadata' : { 'location' : link_url },
                        'primary_audio_language_code' : 'en',
                        })
                    titleStatus = 'PUT' + ('' if doPut else '-x')
                    if verbose: print '{0:s} {1:s} {2:s} {3:s}'.format(titleStatus, amaraHeaders, amaraUrl, json.dumps(newData, indent=2))

                    if (doPut):
                        if not doNotAsk:
                            raw_input("Continue?")
                        myResponse = session.put(amaraUrl, data=newData, headers=amaraHeaders)
                        if not(myResponse.ok):
                            print myResponse, jData
                        else:
                            jData = myResponse.json()
                            if verbose: print myResponse, "Amara ID:", jData['id']                        
                            amaraVideo['id'] = jData['id']

                    if update_video_urls:
                        assert amaraRecord
                        amaraUrl = amaraBaseUrl + 'videos/' + amaraRecord['id'] + '/urls/'
                        newData = json.JSONEncoder().encode({
                            'url' : linkTitleU['video'],
                            'primary' : True,
                            'original' : False
                        })
                        titleStatus = 'POST-URL' + ('' if doPost else '-x')
                        if verbose: print '{0:s} {1:s} {2:s} {3:s}'.format(titleStatus, amaraHeaders, amaraUrl, json.dumps(newData, indent=2))
                        if (doPost):
                            if not doNotAsk:
                                raw_input("Continue?")
                            resp = session.post(amaraUrl, data=newData, headers=amaraHeaders)

                            if (not resp.ok):
                                print resp
                            else:
                                jData = myResponse.json()
                                if verbose: print myResponse
                            assert resp.ok



                else:
                    if verbose: print u'SYNCED: \"{0:s}\", AmaraID: {1:s}'.format(linkTitleU['title'], amaraVideo['id'])
                    titleStatus = 'SYNCED'
                    teamName = amaraVideo['team']
                    projectName = amaraVideo['project']

            else:
                amaraVideo = {}
                amaraUrl = amaraBaseUrl + 'videos/'
                projectName = 'batch-3'
                teamName = 'ondemand578'
                newData = json.JSONEncoder().encode({
                    'video_url' : linkTitleU['video'],
                    'title' : linkTitleU['title'],
                    'description' : linkTitleU['description'],
                    'thumbnail' : linkTitleU['thumb'],
                    'duration' : int(float(linkTitleU['duration'])),
                    'project' : projectName,
                    'team' : teamName,
                    'metadata' : { 'location' : 'https://www.jauntvr.com/title/' + linkTitleU['link_id'] },
                    'primary_audio_language_code' : 'en',
                    })

                if (amaraRecord):
                    print amaraRecord
                    assert False

                titleStatus = 'POST' + ('' if doPost else '-x')
                amaraVideo['id'] = ''
                if verbose: print '{0:s} {1:s} {2:s} {3:s}'.format(titleStatus, amaraHeaders, amaraUrl, json.dumps(newData, indent=2))
                if (doPost):
                    if not doNotAsk:
                        raw_input("Continue?")
                    myResponse = session.post(amaraUrl, data=newData, headers=amaraHeaders)
                    if not(myResponse.ok):
                        print myResponse
                    else:
                        jData = json.loads(myResponse.content)
                        print myResponse, "Amara ID:", jData['id']
                        amaraVideo['id'] = jData['id']
                        amaraUrl = amaraBaseUrl + 'videos/' + amaraVideo['id']
                else:
                        amaraUrl = ''

            amaraTitle = {
                'index' : linkTitleU['index'],
                'title' : linkTitleU['title'],
                'description' : linkTitleU['description'],
                'thumbnail' : linkTitleU['thumb'],
                'duration' : int(float(linkTitleU['duration'])),
                'amara_project' : projectName,
                'amara_team' : teamName,
                'primary_audio_language_code' : 'en',
                'amara_id' : amaraVideo['id'],
                'amara_url' : amaraUrl,
                'amara_video' : amaraVideoUrl,
                'link_id' : linkTitleU['link_id'],
                'status' : titleStatus
            }
            amaraTitles[amaraTitle['link_id']] = amaraTitle
    else:
        # If response code is not ok (200), print the resulting http error code with description
        myResponse.raise_for_status()
    writeTitlesToCSV(amaraTitles, "amara-status.csv")

    if (doExtract == True):
        amaraExtract = {}
        for amaraTitle in amaraTitles.values():
            if (amaraTitle['status'] == 'SYNCED'):
                myResponse = session.get(amaraTitle['amara_url'], headers=amaraHeaders)
                extractTitle = { 'id' : amaraTitle['link_id'], 'url' : amaraTitle['amara_url'], 'title' : amaraTitle['title'], 'description' : amaraTitle['description'] }
                if(myResponse.ok):
                    jData = json.loads(myResponse.content)
                    if verbose: print "GET", amaraTitle['amara_url'], " Langs:", len(jData['languages'])
                    jcs_path = './subtitles/link/' + amaraTitle['link_id'] + "/"
                    if not os.path.exists(jcs_path):
                        os.makedirs(jcs_path)
                    amara_path = './subtitles/amara/' + amaraTitle['amara_id'] + "/"
                    if not os.path.exists(amara_path):
                        os.makedirs(amara_path)
                    extractTitle['langs'] = len(jData['languages'])
                    max_version = 0
                    lang_count = 0

                    for lang in jData['languages']:
                        if (not lang['published']):
                            continue
                        lang_count += 1
                        myResponse = session.get(lang['resource_uri'], headers=amaraHeaders)

                        if(myResponse.ok):
                            jData2 = myResponse.json()

                            amara_filename = '1.' + 'title' + '.' + lang['code']  + '.txt'
                            with open(os.path.join(amara_path, amara_filename), 'wb') as temp_file:
                                temp_file.write(jData2['title'].encode('utf-8'))
                            extractTitle[amara_filename] = jData2['title']

                            amara_filename = '2.' + 'description' + '.' + lang['code']  + '.txt'
                            with open(os.path.join(amara_path, amara_filename), 'wb') as temp_file:
                                temp_file.write(jData2['description'].encode('utf-8'))
                            extractTitle[amara_filename] = jData2['description']

                            max_version = max([ x['version_no'] for x in jData2['versions'] ])

                        myResponse = session.get(lang['subtitles_uri'] + '?format=vtt', headers=amaraHeaders)
                        if(myResponse.ok):
                            jcs_filename = amaraTitle['link_id'] +  '.' + amaraTitle['amara_id'] + '.' + lang['code']  + '.v' +  str(max_version) + '.vtt'
                            amara_filename = '3.' + 'subtitles' + '.' + lang['code']  + '.vtt.txt'
                            with open(os.path.join(amara_path, amara_filename), 'wb') as temp_file:
                                temp_file.write(myResponse.content)
                            with open(os.path.join(jcs_path, jcs_filename), 'wb') as temp_file:
                                temp_file.write(myResponse.content)
                            extractTitle[amara_filename] = len(myResponse.content)
                extractTitle['langs'] = lang_count
                amaraExtract[extractTitle['id']] = extractTitle
                print extractTitle
        cols = ['id', 'url', 'title', 'description', 'langs'];
        for lang in ['meta-geo', 'meta-tw', 'en', 'zh-cn', 'zh-tw', 'fr', 'de', 'ja']:
            cols.extend ([
                '1.title.' + lang + '.txt',
                '2.description.' + lang + '.txt',
                '3.subtitles.' + lang + '.vtt.txt'
                ])
        #print cols
        writeTitlesToCSV(amaraExtract, "amara-extract.csv", cols, True)

class AmaraJob(object):
    """ An Amara Job Object

    Attributes:
        session:    the HTTP session for this object
        lang:       the language of the job
        job_id:     the name of the subtitle file.  Properly "<Link ID>.<Amara ID>.<Lang>.<Ver>.vtt"
        amara_id:   the Amara ID of the video
        team:       the Amara team slug
        json:       the JSON representation of the job
    """

    medusa_url = None
    jcs_headers = None

    def __init__ (self, session, headers, team, lang, amara_id):
        self.session = session
        self.headers = headers
        self.team = team
        self.lang = lang
        self.amara_id = amara_id
        self.job_id = None
        self.status = None
        self.work_status = None
        self.json = None

    def __repr__(self):
        return str(self)

    def __str__(self):
        if (self.json):
            return 'AmaraJob(video={}, job={}, lang={}, status={}, {})'.format(self.amara_id, self.job_id, self.lang, self.status, self.work_status)
        else:
            return 'AmaraJob(video={}, job={}, lang={}, no-JSON)'.format(self.amara_id, self.job_id, self.lang)

    def get(self, status=None):
        amaraUrl = '{}teams/{}/subtitle-requests/?video={}&language={}{}{}'.format(
                amaraBaseUrl, self.team, self.amara_id, self.lang, '&status=' if status else '', status if status else '')
        resp = self.session.get(amaraUrl, headers=self.headers)
        if (not resp.ok):
            print resp.json()
        assert resp.ok

        if (resp.json()['meta']['total_count'] > 0):
            self.json = resp.json()['objects'][0]
            self.job_id = self.json['job_id']
            self.status = self.json['status']
            self.work_status = self.json['work_status']

    def refresh(self):
        amaraUrl = '{}teams/{}/subtitle-requests/{}/'.format(amaraBaseUrl, self.team, self.job_id)
        resp = self.session.get(amaraUrl, headers=self.headers)
        if (not resp.ok):
            print resp.json()
        assert resp.ok

        self.json = resp.json()
        self.job_id = self.json['job_id']
        self.status = self.json['status']
        self.work_status = self.json['work_status']

    def assign_users(self, subtitler=None, reviewer=None, approver=None):
        req_data = json.dumps({ 'subtitler' : subtitler, 'reviewer' : reviewer , 'approver' : approver })
        amaraUrl = '{}teams/{}/subtitle-requests/{}/'.format(amaraBaseUrl, self.team, self.job_id)
        resp = self.session.put(amaraUrl, headers=self.headers, data=req_data)
        if not resp.ok:
            print resp.json()
        assert resp.ok

    def assign_users_auto(self, username):

        if (self.work_status == 'being-subtitled'): return
        if (self.work_status == 'being-reviewed'): return
        if (self.work_status == 'being-approved'): return

        #reset users
        self.assign_users ()

        #set as needed
        if (self.work_status == 'needs-subtitler'):
            self.assign_users (subtitler=username)
        elif (self.work_status == 'needs-reviewer'):
            self.assign_users (reviewer=username)
        elif (self.work_status == 'needs-approver'):
            self.assign_users (approver=username)

        self.refresh()

    def set_complete(self):
        # set jobs status to be complete
        if (not self.job_id): return

        amaraUrl = '{}teams/{}/subtitle-requests/{}/'.format(amaraBaseUrl, self.team, self.job_id)
        req_data = json.dumps({ 'work_status' : 'complete' })
        resp = self.session.put(amaraUrl, headers=self.headers, data=req_data)
        print resp.json()
        assert resp.ok

        self.refresh()

def upload_vtt_directory(lang_code, working_dir):

    logger.setLevel(logging.DEBUG)
    print 'upload_vtt_directory "{}" for {} subtitles'.format(working_dir, lang_code)

    subtitles_by_amara_id = {}

    csvFileName = None
    for dirpath, dirnames, filenames in os.walk(working_dir):
        for filename in [f for f in filenames if f.endswith(".csv")]:
            filename = os.path.join(dirpath, filename)
            if (csvFileName):
                print 'Igoring extra CSV file: {}'.format(filename)
            else:
                print 'Found CSV file: {}'.format(filename)
                csvFileName = filename

        for filename in [f for f in filenames if f.endswith(".vtt")]:
            sf = SubtitleFile(fullpath=os.path.join(dirpath, filename))
            sf.readfile()
            #print sf
            #print sf.content
            assert sf not in subtitles_by_amara_id
            subtitles_by_amara_id[sf.amara_id] = sf

    if (csvFileName):
        csvfile = open(csvFileName, 'rb')
        dialect = csv.Sniffer().sniff(csvfile.read(40))
        csvfile.seek(0)
        csvDict = csv.DictReader( csvfile, dialect=csv.excel, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    dict_size = 0
    for x in csvDict:
        assert x['subtitle Amara ID'] in subtitles_by_amara_id
        sf = subtitles_by_amara_id[x['subtitle Amara ID']]
        sf.title = x['Traditional Chinese Title Name']
        sf.description = x['Traditional Chinese Description']
        dict_size += 1

        print sf.amara_id, sf.title

    print 'upload_vtt_directory found {} == {} titles'.format(dict_size, str(len(subtitles_by_amara_id)))

    session = requests.Session()

    for sf in subtitles_by_amara_id.values():

        amaraUrl = '{}videos/{}/'.format(amaraBaseUrl, sf.amara_id)
        resp = session.get(amaraUrl, headers=amaraHeaders)
        assert resp.ok

        team = resp.json()['team']
        langExists = False
        for lang in resp.json()['languages']:
            #print '{} lang: {}'.format(sf.amara_id, lang['code'])
            if (lang['code'] == lang_code):
                langExists = True
                lang_uri = lang['resource_uri']
                break

        if (langExists):
            resp = session.get(lang_uri, headers=amaraHeaders)
            assert resp.ok
            aj = AmaraJob(session=session, headers=amaraHeaders, team=team, amara_id=sf.amara_id, lang=lang_code)
            aj.get()
            print aj

            if (resp.json()['subtitles_complete']):
                assert (aj.status == 'complete')

                author = resp.json()['versions'][0]['author']['username']
                print 'Amara ID: {}, Language {} exists and subtitles complete. Author="{}" Skipping'.format(sf.amara_id, lang_code, author)
                #raw_input('Continue?')

                continue

        if (not langExists):
            if True:
                inp = 'Y'
                print('Amara ID: {}, Add language "{}"" to video'.format(sf.amara_id, lang_code))
            else:
                inp = raw_input('Amara ID: {}, Add language "{}"" to video (Y/N)? [Y]'.format(sf.amara_id, lang_code))
            if (inp != 'N'):
                amaraUrl = '{}videos/{}/languages/'.format(amaraBaseUrl, sf.amara_id)
                lang_data = json.dumps({ 'language_code' : lang_code })
                resp = session.post(amaraUrl, headers=amaraHeaders, data=lang_data)
                assert resp.ok
                langExists = True
            else:
                print 'Skipping title'
                continue


        if True:
            inp = 'Y'
            print('Amara ID: {}, Language {}: Attempt subtitle creation'.format(sf.amara_id, lang_code))
        else:
            inp = raw_input('Amara ID: {}, Language {}: Attempt subtitle creation (Y/N)? [Y]'.format(sf.amara_id, lang_code))
        if (inp != 'N'):

            job_id = None

            # check for an existing in-progress job request
            aj = AmaraJob(session=session, headers=amaraHeaders, team=team, amara_id=sf.amara_id, lang=lang_code)
            aj.get()
            #aj.get('in-progress')
            print aj

            if not aj.job_id:
                # create a subtitle job request
                amaraUrl = '{}teams/{}/subtitle-requests/'.format(amaraBaseUrl, team)
                req_data = json.dumps({ 'video' : sf.amara_id, 'language' : lang_code })
                resp = session.post(amaraUrl, headers=amaraHeaders, data=req_data)
                if (not resp.ok):
                    print resp.json()
                assert resp.ok
                aj.job_id = resp.json()['job_id']
                aj.refresh()

            aj.assign_users_auto('olaf.brandt')
            print aj

            if (aj.work_status == 'being-subtitled'):

                amaraUrl = '{}videos/{}/languages/{}/subtitles/'.format(amaraBaseUrl, sf.amara_id, lang_code)
                sf_data = json.dumps({
                        'subtitles' : sf.content,
                        'sub_format' : 'vtt',
                        'title' : sf.title,
                        'description' : sf.description
                    })
                resp = session.post(amaraUrl, headers=amaraHeaders, data=sf_data)
                assert resp.ok

                aj.assign_users_auto('olaf.brandt')
                print aj

                amaraUrl = '{}videos/{}/languages/{}/subtitles/actions/'.format(amaraBaseUrl, sf.amara_id, lang_code)
                req_data = json.dumps({ 'action' : 'endorse' })
                resp = session.post(amaraUrl, headers=amaraHeaders, data=req_data)
                if (not resp.ok):
                    print resp.content
                assert resp.ok

            aj.assign_users_auto('olaf.brandt')
            print aj

            if (aj.work_status == 'being-approved'):
                # set jobs status to be complete
                aj.set_complete()
                print aj

        else:
            print 'Skipping title'
            continue

        #assert False

    return
    
def showUsage (progName):
    print "Usage: "+progName+":"
    sys.exit()

def main(argv):
    global verbose
    global inputfile
    global outputfile
    global genCsv
    global doNotAsk

    linkBaseUrl = "https://www.jauntvr.com"

    doTitles = False
    doLobbies = False
    doAmara = False
    doPost = False
    doPut = False
    doExtract = False
    doEnumAmara = False
    doInteractive = False
    doIngestHant = False
    doUnlisted = False
    doNotAsk = False

    if (len(argv) <= 1):
        showUsage(argv[0])
    try:
        opts, args = getopt.getopt(argv[1:], "vhltaxo:i:",
                ["verbose", "lobbies", "titles", "amara", "help", "post", "put", "ofile=", "ifile=", "staging", "linklive", "linkdev", "extract", "enumAmara", "interactive", "china", "ingestHant", "unlisted", "logrequests", "noask"])
    except getopt.GetoptError as errMsg:
        print "Invalid argument: "+ str(errMsg)
        showUsage(argv[0])        
    for opt, arg in opts:
        if (opt == "-h"):
            showUsage(argv[0])
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-t", "--titles"):
            doTitles = True
        elif opt in ("-l", "--lobbies"):
            doLobbies = True
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-a", "--amara"):
            doAmara = True
        elif opt in ("--post"):
            doPost = True
        elif opt in ("--interactive"):
            doInteractive = True
        elif opt in ("--put"):
            doPut = True
        elif opt in ("--linklive"):
            linkBaseUrl = link_live_base_url
        elif opt in ("--staging"):
            linkBaseUrl = link_staging_base_url
        elif opt in ("--linkdev"):
            linkBaseUrl = link_dev_base_url
        elif opt in ("--china"):
            linkBaseUrl = link_china_staging_base_url
        elif opt in ("--extract"):
            doExtract = True
        elif opt in ("--enumAmara"):
            doEnumAmara = True;
        elif opt in ("--ingestHant"):
            doIngestHant = True;
        elif opt in ("--unlisted"):
            doUnlisted = True;
        elif opt in ("--noask"):
            doNotAsk = True;
        elif opt in ("--logrequests"):
            doLogRequests = True
            logger.setLevel(logging.DEBUG)


    if (doIngestHant):
        upload_vtt_directory(lang_code='zh-tw', working_dir='./zht')
        sys.exit()

    if (doEnumAmara):
        enumAmaraVideos(write_file=True)
        sys.exit()

    if (doTitles):
        crawlAllTitles(linkBaseUrl, doUnlisted=doUnlisted)
        if (len(outputfile) >= 1):
            writeTitlesToCSV(linkTitles, outputfile, inplaceOrder=True)
    elif (doLobbies):
        crawlAllLobbies(linkBaseUrl)
        if (len(outputfile) >= 1):
            writeTitlesToCSV(linkTitles, outputfile)

    if (doAmara):
        enumAmaraVideos(write_file=False)
        publishToAmara(inputfile, doPost=doPost, doPut=doPut, doExtract=doExtract)

if __name__ == "__main__":
   main(sys.argv)


