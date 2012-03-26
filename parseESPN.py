'''
Parsing modules specifically for handling ESPN sports pages (tested only on
NBA data thus far);
'''
import sys, os, re
from BeautifulSoup import BeautifulSoup as BS
import genBSandURLtools

null_value      = '&nbsp;'

def getESPNpbp(data_in, mode='url'):
    '''
    url is a play-by-play url obtained from score-summary ESPN page;
    use BeautifulSoup to parse apart data_in; all relevant data found
    in 'table' HTML structures, hence we grab those;
    '''
    tables          = genBSandURLtools.getDataType(data_in, 'table', mode)
    pbp             = [t for t in tables if t.text.find('TIME') > -1]
    if pbp:
        pbp         = pbp[0].findAll('tr')
    else:
        raise AttributeError, "Houston, there is a fucking problem"
    '''Use BS to get the headers (e.g., home and away team for game)'''
    header          = [str(h.text) for h in pbp[1].findAll('th')] # time, away, score, home
    content         = []
    for line in pbp[2:]:
        temp        = line.findAll('td')
        content.append([str(e.text) for e in temp])
    return {'head':header, 'content':content}

def getESPNbox(data_in, mode='url'):
    '''
    url is a box score url obtained from score-summary ESPN page;
    use BeautifulSoup to parse apart data_in; all relevant data found
    in 'table' HTML structures, hence we grab those;
    '''
    tables          = genBSandURLtools.getDataType(data_in, 'table', mode)
    summary         = [t for t in tables if t.text.find('STARTERS') > -1]
    if summary:
        summary     = summary[0].findAll('tr')
    else:
        raise AttributeError, "Houston, there is a fucking problem"
    details         = []
    content         = []
    for line in summary:
        '''
        "details" are headers, teams stuff;
        "content" is actual player data
        '''
        details.append([str(h.text) for h in line.findAll('th')])
        content.append([str(h.text) for h in line.findAll('td')])
    playerlink_dict = getESPNplayerlinks(summary)
    return {'details':details, 'content':content,
            'playerlinks':playerlink_dict}

def getESPNplayerlinks(summary):
    '''
    Gets the ESPN page urls for players in the game from the box score page;
    keys are the full names of players used in box score, and values are
    the urls;
    '''
    playerlink_dict = dict()
    for line in summary:
	temp = line.findAll('a')
	if temp:
            temp    = temp[0]
            if str(temp.get('href')):
		playerlink_dict[str(temp.text)] = str(temp.get('href'))
    return playerlink_dict
    
