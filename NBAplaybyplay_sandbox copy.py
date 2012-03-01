##def parseaction(action, team):
##    index = 0
##    split_action = action.split()
##    name1 = split_action[index]
##    index += 1
##    if name1.endswith('.'):
##        name1 = name1 + ' ' + split_action[index]
##        index += 1
##    action1 = split_action[index]
##    index += 1
##
##def getactionsdict(actions):
##    for action in actions:
##        sa = re.split(r'(\[|\])', action)[-1].split()
##        index = 1
##        if sa[0].endswith('.'):
##            index = 2
##        sa = nltk.bigrams(sa[index:])
##        for gram in sa:
##            actiondict[gram] += 1
##    return actiondict
##
##sub = playbyplay[gameIDdict[gameID][0]:gameIDdict[gameID][1]]
##for i, e in enumerate(sub):
##    temp = e[3]
##    temp = re.split(r'(\[|\])', temp)
##    if len(temp)>1:
##        '''Reg game play stuff'''
##        team = re.split(r'( |:|\(|\))', temp[2]
##        action = parseaction(temp[-1], team)



def _getphrase(line, index):
    '''Finds the next keyword phrase in line, or eol'''
    phrases = ['free', '3pt', 'shot', 'foul', 'timeout', 'violation',
               'rebound', 'turnover', 'tunover', 'steal', 'assist', 'block']
    if line[index].lower() in phrases:
        phrase = line[index].lower()
        index += 1
    elif index < len(line):
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

def _isplayer(player, playerid):
    '''
    Not what you expect from an "_is..." module;
    if "player" is a player, returns "player"; else,
    returns "None";
    '''
    if player not in playerid.keys():
        player = None
    return player

def _getofdf(line, player, players):
    '''
    Returns whether the player is currently on offense
    or defense; used for rebound stats, etc.
    '''
    team = _getteam(line[0])
    if players[player]==team:
        ofdf = 'OF'
    else:
        ofdf = 'DF'
    return ofdf

def _getteam(team):
    '''
    Take the 1st entry of a line and extracts the 3-letter
    abvr. corresponding to a team.
    '''
    team = team.strip('[')
    team = team.strip(']')
    return team

def _getteamoth(team):
    '''
    Finds current team (as denoted by the 1st entry on a line)
    and returns the 3 letter abrv. for the other team playing
    by using the 'teams' variable, the list of the 2 teams
    playing
    '''
   # global teams
    team = _getteam(team)
    team = list(set(teams).difference(set([team])))[0]
    return team

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

def _updategamescore(team, newscore):
    '''
    Uses the info in action[:1] to update the score for the
    team on offense after they have scored
    '''
    team = _getteam(team)
    score = newscores.strip(']').split('-')[0]
    _updatescore(team, score)

def _updategameposition(update, quarter=0):
    if update=='start':
        quarter += 1
    if update=='jump' and quarter>=4:
        # start or cont. overtime
        OT = True
        quarter += 1
    

