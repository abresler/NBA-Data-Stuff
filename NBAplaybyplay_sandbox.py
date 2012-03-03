##self._mins  = 0.0
##        self._fg    = 0
##        self._fga   = 0
##        self._3p    = 0
##        self._3pa   = 0
##        self._ft    = 0
##        self._fta   = 0
##        self._stl   = 0
##        self._ast   = 0
##        self._blk   = 0
##        self._blkd  = 0
##        self._rbo   = 0
##        self._rbd   = 0
##        self._pf    = 0
##        self._pft   = 0
##        '''
##        Handles request for player team given Year; if Year not
##        provided, returns most recent team played for / last team
##        played for; self._teams is a dict of YYYY:TTT (year:team
##        keys and values)
##        '''
##        Year = Year if Year else max(self._teams.keys())
##        try:
##            team = self._teams[Year]
##        except KeyError:
##            print(self._name, 'has no team listed for', str(Year))
##            print('Returning most recent team:  ',
##                  str(max(self._teams.keys())))
##            team = max(self._teams.keys())


def parseaction(action, team):
    index = 0
    split_action = action.split()
    name1 = split_action[index]
    index += 1
    if name1.endswith('.'):
        name1 = name1 + ' ' + split_action[index]
        index += 1
    action1 = split_action[index]
    index += 1

def getactionsdict(actions):
    for action in actions:
        sa = re.split(r'(\[|\])', action)[-1].split()
        index = 1
        if sa[0].endswith('.'):
            index = 2
        sa = nltk.bigrams(sa[index:])
        for gram in sa:
            actiondict[gram] += 1
    return actiondict

sub = playbyplay[gameIDdict[gameID][0]:gameIDdict[gameID][1]]
for i, e in enumerate(sub):
    temp = e[3]
    temp = re.split(r'(\[|\])', temp)
    if len(temp)>1:
        '''Reg game play stuff'''
        team = re.split(r'( |:|\(|\))', temp[2])
        action = parseaction(temp[-1], team)


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



#######################################
'''old run parse'''
gameID = '20080428BOSATL'
stats = ['mins', 'fg', 'fga', '3pt', '3pta', 'ft', 'fta',
             'pts', 'stl', 'ast', 'blk', 'rbo', 'rbd', 'pf', 'rb', 'to']

playerIDdict, playerteamdict = \
         NBA1._getplayersteam(fhandlenam, teams)
'''Create array for storing player stats by player name'''
playerid = {}
count = 0
for player in playerIDdict.keys():
    playerid[player] = count
    count += 1

stats_array = []
for i in range(count):
    stats_array.append([0.0 for j in range(len(stats))])
'''Process play-by-play for game "gameID"'''
sub = playbyplay[gameIDdict[gameID][0]:gameIDdict[gameID][1]]
actions = NBA1._getactions(sub, playbyplay[0])
stats_array, gamescore = NBA2.processgameactions(actions, playerid,
                                      teams, stats_array,
                                      playerteamdict)

