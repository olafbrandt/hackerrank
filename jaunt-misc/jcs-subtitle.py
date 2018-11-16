#!/usr/bin/python

import requests
import urlparse
from requests.auth import HTTPDigestAuth
import json
import re
import csv
import sys, getopt
import os
import getpass
import boto3
import logging
import codecs
import locale
from abc import ABCMeta, abstractmethod

jcs_video_titles = {}

local_subtitles = {}
local_video_titles = {}

hack_force_submit = [
    # 'e565aef18e',
    # 'a1ba526ccc',
    # 'be9ea6ef66',
    # '97771336ec',
    # '31670c278c',
    ]

hack_rv_map = {
    #58432: 58502,
    #58436: 58421,
    #57095: 58001,
    #58473: 58556,
    #58439: 58438,
    #58672: 58582,   # link id: e565aef18e -- Camp Life: Woodward - Trailer
    #58883: 58001,   # link_id: be9ea6ef66
    #58436: 58421,   # link_id: e09d7d4419
    #58455: 58546,
    #57215: 57651
}

link_to_project_map = {}
link_to_subtitle_map = {}
#jcs_software_version = 'latest'
jcs_software_version = '7.0.36750_20170323'
bearer_token = None
jcs_headers = ''


vl_jcs = None
vl_fs = None

import requests
import urlparse
import logging
import json
import time
logging.basicConfig()
logger = logging.getLogger()
#logger.setLevel(logging.DEBUG)

def healthcheck_renderversion(session, link_id, token, medusa_instance):

    global vl_jcs

    dock_url = urlparse.urljoin(medusa_instance, 'api/v3/dock/')
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(token)}
    logger.debug('dock URL: {}'.format(dock_url))

    title_get = session.get(urlparse.urljoin(dock_url, 'titles/'), headers=headers, params={'link_id': link_id})
    if title_get.status_code != 200:
        logger.error('Failed to get title')
        return
    if title_get.json().get('count', 0) != 1:
        logger.error('More than one title found')
        return
    project_id = title_get.json().get('results')[0].get('project')

    print 'HEALTH CHECK: update(link_id: {}, https://www.jauntvr.com/titles/{}/'.format(str(link_id), str(link_id))

    #logger.debug('Using project: {}'.format(project_id))
    link_submission = title_get.json().get('results')[0].get('link_submission')
    if link_submission is None:
        logger.error('No link submission found')
        return
    linktitle_get = session.get(urlparse.urljoin(dock_url, 'linktitles/{}/'.format(link_submission)),
                                 headers=headers)
    if linktitle_get.status_code != 200:
        logger.error('LinkTitle not found')
        return
    title_version = linktitle_get.json().get('title_version')
    if title_version is None:
        logger.error('No Title Version found')
        return
    titleversion_get = session.get(urlparse.urljoin(dock_url, 'titleversions/{}/'.format(title_version)),
                                    headers=headers)
    if titleversion_get.status_code != 200:
        return
    mono_cut = titleversion_get.json().get('mono_cut')
    stereo_cut = titleversion_get.json().get('stereo_cut')

    if mono_cut is None and stereo_cut is None:
        logger.error('No cut found')
        return

    reapprove_mono = None
    reapprove_stereo = None
    if stereo_cut is not None:
        renderversion = titleversion_get.json().get('stereo_renderversion')

        task_get = session.get(urlparse.urljoin(dock_url, 'tasks/?rendering={}'.format(renderversion)), headers=headers)
        if task_get.status_code != 200:
            print task_get.json()
            assert False
        if (task_get.json().get('count') == 0):
            print 'No jobs for renderversion: {}'.format(renderversion)
        else:
            cut_id = task_get.json().get('results')[0].get('cut')
            if (cut_id != stereo_cut):
                print 'Job mismatch on renderversion: rv={}, job: {} != {}'.format(renderversion, cut_id, stereo_cut)    

        task_get = session.get(urlparse.urljoin(dock_url, 'tasks/?title={}&ordering=-id'.format(stereo_cut)), headers=headers)
        if task_get.status_code != 200:
            assert False
        cut_id = task_get.json().get('results')[0].get('cut')
        rv_id = task_get.json().get('results')[0].get('rendering')
        assert cut_id == stereo_cut
        if (rv_id != renderversion):
            hack_rv_map[renderversion] = rv_id
            print 'Possible missing job: Link ID: {}, stereo cut {}: titleversion={}, last RV with jobs={}'.format(link_id, cut_id, renderversion, rv_id)
            return False

    if mono_cut is not None:
        renderversion = titleversion_get.json().get('mono_renderversion')
        task_get = session.get(urlparse.urljoin(dock_url, 'tasks/?title={}&ordering=-id'.format(mono_cut)), headers=headers)
        if task_get.status_code != 200:
            assert False
        cut_id = task_get.json().get('results')[0].get('cut')
        rv_id = task_get.json().get('results')[0].get('rendering')
        assert cut_id == mono_cut
        if (rv_id != renderversion):
            print 'Possible missing job: Link ID: {}, mono cut {}: titleversion={}, last RV with jobs={}'.format(link_id, cut_id, renderversion, rv_id)
            hack_rv_map[renderversion] = rv_id
            return False

    return True


