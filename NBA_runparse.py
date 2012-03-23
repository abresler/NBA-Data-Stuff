import os, sys
import NBA_parseplaybyplay as PPBP
import NBA_playerclass as NBAP
import NBA_loadandsplit as LAS
import write-out-data-01 as WRT

def getgames(games):
    '''
    Returns the stats from all games contained in self as a dictionary
    with keys as game ids and values as returns from 'getgame(game id)";
    '''
    out = dict()
    for game in games.keys():
        out[game] = game.getgame()
    out['statlist'] = NPAP.getstatlist()
    return out

print('checking files and loading game files...')
chdir = os.getcwd()
pbpfname    = "playbyplay20072008reg20081211"
plafname    = "players20072008reg20081211"
fhandlepbp  = os.path.join(chdir,'DataFiles', pbpfname+'.txt')
fhandlenam  = os.path.join(chdir,'DataFiles', plafname+'.txt')

# initialize players dictionary, game dictionary
pstats = LAS.createplayers(fhandlenam)
gstats = []
# load play-by-play and find game indicies; pbp is times and actions
gamedict, pbp = LAS.getpbp(fhandlepbp, ['times', 'actions'])

# iterate over games and parse play-by-play
print('parsing play-by-play data...')
for game in gamedict.keys():
    print('on game', game)
    # get teams
    home, away = game[-3:], game[-6:-3]
    teams = [home, away]
    # get players on those teams
    active = [p for p in pstats.keys() if pstats[p].team() in teams]
    # initialize new game for those players
    for p in active:
        pstats[p]._newgame(game)
    # parse game
    data = pbp[gamedict[game][0]:gamedict[game][1]]
    pstats, score = PPBP.processgame(data, pstats, teams, active)

    # get players from game that actually played
    played_game = [p for p in active if pstats[p].playedgame()]
                   
    # get total game stats from players involved
    gstats[game] = NBAP.game(game, pstats, score, players)
    update(game, pstats, active, score)
                       
    # flush game stats for players involved
    for p in active:
        pstats[p]._flushgame()
        

# write out data parsed from pbp
print("writing out game stats...")
gamestats = getgames(gstats)
WRT.write_out_games(gamestats, pbpfname)


# write out data for each player
print('writing out player stats...')
playerstats = [pstats[p].getgames() for p in pstats.keys()]
playerfeeds = [pstats[p].actionfeed for p in pstats.keys()]
rgtorder = WRT.getrgtorder(playerstats)
WRT.write_out_pstats(playerstats, rgtorder, pbpfname)
WRT.write_out_pfeeds(playerfeeds, rgtorder, pbpfname)

print 'Done'
