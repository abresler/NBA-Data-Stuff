

class player():
    def __init__(self, name, team):
        self._name = name
        self._team = team
        #for stat in statslist:

        self._mins  = 0.0
        self._fg    = 0
        self._fga   = 0
        self._3p    = 0
        self._3pa   = 0
        self._ft    = 0
        self._fta   = 0
        self._stl   = 0
        self._ast   = 0
        self._blk   = 0
        self._blkd  = 0
        self._rbo   = 0
        self._rbd   = 0
        self._pf    = 0
        self._pft   = 0
        
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

    def updatestat(self, playerstat, stat, increment):
        '''
        Updates stat "stat" in "playerstats" by "increment; I think
        there is a way to handle these together instead of writing out
        separate updates for each one...idk
        '''