def check_renderversion(session, cut_id, headers, dock_url, renderversion, subtitle_id, software_version, verbose=False):
    
    global vl_jcs

    do_process = False
    current_data = {}

    #print 'check_renderversion'

    if not isinstance(subtitle_id, list):
        subtitle_id = list(subtitle_id)

    renderversion_get = session.get(urlparse.urljoin(dock_url, 'renderversions/{}/'.format(renderversion)),
                                       headers=headers)
    if renderversion_get.status_code != 200:
        logger.error('Failed to get renderversion')
        assert False
        return (do_process, current_data)
    
    current_data = {
        'original_language': renderversion_get.json().get('original_language'),
        'subtitles': renderversion_get.json().get('subtitles'),
        'software': renderversion_get.json().get('original_language')
    }

    current_subids_annotated = []
    for sub_id in sorted(current_data['subtitles']):
        x = vl_jcs.subtitleids[sub_id]
        current_subids_annotated.append(str(sub_id)+'.'+str(x.amara_lang)+'.v'+str(x.version))

    new_subids_annotated = []
    for sub_id in sorted(subtitle_id):
        x = vl_jcs.subtitleids[sub_id]
        new_subids_annotated.append(str(sub_id)+'.'+str(x.amara_lang)+'.v'+str(x.version))

    subid_change = False
    if (len(subtitle_id) != len(current_data['subtitles'])):
        subid_change = True
        print 'Subtitle ID change: {} --> {}'.format(
            str(current_subids_annotated), str(new_subids_annotated))
    else:
        for sub_id in subtitle_id:
            if (not sub_id in current_data['subtitles']):
                subid_change = True
                break

    if (subid_change):
        print "subtitle id change: ", current_data['subtitles'], "-->", subtitle_id
        do_process = True
    elif (verbose):
        print "subtitle id NO change: ", current_data['subtitles'], "-->", subtitle_id

    if (current_data['original_language'] != 'en-US'):
            print "original language: ", current_data['original_language']
            do_process = True

    return (do_process, current_data)

def process_renderversion(session, link_id, cut_id, headers, dock_url, renderversion, subtitle_id, software_version, no_execute=True):

    global hack_force_submit
    global hack_rv_map

    print 'process_renderversion (cut_id={}, renderversion={}, subtitle_id={})'.format(cut_id, renderversion, str(subtitle_id))

    # HACK Alert
    force_update = False
    
    if link_id in hack_force_submit:
        print 'HACK: link_id {} force re-submit'.format(str(link_id))
        force_update = True
        raw_input ('Continue with Hack fix?')
    

    if renderversion in hack_rv_map:
        print 'HACK: link_id {} update renderversion {} --> {}'.format(str(link_id), renderversion, hack_rv_map[renderversion])
        renderversion = hack_rv_map[renderversion]
        force_update = True
        raw_input ('Continue with Hack fix?') 

    if not force_update:

        (do_process, current_data) = check_renderversion(session, cut_id, headers, dock_url, renderversion, subtitle_id, software_version)

        if (not do_process):
            print 'process_renderversion: current: {} {} nothing to do'.format(current_data['original_language'], current_data['subtitles'])
            return 0 # nothing to do
        else:
            print 'process_renderversion{}: do process: lang=\"{}\"-->\"{}\" ids={}-->{}'.format('-x' if no_execute else '', current_data['original_language'], 'en-US', current_data['subtitles'], subtitle_id)
                
    if (no_execute):
        return

    raw_input ('Continue with update_assets?')

    unapprove_patch = session.patch(urlparse.urljoin(dock_url, 'cuts/{}/'.format(cut_id)),
                                     headers=headers,
                                     data=json.dumps({'approved': False}))
    
    if unapprove_patch.status_code != 200:
        logger.error('Could not unapprove cut')
        return

    if not isinstance(subtitle_id, list):
        subtitle_id = list(subtitle_id)

    update_data = json.dumps({
        'original_language': 'en-US',
        'subtitles': subtitle_id,
        'software': software_version
    })

    update_assets_url = urlparse.urljoin(dock_url, 'renderversions/{}/update_assets/'.format(renderversion))

    print 'POST ({}, {})'.format(update_assets_url, json.dumps(update_data, indent=2))

    renderversion_post = session.post(urlparse.urljoin(dock_url, 'renderversions/{}/update_assets/'.format(renderversion)),
                                       headers=headers,
                                       data=update_data)
    if renderversion_post.status_code != 202:
        print 'update_assets failed: status={}, json={}, resp={}'.format(renderversion_post.status_code, renderversion_post.json(), renderversion_post)
        logger.error('Failed to update_assets')
        return
    logger.debug('response: {}'.format(renderversion_post.json()))
    manifest_pass = False
    for _pass in renderversion_post.json().get('passes', []):
        if 'manifest' in _pass.get('name', ''):
            manifest_pass = True
            break
    if not manifest_pass:
        logger.error('No manifest passes')
        return
    task_status = session.get(urlparse.urljoin(dock_url, 'tasks/'), headers=headers,
                               params={'rendering': renderversion_post.json().get('id'), 'finished': 'False'})
    while task_status.json().get('count', 0) != 0:
        time.sleep(5)
        task_status = session.get(urlparse.urljoin(dock_url, 'tasks/'), headers=headers,
                                   params={'rendering': renderversion_post.json().get('id'), 'finished': 'False'})
    approve_patch = session.patch(urlparse.urljoin(dock_url, 'cuts/{}/'.format(cut_id)),
                                   headers=headers,
                                   data=json.dumps({'approved': True}))
    if approve_patch.status_code != 200:
        logger.error('Approve patch failed')
        return
    return renderversion_post.json().get('id')


