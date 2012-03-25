import sys, os, re
import urllib2
from BeautifulSoup import BeautifulSoup as BS


def getESPNpbp(data_in, mode='url'):
    '''url is a play-by-play url obtained from score-summary ESPN page'''
    if mode=='url':
        try:
            raw_pbp = urllib2.urlopen(data_in).read()
        except:
            raise ValueError, 'Something bad happened with the url...'
    elif mode=='page':
        raw_pbp     = data_in
    '''The BS way...'''
    soup_pbp        = BS(raw_pbp)       # want to keep this for later, maybe
    tables          = page_soup.findAll('table')
    pbp             = [t for t in tables if t.text.find('TIME')]
    if pbp:
        pbp         = pbp[0].findall('tr')
    else:
        raise AttributeError, "Houston, there is a fucking problem"
    '''Use BS to get the headers (e.g., home and away team for game)'''
    null_value      = '&nbsp;'
    header          = [str(h.text) for h in pbp[1].findAll('th')] # time, away, score, home
    content         = []
    for line in pbp[2:]:
        temp        = line.findAll('td')
        content.append([str(e.text) for e in temp])
    return header, content

def getESPNbox(data_in, mode='url'):
    '''url is a box score url obtained from score-summary ESPN page'''
     if mode=='url':
        try:
            raw_box = urllib2.urlopen(data_in).read()
        except:
            raise ValueError, 'Something bad happened with the url...'
    elif mode=='page':
        raw_box     = data_in
    '''The BS way...'''
    soup_box        = BS(raw_box)
    tables          = soup_box.findAll('table')
    summary         = [t for t in tables if t.text.find('STARTERS') > -1]
    if summary:
        summary     = summary[0].findAll('tr')
    else:
        raise AttributeError, "Houston, there is a fucking problem"
    details         = []
    content         = []
    for line in summary:
        '''
        "details" are headers, trams stuff;
        "content" is actual player data
        Gets Teams, Headers, splits; fields should be:
        Should be:
        ['STARTERS', 'MIN', 'FGM-A', '3PM-A', 'FTM-A', 'OREB',
        'DREB', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PF', '+/-', 'PTS']
        '''
        details.append([str(h.text) for h in line.findAll('th')])
        content.append([str(h.text) for h in line.findAll('td')])
    return details, content
    
