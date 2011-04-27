# -*- coding: ISO-8859-1 -*-
import unittest
import logging
import logging.config
import datetime

import MemoryCache
import domainmodel as dm
import iRacingUtils

class MemoryCacheDAL_Test(unittest.TestCase):

    logging.config.fileConfig(iRacingUtils.getConfigFileName())
    custid = 1000
    subsessionid = 99

    def testGetNoLaps(self):
        dal = MemoryCache.MemoryCache()
        laps = dal.getLaps(self.subsessionid, self.custid)
        self.assertIsNotNone(laps)
        self.assertEquals(len(laps), 0)
        
    def testSingleSetLaps(self):
        dal = MemoryCache.MemoryCache()

        laps = []
        laps.append(dm.Lap(0, datetime.timedelta(seconds = 1),0))
        laps.append(dm.Lap(1, datetime.timedelta(seconds = 2),0))
        laps.append(dm.Lap(2, datetime.timedelta(seconds = 3),0))
        dal.setLaps(self.subsessionid, self.custid, laps)
        
        comp = dal.getLaps(self.subsessionid, self.custid)
        self.assertEqual(laps, comp)
        
    def testMultipleSetLaps(self):        

        dal = MemoryCache.MemoryCache()

        laps = []
        laps.append(dm.Lap(0, datetime.timedelta(seconds = 1),0))
        laps.append(dm.Lap(1, datetime.timedelta(seconds = 2),0))
        laps.append(dm.Lap(2, datetime.timedelta(seconds = 3),0))
        
        for i in range(5):
            dal.setLaps(self.subsessionid+i, self.custid+i, laps)
            comp = dal.getLaps(self.subsessionid+i, self.custid+i)
            self.assertEqual(comp, laps)
        
    def testSetSeasonRaces(self):
        races = []
        races.append(dm.Race(0,1, 20000, True))
        races.append(dm.Race(0,2, 20001, True))
        races.append(dm.Race(0,3, 20002, True))
        
        dal = MemoryCache.MemoryCache()
        dal.setSeasonRaces(season = 430, week = 1, races=races)
        
        comp = dal.getSeasonRaces(season=430, week=1)
        self.assertIsNotNone(comp)
        self.assertEquals(len(comp), len(races))
        self.assertEqual(comp, races)
        for i in range(0, len(races)):
            self.assertEqual(comp[i], races[i])
        
    def testSetMultipleSeasonRaces(self):        
        dal = MemoryCache.MemoryCache()        
        races = []
        races.append(dm.Race(0,1, 20001, True))
        races.append(dm.Race(0,2, 20002, True))
        races.append(dm.Race(0,3, 20003, True))
        dal.setSeasonRaces(season = 430, week = 1, races=races)

        races1 = []
        races1.append(dm.Race(0,4, 20004, True))
        races1.append(dm.Race(0,5, 20005, True))
        races1.append(dm.Race(0,6, 20006, True))
        dal.setSeasonRaces(season = 431, week = 2, races=races1)
        
        comp = dal.getSeasonRaces(season=431, week=2)
        self.assertIsNotNone(comp)
        self.assertEquals(len(comp), len(races1))
        self.assertEqual(comp, races1)
        for i in range(0, len(races1)):
            self.assertEqual(comp[i], races1[i])

    def testSetMoreSeasonRaces(self):
        """ Make sure that adding races for a week does not replace any existing races for that week """        
        
        dal = MemoryCache.MemoryCache()        
        races = []
        races.append(dm.Race(0,1, 20001, True))
        races.append(dm.Race(0,2, 20002, True))
        races.append(dm.Race(0,3, 20003, True))
        dal.setSeasonRaces(season = 430, week = 1, races=races)
        
        races = []
        races.append(dm.Race(0,4, 20004, True))
        races.append(dm.Race(0,5, 20005, True))
        races.append(dm.Race(0,6, 20006, True))
        dal.setSeasonRaces(season = 430, week = 1, races=races)
        
        comp = dal.getSeasonRaces(430, 1)
        self.assertEquals(len(comp), 6)
        
        