def chrisr_update(session, link_id, token, medusa_instance, subtitle_id, software_version, no_execute=True):
    dock_url = urlparse.urljoin(medusa_instance, 'api/v3/dock/')
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(token)}
    logger.debug('dock URL: {}'.format(dock_url))
    title_get = session.get(urlparse.urljoin(dock_url, 'titles/'), headers=headers, params={'link_id': link_id})
    if title_get.status_code != 200:
        logger.error('Failed to get title')
        return
    if title_get.json().get('count', 0) != 1:
        logger.error('More than one title found')
        return
    project_id = title_get.json().get('results')[0].get('project')

    #print 'CHECK: update(link_id: '+str(link_id)+'), https://www.jauntvr.com/titles/'+str(link_id)+'/'

    #logger.debug('Using project: {}'.format(project_id))
    link_submission = title_get.json().get('results')[0].get('link_submission')
    if link_submission is None:
        logger.error('No link submission found')
        return
    linktitle_get = session.get(urlparse.urljoin(dock_url, 'linktitles/{}/'.format(link_submission)),
                                 headers=headers)
    if linktitle_get.status_code != 200:
        logger.error('LinkTitle not found')
        return
    title_version = linktitle_get.json().get('title_version')
    if title_version is None:
        logger.error('No Title Version found')
        return
    titleversion_get = session.get(urlparse.urljoin(dock_url, 'titleversions/{}/'.format(title_version)),
                                    headers=headers)
    if titleversion_get.status_code != 200:
        return
    mono_cut = titleversion_get.json().get('mono_cut')
    stereo_cut = titleversion_get.json().get('stereo_cut')

    if mono_cut is None and stereo_cut is None:
        logger.error('No cut found')
        return
    reapprove_mono = None
    reapprove_stereo = None
    if stereo_cut is not None:
        renderversion = titleversion_get.json().get('stereo_renderversion')
        reapprove_stereo = process_renderversion(session, link_id, stereo_cut, headers, dock_url, renderversion, subtitle_id, software_version, no_execute)
        if (not no_execute and (reapprove_stereo is None)):
            logger.error('Failed to process stereo renderversion')
    if mono_cut is not None:
        renderversion = titleversion_get.json().get('mono_renderversion')
        reapprove_mono = process_renderversion(session, link_id, mono_cut, headers, dock_url, renderversion, subtitle_id, software_version, no_execute)
        if (not no_execute and (reapprove_mono is None)):
            logger.error('Failed to process mono renderversion')

    # check for no-op case
    if (((reapprove_stereo is None) and (reapprove_mono == 0)) or
        ((reapprove_mono is None) and (reapprove_stereo == 0))):
        #print 'No Change, No Submit'
        return

    if no_execute:
        print 'SUBMIT-X: update(link_id={}, subtitle_id={}, software_version={})'.format(str(link_id), str(subtitle_id), software_version)
    else:
        print 'SUBMIT: update(link_id={}, subtitle_id={}, software_version={})'.format(str(link_id), str(subtitle_id), software_version)

    if no_execute:
        return

    titleversion_update = dict()
    if reapprove_stereo is not None:
        titleversion_update['stereo_renderversion'] = reapprove_stereo
    if reapprove_mono is not None:
        titleversion_update['mono_renderversion'] = reapprove_mono
    titleversion_patch = session.patch(urlparse.urljoin(dock_url, 'titleversions/{}/'.format(title_version)),
                                        headers=headers,
                                        data=json.dumps(titleversion_update))
    if titleversion_patch.status_code != 200:
        logger.error('Failed to patch titleversion')
        return
    new_titleversion_id = titleversion_patch.json().get('id')
    submit_title = session.post(urlparse.urljoin(dock_url, 'titles/{}/submit/'.format(title_get.json().get('results')[0].get('id'))),
                                 headers=headers,
                                 data=json.dumps({'version': new_titleversion_id,
                                                  'update_manifest' : True,  # Link Submission via Patch
                                                  'copyright_owner': 'True'}))



