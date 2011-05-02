import logging
import DALBase
import domainmodel
import iRacingDAL
import MemoryCache

class cachingDAL(DALBase.DALBase):
    def __init__(self, primaryDAL, cacheDAL):
        
        self.primaryDAL = primaryDAL
        self.cacheDAL = cacheDAL
        
    def getRaceResults(self, subsessionid):
        """
        Returns a list of RaceResult objects for the specified race session
        """
        r = self.cacheDAL.getSessionResults(subsessionid)
        if r is None:
            r = self.primaryDAL.getSessionResults(subsessionid)
            if r is not None:
                self.cacheDAL.setRaceResults(subsessionid, r)
            
        return r
    
    def getLaps(self, subsessionid, custid):
        """
        Returns a list of Lap objects for the specified race session and customer
        """
        r = self.cacheDAL.getLaps(subsessionid, custid)
        if len(r) == 0:
            r = self.primaryDAL.getLaps(subsessionid, custid)
            if len(r) != 0:
                self.cacheDAL.setLaps(subsessionid, custid, r)
        return r

        
    def getSeasonRaces(self, season, week = 0):
        """
        Returns a list of Race objects for the specified season and week
        """
        r = self.cacheDAL.getSeasonRaces(season, week)
        if len(r) == 0:
            r = self.primaryDAL.getSeasonRaces(season, week)
            if len(r) > 0:
                self.cacheDAL.setSeasonRaces(season, week, r)
        return r
                
    def searchForDrivers(self, driverName):
        """
        Returns a list of Driver objects.
        
        A DAL may return only a single Driver object if there is an exact match against driverName. It may also return a 
        zero length list if there is not an exact match.
        
        """
        r = self.cacheDAL.searchForDrivers(driverName)
        if len(r) == 0:
            r = self.primaryDAL.searchForDrivers(driverName)
            if len(r) > 0:
                self.cacheDAL.setDrivers(r)
        return r

        
    def getSeasonStandings(self, season):
        """
        Returns a populated SeasonStanding object
        """
        r = self.cacheDAL.getSeasonStandings(season)
        if r is None:
            r = self.primaryDAL.getSeasonStandings(season)
            if r is not None:
                self.cacheDAL.setSeasonStandings(r)
        return r
    
    def getPersonalBests(self, carid, custid):
        """
        """
        r = self.cacheDAL.getPersonalBests(carid, custid)
        if len(r) == 0:
            r = self.primaryDAL.getPersonalBests(carid, custid)
            if len(r) != 0:
                self.cacheDAL.setPersonalBests(carid, custid, r)
        return r

            
