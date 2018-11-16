#!/usr/bin/python

import requests
from requests.auth import HTTPDigestAuth
import json
import re
import csv
import sys, getopt

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

linkHeaders = { 'Accept' : 'application/json;indent=2' }

amaraHeaders = {
    'X-api-username' : 'olaf.brandt',
    'X-api-key' : '558fc7b79e656543cab091c1cf3509c0b61d02e7',
    'Content-Type' : 'application/json'
    }

amaraUrl = 'https://amara.org/api/videos/?team=ondemand578'

tc = 0
uc = 0
verbose = False
inputfile = ""
outputfile = ""
genCsv = False
doLobbies = False
doTitles = False

linkTitles = {}

def crawlTitle(titleUrl):
    global linkTitles
    global uc
    global tc
    global verbose

    #if verbose: print ("TITLE:", titleUrl)

    # It is a good practice not to hardcode the credentials. So ask the user to enter credentials at runtime
    myResponse = requests.get(titleUrl, headers=linkHeaders)
    #print (myResponse.status_code)

    # For successful API call, response code will be 200 (OK)
    if (myResponse.ok):

        # Loading the response data into a dict variable
        # json.loads takes in only binary or string variables so using content to fetch binary content
        # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
        jData = json.loads(myResponse.content)

        tc += 1
        if not (jData['id'] in linkTitles.keys()):
            uc += 1
            videoUrl = ""
            for v in jData['videos']:
                videoUrl = v['url']
                if v['video_format_id'] == "web-he":
                    break
            thumbUrl =jData['display']['thumb']
            thumbUrl = thumbUrl.replace("cdn-cf", "cdn")
            videoUrl = videoUrl.replace("cdn-cf", "cdn")
            titleEntry = {
                "index" : uc,
                "link_id" : jData['id'],
                "duration" : jData['duration'],
                "title" : jData['display']['title'],
                "description" : jData['display']['description'],
                "thumb" : thumbUrl,
                "video" : videoUrl,
                "creation_time" : jData['creation_time'],
            }
            linkTitles[jData['id']] = titleEntry
            if verbose: print "NEW", titleEntry
        else:
            uc += 0
            if verbose: print "DUPLICATE: \""+jData['display']['title']+"\"  "+jData['id']

    else:
      # If response code is not ok (200), print the resulting http error code with description
        myResponse.raise_for_status()


def crawlPlaylist(playlistUrl): 
    global tc
    global uc
    global linkHeaders

    if verbose: print ("PLAYLIST:", playlistUrl)

    while True:
        # It is a good practice not to hardcode the credentials. So ask the user to enter credentials at runtime
        myResponse = requests.get(playlistUrl, headers=linkHeaders)
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
                    if verbose: print '{0:3d}; {2:10s}; {1:s}'.format(tc, playItem['display']['title'], titleUrl)
                    crawlTitle(titleUrl)

            if jData.get('next') == None:
                break
            linkUrl = jData['next']
            linkUrl = re.sub("(.*)(\?.*)(\?.*)", "\\1\\3&format=json", linkUrl)
        else:
          # If response code is not ok (200), print the resulting http error code with description
            myResponse.raise_for_status()

def crawlLobby(linkBaseUrl, lobbyName):
    global tc
    global linkHeaders

    lobbyUrl = linkBaseUrl + "/lobby/" + lobbyName
    if verbose: print ("LOBBY:", lobbyName)

    # It is a good practice not to hardcode the credentials. So ask the user to enter credentials at runtime
    myResponse = requests.get(lobbyUrl, headers=linkHeaders)
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

def crawlAllTitles(linkBaseUrl):
    linkUrl = linkBaseUrl + "/title/"
    while True:
        # It is a good practice not to hardcode the credentials. So ask the user to enter credentials at runtime
        myResponse = requests.get(linkUrl, headers=linkHeaders)
        #print (myResponse.status_code)

        # For successful API call, response code will be 200 (OK)
        if(myResponse.ok):

            # Loading the response data into a dict variable
            # json.loads takes in only binary or string variables so using content to fetch binary content
            # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
            jData = json.loads(myResponse.content)

            #print("The response contains {0} titles".format(len(jData['titles'])))
            #print("\n")
            for title in jData['titles']:
                crawlTitle(title['url'])

            if jData.get('next') == None:
                break
            
            linkUrl = jData['next']
            linkUrl = re.sub("(.*)(\?.*)(\?.*)", "\\1\\3", linkUrl)
        else:
          # If response code is not ok (200), print the resulting http error code with description
            myResponse.raise_for_status()
    print "Title Count:", tc, "Unique:", uc