class BearerToken(object):
    """ A Bearer Token object

    Attributes:
        username:   user name
        url:        Medusa base url
        password:   password for user
        token:      token string
        headers:    http headers with bearer token

    """
    client_id = 'aLykTRYdA0HeJtCu1BAwgYOTCni9MarovfK0x6lY'
    client_secret = 'q86d7Cy81L7GjLpM0yi1LK8VxTRucMYsoddjinXvnRuX1pjJkQaSl7jwh9fIlNxE5nZxkfRBVoOkHmW0oqqPsOmJQfLB5RNHiMPmXhO48nSzncDELsV2ZESHTyXo5JkC'

    def __init__ (self, username, password, url):
        self.username = username
        self.password = password
        self.url = url
        self.token = None
        self.headers = None

    def collect_password(self):
        print 'user:    ', self.username
        self.password = getpass.getpass()

    def request_token(self):

        if (self.token == None):

            if (self.password == None):
                self.collect_password()

            post_data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'password',
                'username': self.username,
                'password': self.password
            }

            response = requests.post(urlparse.urljoin(self.url, 'oauth2/access_token/'), data=post_data)
            if not response.ok:
                print response
            else:
                self.token = response.json()
            assert response.ok

        return self.token

    def access_token(self):
        if (self.headers == None):
            token = self.request_token()
        return self.token["access_token"]

    def http_headers(self):
        if (self.headers == None):
            token = self.request_token()
            self.headers = {
                'Authorization' : 'Bearer {}'.format(token["access_token"]),
                'content-type' : 'application/json',
                'User-Agent' : 'Medusa/2.0'
            }

        return self.headers

