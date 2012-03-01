"""
This file is meant to parse the play-by-play data obtained from
http://basketballvalue.com/downloads.php; these files contain 4 columns:
"GameID", "LineNumber", "TimeRemaining", and "Entry", which describes the
event that took place at this time.
"""
import sys, os, re


def _getindex(header, detail):
    '''Pretty simple at the moment, by allows for dict'''
    try:
        pos = header.index(detail)
    except ValueError:
        print "ValueError:  data field not in header:  " + detail
        pos = -1
    return pos


def _getindexes(header, details):
    '''Feeds into _getindex to obtain multi positions'''
    poses = []
    for detail in details:
        pos = _getindex(header, detail)
        if pos==-1:
            poses.append('NONE')    # to prevent errors w/ '-1' ind
        else: poses.append(pos)
    return poses
        

def _getgameIDs(data, header):
    '''
    Gets the set of game IDs in the data set; they are in the format:
    "YYYYMMDDAWAHOM" (i.e., 4-digit year, 2-digit mon, 2-digit day,
    away team 3-letter abvr., home team 3-letter abvr.)
    '''
    pos = _getindex(header, 'GameID')
    if pos > -1:
        gameIDs = set(e[pos] for e in data)
    else: gameIDs = []
    return gameIDs


def _getactions(data, header=None):
    '''
    Obtains the set of actions under the "Entry" columnn in the playbyplay
    data; splits each line into it's most basic parts to be easily
    read and data extracted
    '''
    header = header if header else data[0]
    data = data[1:] if header==data[0] else data
    pos = _getindex(header, 'Entry')
    actions = [line[pos] for line in data if line not in ['', ['']]]
    actions = [re.split(r'(:|\(|\))', e) for e in actions]
    actions = [' '.join(e).split() for e in actions]
    return actions


def _getgamelines(data, header=None):
    '''
    Creates a dictionary for which lines the data for each game
    reside on; if issues with finding start / stop lines for a game,
    imforms user, but creates dict for other games; if no gamesID
    list exists, informs user and does not return any values in dict
    '''
    header = header if header else data[0]
    data = data[1:] if header==data[0] else data
    gameIDs = _getgameIDs(data, header=header)
    if gameIDs != []:
        gamelinesdict = {}
        pos = _getindex(header, 'GameID')
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


def _getplayersteam(fhandle, teams):
    '''
    Given an fhandle corresponding to a playersYYYY.. file,
    e.g. "players2008playoffs20081211", and a 3 letter team abvr.,
    e.g. "HOU", obtains the set of player names associated with that
    team from the file, and creates a name-id dictionary for those players
    '''
    playersteams = loadfile(fhandle)
    ID, Name, Team = _getindexes(playersteams[0], \
                                 ["PlayerID", "PlayerName", "TeamName3"])
    playerIDdict = {}
    playerteamdict = {}
    for line in playersteams[1:]:
        ##line = line.split("\t")
	if line[Team] in teams:
            playerIDdict[line[Name]] = line[ID]
            playerteamdict[line[Name]] = line[Team]
    return playerIDdict, playerteamdict


def _makenameIDdict(fhandle):
    '''
    Does as advertised, using the file
    "playersYYYYseason_typeYYYY.txt" file
    '''
    data = loadfile(fhandle)
    ID, name = _getindexes(data[0], ["PlayerID","PlayerName"])
    if ID!='NONE' and name!='NONE':
        nameIDdict = {}
        for line in data[1:]:
            nameIDdict[line[name]] = line[ID]
    else:
        print 'Error with finding data field; no name dict created'
    return nameIDdict
    

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

    

