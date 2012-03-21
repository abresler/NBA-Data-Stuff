import os, sys
import NBA_parseplaybyplay as NBA1
import NBA_playerclass as NBAP
import NBA_loadandsplit as LAS

print('checking files and loading game files...')
chdir = os.getcwd()
fhandlepbp = os.path.join(chdir,'DataFiles', "playbyplay20072008reg20081211.txt")
fhandlenam = os.path.join(chdir,'DataFiles', "players20072008reg20081211.txt")
##fhandlepbp = os.path.join(chdir, "playbyplay2008playoffs20081211.txt")
##fhandlenam = os.path.join(chdir, "players2008playoffs20081211.txt")
# initialize players dictionary, game dictionary
pstats = LAS.createplayers(fhandlenam)
gstats = LAS.creategames(fhandlepbp, fhandlenam)
# load play-by-play and find game indicies; pbp is times and actions
gamedict, pbp = LAS.getpbp(fhandlepbp, ['times', 'actions'])
# iterate over games and parse play-by-play
print('parsing play-by-play data...')
for game in gamedict.keys():
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
    pstats, score = NBA1.processgame(data, pstats, teams, active)
    # get total game stats from players involved
    gstats.update(game, pstats, active, score)
    # flush game stats for player involved
    for p in active:
        pstats[p]._flushgame()
        
# write out data parsed from pbp
print("writing out game stats...")
gamestats = gstats.getgames()

with open(os.path.join(chdir ,'DataFiles', gstats._pbpfile + \
                       "GameStats.txt"), 'w') as f1:
    for game in gamestats.keys():
        if game != 'statlist':
            home, away = gamestats[game]['home'], gamestats[game]['away']
            f1.write(game + '\tFinal:\t' + \
                     home + ' ' + str(gamestats[game][home]) + '\t' +\
                     away + ' ' + str(gamestats[game][away]) + '\t' +\
                     '\n\n')
            # header for stats
            f1.write('Names\tID\tTeam\t' + \
                     '\t'.join(gamestats['statlist']) + '\n')
            # iterate over home team
            for p in gamestats[game][home+'Team']:
                f1.write(\
                gamestats[game][p]['Name']  + '\t' + \
                gamestats[game][p]['ID']    + '\t' + \
                gamestats[game][p]['Team']  + '\t' + \
                '\t'.join(str(gamestats[game][p][stat]) \
                            for stat in gamestats['statlist']) + '\n')
            f1.write('\n')
            # iterate over away team
            for p in gamestats[game][away+'Team']:
                f1.write(\
                gamestats[game][p]['Name']  + '\t' + \
                gamestats[game][p]['ID']    + '\t' + \
                gamestats[game][p]['Team']  + '\t' + \
                '\t'.join(str(gamestats[game][p][stat]) \
                            for stat in gamestats['statlist']) + '\n')
            f1.write('\n\n')

# write out data for each player
print('writing out player stats...')
playerstats = [pstats[p].getgames() for p in pstats.keys()]
idlist = [int(p['ID']) for p in playerstats]
rgtorder = []
for k in range(min(idlist), max(idlist)+1):
    try:
        rgtorder.append(idlist.index(k))
    except ValueError:
        pass

with open(os.path.join(chdir, 'DataFiles', gstats._pbpfile + \
                       "PlayerStats.txt"), 'w') as f1:
    f1.write('Name' + '\t' + 'ID' + '\t' + 'Team' + '\n')
    for ID in rgtorder:
        p = playerstats[ID]
        f1.write(p['Name'] + '\t' + p['ID'] + '\t' + p['Team'] + '\n\n')
        f1.write('GameID\t' + '\t'.join(p['statlist']) + '\n')
        for game in p['games']:
            f1.write(str(game) + '\t' + \
                     '\t'.join(str(p[game][stat]) \
                            for stat in p['statlist']) + '\n')
        f1.write('\n\n')

playerfeeds = [pstats[p].actionfeed for p in pstats.keys()]
with open(os.path.join(chdir ,'DataFiles', gstats._pbpfile + \
                       "PlayerFeedStats.txt"), 'w') as f1:
    for ID in rgtorder:
        p = playerfeeds[ID]
        f1.write(str(ID) + '\n')
        for line in p:
            f1.write('\t'.join(line) + '\n')
        f1.write('\n\n')
        
            
print 'Done'
