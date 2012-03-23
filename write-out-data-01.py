

def write_out_games(gamestats, outname):
    '''Writes out game stats file for "runparse"'''
    with open(os.path.join(chdir ,'DataFiles', outname + \
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

def write_out_pstats(playerstats, rgtorder, outname):
    '''Writes out player stats file for "runparse"'''
    with open(os.path.join(chdir, 'DataFiles', outname + \
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

def write_out_pfeeds(playerfeeds, rgtorder, outname):
    '''Writes out player feed file for "runparse"'''
    with open(os.path.join(chdir ,'DataFiles', outname + \
                           "PlayerFeedStats.txt"), 'w') as f1:
        for ID in rgtorder:
            p = playerfeeds[ID]
            f1.write(str(ID) + '\n')
            for line in p:
                f1.write('\t'.join(line) + '\n')
            f1.write('\n\n')

def getrgtorder(playerstats):
    '''Renumbers player IDs to remove gaps between IDs'''
    idlist = [int(p['ID']) for p in playerstats]
    rgtorder = []
    for k in range(min(idlist), max(idlist)+1):
        try:
            rgtorder.append(idlist.index(k))
        except ValueError:
            pass
    return rgtorder

        
            