class VideoLibrary(object):
    """ A VideoLibrary object

    Attributes:
        amara_titles:   A dict of titles by amara_id
        link_titles:    A dict of titles by link_id
        base_titles:    A dict of titles by basename
        subtitles:      A dict of all SubtitleFile by filename
        subtitleids:    A dict of all SubtitleFile id
    """

    medusa_url = None
    jcs_headers = None

    def __init__ (self, name=None):
            self.subtitles = {}
            self.amara_titles = {}
            self.link_titles = {}
            self.base_titles = {}
            self.subtitleids = {}
            self.name = name

    def add_subtitle(self, sf):
        assert not self.subtitles.has_key(sf.filename)
        self.subtitles[sf.filename] = sf

        vt = self.base_titles.get(sf.basename(), None)
        if (not vt):
            #print 'New title \"{}\"'.format(sf.basename())

            assert not self.amara_titles.has_key(sf.amara_id)
            assert not self.link_titles.has_key(sf.link_id)

            vt = VideoTitle()

            self.base_titles[sf.basename()] = vt
            self.amara_titles[sf.amara_id] = vt
            self.link_titles[sf.link_id] = vt
            vt.link_id = sf.link_id

        #print 'add_subtitle (link_id: {}, {}'.format(self.link_id, sf)
        assert sf.filename not in vt.subtitles
        vt.subtitles[sf.filename] = sf
        if (sf.subtitle_id):
            self.subtitleids[sf.subtitle_id] = sf

        vtl = vt.langs.get(sf.amara_lang, None)
        if (vtl):
            if (sf.version in vtl):
                print '*** Subtitle Collision *** ', str(vtl[sf.version]), str(sf)
                assert False
            else:                      
                #print 'New version {}+{} for lang \"{}\" for title \"{}\"'.format(str(sorted(vtl.keys(), reverse=True)), str(sf.version), sf.amara_lang, sf.basename())
                #if sf.link_id == '8e52131e76':
                #    print 'New version {}+{} for lang \"{}\" for title \"{}\"'.format(str(sorted(vtl.keys(), reverse=True)), str(sf.version), sf.amara_lang, sf.basename())
                vtl[sf.version] = sf
        else:
            #print 'New language \"{}\" for title {}'.format(sf.amara_lang, sf.basename())
            #if sf.link_id == '8e52131e76':
            #    print 'New language \"{}\" for title {}'.format(sf.amara_lang, sf.basename())
            vt.langs[sf.amara_lang] = { sf.version : sf }

        if (False and (sf.link_id == '8e52131e76')):
            print 'sf.subtitle_id = {}'.format(sf.subtitle_id)
            if (sf.subtitle_id > 0):
                print 'sub_ids: {}'.format(vt.current_subtitle_ids())


    def crawl_filesystem(self, working_dir):

        print 'VideoLibrary::crawl_fs for subtitles: '

        count = 0
        for dirpath, dirnames, filenames in os.walk(working_dir):
            for filename in [f for f in filenames if f.endswith(".vtt")]:
                
                sf = SubtitleFile(fullpath=os.path.join(dirpath, filename))
                
                # ignore meta-geo language
                if (sf.amara_lang == 'meta-geo'):
                    continue

                count += 1
                if (count % 4 == 0):
                    sys.stdout.write('.')
                    sys.stdout.flush()

                self.add_subtitle(sf)
        print '\nFS:  Total Subtitles: {}, Total Videos: {}'.format(len(self.subtitles.keys()), len(self.link_titles.keys()))


    def crawl_jcs_subtitles(self, medusa_url):

        count = 0
        nextUrl = medusa_url + 'api/v3/dock/subtitles/'
        self.base_titles = {}

        session = requests.Session()

        print 'VideoLibrary::crawl_jcs_subtitles({})'.format(medusa_url)

        while (nextUrl):
            response = session.get(nextUrl, headers=jcs_headers)
            assert response.ok
            jdata = response.json();
            nextUrl = jdata['next']

            for subtitle_entry in jdata['results']:
                sf = SubtitleFile(filename=subtitle_entry['name'])
                sf.project_id = subtitle_entry['project']
                sf.subtitle_id = subtitle_entry['id']
                sf.jcs_json = subtitle_entry
        
                if (not (sf.version > 0)):
                    print 'crawl_jcs_subtitles({}): ignoring malformed subtitle: {}'.format(self.name, str(sf))
                    continue
                
                if ((subtitle_entry['language'] != sf.jcs_lang) or (subtitle_entry['cc'] != sf.cc_flag)):
                    print 'crawl_jcs_subtitles({}): {} language code & cc flag problem {},{} != {},{}'.format(self.name, subtitle_entry['url'], subtitle_entry['language'], sf.jcs_lang, subtitle_entry['cc'], sf.cc_flag)

                if (len(subtitle_entry['translation_service_url']) < 1):
                    print 'crawl_jcs_subtitles({}):'.format(self.name, subtitle_entry['url'], 'missing translation_service_url')

                count += 1
                if (count % 4 == 0):
                    sys.stdout.write('.')
                    sys.stdout.flush()

                self.add_subtitle(sf)
        print '\n{}: Total Subtitles: {}, Total Videos: {}'.format(self.name, len(self.subtitles.keys()), len(self.link_titles.keys()))

    def link_id_to_subtitle_map(self):
        litsm = self.link_titles.values()

    def dump_link_titles(self, name=None):
        print 'VideoLibrary {}: {} titles, {} subtitles'.format(name, len(self.link_titles.items()), len(self.subtitles.items()))
        for lt in self.link_titles.values():
            lt.dump()

    def bind_link_ids_to_projects(self, link_ids, medusa_url):   # AKA crawl_jcs_for_projects
        global jcs_headers

        print 'bind_link_ids_to_projects({}) '.format(medusa_url)

        session = requests.Session()

        bind_count = 0
        total_count = 0

        if True:

            jcs_titles_url = medusa_url + 'api/v3/dock/titles/'
            while (jcs_titles_url):
                resp = session.get(jcs_titles_url, headers=jcs_headers)
                jdata = resp.json()
                if (not resp.ok):
                    print jdata
                assert resp.ok

                jcs_titles_url = jdata['next']
                for title_entity in jdata['results']:

                    total_count += 1

                    title_id = title_entity['id']               
                    release_name = title_entity['release_name']
                    linktitle_id = title_entity['link_submission']
                    project_id = title_entity['project']
                    lid = title_entity['link_id']
                    if (not lid or not lid in link_ids):
                        #print 'bind_link_ids_to_projects: skipping title with link_id: {}, name: "{}"'.format(lid, release_name)
                        continue

                    #print 'bind_link_ids_to_projects: bind title with link_id: {}, name: "{}"'.format(lid, title_entity['name'])
                    link_ids.remove(lid)

                    if lid in self.link_titles:
                        vt = self.link_titles[lid]

                        vt.link_id = lid
                        vt.title_id = title_id
                        vt.release_name = release_name
                        vt.linktitle_id = linktitle_id
                        vt.project_id = project_id

                        for sf in vt.subtitles.values():
                            sf.link_id = lid
                            sf.title_id = title_id
                            sf.release_name = release_name
                            sf.project_id = project_id
                    else:
                        #print 'bind_link_ids_to_projects({}): No subtitles for title with link id: {}'.format(self.name, lid)

                        vt = VideoTitle()

                        vt.link_id = lid
                        vt.title_id = title_id
                        vt.release_name = release_name
                        vt.linktitle_id = linktitle_id
                        vt.project_id = project_id

                        self.link_titles[vt.link_id] = vt

                    bind_count += 1
                    if (bind_count % 4 == 0):
                        sys.stdout.write('.')
                        sys.stdout.flush()


            assert len(link_ids) == 0


        else:

            for lid in link_ids:

                response = session.get(medusa_url + 'api/v3/dock/titles/?link_id=' + lid, headers=jcs_headers)
                assert response.ok
                jdata = response.json()

                title_entity = jdata['results'][0]

                title_id = title_entity['id']
                release_name = title_entity['release_name']
                linktitle_id = title_entity['link_submission']
                project_id = title_entity['project']

                if lid in self.link_titles:
                    vt = self.link_titles[lid]

                    vt.link_id = lid
                    vt.title_id = title_id
                    vt.release_name = release_name
                    vt.linktitle_id = linktitle_id
                    vt.project_id = project_id

                    for sf in vt.subtitles.values():
                        sf.link_id = lid
                        sf.title_id = title_id
                        sf.release_name = release_name
                        sf.project_id = project_id
                else:
                    #print 'bind_link_ids_to_projects({}): No subtitles for title with link id: {}'.format(self.name, lid)

                    vt = VideoTitle()

                    vt.link_id = lid
                    vt.title_id = title_id
                    vt.release_name = release_name
                    vt.linktitle_id = linktitle_id
                    vt.project_id = project_id

                    self.link_titles[vt.link_id] = vt

                bind_count += 1
                total_count += 1
                if (bind_count % 4 == 0):
                    sys.stdout.write('.')
                    sys.stdout.flush()
           
        print '\nTotal Bindings: {}, Total JCS Titles: {}'.format(bind_count, total_count)