def writeTitlesToCSV(titles, outfile):
    global verbose

    if (len(outfile) <= 0):
        outfile = 'titles.csv'
    csvcols = []
    allcols = titles[titles.keys()[0]].keys()
    prefcols = ["index", "link_id", "amara_id", "amara_team", "amara_project", "title", "duration", "video", "thumb", "description"]
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


def publishToAmara(infile, doPost, doPut):

    global amaraHeaders
    global amaraUrl
    global verbose

    if (len(infile) == 0):
        infile = '80titles.csv'
    if verbose: print "doAmara(\"" + infile + "\")"
    csvfile = open(infile, 'rb')
    dialect = csv.Sniffer().sniff(csvfile.read(40))
    csvfile.seek(0)
    #print csv.list_dialects()
    #csvDict = csv.DictReader( csvfile, dialect=csv.excel, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csvDict = csv.DictReader( csvfile, dialect=csv.excel, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

    amaraTitles = {}
    projectName = 'batch-2'
    teamName = 'ondemand578'

    maxIter = 200
    for linkTitle in csvDict:
        if (maxIter < 1):
            break
        maxIter -= 1
        linkTitleU = {}
        titleStatus = 'GET'
        #print "linkTitle=", linkTitle
        for k in linkTitle.keys():
            #print "linkTitle[k]", linkTitle[k]
            linkTitleU[k] = linkTitle[k].decode('utf-8') if isinstance(linkTitle[k], basestring) else linkTitle[k]
        linkTitle = {}
        #print "linkTitleU=", linkTitleU

        if ((len(linkTitleU['video']) < 1) or
            (len(linkTitleU['title']) < 1) or
            (len(linkTitleU['description']) < 1) or
            (len(linkTitleU['thumb']) < 1) or
            (linkTitleU['duration'] < 1.0)):
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

        #print "BEFORE", linkTitleU['link_id']
        #print "BEFORE", linkTitleU['video']
        linkTitleU['link_id'] = re.sub(r'(CatalinaAB-dip.v)[0-9]+', r'\g<1>04', linkTitleU['link_id'])
        linkTitleU['video'] = re.sub(r'(CatalinaGat-v)[0-9]+(-web-he-26481f80f0d248439cda944969c8cbd5)', r'\g<1>14\g<02>', linkTitleU['video'])
        linkTitleU['video'] = re.sub(r'(CatalinaPar-v)[0-9]+(-web-he-5baeaf31e92c402fbb579da830128491)', r'\g<1>19\g<02>', linkTitleU['video'])
        linkTitleU['video'] = re.sub(r'(HonorFlightVR_NoBumper-v)[0-9]+(-web-he-544f99c89c8e476c89c70640c3f561c5)', r'\g<1>02\g<02>', linkTitleU['video'])
        linkTitleU['video'] = re.sub(r'SalkantayTrek-v14-web-he-30e4fa5cd659442ab0f644d19f68f80f.mp4', r'SobekSalkantayTrek-v01-web-he-8897fbed6eed46eeb426bb30447435a5.mp4', linkTitleU['video'])
        linkTitleU['video'] = re.sub(r'(http)s(://cdn.jauntvr.com/videos/CatalinaDip-v16-web-he-0c5bfe80822e4e408ec83b101efacc08.mp4)', r'\g<1>\g<02>', linkTitleU['video'])
        #print "AFTER ", linkTitleU['link_id']
        #print "AFTER ", linkTitleU['video']

        amaraUrl = ''
        amaraVideoUrl = linkTitleU['video']

        amaraGet = 'https://amara.org/api/videos/?video_url='+amaraVideoUrl


        myResponse = requests.get(amaraGet, headers=amaraHeaders)
        if(myResponse.ok):
            jData = json.loads(myResponse.content)
            if verbose: print "GET", amaraGet, " Count:", jData['meta']['total_count']
            if (jData['meta']['total_count'] == 1):
                amaraVideo = jData['objects'][0]
                amaraUrl = jData['objects'][0]['resource_uri']
                if ((amaraVideo['title'] != linkTitleU['title']) or
                    (amaraVideo['description'] != linkTitleU['description']) or
                    (amaraVideo['thumbnail'] != linkTitleU['thumb']) or
                    #(amaraVideo['duration'] != linkTitleU['duration']) or
                    (amaraVideo['title'] != linkTitleU['title']) or
                    (amaraVideo['title'] != linkTitleU['title'])):
                    newData = json.JSONEncoder().encode({
                        'title' : linkTitleU['title'],
                        'description' : linkTitleU['description'],
                        'thumbnail' : linkTitleU['thumb'],
                        'duration' : int(float(linkTitleU['duration'])),
                        'project' : projectName,
                        'team' : teamName,
                        'primary_audio_language_code' : 'en',
                        })
                    titleStatus = 'PUT' + ('' if doPost else '-x')
                    if verbose: print '{0:s} {1:s} {2:s} {3:s}'.format(titleStatus, amaraHeaders, amaraUrl, json.dumps(newData, indent=2))

                    if (doPut):
                        myResponse = requests.put(amaraUrl, data=newData, headers=amaraHeaders)
                        jData = json.loads(myResponse.content)
                        if not(myResponse.ok):
                            print myResponse, jData
                        else:
                            if verbose: print myResponse, "Amara ID:", jData['id']                        
                            amaraVideo['id'] = jData['id']
                else:
                    #if verbose: print 'SYNCED: \"{0:s}\", AmaraID: {1:s}, {2:3d} == {3:06.2f}'.format(linkTitleU['title'], amaraVideo['id'], amaraVideo['duration'], float(linkTitleU['duration']))
                    if verbose: print 'SYNCED: \"{0:s}\", AmaraID: {1:s}'.format(linkTitleU['title'], amaraVideo['id'])
                    titleStatus = 'SYNCED'



            else:
                amaraVideo = {}
                amaraUrl = 'https://amara.org/api/videos/'
                newData = json.JSONEncoder().encode({
                    'video_url' : linkTitleU['video'],
                    'title' : linkTitleU['title'],
                    'description' : linkTitleU['description'],
                    'thumbnail' : linkTitleU['thumb'],
                    'duration' : int(float(linkTitleU['duration'])),
                    'project' : 'batch-2',
                    'team' : 'ondemand578',
                    'primary_audio_language_code' : 'en',
                    })
                titleStatus = 'POST' + ('' if doPost else '-x')
                amaraVideo['id'] = ''
                if verbose: print '{0:s} {1:s} {2:s} {3:s}'.format(titleStatus, amaraHeaders, amaraUrl, json.dumps(newData, indent=2))
                if (doPost):
                    #myResponse = requests.post(amaraUrl, data=newData, headers=amaraHeaders)
                    jData = json.loads(myResponse.content)
                    if not(myResponse.ok):
                        print myResponse, jData
                    else:
                        print myResponse, "Amara ID:", jData['id']
                        amaraVideo['id'] = jData['id']
                        amaraUrl = 'https://amara.org/api/videos/' + amaraVideo['id']
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
    writeTitlesToCSV(amaraTitles, "fred.csv")


