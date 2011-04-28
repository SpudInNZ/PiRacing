import cachingDAL
import logging
import iRacingDAL
import MemoryCache
import iRacingUtils
import getopt, sys, os
import pickle
import threading

class WeekThread(threading.Thread):
    def __init__(self, folder, season, week, verbose):
        self.folder = folder
        self.season = season
        self.week = week
        self.verbose = verbose
        threading.Thread.__init__(self)
    
    def run(self):
        getRaces(self.folder, self.season, self.week, self.verbose)

def readRaces(folder, season, week, verbose):
    fileName = "%s/Season %d Week %d.txt" % (folder, season, week)
    if not os.path.exists(fileName):
        print "%s not found" % fileName
        exit(1)
    
    cache = MemoryCache.MemoryCache()        
        
    logging.config.fileConfig(iRacingUtils.getConfigFileName())
    if not verbose: logging.getLogger().setLevel(logging.ERROR)
    
    with open(fileName,"r") as file:
        logging.getLogger().info("Loading cached data from %s" % fileName)
        try:
            cache.races = pickle.load(file)
            logging.getLogger().info("Cached data loaded successfully")
        except BaseException as e:
            logging.getLogger().error("Error loading data from cache: %s" % e)

    logging.getLogger().info("Read %d races from file" % len(cache.races))
    
def getRaces(folder, season, week, verbose):

    fileName = "%s/Season %d Week %d.txt" % (folder, season, week)
    if os.path.exists(fileName):
        print "%s already exists, exiting" % fileName
        exit(1)
        
    logging.config.fileConfig(iRacingUtils.getConfigFileName())
    
    username, password = iRacingUtils.getAccountDetails()
    primaryDAL = iRacingDAL.iRacingDAL(username, password)
    
    cache = MemoryCache.MemoryCache()
    dal = cachingDAL.cachingDAL(primaryDAL, cache)
    
    if not verbose: logging.getLogger().setLevel(logging.ERROR)
    races = dal.getSeasonRaces(season, week)
    logging.getLogger().info("Processing %d races for season %d week %d" % (len(races), season, week))
    i = 0
    for race in races:
        i += 1
        logging.getLogger().info("(%d,%d) race %d of %d" % (season, week, i, len(races)) )
        if race.isofficial:
            race.setResults(dal.getRaceResults(race.subsessionid))
            for result in race.getResults().itervalues():
                if result.laps == None:
                    result.setLaps(dal.getLaps(race.subsessionid, result.custid))
   
    if len(cache.races) == 0:
        logging.getLogger().info("No races were downloaded. No file written.")
        exit(0)
        
    iRacingUtils.writeCacheToPickle(cache, fileName)
    
    
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "s:w:f:v")
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    output = None
    verbose = False
    folder = "racecache"
    week = -1
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-s", "--season"):
            season = int(a)
        elif o in ("-w", "--week"):
            week = int(a)
        elif o in ("-f", "--folder"):
            folder = a
        else:
            assert False, "unhandled option"

    if not os.path.exists(folder):
        print "Sorry, folder '%s' does not exist" % folder
        exit(1)
    if not os.path.isdir(folder):
        print "Sorry, '%s' is not a folder, is it a file?" % folder
        exit(1)
    if week != -1:
        getRaces(folder, season, week, verbose)
    else:
        threads = []
        for week in xrange(12):
            t = WeekThread(folder, season, week, verbose)
            t.start()
            threads.append(t)
        for thread in threads:
            thread.join()
        
def usage():
    print "downloadweek -s season [-w week] [-f foldername] [-v]erbose"

if __name__ == "__main__":
    main()                    