import sys, os

class player():
    def __init__(self, name, team, ID):
        self._name  = name
        self._team  = team
        self._ID    = ID
        #for stat in statslist:

        self._games = set()

    def _newgame(self, gameID):
        '''
        Sets the gameID as the current game, and sets the
        current stats equal to 0's; also, automatically flushes old stats
        if they have not been flushed;
        '''
        stats = {'mins':0.0, 'fg':0, 'fga':0, '3pt':0, '3pta':0, 'ft':0,
                 'fta':0, 'pts':0, 'stl':0, 'ast':0, 'blk':0, 'rbo':0,
                 'rbd':0, 'pf':0, 'rb':0, 'to':0}
    

        if self.currentgame not in self._games:
            self._flushgame()
        self.currentgame = gameID
        self.stats = stats
        
    def _flushgame(self):
        '''
        Adds the new game ID to the set of games played in, and
        moves the current game data to a stats dictionary with
        keys as game ids, and entries are dictionaries with stat
        handles as keys;
        '''
        self._games.add(gameID)
        self._gamestats[gameID] = self.stats
        
        
    def update(self, name, stat, increment):
        '''
        Checks to make sure "name" in a valid player and "stat"
        is a valid stat; if so, calls updatestat module to increment
        "stat" by "increment"; if not, returns a ValueError
        '''
        if name in playerlist:
            if stat in statlist:
                playerstats = PlayerStats[name]
                playerstats = updatestat(playerstat, stat, increment)
                PlayerStats[name] = playerstats
            else:
                raise ValueError, 'stat "%s" not a player stat' % stat
        else:
            raise ValueError, 'player "%s" not a player' % name


    def updatestat(self, stat, arg):
        '''
        Updates stat "stat" in "playerstats" by "increment; I think
        there is a way to handle these together instead of writing out
        separate updates for each one...idk
        '''
        reqargs = ['pts', 'fg', '3pt', 'ft', 'rb']

        if stat.lower() in stats:
            if stat.lower() in reqargs and args==None:
                return -1
            else:
                if stat=='PTS':
                    self.stats['pts'] += args
                elif stat=='FG':
                    self.stats['fga'] += 1
                    if args=='Made':
                        self.stats['fg'] += 1
                elif stat=='3PT':
                    self.stats['3pta'] += 1
                    if args=='Made':
                        self.stats['3pt'] += 1
                elif stat=='FT':
                    self.stats['fta'] += 1
                    if args=='Made':
                        self.stats['ft'] += 1
                elif stat=='STL':
                    self.stats['stl'] += 1
                elif stat=='AST':
                    self.stats['ast'] += 1
                elif stat=='BLK':
                    self.stats['blk'] += 1  
                elif stat=='TO':
                    self.stats['to'] += 1
                elif stat=='PF':
                    self.stats['pf'] += 1
                elif stat=='RB':
                    args = args.split()
                    args = [arg.split(":") for arg in args]
                    self.stats['rbo']  = int(args[2][0])
                    self.stats['rbd']  = int(args[5][0])
                    self.stats['rb']   = int(args[2][0]) + int(args[5][0])
                return 1
        else:
            return -2



    def team(self, Year=None):
        '''
        Handles request for player team given Year; if Year not
        provided, returns most recent team played for / last team
        played for; self._teams is a dict of YYYY:TTT (year:team
        keys and values)
        '''
        Year = Year if Year else max(self._teams.keys())
        try:
            team = self._teams[Year]
        except KeyError:
            print(self._name, 'has no team listed for', str(Year))
            print('Returning most recent team:  ',
                  str(max(self._teams.keys())))
            team = max(self._teams.keys())
        return team
             
