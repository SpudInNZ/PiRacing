# -*- coding: ISO-8859-1 -*-
import unittest
import iRacingDAL
import logging
import logging.config
import datetime
import iRacingUtils
from domainmodel import RaceResult
from domainmodel import Lap
from domainmodel import Race

class iRacingDAL_Tests(unittest.TestCase):
    
    logging.config.fileConfig(iRacingUtils.getConfigFileName())
    
    dal = iRacingDAL.iRacingDAL(iRacingUtils.getAccountDetails())
        
    seasons = [ (368, "MX-5 Season 4B", 4092, 781), (369, "MX-5 Season 4C", 4253, 908 ), (374, "Skip Barber 2010 S4", 2518, 181) ]
                

    def testGetSeasonRaces(self):
        for season, name, driverCount, raceCount in self.seasons:
            races = self.dal.getSeasonRaces(season, 0)
            self.assertIsNotNone(races)
            self.assertEquals(len(races), raceCount)
            self.assertIsInstance(races[0], Race)
            
    def testGetBadSeasonRaces(self):
        races = self.dal.getSeasonRaces(368, -1)
        self.assertIsNotNone(races)
        self.assertEquals(len(races), 0)
        
    def testGetRaceResult(self):
        rr = self.dal.getRaceResults(2790352) # Mazda mx-5 season 4B 2010-12-05 1.00pm
        # http://members.iracing.com/membersite/member/EventResult.do?&subsessionid=2790352&custid=57702
        self.assertIsNotNone(rr)
        self.assertEquals(len(rr), 12)
        self.assertIsInstance(rr[0],RaceResult)
        
    def testGetBadRaceResult(self):
        # Mazda mx-5 season 4B 2010-12-05 1.00pm
        rr = self.dal.getRaceResults(-1) 
        self.assertIsNotNone(rr)
        self.assertEquals(len(rr), 0)
        
    def testGetLapData(self):
        # http://members.iracing.com/membersite/member/EventResult.do?&subsessionid=2884449&custid=57702
        # 2010 Season 4B
        # 2010-12-27 1:00 pm

        rr = self.dal.getRaceResults(2884449) 
        self.assertIsNotNone(rr)
        self.assertEquals(len(rr), 12)
        
        """
        Finished in 11th place
        
        http://members.iracing.com/membersite/member/eventresult_laps.jsp?&subsessionid=2884449&custid=55267&simsessnum=0
        Jason Workman
        iRacing Mazda Cup - 2010 Season 4B
        2010-12-27 1:00 pm
        Race Session: 14085234/2884449 undefined
        Mazda Raceway Laguna Seca - Full Course
        #	Time	Comments
        0	- -:- -.- - -	
        1	01:48.161	off track
        2	01:57.394	fastest lap
        3	01:44.886	off track
        4	01:57.633	car contact, lost control
        """
        
        raceResult = rr[10]
        self.assertIsInstance(raceResult, RaceResult)
        self.assertEquals(raceResult.custid, 55267)
        laps = self.dal.getLaps(2884449, 55267)
        self.assertIsNotNone(laps)
        self.assertEquals(len(laps), 5, "5 laps should have been returned")
        self.assertIsInstance(laps[0], Lap)
        
        self.assertFalse(laps[0].isGoodLap(), "Lap 0 should not be a good lap")
        self.assertFalse(laps[0].isCleanLap(), "Lap 0 should not be a clean lap")
        
        self.assertTrue(laps[1].isGoodLap(), "Lap 1 should be a good lap")
        self.assertTrue(laps[1].flags & Lap.FLAG_OFF_TRACK)        
        self.assertEquals(laps[1].time, datetime.timedelta(minutes=1, seconds=48, milliseconds=161)) 
        
        self.assertTrue(laps[2].isGoodLap(), "Lap 2 should be a good lap")
        self.assertTrue(laps[2].isCleanLap(), "Lap 2 should be a clean lap")        
        self.assertEquals(laps[2].time, datetime.timedelta(minutes=1, seconds=57, milliseconds=394))         
        
        self.assertTrue(laps[3].isGoodLap())
        self.assertTrue(laps[3].flags & Lap.FLAG_OFF_TRACK)
        self.assertEquals(laps[3].time, datetime.timedelta(minutes=1, seconds=44, milliseconds=886))
        
        self.assertFalse(laps[4].isGoodLap())
        self.assertTrue(laps[4].flags & Lap.FLAG_CAR_CONTACT)
        self.assertTrue(laps[4].flags & Lap.FLAG_LOST_CONTROL)
        self.assertEquals(laps[4].time, datetime.timedelta(minutes=1, seconds=57, milliseconds=633))
        
    def testGoodSeasonStandings(self):
        for season, name, driverCount,raceCount in self.seasons:
            seasonStandings = self.dal.getSeasonStandings(season)
            self.assertIsNotNone(seasonStandings)
            
            self.assertIsNotNone(seasonStandings.standings)
            self.assertEquals(seasonStandings.season, season)
            self.assertEqual(len(seasonStandings.standings), driverCount)  
        
    def testMissingSeasonStandings(self):
        seasonstandings = self.dal.getSeasonStandings(99999)
        self.assertEqual(len(seasonstandings.standings), 0)
        
    def testSearchForDrivers(self):
        drivers = self.dal.searchForDrivers("Ian Bevan")
        self.assertIsNotNone(drivers)
        self.assertEqual(len(drivers), 1)
        self.assertEqual("Ian Bevan", drivers[0].name)
        self.assertEqual(57702, drivers[0].custid)
        self.assertEqual({}, drivers[0].personalbests)
        
    def testSearchForUTFDriverName(self):
        drivers = self.dal.searchForDrivers(u'Jyri Mäntylä')
        self.assertIsNotNone(drivers)
        self.assertEqual(len(drivers), 1)
        self.assertEqual(u'Jyri Mäntylä', drivers[0].name)
        self.assertEqual(28078, drivers[0].custid)
        self.assertEqual({}, drivers[0].personalbests)
        
if __name__ == "__main__":
    
    unittest.main()  
        
        