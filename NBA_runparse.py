import os, sys
import NBA_parseplaybyplay as NBA1
import NBAplaybyplay_sandbox as NBA2
##global teams
##global players
##global stats_array

chdir = os.getcwd()

fhandlepbp = os.path.join(chdir, "playbyplay2008playoffs20081211.txt")
fhandlenam = os.path.join(chdir, "players2008playoffs20081211.txt")
gameID = '20080428BOSATL'
stats = ['mins', 'fg', 'fga', '3pt', '3pta', 'ft', 'fta',
             'pts', 'stl', 'ast', 'blk', 'rbo', 'rbd', 'pf', 'rb', 'to']
home = gameID[-3:]
away = gameID[-6:-3]
teams = [home, away]
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
playbyplay = NBA1.loadfile(fhandlepbp)
gameIDdict = NBA1._getgamelines(playbyplay)
sub = playbyplay[gameIDdict[gameID][0]:gameIDdict[gameID][1]]
actions = NBA1._getactions(sub, playbyplay[0])
stats_array, gamescore = NBA2.processgameactions(actions, playerid,
                                      teams, stats_array,
                                      playerteamdict)

with open(os.path.join(chdir, "outputstats.txt"), 'w') as f1:
    f1.write('names\tteam\t' + '\t'.join(stats) + '\n')
    for i,line in enumerate(stats_array):
        f1.write(playerid.keys()[i] + '\t' + \
                 playerteamdict[playerid.keys()[i]] + '\t' + \
                 '\t'.join(str(e) for e in line) + '\n')
    f1.write('\n')
    f1.write(gamescore.keys()[0] + '\t' + str(gamescore.values()[0]) + '\t' + \
             gamescore.keys()[1] + '\t' + str(gamescore.values()[1]))
print 'Done'
