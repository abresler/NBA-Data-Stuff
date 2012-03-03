"""
This file is meant to parse the play-by-play data obtained from
http://basketballvalue.com/downloads.php; these files contain 4 columns:
"GameID", "LineNumber", "TimeRemaining", and "Entry", which describes the
event that took place at this time.
"""
import sys, os, re

"""
'PTS'
'3PT'   'Missed', 'Made'
'FT'    'Missed', 'Made'
'STL'
'BLK'
'RB'    'OF', 'DF'
'AST'
'PF'
"""
stats = ['mins', 'fg', 'fga', '3pt', '3pta', 'ft', 'fta',
         'pts', 'stl', 'ast', 'blk', 'rbo', 'rbd', 'pf', 'rb', 'to']
reqargs = ['pts', 'fg', '3pt', 'ft', 'rb']


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


def _getphrase(line, index):
    '''Finds the next keyword phrase in line, or eol'''
    phrases = ['free', '3pt', 'shot', 'foul', 'timeout', 'violation',
               'rebound', 'turnover', 'tunover', 'steal', 'assist', 'block']
    if line[index].lower() in phrases:
        phrase = line[index].lower()
        index += 1
    elif index+1 < len(line):
        phrase, index = _getphrase(line, index+1)
    else:
        phrase, index = None, len(line)+1
    return phrase, index


def _getplayer(line, index, playerid):
    '''
    Gets the name of the current player in Entry, and returns
    the name and the new starting index (sicne some player's
    names take up 2 entries in line)
    '''
    player = line[index]
    index += 1
    if player.endswith('.'):
        player = player + ' ' + line[index]
        index += 1
    player = _isplayer(player, playerid)
    if not player:
        # shift index back one space
        index -= 1
    return player, index


def _getteam(team):
    '''
    Take the 1st entry of a line and extracts the 3-letter
    abvr. corresponding to a team.
    '''
    team = team.strip('[')
    team = team.strip(']')
    return team


def _getteamoth(team, teams):
    '''
    Finds current team (as denoted by the 1st entry on a line)
    and returns the 3 letter abrv. for the other team playing
    by using the 'teams' variable, the list of the 2 teams
    playing
    '''
    team = _getteam(team)
    team = list(set(teams).difference(set([team])))[0]
    return team


def _handleevent(line, phrase, index, stats_array, teams,
                 player=None, playerid = [], playerteamdict = []):
    '''
    This module hnadles events in the "Entry" colum of the play-by-play
    data; given a phrase, line, player, etc., defines the 'players', 'stats',
    and 'args' variables to be passed to the "_updatestats" module;
    '''
    players = None
    stats = None
    args = None
    if phrase=='free':
        # throw always follows free; 2 versions
        try:
            # look for '(' to signal made shot
            index = _updateisym(line, index, ")")
            players = [player, player]
            stats = ['PTS', 'FT']
            args = [1, 'Made']
        except ValueError:
            # look for [M|m]issed to signal missed shot
            case = re.findall(r'(M|m)issed', ' '.join(line[index:]))
            index = _updateisym(line, index, case[0]+'issed')
            players = [player]
            stats = ['FT']
            args = ['Missed']
    elif phrase=='3pt' or phrase=='shot':
        index = _updateisym(line, index, ':')
        players = [player]
        made = line[index]
        if made=='Made':
            players.append(player)
            stats = ['FG', 'PTS']
            args = ['Made']
            if phrase=='3pt':
                players.append(player)
                stats.append('3PT')
                args.extend([3, 'Made'])
            else:
                args.append(2)
            index = _updateisym(line, index, ")")
        elif made=='Missed':
            stats = ['FG']
            args = ['Missed']
            if phrase=='3pt':
                players.append(player)
                stats.append('3PT')
                args.append('Missed')
            index += 1
        else:
            raise ValueError, 'unexpected next phrase:  ' + made
    elif phrase=='foul':
        players = [player]
        stats = ['PF']
        args = [None]
        index = _updateisym(line, index, ")")
    elif phrase=='timeout':
        index = len(line)+1
    elif phrase=='violation':
        index = len(line)+1
    ##    if player != 'Team':
    ##    else:
    elif phrase=='rebound':
        if player != 'Team':
            start = _updateisym(line, index, "(")
            index = _updateisym(line, start, ")")
            players = [player]
            stats = ['RB']
            args = [' '.join(line[start:index])]
        else:
            players = [_getteam(line[0])]
            stats = ['RB']
            args = [' '.join(line[start:index])]
            index = len(line) + 1
            
    elif phrase=='turnover' or phrase=='tunover':
        if player != 'Team':
            players = [player]
            stats = ['TO']
            args = [None]
            index = _updateisym(line, index, ")")
        else:
            players = [_getteam(line[0]), _getteamoth(line[0], teams)]
            args = ['TO', 'STL']
            args = [None, None]
            index = len(line) + 1
    elif phrase=='steal':
        player2, index = _getplayer(line,index+1, playerid)
        players = [player2]
        stats = ['STL']
        args = [None]
        index = _updateisym(line, index, ")")
    elif phrase=='assist':
        player2, index = _getplayer(line,index+1, playerid)
        players = [player2]
        stats = ['AST']
        args = [None]
        index = _updateisym(line, index, ")")
    elif phrase=='block':
        player2, index = _getplayer(line,index+1, playerid)
        players = [player2]
        stats = ['BLK']
        args = [None]
        index = _updateisym(line, index, ")")

    if players and stats and args:
        _updatestats(players, stats, args, playerid, stats_array)
        
    return index

    
