import sys
import MYSQLdb as ms
from connect import handcon

'''
Grab the connection to the correct database first; if this fails,
there is really no reason to parse files or anything like that;
'''

args = sys.argv[1:]
if len(args) < 1:
    raise ValueError, 'no play-by-play file provided'
elif len(args) < 2:
    pbpFile = args[0]
    print 'Warning:  no password provided'
    password = ''
else:
    pbpFile     = args[0]
    password    = sys.argv[1]

'''Attempt to establish connection to the NBAStats DB on server'''
conn = connect.handcon(db   ='NBAStats',
                       h    ='localhost',
                       u    ='sinn',
                       p    =password)

'''Check type of pbp file; is it a text w/ multi-files, or just one?'''

'''
This will probably iterate over several pbp files, but could just
be one; for now, just deal with the basic stuff (as-provided play-by-
play files, NOT new-fangled player action data, global player IDs,
player game IDs, etc.);
'''
last_val = int()
for PBP in PBPFiles:

    # Step 1: Parse file (for now, just basic parse...)
    '''
    Load and close;
    Use parse play-by-play;
    etc;
    '''

    # Step 2: Get last line in pbp table:
    if not last_val:
        cursor = conn.cursor()
        cursor.execute("SELECT Dummy FROM GamePBP ORDER BY Dummy DESC LIMIT 1")
        last_val = cursor.fetchall()[0][0]
        cursor.close()

    # Step 3: Create [(GameID, Start_Value, Stop_Value)]

    # Step 4: Push all game pbp from file to GamePBP table (or append file)
    # if a push: confirm ID agreement in GamePBP table; raise err if non-match

    # Step 4b: Update last_val
    last_val += num_new_entries

    # Step 5: Push all [(GameID, Start_Value, Stop_Value)] (or append file)

    # Step 6: Clean up (whatever that involves)

