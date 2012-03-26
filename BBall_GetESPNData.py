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
import sys, os, re
import pickle
import datetime
import urllib2
from BeautifulSoup import BeautifulSoup as Soup
import parseESPN

'''
nba_root    = "http://scores.espn.go.com/nba/scoreboard?date="
nba_pbp_all = "http://scores.espn.go.com/nba/playbyplay?gameId="+ gameID + "&period=0"
nba_box     = "http://scores.espn.go.com/nba/boxscore?gameId=" + gameID
ncaa_root   = "http://scores.espn.go.com/ncb/scoreboard?date="
'''
'''Links and paths'''
nba_root        = "http://scores.espn.go.com/nba/scoreboard?date="
ncaa_root       = "http://scores.espn.go.com/ncb/scoreboard?date="
nba_box         = "http://scores.espn.go.com/nba/boxscore?gameId="
nba_pbp         = "http://scores.espn.go.com/nba/playbyplay?gameId="
default_path    = "/Users/sinn/NBA-Data-Stuff/DataFiles"

root_dict       = {'NBA':nba_root,
                   'NCAM':ncaa_root
                   }
null_value      = '&nbsp;'
max_args        = 2

def getpbp(gameid, mode=2):
    '''Given an ESPN game ID, grabs the raw play-by-play feed page'''
    try:
        url = nba_pbp + str(gameid) + "&period=0"
        if mode==1:
            pbp = urllib2.urlopen(url).read()
        elif mode==2:
            pbp = parseESPN.getESPNpbp(url)
        return pbp
    except ValueError:
        # need some stuff to spit out error info...
        print('Failed to retreive play-by-play for game ' + str(gameid))
        return list()

def getbox(gameid, mode=2):
    '''Given an ESPN game ID, grabs the raw box score page'''
    try:
        url = nba_box + str(gameid)
        if mode==1:
            box = urllib2.urlopen(url).read()
        elif mode==2:
            box = parseESPN.getESPNbox(url)
        return box
    except ValueError:
        # need some stuff to spit out error info...
        print('Failed to retreive box score for game ' + str(gameid))
        return list()

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
            try: raw_day_summary = urllib2.urlopen(root_dict['NBA']+date).read()
            except: pass
        except:
            # again, need to get error type and return, handle, etc...
            pass
        finally:
            gameids = key_phrase.findall(raw_day_summary)
            return gameids
                
def getargs():
    '''
    Grabs args from terminal run; as of now, just a file containing
    the ESPN game ids desired, and maybe an output file name; change
    to make argstupple an "argsdict";
    '''
    if len(sys.argv[1:]) > max_args: print('disregarding extra args')
    try:
        gameid_file, output_name = sys.argv[1:3]
        return gameid_file, output_name
    except:
        '''Assume no output file name, try to get game id file'''
        try:
            gameid_file = sys.argv[1]
            return gameid_file, str()
        except:
            raise ValueError, 'no game id or game id file provided'

def picklehandle(data, argstuple):
    '''Pickle data, if dicts are not empty'''
    pbp_store = data[0]
    box_store = data[1]
    print "Pickling files..."
    if pbp_store:
        fname = argstuple[1] + "_PBP.pkl" \
                if argstuple[1] else "temp01_PBP.pkl"
        fname = os.path.join(default_path, fname)
        pickledata(fname, pbp_store)
    if box_store:
        fname = argstuple[1] + "_BOX.pkl" \
                if argstuple[1] else "temp01_BOX.pkl"
        fname = os.path.join(default_path, fname)
        pickledata(fname, box_store)

def pickledata(fname, data):
    '''For easy pickling'''
    with open(fname, 'wb') as dbfile:       # use binary mode files in 3.X
        pickle.dump(data, dbfile)           # data is bytes, not str

def unpickledata(fname):
    '''For easy un-pickling'''
    with open(fname, 'rb') as dbfile:
        data = pickle.load(dbfile)
        return data
    
def runmain(gameids, argstuple):
    pbp_store = dict()
    box_store = dict()
    '''Grab data from pages'''
    for gameid in gameids:
        print('Grabbing game ' + str(gameid) + '...')
        pbp_store[gameid] = getpbp(gameid)
        box_store[gameid] = getbox(gameid)
    if argstuple['output']=='raw':
        '''Pickle raw data'''
        picklehandle((pbp_store,box_store), argstuple)
    elif argstuple['output']=='processed':
        '''Extract info from games'''
        
    return 1

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
    argstuple = getargs()
    if argstuple:
        if os.path.isfile(argstuple[0]):
            gameids = getidsfile(argstuple[0])
        elif os.path.isfile(os.path.join(default_path, argstuple[0])):
            gameids = getidsfile(os.path.join(default_path, argstuple[0]))
        else:
            try:
                '''Assume 1-st arg is a date; try to grab main page'''
                gameids = getidswebs(argstuple[0])
            except ValueError:
                msg = 'game id file path invalid OR non-int game id provided'
                raise ValueError, msg
        if not gameids:
            msg = 'No valid game ids provided. Terminating program.'
            raise ValueError, msg
        else:
            '''If everything is OK up to this point, run the main code'''
            if runmain(gameids, argstuple):
                print "Process complete."
                
