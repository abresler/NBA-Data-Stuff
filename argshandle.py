import sys, os

max_args = 2
def getargs():
    '''
    Grabs args from terminal run; as of now, just a file containing
    the ESPN game ids desired, and maybe an output file name;
    '''
    if len(sys.argv[1:]) > max_args: print('disregarding extra args')
    try:
        gameid_file, output_name = sys.argv[1:3]
        return gameid_file, output_name
    except:
        '''Assume no output file name, try to get game id file'''
        try:
            gameid_file = sys.argv[1]
            return gameid_file,
        except:
            raise ValueError, 'no game id or game id file provided'

if __name__=='__main__':
    """
    Default run from terminal; grab the text file with a list of game
    id's and get the raw pbp and box score pages for each; pickle results
    """
    argstuple = getargs()
    if argstuple:
        num = int(argstuple[0])
        print num
