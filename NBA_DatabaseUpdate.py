import sys, os
import MYSQLdb as ms
from connect import handcon
import NBA_loadandsplit as LAS

'''
The new "runparse" file, esentially...
Grab the connection to the correct database first; if this fails,
there is really no reason to parse files or anything like that;
'''

def getargs():
    '''Grab terminal args when calling to run'''
    args = sys.argv[1:]
    if len(args) < 1:
        raise ValueError, 'no play-by-play file provided'
    elif len(args) < 2:
        pbpFile = args[0]
        print 'Warning:  no password provided'
        password = ''
    elif len(args) < 3:
        filetype = 'single'
    else:
        pbpFile     = args[0]
        password    = args[1]
        filetype    = args[2]
    return pbpFile, password, filetype

def makecon(p):
    '''Attempt to establish connection to the NBAStats DB on server'''
    conn = connect.handcon(db   = 'NBAStats',
                           h    = 'localhost',
                           u    = 'sinn',
                           p    = password)
    return conn

def filecheck(pbpfile, filetype):
    '''Check type of pbp file; is it a text w/ multi-files, or just one?'''
    if filetype=='single':
        PBPFiles = [pbpFile]
    else:
        with open(pbpFile, 'r') as f1:
            pbpFiles = f1.read()
            pbpFiles = pbpFiles.split('\n')
    return pbpFiles

def getlastID(conn, table):
    '''Gets the last index value from the given table; stick w/ Dummy'''
    cursor = conn.cursor()
    statement = "SELECT Dummy FROM " + table +  "ORDER BY Dummy DESC LIMIT 1"
    cursor.execute(statement)
    last_val = cursor.fetchall()[0][0]
    cursor.close()
    return last_val

def runparse(PBPFiles, conn):
    '''
    This will probably iterate over several pbp files, but could just
    be one; for now, just deal with the basic stuff (as-provided play-by-
    play files, NOT new-fangled player action data, global player IDs,
    player game IDs, etc.);
    '''
    for PBP in PBPFiles:

        # Step 1: Parse file (for now, just basic parse...)
        '''
        Load and close;
        Use parse play-by-play;
        etc;
        '''
        gstats, pstats = parsegamefile(args_in)


        # commit all of pbp to table
        # load play-by-play and find game indicies; pbp is
        # ['gameID','linenum','times','actions']
        gamedict, pbp = LAS.getpbp(fhandlepbp, 'all')
        cursor = conn.cursor()
        for entry in pbp:
            cursor.execute('''
                           INSERT INTO GamePBP (GameID,
                                                LineNum,
                                                TimeRemaining,
                                                Entry)
                           VALUES(%s,%s,%s,%s,%s)
                           ''', entry)
        cursor.close()

        
        # Step 2: Get last line in pbp table:
        last_val = getlastID(conn, "GamePBP")

        # Step 3: Create [(GameID, Start_Value, Stop_Value)] using game_dict
        cursor = conn.cursor()
        last_val += 1
        for game in gamedict.keys():
            cursor.execute('''

                           INSERT INTO GamePBP (GameID,
                                                StartPBPLine,
                                                StopPBPLine)
                           VALUES(%s,%s,%s)
                           ''',(game,
                                last_val+gamedict[game][0]+1,
                                last_val+gamedict[game][1]+1))
        cursor.close()

        # Step 4: Push all game pbp from file to GamePBP table (or append file)
        # if a push: confirm ID agreement in GamePBP table; raise err if non-match

        # Step 5: Push all [(GameID, Start_Value, Stop_Value)] (or append file)

        # Step 6: Clean up (whatever that involves)

