#!/usr/bin/python

import re

class SubtitleFile(object):
    """ A Subtitle File object

    Attributes:
        filename:   the name of the subtitle file.  Properly "<Link ID>.<Amara ID>.<Lang>.<Ver>.vtt"
        fullpath:   the fullpath of the subtitle file object
        amara_id:   The Amara ID of the associated video
        link_id:    The Link ID of the associated video
        amara_lang: The Amara language ID (BCP 47)
        jcs_lang:   The JCS language ID (IETF Language Code)
        cc_flag:    Boolean indicator if this subtitle file is for SDH
        version:    The Amara subtitle version number
        video_title:    The VideoTitle for this subtitle
        ----------------------------
        release_name:   The JCS release_name
        subtitle_id:    The JCS subtitle ID
        project_id:     The JCS project ID
        jcs_json:       The JCS json for the subtitle
    """

    medusa_url = None
    jcs_headers = None

    def __init__ (self, fullpath=None, filename=None):
        self.fullpath = fullpath
        self.filename = None if fullpath else filename
        self.amara_id = 0
        self.link_id = 0
        self.amara_lang = None
        self.jcs_lang = None
        self.cc_flag = None
        self.version = 0
        self.video_title = None
        #################
        self.release_name = None
        self.subtitle_id = 0
        self.project_id = 0
        self.jcs_json = None
        #################
        self.content = ''
        self.title = ''
        self.description = ''
        #################
        self.parse_me()

    def __repr__(self):
        return 'SubtitleFile('+self.filename+')'

    def __str__(self):
        if (self.subtitle_id):
            return 'SubtitleFile(id:'+str(self.subtitle_id)+', '+str(self.filename)+', '+str(self.link_id)+', '+str(self.amara_id)+', '+str(self.jcs_lang)+', CC:'+str(self.cc_flag)+', Ver:'+str(self.version)+')'
        else:
            return 'SubtitleFile('+str(self.filename)+', '+str(self.link_id)+', '+str(self.amara_id)+', '+str(self.jcs_lang)+', CC:'+str(self.cc_flag)+', Ver:'+str(self.version)+')'

    def parse_me(self):
        if (self.fullpath):
            matchObj = re.match('(?P<path>^.*)\/(?P<file>[^/]+)$', self.fullpath)
            self.filename = matchObj.group('file')
        matchObj = re.match('(?P<link_id>^.*)\.(?P<amara_id>[^.]+)\.(?P<lang>[^.]+)\.v(?P<version>[^.]+)\.vtt$', self.filename)

        if ((matchObj == None) or
            (not matchObj.group('link_id')) or 
            (not matchObj.group('amara_id')) or
            (not matchObj.group('lang')) or
            (not matchObj.group('version'))):
            print 'SubtitleFile: misformatted subtitle filename: \"' +str(self.filename) + '\"'
        else:
            self.cc_flag = False
            self.link_id = str(matchObj.group('link_id'))
            self.amara_id = str(matchObj.group('amara_id'))
            self.amara_lang = str(matchObj.group('lang'))
            self.version = str(matchObj.group('version'))
            self.jcs_lang = self.amara_lang
            if (self.amara_lang == 'en'):
                self.jcs_lang = 'en-US'
                self.cc_flag = True
            elif (self.amara_lang =='meta-tw'):
                self.jcs_lang = 'en-US'
                self.cc_flag = False
            elif (self.amara_lang == 'zh-cn'):
                self.jcs_lang = 'zh-Hans'
                self.cc_flag = False
            elif (self.amara_lang == 'zh-tw'):
                self.jcs_lang = 'zh-Hant'
                self.cc_flag = False
            elif (self.amara_lang == 'de'):
                self.jcs_lang = 'de-DE'
                self.cc_flag = False
            elif (self.amara_lang == 'fr'):
                self.jcs_lang = 'fr-FR'
                self.cc_flag = False
            elif (self.amara_lang == 'ja'):
                self.jcs_lang = 'ja-JP'
                self.cc_flag = False
            elif (self.amara_lang == 'meta-geo'):
                self.jcs_lang = self.amara_lang
                self.cc_flag = True
            else:
                print 'SubtitleFile: unexpected language code', filename
                assert 'SubtitleFile: unexpected language code', filename

    def basename(self):
        return (str(self.link_id)+'.'+str(self.amara_id))

    def basename_lang(self):
        return (str(self.link_id)+'.'+str(self.amara_id)+'.'+str(self.amara_lang))

    def readfile(self):
        with open(self.fullpath, 'r') as content_file:
            self.content = content_file.read()