def _isplayer(player, playerid):
    '''
    Not what you expect from an "_is..." module;
    if "player" is a player, returns "player"; else,
    returns "None";
    '''
    if player not in playerid.keys():
        if player!='Team':
            player = None
    return player


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


def _updateisym(line, index, sym):
    '''
    Moves the current index on the current line to the first
    position following the symbol 'sym'; if symbol not found,
    then there is a grave issue with the parsing
    '''
    try:
        index = line[index:].index(sym)+1+index
    except ValueError:
        raise ValueError, 'symbol not found; serious issue'
    return index


def _updategamescore(team, newscore, gamescore):
    '''
    Uses the info in action[:1] to update the score for the
    team on offense after they have scored
    '''
    team = _getteam(team)
    score = newscore.strip(']').split('-')[0]
    gamescore[team] = int(score)


def _updategameposition(update, quarter=0):
    if update=='start':
        quarter += 1
    if update=='jump' and quarter>=4:
        # start or cont. overtime
        OT = True
        quarter += 1
    

def _updatestats(players, stats, args, playerid, stats_array):
    for i in range(len(players)):
        _updatestat(players[i], stats[i], args[i], playerid, stats_array)


def _updatestat(player, stat, args, playerid, stats_array):
    
    if stat.lower() in stats:
        if stat.lower() in reqargs and args==None:
            raise AttributeError, 'this stat requires an argument: ' + stat
        #-1
        else:
            index = playerid[player]
            if stat=='PTS':
                stats_array[index][stats.index('pts')] += args
            elif stat=='FG':
                stats_array[index][stats.index('fga')] += 1
                if args=='Made':
                    stats_array[index][stats.index('fg')] += 1
            elif stat=='3PT':
                stats_array[index][stats.index('3pta')] += 1
                if args=='Made':
                    stats_array[index][stats.index('3pt')] += 1
            elif stat=='FT':
                stats_array[index][stats.index('fta')] += 1
                if args=='Made':
                    stats_array[index][stats.index('ft')] += 1
            elif stat=='STL':
                stats_array[index][stats.index('stl')] += 1
            elif stat=='AST':
                stats_array[index][stats.index('ast')] += 1
            elif stat=='BLK':
                stats_array[index][stats.index('blk')] += 1  
            elif stat=='TO':
                stats_array[index][stats.index('to')] += 1
            elif stat=='PF':
                stats_array[index][stats.index('pf')] += 1
            elif stat=='RB':
                args = args.split()
                args = [arg.split(":") for arg in args]
                stats_array[index][stats.index('rbo')] = int(args[2][0])
                stats_array[index][stats.index('rbd')] = int(args[5][0])
                stats_array[index][stats.index('rb')] = \
                                       int(args[2][0]) + int(args[5][0])
    else:
        raise ValueError, 'stat "%s" not a player stat' % stat
    #-2
    

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

    
def processgameactions(actions, playerid, teams, stats_array, playerteamdict):
    '''
    Does as advertised; given a set of actions, in the format as output by
    "_getactions()", interates over the set to extract the information from
    each line and update the relevant tables accordingly;
    players is a dictionary, with player names as keys, player team as val
    teams is a list of the 2 teams involved in the game
    '''
    gamescore = {}
    gamescore[teams[0]] = 0
    gamescore[teams[1]] = 0
    for action in actions:
        index = 0
        if action[index].lower()=='start' or action[index].lower()=='end' \
           or action[index].lower()=='jump':
            '''These tags mark start / end of quarter / game'''
            _updategameposition(action[0].lower())
        elif action[index].lower=='timeout':
            pass
        elif action[index].startswith('['):
            '''This is an event-driven Entry; parse as such'''
            index += 1
            if action[index].endswith(']'):
                # team scored, move one space right
                _updategamescore(action[0], action[1], gamescore)
                index += 1
            while index < len(action):
                player, index = _getplayer(action, index, playerid)
                phrase, index = _getphrase(action, index)
                if phrase and index < len(action):
                    index = _handleevent(action, phrase.lower(), index,
                                         stats_array, teams,
                                         player=player, playerid=playerid,
                                         playerteamdict=playerteamdict)
                else:
                    index = len(action)+1
    return stats_array, gamescore


def parsepbp(fhandle, gameid=None):

    playbyplay = loadfile(fhandlepbp)
    gameIDdict = _getgamelines(playbyplay)
    gameids = list(gameid) if gameid else gameIDdict.keys()
    for game in gameids:
        