class VideoTitle(object):
    """ A VideoTitle File object

    Attributes:
        subtitles:      A dict of subtitles for this VideoTitle
        langs:          A dict of languages of a dict of basenames of a dict of subtitles
        ----------------------------
        release_name:   The JCS release_name
        project_id:     The JCS project ID
        title_id:       The JCS title ID
        link_id:        The JCS Link ID
        tv_id:          The JCS title version ID
        linktitle_id:   The JCS linktitle ID
        mono_cut_id:    The JCS mono cut ID
        stereo_cut_id:  The JCS stereo cut ID
        mono_rv_id:     The JCS mono cut ID
        stereo_rv_id:   The JCS stereo cut ID
    """
    medusa_url = None
    jcs_headers = None

    def __init__ (self):
            self.subtitles = {}
            self.langs = {}
            #################
            self.release_name = None
            self.subtitle_id = 0
            self.project_id = 0
            self.link_id = 0
            self.title_id = 0
            self.tv_id = 0
            self.linktitle_id = 0
            self.mono_cut_id = 0
            self.stereo_cut_id = 0
            self.mono_rv_id = 0
            self.stereo_rv_id = 0
            #################
    
    def dump(self):
        if (len(self.subtitles.values()) > 0):
            print '  VideoTitle: {} {}'.format(self.subtitles.values()[0].basename(), self.release_name)
        else:
            print '  VideoTitle: {} {}'.format(self.link_id, self.release_name)
        for l in self.langs.keys():
            print '    Lang {}:'.format(l) 
            for v in sorted(self.langs[l].keys()):
                print '      Ver {}: {}'.format(v, self.langs[l][v])
            if len(self.langs[l].keys()) > 1:
                #raw_input('Continue?')
                None

    def current_subtitle_ids(self):
        sub_ids = []
        for l in self.langs.keys():
            sf = self.langs[l][max(self.langs[l].keys())]
            sub_ids.append(sf.subtitle_id)
        if False:
            if (len(sub_ids) != len(self.subtitles)):
                print 'current_subtitle_ids: {} != {}'.format(len(sub_ids), len(self.subtitles))
                self.dump()
                raw_input('Continue?')
        return (sorted(sub_ids))

    def assign_subtitles (self, medusa_url, session=None, no_execute=True, health_check=False):

        global jcs_software_version

        if (not session):
            session = requests.session()

        try:
            sf = self.subtitles.values()[0] 
        except IndexError:
            self.dump()
            assert False
        release_name = sf.release_name
        project_id = self.subtitles.values()[0].project_id
        sub_ids = self.current_subtitle_ids()
        token = bearer_token.access_token()

        if health_check:
            healthcheck_renderversion(session, self.link_id, token, medusa_url)
        else:
            chrisr_update(session, self.link_id, token, medusa_url, sub_ids, '7.0.36719_20170318', no_execute)

        return

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

def crawl_link_titles(linkBaseUrl):
    link_ids = []
    linkUrl = linkBaseUrl + "title/"
    linkHeaders = { 'Accept' : 'application/json;indent=2' }
    count = 0
    print 'crawl_link_titles({}) '.format(linkUrl)

    session = requests.Session()
    
    while True:
        myResponse = session.get(linkUrl, headers=linkHeaders)
        assert myResponse.ok
        jData = json.loads(myResponse.content)
        for title in jData['titles']:
            title_url = re.sub("^.*title/(.*)", "\\1", title['url'])
            count += 1
            if (count % 4 == 0):
                sys.stdout.write('.')
                sys.stdout.flush()
            link_ids.append (title_url)

        if jData.get('next') == None:
            break
            
        linkUrl = jData['next']
        linkUrl = re.sub("(.*)(\?.*)(\?.*)", "\\1\\3", linkUrl)
    print
    print 'Total: {}'.format(str(len(link_ids)))
    return link_ids

