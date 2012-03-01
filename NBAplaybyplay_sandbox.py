gameID = '20080428BOSATL'
home = gameID[-3:]
away = gameID[-6:-3]

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

def getstripactions(actions):
    keep = []
    for action in actions:
        sa = re.split(r'(\[|\])', action)[-1].split()
        index = 1
        if sa[0].endswith('.'):
            index = 2
        keep.append(sa[index:])
    return keep

def _getactions(data):
    actions = [line[3] for line in data if line not in [[''], '']]
    actions = [re.split(r'(:|\(|\))', e) for e in actions]
    actions = [' '.join(e).split() for e in actions]
    return actions


sub = playbyplay[gameIDdict[gameID][0]:gameIDdict[gameID][1]]
for i, e in enumerate(sub):
    temp = e[3]
    temp = re.split(r'(\[|\])', temp)
    if len(temp)>1:
        '''Reg game play stuff'''
        team = temp[2].split()
        action = parseaction(temp[-1], team)


'''Reformat actions, get various info about phrase ordering'''
actions = _getactions(playbyplay)
fd = nltk.FreqDist(word.lower() for line in actions for word in line)
adfd = nltk.FreqDist((w1.lower(), w2.lower()) for line in actions \
                     for (w1,w2) in nltk.bigrams(line))
'''Dictionary of terms that follow other terms'''
followme = nltk.defaultdict(set)
for line in actions:
    for i,word in enumerate(line[:-1]):
	followme[word.lower()].add(line[i+1].lower())      

'''Similar to a cfd, but looks for co-occurances of phrases
in the same line; don't need to be adjacent'''w
counts['t'] = 0
counts['('] = 0
counts['m'] = 0
counts['c'] = 0
for line in actions:
	try:
		start = line.index('Shot')
		counts['t'] += 1
		try:
			loc = line.index("(", start)
			counts['('] += 1
		except ValueError:
			if re.search(r'(M|m)issed', ' '.join(line[start:])):
				counts['m'] += 1
			elif re.search(r'Clock', ' '.join(line[start:])):
				counts['c'] += 1
	except ValueError: pass
