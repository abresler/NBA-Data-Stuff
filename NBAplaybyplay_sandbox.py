##self._mins  = 0.0
##        self._fg    = 0
##        self._fga   = 0
##        self._3p    = 0
##        self._3pa   = 0
##        self._ft    = 0
##        self._fta   = 0
##        self._stl   = 0
##        self._ast   = 0
##        self._blk   = 0
##        self._blkd  = 0
##        self._rbo   = 0
##        self._rbd   = 0
##        self._pf    = 0
##        self._pft   = 0


def parseaction(action, team):
    index = 0
    split_action = action.split()
    name1 = split_action[index]
    index += 1
    if name1.endswith('.'):
        name1 = name1 + ' ' + split_action[index]
        index += 1
    action1 = split_action[index]
    index += 1

def getactionsdict(actions):
    for action in actions:
        sa = re.split(r'(\[|\])', action)[-1].split()
        index = 1
        if sa[0].endswith('.'):
            index = 2
        sa = nltk.bigrams(sa[index:])
        for gram in sa:
            actiondict[gram] += 1
    return actiondict

sub = playbyplay[gameIDdict[gameID][0]:gameIDdict[gameID][1]]
for i, e in enumerate(sub):
    temp = e[3]
    temp = re.split(r'(\[|\])', temp)
    if len(temp)>1:
        '''Reg game play stuff'''
        team = re.split(r'( |:|\(|\))', temp[2]
        action = parseaction(temp[-1], team)