def upload_subtitle_file_to_project(medusa_url, sf, username, no_execute=True):
    global verbose

    if False:
        for xx in range(56, 58):
            subtitleUrl = 'https://cloudpreview.jauntvr.com/api/v3/dock/subtitles/' + str(xx) + '/'
            print "DELETE", subtitleUrl
            response = requests.delete(subtitleUrl, headers=jcs_headers)
            if not(response.ok):
                print response
    

    print 'upload_subtitle_file_to_project({}, {}, {}, {})'.format(sf.fullpath, sf.filename, sf.project_id, sf.amara_id)
    #return

    response = requests.get('https://cloudpreview.jauntvr.com/api/v3/dock/users/?email='+username, headers=jcs_headers)
    if not(response.ok):
        print response
        sys.exit()
    jData = json.loads(response.content)
    user_id = jData['results'][0]['id']
    #print username, 'user_id:', user_id

    uploadTokenUrl = medusa_url + 'api/v3/dock/users/' + str(user_id) + '/upload_token/'
    #print "GET", uploadTokenUrl
    upload_token_response = requests.get(uploadTokenUrl, headers=jcs_headers)
    if not(upload_token_response.ok):
        print upload_token_response

    jData = json.loads(upload_token_response.content)
    identityPoolId = jData['IdentityPoolId']
    upload_Region = jData['Upload_Region']
    upload_Bucket = jData['Upload_Bucket']
    identityId = jData['IdentityId']
    logins = jData['Logins']

    newData = json.JSONEncoder().encode(
        {
            'project' : sf.project_id,
            'name' : sf.filename,
            'language' : sf.jcs_lang,
            'format' : 'vtt',
            'cc' : sf.cc_flag,
            'translation_service_url' : 'https://amara.org/api/videos/' + sf.amara_id + '/'
        })
    
    print 'POST{} {} {}'.format('-X' if no_execute else '', urlparse.urljoin(medusa_url, 'api/v3/dock/subtitles/'), json.dumps(newData, indent=2))

    #last chance to chicken out
    if (no_execute):
        return

    response = requests.post(medusa_url + 'api/v3/dock/subtitles/', data=newData, headers=jcs_headers)
    if not(response.ok):
        print response
    #print response.content
    jData2 = json.loads(response.content)
    relativePath = jData2['relative_path']
    subtitleUrl = jData2['url']
    print "relative_path: %s"%(relativePath)
    print "url:           %s"%(subtitleUrl)

    boto3.set_stream_logger(name='boto3', level=10)

    client = boto3.client('cognito-identity','us-east-1')
    response = client.get_credentials_for_identity(IdentityId=identityId, Logins=logins)
    secretKey = response['Credentials']['SecretKey']
    sessionToken = response['Credentials']['SessionToken']
    accessKey = response['Credentials']['AccessKeyId']
    #print "SecretKey:     %s"%(secretKey)
    #print "SessionToken:  %s"%(sessionToken)
    #print "AccessKeyId:   %s"%(accessKey)
    #print response

    # Upload a new file
    data = open(sf.fullpath, 'rb')
    s3Key = relativePath + '/'+ sf.filename

    print "put_object"
    s3 = boto3.client('s3', aws_access_key_id=accessKey, aws_secret_access_key=secretKey, aws_session_token=sessionToken)
    print "\nConnection:  %s"%(s3)

    response = s3.put_object(Bucket=upload_Bucket, Key=s3Key, Body=data)
    print 'response: ', response

    print "GET", subtitleUrl
    response = requests.get(subtitleUrl, headers=jcs_headers)
    if not(response.ok):
        print response
    print response.content
    
    newData = json.JSONEncoder().encode({'file' : s3Key})
    print "PATCH", subtitleUrl, json.dumps(newData, indent=2)
    response = requests.patch(subtitleUrl, data=newData, headers=jcs_headers)
    if not(response.ok):
        print response

    print response.content

