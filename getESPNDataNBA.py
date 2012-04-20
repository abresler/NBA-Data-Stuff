"""
This file grabs complete play-by-play pages and box score pages for games
specified; run from terminal with:

python BBall_GetESPNData.py date|gameidfile|gameid [outputname]

where the first arg can be: a date with the form YYYYMMDD, a file containing
a list of ESPN game ids, or a single ESPN game id; the second, optional arg
is the root name of the output pickle files, one for the play-by-play raw
pages, and the other for the box score raw pages; data format is dictionaries
with the ESPN game ids as keys and the raw pages as values; if a date is used
as input, the program attempts to locate that page, and extracts the
ESPN game ids from the scores summary page for that date;
"""
import sys, os
import re
import datetime
import urllib2

from BeautifulSoup import BeautifulSoup as Soup

import parseESPN
from argshandle import getargs
from picklingIsEasy import picklehandle

'''
nba_root    = "http://scores.espn.go.com/nba/scoreboard?date=" + date
nba_pbp_all = "http://scores.espn.go.com/nba/playbyplay?gameId=" + gameID + "&period=0"
nba_box     = "http://scores.espn.go.com/nba/boxscore?gameId=" + gameID
ncaa_root   = "http://scores.espn.go.com/ncb/scoreboard?date=" + date
'''
'''Links and paths'''
nba_root        = "http://scores.espn.go.com/nba/scoreboard?date="
ncaa_root       = "http://scores.espn.go.com/ncb/scoreboard?date="
nba_ext         = "http://scores.espn.go.com/nba/recap?gameId="
nba_box         = "http://scores.espn.go.com/nba/boxscore?gameId="
nba_pbp         = "http://scores.espn.go.com/nba/playbyplay?gameId="
nba_shots       = "http://scores.espn.go.com/nba/shotchart?gameId="
default_path    = "/Users/sinn/NBA-Data-Stuff/DataFiles"

root_dict       = {'NBA':nba_root,
                   'NCAM':ncaa_root
                   }
null_value      = '&nbsp;'
max_args        = 2

def runmain(gameids, argdict):
    pbp_store = dict()
    box_store = dict()
    ext_store = dict()
    '''Grab data from pages'''
    for gameid in gameids:
        print('Grabbing game ' + str(gameid) + '...')
        pbp_store[gameid] = getpbp(gameid)
        box_store[gameid] = getbox(gameid)
        ext_store[gameid] = getext(gameid)
    picklehandle({'pbp':pbp_store,
                  'box':box_store,
                  'ext':ext_store},
                 argdict)
    return 1

def getext(gameID):
    '''
    Really this is the recap page, but also grabs some other info like game
    location and time, etc; also story analysis of game;
    '''
    try:
        url = nba_ext + str(gameid)
        ext = parseESPN.processESPNpage(url, 'extta')
        return ext
    except ValueError:
        # need some stuff to spit out error info...
        print('Failed to retreive recap for game ' + str(gameid))
        return list()

def getpbp(gameid):
    '''
    Given an ESPN game ID grabs the raw play-by-play feed page if mode==1;
    if mode==2, processes the page with parseESPN.getESPNpbp module;
    '''
    try:
        url = nba_pbp + str(gameid) + "&period=0"
        pbp = parseESPN.processESPNpage(url, 'pbp')
        return pbp
    except ValueError:
        # need some stuff to spit out error info...
        print('Failed to retreive play-by-play for game ' + str(gameid))
        return list()

def getbox(gameid):
    '''
    Given an ESPN game ID grabs the raw bow score feed page if mode==1;
    if mode==2, processes the page with parseESPN.getESPNbox module;
    '''
    try:
        url = nba_box + str(gameid)
        box = parseESPN.processESPNpage(url, 'box')
        return box
    except ValueError:
        # need some stuff to spit out error info...
        print('Failed to retreive box score for game ' + str(gameid))
        return list()

'''These two modules handle obtaining the game ids we want to grabs pages for'''
def getidsfile(fhandle):
    with open(fhandle, 'r') as f1:
        raw = f1.read()
        try:
            gameids = [int(gameid) for gameid in raw.split('\n')]
        except ValueError:
            '''Not all ids in file are valid...'''
            print('Some game ids are not valid; removing invalid ids')
            gameids = list()
            for gameid in raw.split('\n'):
                try: gameids.append(int(gameid))
                except ValueError: pass
        return gameids

def getidswebs(date, cat='NBA'):
    '''Code for parsing main scores page, given a date and category'''
    key_phrase = re.compile(r'''var thisGame = new gameObj\("(\d{7,12})".*\)''')
    if verifydate(date):
        date_formatted = date[4:6] + ' ' + date[6:] + ', ' + date[:4]
        print "Attempting to get %s page from %s" % (cat, date_formatted)
        try:
            raw_day_summary = urllib2.urlopen(root_dict[cat]+date).read()
        except KeyError:
            print 'Non-valid category, %s, provided; using "NBA"' % cat
            try:
                raw_day_summary = urllib2.urlopen(root_dict['NBA']+date).read()
            except urllib2.URLError:
                print 'Failed to fetch ' + root_dict['NBA']+date
        except urllib2.URLError:
            print 'Failed to fetch ' + root_dict[cat]+date
        finally:
            gameids = key_phrase.findall(raw_day_summary)
            return gameids
''''''

def verifydate(date):
    '''Checks to make sure provided date is valid format, in past or now'''
    now = datetime.datetime.now()
    if len(date) != 8:
        print 'WARNING: non-valid date or date in invalid format'
    try:
        if int(date[:4])  <= now.year and\
           int(date[4:6]) <= now.month and\
           int(date[6:])  <= now.day:
            return True
        else:
            return False
    except ValueError:
        print 'non-valid date or date in invalid format'
        
        

if __name__=='__main__':
    """
    Default run from terminal; grab the text file with a list of game
    id's and get the raw pbp and box score pages for each; pickle results
    """
    argdict = getargs(argslist=['file', 'date', 'outname', 'outform'])
    if not argdict.has_key('outform'): argdict['outform'] = 'processed'
    if not argdict.has_key('outname'): argdict['outname'] = "temp01_PBP.pkl"
    if argdict:
        if argdict.has_key('file'): 
            if os.path.isfile(argdict['file']):
                gameids = getidsfile(argdict['file'])
            elif os.path.isfile(os.path.join(default_path, argdict['file'])):
                gameids = getidsfile(os.path.join(default_path, argdict['file']))
        elif argdict.has_key('date'):
            gameids = getidswebs(argdict['date'])
        if not gameids:
            msg = 'No valid game ids provided. Terminating program.'
            raise ValueError, msg
        else:
            '''If everything is OK up to this point, run the main code'''
            if runmain(gameids, argdict):
                print "Process complete."
                
