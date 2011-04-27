import CacheBase
import DALBase

class MemoryCache(DALBase.DALBase, CacheBase.CacheBase):
    """
    Cache that uses in-memory lists and dictionaries.
    """

    def __init__(self):
        
        self.raceResults = {} # subsessionid, list(raceresult)
        self.races = {} # season, { week, { subsessionid, Race } } 
        self.driversByName = {} #name, driver
        self.driversByCustid = {} #custid, driver
        self.seasonStandings = {} # season, SeasonStandings
        self.personalBests = {} # (custid, driverid),list(Laptime)
        self.laps = {} # (subsessionid, cusid), list(Lap)
        
    def mergeWith(self, otherCache):
        assert(isinstance(otherCache, MemoryCache))
        self.raceResults = dict(self.raceResults.items() + otherCache.raceResults.items())
        self.driversByName = dict(self.driversByName.items() + otherCache.driversByName.items())
        self.driversByCustid = dict(self.driversByCustid.items() + otherCache.driversByCustid.items())
        self.seasonStandings = dict(self.seasonStandings.items() + otherCache.seasonStandings.items())
        self.personalBests = dict(self.personalBests.items() + otherCache.personalBests.items())
        self.laps = dict(self.laps.items() + otherCache.laps.items())
        for seasonkey in otherCache.races:
            if not self.races.has_key(seasonkey):
                self.races[seasonkey] = otherCache.races[seasonkey]
            else:
                for weekkey in otherCache.races[seasonkey]:
                    if not self.races[seasonkey].has_key(weekkey):
                        d = self.races[seasonkey]
                        d[weekkey] = otherCache.races[seasonkey].get(weekkey)
                    else:
                        myracesdict = self.races[seasonkey].get(weekkey)
                        assert(isinstance(myracesdict, dict))
                        otherracesdict = otherCache.races[seasonkey].get(weekkey)
                        for race in otherracesdict.values():
                            myracesdict[race.subsessionid] = race
                            
                            
                    
        
    def getRaceResults(self, subsessionid):
        """
        Returns a list of RaceResult objects for the specified race session
        """
        return self.raceResults.get(subsessionid, None)
    
    def setRaceResults(self, subsessionid, raceResult):
        self.raceResults[subsessionid] = raceResult

    def getSeasonRaces(self, season, week = 0):
        """
        Returns a list of Race objects for the specified season and week
        """
        weekDict = self.races.get(season, None)
        if weekDict is None:
            return []

        raceDict = weekDict.get(week, {} )        
        
        races = []
        [races.append(race) for race in raceDict.itervalues()]
        return races
    
    def setSeasonRaces(self, season, week, races):
        
        # Append the races to any races we already have the for specified week and season
        
        # Get the races for the specified season/week
        weekDict = self.races.get(season, {})
        
        raceDict = weekDict.get(week, {} )
        for race in races:
            raceDict[race.subsessionid] = race
        
        weekDict[week] = raceDict
        self.races[season] = weekDict        
        
    def searchForDrivers(self, name=None, custid=None):
        """
        Returns a list of Driver objects.
        
        A DAL may return only a single Driver object if there is an exact match against driverName. It may also return a 
        zero length list if there is not an exact match.
        
        """
        
        if name is not None:
            # iracing puts + signs instead of spaces for some reason
            driver = self.driversByName.get(name, None)
        else:
            driver = self.driversByCustid.get(custid, None)
        
        matches = list()
        if driver is not None: matches.append(driver)
        return matches

    def getLaps(self, subsessionid, custid):
        """
        Returns a list of Lap objects for the specified race session and customer
        """
        
        return self.laps.get( (subsessionid, custid), list())
    
    def setLaps(self, subsessionid, custid, laps):
        assert(isinstance(laps, list().__class__))
        self.laps[ (subsessionid, custid) ] = laps

    def getSeasonStandings(self, season):
        return self.seasonStandings.get(season, None)
    
    def setSeasonStandings(self, standings):
        self.seasonStandings[standings.season] = standings
        
    def setDrivers(self, drivers, season = None):
        if season is not None: self.driversBySeason[season] = drivers
        
        for driver in drivers:
            if driver.custid is not None:
                self.driversByCustid[driver.custid] = driver
            if driver.name is not None:
                self.driversByName[driver.name] = driver

    def getPersonalBests(self, carid, custid):
        return self.personalBests.get( (carid, custid), list())
    
    def setPersonalBests(self, carid, custid, laptimes):
        self.personalBests[ (carid, custid) ] = laptimes
