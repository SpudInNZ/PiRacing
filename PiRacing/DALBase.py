class DALBase:
    """
    Provides the interface that a DAL should implement.
    """
    def getRaceResults(self, subsessionid):
        """
        Returns a list of RaceResult objects for the specified race session
        """
        raise NotImplementedError()
    
    def getLaps(self, subsessionid, custid):
        """
        Returns a list of Lap objects for the specified race session and customer
        """
        raise NotImplementedError()
        
    def getSeasonRaces(self, season, week = 0):
        """
        Returns a list of Race objects for the specified season and week
        """
        raise NotImplementedError()
        
    def searchForDrivers(self, driverName):
        """
        Returns a list of Driver objects.
        
        A DAL may return only a single Driver object if there is an exact match against driverName. It may also return a 
        zero length list if there is not an exact match.
        
        """
        raise NotImplementedError()
        
    def getSeasonStandings(self, season):
        """
        Returns a list of Drivers who have driven during the specified season
        """
        raise NotImplementedError()
        
    def getPersonalBests(self, carid, custid):
        """
        Returns a list of personal bests for the specified car and driver
        """
        raise NotImplementedError()
        
    
        