def _updateplaystat(player, playerid, stat, args=None):
    """
    need some actual content here, eh?
    
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
    if stat.lower() in stats:
        if stat.lower() in reqargs and args==None:
            raise AttributeError, 'this stat requires an argument: ' + stat
        else:
            index = playerid[player]
            if stat=='PTS':
                stats_array[index][stats.index('pts')] += args
            elif stat=='FG':
                stats__array[index][stats.index('fga')] += 1
                if args=='Made':
                    stats__array[index][stats.index('fg')] += 1
            elif stat=='3PT':
                stats__array[index][stats.index('3pta')] += 1
                if args=='Made':
                    stats__array[index][stats.index('3pt')] += 1
            elif stat=='FT':
                stats__array[index][stats.index('fta')] += 1
                if args=='Made':
                    stats__array[index][stats.index('ft')] += 1
            elif stat=='STL':
                stats__array[index][stats.index('stl')] += 1
            elif stat=='AST':
                stats__array[index][stats.index('ast')] += 1
            elif stat=='BLK':
                stats__array[index][stats.index('blk')] += 1  
            elif stat=='TO':
                stats__array[index][stats.index('to')] += 1
            elif stat=='PF':
                stats__array[index][stats.index('pf')] += 1
            elif stat=='RB':
                if args=='OF':
                    stats__array[index][stats.index('rbo')] += 1
                elif args=='DF':
                    stats__array[index][stats.index('rbd')] += 1
    else:
        raise ValueError, 'stat "%s" not a player stat' % stat
            
    
       
def _handleevent(line, phrase, index, player=None):
    '''
    This module hnadles events in the "Entry" colum of the play-by-play
    data; 
    '''
    if phrase=='free':
        # throw always follows free; 2 versions
        try:
            # look for '(' to signal made shot
            index = _updateisym(line, start, ")")
            players = [player, player]
            stats = ['PTS', 'FT']
            args = [1, 'Made']
        except ValueError:
            # look for [M|m]issed to signal missed shot
            case = re.findall(r'(M|m)issed', ' '.join(line[index]))
            index = _updateisym(line, index, case[0]+'issed')
            players = [player]
            stats = ['FT']
            args = ['Missed']
    elif phrase=='3pt' or phrase=='shot':
        index = _updateisym(line, index, ':')
        players = [player player]
        made = line[index]
        if made=='Made':
            stats = ['FG', 'PTS']
            args = ['Made']
            if phrase=='3pt':
                players.append[player]
                stats.append('3pt')
                args.extend([3, 'Made'])
            else:
                args.append(2)
            index = _updateisym(line, index, ")")
        elif made=='Missed':
            stats = ['FG']
            args = ['Missed']
            if phrase=='3pt':
                stats.append('3pt')
                args.append('Missed')
            index += index
        else:
            raise ValueError, 'unexpected next phrase:  ' + made
    elif phrase=='foul':
        player = [player]
        stat = ['PF']
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
            _updateplaystat(player, playerid,
                            'RB', args=_getofdf(player,line[0]))
        else:
            _updateplaystat(_getteam(line[0]), playerid, 'RB',
                            args=_getofdf(_getteam(line[0]), line[0]))
            index = len(line)
            
    elif phrase=='turnover' or phrase=='tunover':
        if player != 'Team':
            _updateplaystat(player, playerid, 'TO')
            index = _updateisym(line, index, ")")
        else:
            _updateplaystat(_getteam(line[0]), playerid, 'TO')
            _updateplaystat(_getteamoth(line[0]), playerid, 'STL')
            index = len(line)
    elif phrase=='steal':
        player2, index = _getplayer(line,index+2)
        _updateplaystat(player2, playerid, 'STL')
        index = _updateisym(line, index, ")")
    elif phrase=='assist':
        player2, index = _getplayer(line,index+2)
        _updateplaystat(player2, playerid,  'AST')
        index = _updateisym(line, index, ")")
    elif phrase=='block':
        player2, index = _getplayer(line,index+2)
        _updateplaystat(player2, playerid,  'BLK')
        index = _updateisym(line, index, ")")

    return index

    
def processgameactions(actions, players, playerid, teams, stats_array):
    '''
    Does as advertised; given a set of actions, in the format as output by
    "_getactions()", interates over the set to extract the information from
    each line and update the relevant tables accordingly;
    players is a dictionary, with player names as keys, player team as val
    teams is a list of the 2 teams involved in the game
    '''
    
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
                _updategamescore(action[0], action[1])
                index += 1
            while index < len(action):
                player, index = _getplayer(action, index, playerid)
                phrase, index = _getphrase(action, index)
                if phrase and index < len(action):
                    index = _handleevent(action, phrase.lower(),
                                         index, player=player)
                else:
                    index = len(action)+1
    return stats_array
