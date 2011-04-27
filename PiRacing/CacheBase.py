class CacheBase:
    """
    Methods that a cache should implement
    """
def setRaceResults(self, subsessionid, raceResult):
    raise NotImplementedError()
    
def setRaces(self, season, week, races):
    raise NotImplementedError()

def setSeasonStandings(self, seasonStandings):
    raise NotImplementedError()
    
def setPersonalBests(self, carid, driver):
    raise NotImplementedError()