import logging
import logging.config
import MemoryCache
import iRacingUtils

logging.config.fileConfig(iRacingUtils.getConfigFileName())

cache = iRacingUtils.loadCacheFromPickle()

if cache is None:
    logging.getLogger().info("Cached data not available, exiting")
    exit(1)

totalraces = 0
totalcounted = 0

for week in range(0,10):
    unofficial = 0
    noresults = 0
    nolaps = 0

    races = cache.getSeasonRaces(420, week)  
    totalraces += len(races)    
    for race in races:
        if not race.isofficial:
            unofficial += 1
            continue
        
        results = race.getResults()    
        
        if results  == None:
            noresults += 1
            continue
        
        laps = results.laps
        if laps == None:
            nolaps += 1
            continue
    racescountedthisweek = len(races)-unofficial-noresults-nolaps
    totalcounted += racescountedthisweek
    logging.getLogger().info("Week %d: Races:%d Counted:%d (Unofficial:%d NoResults:%d NoLaps:%d)" % (week, len(races), racescountedthisweek , unofficial,noresults, nolaps ))   
                
