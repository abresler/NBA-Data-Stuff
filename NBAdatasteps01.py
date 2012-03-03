import os, sys, numpy as np

maindirec = "/Volumes/NO NAME/NBAData/"

def buildIDsdict(data):
    '''
    'minthresh' is the minimum time a player needs to have been involved in
    order to be considered a player of interest; players below this threshold
    are considered comparison players; the 'playermins' list is (playerID, min)
    tuples for each player; players with no mins played are given '-999' IDs;
    though a '999' assignment would not change the analysis, the -999'
    assignment may be useful for post analysis
    '''

    '''
    Reg version, w/ o min players left in
    '''
    IDsdict = {}
    threshmins = data[0].split('\t')
    for i,thresh in enumerate(threshmins[1:]):
        temp = {}
        for e in data[1:]:
            e = e.split('\t')
            temp[int(e[0])] = int(e[i+1])
        IDsdict[int(thresh)] = temp
    '''
    Alt version w/ 0 min players removed
    '''
    ##with open("/Volumes/NO NAME/NBAData/reassignids02.txt", 'r') as f1:
    ##	newIDs = f1.readlines()
    # newIDs = [(e.split('\t')[0], e.split)'\t')[1]) for e in newIDs]
    return IDsdict

def getadjIDsdict(dictIDs):
    IDs = [(key,dictIDs[key]) for key in dictIDs.keys()]
    sortIDsset = list(sorted(set(int(new) for (old,new) in IDs)))
    adjIDsdict = {}
    revadjIDsdict = {}
    for i,v in enumerate(sortIDsset[1:]):
        adjIDsdict[v] = i-1
        revadjIDsdict[i-1] = v
    return adjIDsdict, revadjIDsdict, i-1

def getExceltxtfile(file_hand):
    # load file, split into lines
    with open(file_hand, 'r') as f1:
        data = f1.readlines()
    data = data[0].split('\r')
    return data

def getnewnbadata(nbadata, cols2keep):
    '''
    With info from 1st row of cols2keep, i.e. regression only info,
    create newnbadata variable and switch data to correct types
    (should be all ints, except for game id and time);
    perhaps it would be reasonible to put [gameID, start, stop]
    as separate variable?; row 0 in cols2keep is the names of
    columns; row 1 is the bool to keep for doing the regression; row 2
    is the bool to keep for interesting info; row 3 is the data type
    (s==str, i==int, f==float)
    '''
    newnbadata_head = [nbadata[0][i] for i in range(len(nbadata[0])) \
                       if cols2keep[2][i]=='1']
    newnbadata = []
    ##for line in nbadata:
    ##    temp = [line[i] for i in range(len(line)) if cols2keep[1][i]=='1']
    ##    newnbadata.append(temp)
    for line in nbadata[1:]:
        temp = []
        for i,e in enumerate(line):
            if cols2keep[2][i]=='1':
                if cols2keep[-1][i]=='i':
                    temp.append(int(line[i]))
                elif cols2keep[-1][i]=='f':
                     temp.append(float(line[i]))
                else: temp.append(line[1])
        newnbadata.append(temp)
    return newnbadata, newnbadata_head

    
def createMARGIN(data, data_head):
    '''
    This is the 'b' column for the regression; if one of the teams did not have
    posession in this time period, ignore the time period (need to fix this;
    shitty way of dealing with the issue, but quick and dirty)
    '''
    homepts,awaypts,homepos,awaypos = \
                                    data_head.index('PointsScoredHome'),\
                                    data_head.index('PointsScoredAway'),\
                                    data_head.index('PossessionsHome'), \
                                    data_head.index('PossessionsAway')
    MARGIN = []
    for line in data:
        if line[homepos]==0 or line[awaypos]==0:
            MARGIN.append('NULL')
        else:
            MARGIN.append((float(line[homepts])/line[homepos] \
                         - float(line[awaypts])/line[awaypos])*100)
    return MARGIN

def createA(data, data_head, MARGIN, IDs, adjIDs):
    # making this sparse would be an exceelent idea, eh?
    '''
    What am I doing here?  So, I think 82Games does the grouping of < 250 min
    players post-regression; here, I'm doing it pre-regression.  A comparison
    home and away player are added to each line; if x home comparison
    players are in the game, and y away comparison players are in the game,
    then the last two entries of the row corresponding to that time interval is
    [x, -y].
    '''
    start_P = data_head.index('HomePlayer1ID')
    stop_P = data_head.index('AwayPlayer5ID')
    A = []
    for i,val in enumerate(MARGIN):
        if val != 'NULL':
            line = data[i]
            temp = [0 for i in range(len(adjIDs.keys()))]
            for e in range(start_P,stop_P+1):
                if e-start_P < 5:
                    if IDs[line[e]] == 999:
                        temp[-2] += 1
                    else:
                        temp[adjIDs[IDs[line[e]]]] =  1
                else:
                    if IDs[line[e]] == 999:
                        temp[-1] -= 1
                    else:
                        temp[adjIDs[IDs[line[e]]]] = -1
            # this is for b_0
            temp.append(1)
            A.append(temp)
    A = np.array(A)
    return A

"""
This is the main potion of the code...
"""

# Load the main data file, which has event-by-event info
with open(maindirec + "matchups2007playoffs20081211.txt", 'r') as f1:
    nbadata = f1.readlines()
for i,line in enumerate(nbadata):
    line = line[:-2]
    nbadata[i] = line.split('\t')


# Reassign IDs based on playing time
main_thresh = 100
threshmins = getExceltxtfile(maindirec + "reassignids03.txt")
dictIDs = buildIDsdict(threshmins)
curr_IDdict = dictIDs[main_thresh]
adjIDsdict, revadjIDsdict, last = getadjIDsdict(curr_IDdict)
# add entries for 'away comparison' and 'b_0'
revadjIDsdict[last+1] = -999
revadjIDsdict[last+2] = 'b0'


# Get the list of which cols you want to keep from the main data set
# and which ones you want to ditch; get newnbadata w/ cols removed
cols2keep = getExceltxtfile(maindirec + "cols2keep.txt")
cols2keep = [e.split('\t') for e in cols2keep]
newnbadata, newnbadata_head = getnewnbadata(nbadata, cols2keep)
# get 'b' column, A   
MARGIN = createMARGIN(newnbadata, newnbadata_head)
# shift into np.array version, no null values
uMARGIN = [val for val in MARGIN if val != 'NULL']
uMARGIN = np.array(uMARGIN)
A = createA(newnbadata, newnbadata_head, MARGIN, curr_IDdict, adjIDsdict)

'''
Here's where the "magic" happens; use numpy's least-squares regression
to get the ratings for each player; then normalize s.t. the mean of the
ratings is 0; from numpy docs for numpy.linalg.lstsq(a, b, rcond=-1):
"We can rewrite the line equation as y = Ap, where A = [[x 1]] and
p = [[m], [c]]. Now use lstsq to solve for p:"
'''
p = np.linalg.lstsq(A, uMARGIN)
ratings = p[0] - np.mean(p[0])

# write out ratings
ratings = p[0]
with open(maindirec + "ratingsout01.txt", 'w') as f1:
    for i, val in enumerate(ratings):
        f1.write(str(revadjIDsdict[i]) + '\t' + str(val) + '\n')
        

