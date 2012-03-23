import os, sys, re
import NBA_playerclass as NBAP


def createplayers(fhandle):
    '''
    Given an fhandle corresponding to a playersYYYY.. file,
    e.g. "players2008playoffs20081211", and a 3 letter team abvr.,
    e.g. "HOU", obtains the set of player names associated with that
    team from the file, and creates a name-id dictionary for those players
    '''
    playerdata = loadfile(fhandle)
    ID, Name, Team = getindexes(playerdata[0], \
                                 ["PlayerID", "PlayerName", "TeamName3"])
    playerstats = {}
    for line in playerdata[1:]:
        playerstats[line[Name]] = NBAP.player(line[Name],
                                              line[Team],
                                              line[ID])
    return playerstats


def creategames(fhandlepbp, fhandlenam):
    '''

    '''
    gamedata = loadfile(
    gamestats = NBAP.game(fhandlepbp, fhandlenam)
    return gamestats


def getpbp(fhandle, args):
    '''
    Loads the play-by-play file at fhandle, creates dictionary of game
    indicies in play-by-play, where keys are game IDs and values are
    (start, stop) tuples, where "start" is the first line the game
    appears on in play-by-play, and "stop" is the last line; only gets
    the data fields in the list "args";
    '''
    playbyplay = loadfile(fhandle)
    gamedict = getgamelines(playbyplay)
    holder = dict()
    if args[0]=='all' or args=='all':
        args = ['gameID','linenum','times','actions']
    if 'gameID' in args:    holder('gameIDs')   = getgameIDs(playbyplay)
    if 'linenum' in args:   holder('linenum')   = getlinenum(playbyplay)
    if 'times' in args:     holder('times')     = gettimes(playbyplay)
    if 'actions' in args:   holder('actions')   = getactions(playbyplay)
    return gamedict, zip(holder(key) for key in args)

def getindex(header, detail):
    '''Pretty simple at the moment, by allows for dict'''
    try:
        pos = header.index(detail)
    except ValueError:
        print "ValueError:  data field not in header:  " + detail
        pos = -1
    return pos

def getindexes(header, details):
    '''Feeds into _getindex to obtain multi positions'''
    poses = []
    for detail in details:
        pos = getindex(header, detail)
        if pos==-1:
            poses.append('NONE')    # to prevent errors w/ '-1' ind
        else: poses.append(pos)
    return poses

def time2secs(time):
    '''Converts HH:MM:SS time format to seconds; pretty straightforward'''
    # check for correct format:
    timepattern = re.compile(r'\d{2}:\d{2}:\d{2}')
    if timepattern.match(time):
        time = time.split(':')
        secs = 60*60*int(time[0]) + \
               60*int(time[1]) + \
               int(time[2])
        return secs
    else:
        raise AttributeError, 'incorrect format for time; expected "HH:MM:SS"'


def loadfile(fhandle):
    '''Load the desired data file; return error if file does not exist'''
    if os.path.isfile(fhandle):
        '''e.g. "/Volumes/NO NAME/NBAData/data2008playoffs20081211.txt"'''
        with open(fhandle, 'r') as f1:
            data = f1.read()
        # check for line delim:
        delim = '\r'
        if data.endswith('\r\n'): delim = '\r\n'
        data = data.split(delim)
        # split each line into the 4 columns
        data = [e.split('\t') for e in data]
        if data[-1] in [[''], '', [' '], ' ']:
            data = data[:-1]
        return data
    else:
        raise IOError, 'No such file or directory'
    

def getgamelines(data, header=None):
    '''
    Creates a dictionary for which lines the data for each game
    reside on; if issues with finding start / stop lines for a game,
    imforms user, but creates dict for other games; if no gamesID
    list exists, informs user and does not return any values in dict
    '''
    header = header if header else data[0]
    data = data[1:] if header==data[0] else data
    gameIDs = getgameIDs(data, header=header)
    if gameIDs != []:
        gamelinesdict = {}
        pos = getindex(header, 'GameID')
        fullIDs = [e[pos] for e in data]
        revfullIDs = [e for e in reversed(fullIDs)]
        for ID in gameIDs:
            try:
                start = fullIDs.index(ID)
                stop = len(fullIDs) - revfullIDs.index(ID)
                gamelinesdict[ID] = (start, stop)
            except ValueError:
                print 'some issue with finding start / stop points:  ' + ID
        return gamelinesdict
    else:
        print 'Error with finding data field; no game dict created'


def getgameIDs(data, header=None):
    '''
    Gets the set of game IDs in the data set; they are in the format:
    "YYYYMMDDAWAHOM" (i.e., 4-digit year, 2-digit mon, 2-digit day,
    away team 3-letter abvr., home team 3-letter abvr.)
    '''
    header = header if header else data[0]
    data = data[1:] if header==data[0] else data
    pos = getindex(header, 'GameID')
    if pos > -1:
        gameIDs = set(e[pos] for e in data)
    else: gameIDs = []
    return gameIDs

def getlinenum(data, header=None):
    '''
    Obtains the set of line nums under the "LineNumber" column in the
    playbyplay data;
    '''
    header = header if header else data[0]
    data = data[1:] if header==data[0] else data
    pos = getindex(header, 'LineNumber')
    linenums = [line[pos] for line in data if line not in ['', ['']]]
    return linenums

def gettimes(data, header=None):
    '''
    Obtains the set of times under the "TimeRemaining" column in the
    playbyplay data;
    '''
    header = header if header else data[0]
    data = data[1:] if header==data[0] else data
    pos = getindex(header, 'TimeRemaining')
    times = [line[pos] for line in data if line not in ['', ['']]]
    return times

def getactions(data, header=None):
    '''
    Obtains the set of actions under the "Entry" columnn in the playbyplay
    data; splits each line into it's most basic parts to be easily
    read and data extracted
    '''
    header = header if header else data[0]
    data = data[1:] if header==data[0] else data
    pos = getindex(header, 'Entry')
    actions = [line[pos] for line in data if line not in ['', ['']]]
    actions = [re.split(r'(:|\(|\))', e) for e in actions]
    actions = [' '.join(e).split() for e in actions]
    return actions

