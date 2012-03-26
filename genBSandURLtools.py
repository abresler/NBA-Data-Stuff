'''
General set of tools for grabbing web pages and extracting relevant info
from them; as of now, 'geared' towards use with ESPN parsing stuff; hope-
fully will expand to other ventures in the near future;
'''
import urllib2
from BeautifulSoup import BeautifulSoup as BS

def getRawPage(url):
    '''Attempts grab of raw page from url'''
    try:
        raw     = urllib2.urlopen(url).read()
    except urllib2.URLError:
        print 'Failed to fetch ' + url
    return raw

def getDataType(data_in, data_type, mode):
    '''
    Either retreives data from provided url, or sets data to raw
    page handed in, depending on mode; BS's data_type, and returns;
    '''
    if mode=='url':
        raw = getRawPage(data_in)
    elif mode=='page':
        raw         = data_in    
    soup_box        = BS(raw)
    data_out        = soup_box.findAll(data_type)
    return data_out
