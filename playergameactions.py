# Get last player action ID from, SQL table
cursor = conn.cursor()
cursor.execute("SELECT Dummy FROM PlayerActions ORDER BY Dummy DESC LIMIT 1")
last_val = cursor.fetchall()[0][0]
cursor.close()

for game in gstats.games:
    g_start = last_val+1
    for playerID in game.players:
        try:
            temp = players[playerID].actionfeed[game]
            # for current player, set (action_start, action_stop)
            start   = last_val+1
            stop    = last_val+len(temp)
            players[playerID].actiondict[game] = (start,stop)
            last_val += len(temp)

        except KeyError:
            '''Do something here to handle the error, yo'''

    # for current game, set (action_start, action_stop)
    gstats[game].getactdict = (g_start, stop)