def main(argv):
    global verbose
    global inputfile
    global outputfile
    global genCsv
    global local_subtitles
    #global jcs_subtitles
    global link_to_subtitle_map
    global jcs_headers
    global bearer_token
    global local_video_titles
    global vl_jcs
    global hack_rv_map
    global hack_force_submit

    doPost = False
    doSubmit = False
    doHealthCheck = False
    doLogRequests = False

    if (len(argv) < 1):
        showUsage(argv[0])
    try:
        opts, args = getopt.getopt(argv[1:], "vhltaxo:i:",
                ["verbose", "help", "post", "submit", "healthcheck", "logrequests" ])
    except getopt.GetoptError as errMsg:
        print "Invalid argument: "+ str(errMsg)
        showUsage(argv[0])

    for opt, arg in opts:
        if (opt == "-h"):
            showUsage(argv[0])
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("--logrequests"):
            doLogRequests = True
        elif opt in ("-h", "--help"):
            showUsage(argv[0])
        elif opt in ("--post"): 
            doPost = True
        elif opt in ("--submit"): 
            doSubmit = True
        elif opt in ("--healthcheck"): 
            doHealthCheck = True

    sys.stdout = codecs.getwriter('utf8')(sys.stdout)

    if doLogRequests:
        logger.setLevel(logging.DEBUG)

    linkBaseUrl = "http://www.jauntvr.com"
    medusa_url = "https://cloudpreview.jauntvr.com/"

    un = 'olaf@jauntvr.com'
    bearer_token = BearerToken(username=un, password=None, url=medusa_url)
    jcs_headers = bearer_token.http_headers()

    SubtitleFile.jcs_headers = jcs_headers
    SubtitleFile.medusa_url = medusa_url


    custom_link_ids = []
    #custom_link_ids = [ 'fb1051a266' ]

    print 'jcs_headers', jcs_headers

    # Enumerate all subtitle entities on JCS
    vl_jcs = VideoLibrary('JCS')
    vl_jcs.crawl_jcs_subtitles(medusa_url=medusa_url)

    # Enumerate all subtitle files found in filesystem location
    vl_fs = VideoLibrary('FS')
    vl_fs.crawl_filesystem('./subtitles/link')

    # Pull all title ID's from Link
    link_ids = crawl_link_titles('https://www.jauntvr.com/')

    #add unlisted titles:
    unlisted_link_ids = [ 'e565aef18e', 'db2c11341b' ]
    link_ids.extend(unlisted_link_ids)

    # For each link ID pull up project info, etc.
    vl_jcs.bind_link_ids_to_projects(link_ids, medusa_url=medusa_url)

    link_id_dict = {}
    for x in link_ids:
        assert len(x) > 0
        l = link_id_dict.get(x, list())
        l.append('Link')
        link_id_dict[x] = l

    for vt in vl_jcs.link_titles.values():
        l = link_id_dict.get(vt.link_id, list())
        l.append('JCS')
        link_id_dict[vt.link_id] = l

    for vt in vl_fs.link_titles.values():
        l = link_id_dict.get(vt.link_id, list())
        l.append('FS')
        link_id_dict[vt.link_id] = l

        # update the JCS subtitles with the project ID for the title.
        jcs_vt = vl_jcs.link_titles.get(vt.link_id, None)
        if (jcs_vt):
            for sf in vt.subtitles.values():
                sf.project_id = jcs_vt.project_id
        else:
            print 'FS link ID \"{}\" has no corresponding JCS subtitles'.format(vt.link_id)
            assert False

    for (link_id, sources) in link_id_dict.items():
        assert (len(sources) <= 3)
        if (len(sources) != 3):
            #print 'NOT3: link_id:{}, sources:{}'.format(str(link_id), str(sources))
            None

    print 'Count of Local Subtitles', len(vl_fs.subtitles)
    print 'Count of JCS Subtitles', len(vl_jcs.subtitles)

    limit = 1000
    for local_sf in vl_fs.subtitles.values():
        if (limit <= 0):
            continue
        
        vt = vl_fs.base_titles[local_sf.basename()]

        max_ver = vt.langs[local_sf.amara_lang][max(vt.langs[local_sf.amara_lang].keys())]
        #print 'checking for downlevel version: max:{} sf:{}'.format(str(max_ver.version), str(local_sf))

        #if (len(vt.langs[local_sf.amara_lang].keys()) > 1):
        #    vt.dump()
        #    raw_input('Continue?')

        if (local_sf.version < max_ver.version):
            print 'skipping downlevel version: max:{} sf:{}'.format(str(max_ver.version), str(local_sf))
            #vt.dump()
            #raw_input('Continue?')
            continue

        if (local_sf.filename in vl_jcs.subtitles):
            jcs_sf = vl_jcs.subtitles[local_sf.filename]
            #print 'jcs_sf: {}, local_sf: {}'.format(jcs_sf, local_sf)
            #print 'jcs file:   ', jcs_sf.filename, '('+str(jcs_sf.subtitle_id) +')'
            #if (jcs_sf.project_id != local_sf.project_id):
            #    print "Potential problem: ", local_sf.filename, jcs_sf.project, " ==? ", local_sf.project, "url:", jcs_sf.jcs_json['url']
            if ((jcs_sf.jcs_lang != local_sf.jcs_lang) or (jcs_sf.cc_flag != local_sf.cc_flag)):
                print "Fix language code: ", jcs_sf.jcs_lang, jcs_sf.cc_flag, " != ", local_sf.jcs_lang, local_sf.cc_flag
                if False:
                    newData = json.JSONEncoder().encode({'language' : local_sf.jcs_lang, 'cc' : local_sf.cc_flag})
                    print "PATCH", jcs_sf.jcs_json['url'], json.dumps(newData, indent=2)
                    response = requests.patch(jcs_sf.jcs_json['url'], data=newData, headers=jcs_headers)
                    if not(response.ok):
                        print response
                    print response.content
            else:
                if False: print "Already present: ", filename
        else:
            limit = limit -1
            vt =  vl_jcs.base_titles.get(local_sf.basename(), None)
            if (vt):
                lang = vt.langs.get(local_sf.amara_lang, None)
                if (lang):
                    ver = lang.get(local_sf.version, None)
                    if (ver):
                            print '*** Collision:', str(ver), str(local_sf)
                            assert False
                    else:
                        print 'New subtitle ver:{} for language:\"{}\" for JCS: {}'.format(str(local_sf.version), str(local_sf.amara_lang), str(local_sf))
                else:
                    print 'New subtitle language:\"{}\" for JCS: {}'.format(local_sf.amara_lang,str(local_sf))

            else:
                print 'First subtitle for title \"{}\" for JCS: {}'.format(str(local_sf.basename()), str(local_sf))


            upload_subtitle_file_to_project(medusa_url, local_sf, un, no_execute=not doPost)

    #assert False
    #logger.setLevel(logging.DEBUG)

    session = requests.Session()

    if (len(custom_link_ids) >= 1):
        link_ids = custom_link_ids
    else:
        link_ids = vl_jcs.link_titles.keys()
    for link_id in link_ids:
        if (link_id in vl_jcs.link_titles):
            if (vl_jcs.link_titles[link_id] and len(vl_jcs.link_titles[link_id].subtitles.values()) > 0):
                vl_jcs.link_titles[link_id].assign_subtitles(medusa_url, session=session, no_execute=not doSubmit, health_check = doHealthCheck)
        else:
            print str(link_id)+' not in link_id array'

    if len(hack_rv_map.keys()) > 0:
        print 'hack_rv_map', hack_rv_map

    
def showUsage (progName):
    print "Usage: "+progName+":"
    sys.exit()

if __name__ == "__main__":
   main(sys.argv)