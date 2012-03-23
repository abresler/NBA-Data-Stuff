"""
This file is meant to parse the play-by-play data obtained from
http://basketballvalue.com/downloads.php; these files contain 4 columns:
"GameID", "LineNumber", "TimeRemaining", and "Entry", which describes the
event that took place at this time.
"""
import sys, os, re, datetime
from NBA_playerclass import player as pl
from NBA_playerclass import game

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



def _getphrase(line, index):
    '''Finds the next keyword phrase in line, or eol'''
    phrases = ['free', '3pt', 'shot', 'foul', 'timeout', 'violation',
               'rebound', 'turnover', 'tunover', 'steal', 'assist',
               'block', 'substitution']
    if line[index].lower() in phrases:
        phrase = line[index].lower()
        index += 1
    elif index+1 < len(line):
        phrase, index = _getphrase(line, index+1)
    else:
        phrase, index = None, len(line)+1
    return phrase, index


def _getplayer(line, index, oncourt):
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
    player = _isplayer(player, oncourt)
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


def _handleevent(times, line, args, pstats, teams, active, oncourt):
    '''
    This module hnadles events in the "Entry" colum of the play-by-play
    data; given a phrase, line, player, etc., defines the 'players', 'stats',
    and 'args' variables to be passed to the "_updatestats" module;
    '''
    player, phrase, index = args
    players = None
    stats = None
    args = None
    if phrase=='free':
        # throw always follows free; 2 versions
        try:
            # look for ')' to signal made shot
            index       = _updateisym(line, index, ")")
            players     = [player, player]
            stats       = ['PTS', 'FT']
            args        = [1, 'Made']
        except ValueError:
            # look for [M|m]issed to signal missed shot
            case        = re.findall(r'(M|m)issed', ' '.join(line[index:]))
            index       = _updateisym(line, index, case[0]+'issed')
            players     = [player]
            stats       = ['FT']
            args        = ['Missed']
    elif phrase=='3pt' or phrase=='shot':
        index           = _updateisym(line, index, ':')
        players         = [player]
        made            = line[index]
        if made=='Made':
            players.append(player)
            stats       = ['FG', 'PTS']
            args        = ['Made']
            if phrase=='3pt':
                players.append(player)
                stats.append('3PT')
                args.extend([3, 'Made'])
            else:
                args.append(2)
            index       = _updateisym(line, index, ")")
        elif made=='Missed':
            stats       = ['FG']
            args        = ['Missed']
            if phrase=='3pt':
                players.append(player)
                stats.append('3PT')
                args.append('Missed')
            index += 1
        else:
            raise ValueError, 'unexpected next phrase:  ' + made
    elif phrase=='foul':
        players         = [player]
        stats           = ['PF']
        args            = [None]
        if 'Technical' not in line:
            index       = _updateisym(line, index, ")")
        else:
            index       = len(line) + 1
    elif phrase=='timeout':
        index           = len(line)+1
    elif phrase=='violation':
        index           = len(line)+1
    ##    if player != 'Team':
    ##    else:
    elif phrase=='rebound':
        if player != 'Team':
            start       = _updateisym(line, index, "(")
            index       = _updateisym(line, start, ")")
            players     = [player]
            stats       = ['RB']
            args        = [' '.join(line[start:index])]
        else:
            players         = [_getteam(line[0])]
            stats       = ['RB']
            args        = [' '.join(line[start:index])]
            index       = len(line) + 1
            
    elif phrase=='turnover' or phrase=='tunover':
        if player != 'Team':
            players     = [player]
            stats       = ['TO']
            args        = [None]
            index       = _updateisym(line, index, ")")
        else:
            players     = [_getteam(line[0]), _getteamoth(line[0], teams)]
            args        = ['TO', 'STL']
            args        = [None, None]
            index       = len(line) + 1
    elif phrase=='steal':
        player2, index  = _getplayer(line, index+1, active)
        players         = [player2]
        stats           = ['STL']
        args            = [None]
        index           = _updateisym(line, index, ")")
    elif phrase=='assist':
        player2, index  = _getplayer(line, index+1, active)
        players         = [player2]
        stats           = ['AST']
        args            = [None]
        index           = _updateisym(line, index, ")")
    elif phrase=='block':
        player2, index  = _getplayer(line, index+1, active)
        players         = [player2]
        stats           = ['BLK']
        args            = [None]
        index           = _updateisym(line, index, ")")
    elif phrase=='substitution':
        player2, index  = _getplayer(line, index+2, active)
        players         = oncourt.copy
        stats           = ['MIN' * len(oncourt)]
        time_ct         = _timeelapsed(times)
        times           = times(1)
        args            = [time_ct * len(oncourt)]
        index           = len(line)+1
        oncourt.remove(player)
        oncourt.append(player2)
        
    if players and stats and args:
        pstats = _updatestats(players, stats, time, args, pstats)
        
    return index, pstats, times(0), oncourt

    
def _isplayer(player, active):
    '''
    Not what you expect from an "_is..." module;
    if "player" is a player, returns "player"; else,
    returns "None";
    '''
    if player not in active:
        if player!='Team':
            player = None
    return player


def _iniscore(teams):
    '''
    Initializes the gamescore for the teams involved;
    '''
    gamescore = {}
    gamescore[teams[0]] = 0
    gamescore[teams[1]] = 0
    return gamescore

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

def _timeelapsed(times):
    '''
    Takes the (previous ref time, time now) tuple and determines
    the elapsed time between the two points; converts result to
    date-time format and returns
    '''
    t1, t2 = times
    t1 = [int(k) for k in last_time.split(':')]
    t2 = [int(k) for k in time.split(':')]
    dt = datetime.time(0,
                       int(d1[0]-d2[1]),
                       int(d1[1]-d2[1]))
    return dt

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


def _updatescore(team, newscore, gamescore):
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
    

def _updatestats(players, stats, time, args, pstats):
    for i in range(len(players)):
        pstats = _updatestat(time, players[i], stats[i], args[i], pstats)
    return pstats


def _updatestat(time, player, stat, arg, pstats):

    if player:
        try:
            val = pstats[player].updatestat(time, stat, arg)
            if val==-1:
                raise AttributeError, 'this stat requires an argument: ' + stat
            elif val==-2:
                raise ValueError, 'stat "%s" not a player stat' % stat
        except AttributeError:
            raise AttributeError, '%s is not a valid player name' % player
    return pstats
        

def processgame(data, pstats, teams, active, starters):
    '''
    Does as advertised; given a set of actions, in the format as output by
    "_getactions()", interates over the set to extract the information from
    each line and update the relevant tables accordingly;
    players is a dictionary, with player names as keys, player team as val
    teams is a list of the 2 teams involved in the game
    '''
    times   = [t for (t,a) in data]
    actions = [a for (t,a) in data]
    score = _iniscore(teams)
    oncourt = starters
    last_time = '00:48:00'
    for k,action in enumerate(actions):
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
                _updatescore(action[0], action[1], score)
                index += 1
            while index < len(action):
                player, index = _getplayer(action, index, oncourt)
                phrase, index = _getphrase(action, index)
                if phrase and index < len(action):
                    args = (player, phrase.lower(), index)
                    index, pstats, last_time, oncourt = \
                           _handleevent((last_time, times[k]),
                                        action, args, pstats,
                                        teams, oncourt, active)
                else:
                    index = len(action)+1
    return pstats, score



        

