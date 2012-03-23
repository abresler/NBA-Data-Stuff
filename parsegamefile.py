import os, sys
import NBA_loadandsplit as LAS
import NBA_parseplaybyplay as PPBP
import NBA_playerclass as NBAP

'''
Assume that each play-by-play file has an associated "players" file that
provides the list of active players and their ESPN IDs, and an associated
player-stats file with data for each game that allows starters to be
assessed;
'''
datadirectory   = os.path.join(chdir,'DataFiles')
playbyplayfile  = os.path.join(datadirectory, playbyplayname)
playerstotfile  = os.path.join(datadirectory, playerstotname)
playesstatfile  = os.path.join(datadirectory, playesstatname)

gstats          = list()
pstats          = LAS.createplayers(playerstotfile)
gamedict, pbp   = LAS.getpbp(playbyplayfile, ['times', 'actions'])

print('parsing play-by-play data...')
for game in gamedict.keys():
    print('on game', game)
    teams       = [game[-3:], game[-6:-3]]      # [home, away]
    curplayers  = [p for p in pstats.keys() if pstats[p].team() in teams]
    curgame     = pbp[gamedict[game][0]:gamedict[game][1]]
    for p in curplayers: pstats[p]._newgame(game)
    pstats, score   = PPBP.processgame(curgame, pstats, teams, curplayers)
    played_game     = [p for p in curplayers if pstats[p].playedgame()]
    for p in active: pstats[p]._flushgame()

return gstats, pstats
print('Done with current file')
