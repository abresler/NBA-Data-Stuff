import sys, os

def getargs(argslist=[], minargtup=[]):
    '''
    Grabs args from terminal run; looks for args with names in argslist;
    requires args with names in at least one minargtup, and raises error
    if at least one set of minimal args is not included; returns found
    args as a dictionary; if names provided, looks for "-name" formate;
    if this not found, assumes args are given in order of argslist;
    '''
    given_args  = sys.argv[1:]
    args_out    = dict()
    if given_args[0].startswith('-'):
        '''Args named, denoted w/ "-"'''
        start = 0
        args = []
        while start < len(given_args):
            end = start + find_next(given_args[start+1:])
            args.append(given_args[start:end+1])
            start = end + 1
        '''clean'''
        for arg in args:
            arg[0] = arg[0].strip('-')
            if arg[0] in argslist:
                start = arg.index('=')
                args_out[arg[0]] = ' '.join(arg[start+1:])
            else:
                raise ValueError, 'invalid argument, %s, supplied' % (arg[0])
    else:
        '''non-named args; assume order of arglist'''
        for i,arg in enumerate(args):
            if i < len(argslist):
                args_out[arglist[i]] = arg
            else:
                print "Ignoring extra arg %s" % (arg)
    return args_out

def find_next(args):
    if not args:
        return 0
    elif args[0].startswith('-'):
        return 0
    else:
        return 1 + find_next(args[1:])
    

if __name__=='__main__':
    """
    Default run from terminal; grab the text file with a list of game
    id's and get the raw pbp and box score pages for each; pickle results
    """
    argstuple = getargs()
    if argstuple:
        num = int(argstuple[0])
        print num
