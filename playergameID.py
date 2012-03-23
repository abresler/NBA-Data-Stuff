# Get last player game id used, MySQL call
last_val = getlastID(conn, "PlayerGame")

for game in gamelist:
    starters = game.starters
    players_seen = list()
    # get list of starting players and assign next 10 ints
    for p in starters:
        players_seen.append(p)
        k = player_list.index(p)
        player_list[k].playergameIDs[game] = last_val+1
        last_val += 1
    # as players are subed in, assign them the next available ints
    if new_player not in players_seen:
        players_seen.append(new_player)
        k = player_list.index(new_player)
        player_list[k].playergameIDs[game] = last_val+1
        last_val += 1    