def showUsage (progName):
    print "Usage: "+progName+":"
    sys.exit()

def main(argv):
    global verbose
    global inputfile
    global outputfile
    global genCsv

    linkBaseUrl = "http://www.jauntvr.com"

    doTitles = False
    doLobbies = False
    doAmara = False
    doPost = False
    doPut = False

    if (len(argv) <= 1):
        showUsage(argv[0])
    try:
        opts, args = getopt.getopt(argv[1:], "vhltaxo:i:", ["verbose", "lobbies", "titles", "amara", "help", "post", "put", "ofile=", "ifile=", "staging"])
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
        elif opt in ("--put"):
            doPut = True
        elif opt in ("--staging"):
            linkBaseUrl = "http://www-staging.jauntvr.net"
    print "verbose=", verbose
    print "outfile=", outputfile

    if (doTitles):
        crawlAllTitles(linkBaseUrl)
        if (len(outputfile) >= 1):
            writeTitlesToCSV(linkTitles, outputfile)
    elif (doLobbies):
        crawlAllLobbies(linkBaseUrl)
        if (len(outputfile) >= 1):
            writeTitlesToCSV(linkTitles, outputfile)

    if (doAmara):
        publishToAmara(inputfile, doPost=doPost, doPut=doPut)

if __name__ == "__main__":
   main(sys.argv)


