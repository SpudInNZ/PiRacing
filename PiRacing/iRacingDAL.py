import urllib2
import urllib
import cookielib
import json
import domainmodel
import StringIO
import csv
import DALBase
import datetime
import iRacingUtils

import logging
import logging.config

from domainmodel import Driver
from domainmodel import Race
from domainmodel import RaceResult
from domainmodel import SeasonStanding
from domainmodel import SeasonStandings
from domainmodel import Laptime
from domainmodel import Lap

class iRacingDAL(DALBase.DALBase):
    
    def __init__(self, username, password):
        self.__isLoggedIn = False
        self.__cookieJar = None
        self.__opener = None
        self.__username = username
        self.__password = password
        self.__logger = logging.getLogger()
        
    def __login(self):
        if not self.__isLoggedIn:
            self.__initConnection()
            params = urllib.urlencode({"username":self.__username,"password":self.__password})
            params = params.encode('utf-8')
            self.__logger.info("Logging in")            
            response = self.__opener.open("https://members.iracing.com/membersite/Login", params)
            if response.getcode() != 200:
                self.__logger.critical("Error logging in " + remotefile.getcode())
                exit

            url = response.geturl()
            if url.endswith("failedlogin.jsp"):
                self.__logger.critical("Error logging in: invalid username or password?")
                exit
            assert url.find("Home.do") != -1
            self.__isLoggedIn = True
    
    def __initConnection(self):
        if self.__cookieJar == None:
            self.__cookieJar = cookielib.CookieJar()
            self.__opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookieJar))
        return self.__opener
    
    def __readUrl(self, url, params = None):
        response = None
        try:
            self.__login()
            response = self.__initConnection().open(url, params)
        except urllib2.HTTPError as ex:
            self.__logger.warn('Failed to access %s HTTP Error %d: %s' % (url, ex.code, ex.msg)) 
            raise ex
        except Exception as e:
            self.__logger.warn('Failed to access %s, %s' % (url, str(e)))
            raise e
        finally:
            return response

    def __makeRace(self, jsonracedata, json_keys):
        racers = jsonracedata[json_keys['sizeoffield']]
        subsessionid = jsonracedata[json_keys['subsessionid']]
        sessionid = jsonracedata[json_keys['sessionid']]
        start_time = jsonracedata[json_keys['start_time']]
        isofficial = jsonracedata[json_keys['officialsession']]
        return Race(sessionid, subsessionid, start_time, isofficial)

    def __readCSVFromUrl(self, url):
        response = self.__readUrl(url)
                
        # iRacing.com supplies the data in CSV format. Create an in-memory file-like reader for the downloaded
        # content, and process it with the standard library csv helper
        
        csvfile = StringIO.StringIO()
        csvfile.write(str(response.read()))
        csvfile.seek(0)
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        reader = csv.reader(csvfile, dialect)
        fieldnames = reader.next() # first row is header row
        rows = []
        [rows.append(result) for result in reader]
        return fieldnames, rows

    def getLaps(self, subsessionid, custid):
        """
        Returns a list of Lap objects for the specified race session and customer
        """
        
        self.__logger.debug("Download laps for subsession %d for custid %d" % (subsessionid,custid ) )
                
        url = 'http://members.iracing.com/membersite/member/GetLaps?&subsessionid=%d&custid=%d&simsessnum=0' % (subsessionid, custid)
        
        response = self.__readUrl(url)
        txt = response.read()
        try:
            j = json.loads(txt)    
        except:
            #sadly iRacing doesn't return legal json for this call
            fixed = ''        
            inStringLiteral = False
            lastCharWasQuote = False
            for i in range(len(txt)):
                c = txt[i]
                
                if c == "'":
                    inStringLiteral = not inStringLiteral
                    fixed = fixed + "\""
                    lastCharWasQuote = True
                    continue
                if inStringLiteral:
                    fixed = fixed + c
                    lastCharWasQuote = False
                    continue
                    
                if c == '{': 
                    fixed = fixed + '{'
                    if txt[i+1] != "}":
                        fixed = fixed + '"'
                        lastCharWasQuote = True
                elif c == '}':
                    if txt[i-1] not in ("]", "{", "}"):
                        fixed = fixed + '"'
                    fixed = fixed + '}'
                    lastCharWasQuote = False
                elif c == ':':
                    fixed = fixed + '":'
                    if txt[i+1] not in ('{', "'", "["):
                        fixed = fixed + '"'                        
                        lastCharWasQuote = True
                elif c == ',':
                    if not lastCharWasQuote and txt[i-1] != "}":
                        fixed = fixed + '"'
                    fixed = fixed + ','
                    if txt[i+1] != "{":
                        fixed = fixed + '"'
                        lastCharWasQuote = True
                else:
                    fixed = fixed + c
                    lastCharWasQuote = False
                    
            j = json.loads(fixed) 
        
        lapdata = j.get('laps', list())
        self.__logger.debug("iRacing returned %d laps" % len(lapdata) )
        
        prevlaptime = 0
        first = True
        laps = list()
        for i in range(len(lapdata)):
            lap = lapdata[i]
            if i == 0:
                laptime = datetime.timedelta()
            else:
                cumulativetime =  int(lap['time'])
                curlaptime = (cumulativetime - prevlaptime) / 10
                
                laptime = datetime.timedelta(milliseconds = curlaptime)
            
            prevlaptime = int(lap['time'])
            flags = int(lap['flags'])
            lapnum = int(lap['lapnum'])
            laps.append(Lap(lapnum, laptime, flags))
                
        return laps
    
    def getRaceResults(self, subsessionid):
        """
        Returns a a list of RaceResult objects for the specified race session
        """
        self.__logger.debug("Download results of race %d" % subsessionid)
        
        url = 'http://members.iracing.com/membersite/member/GetEventResultsAsCSV?subsessionid=%d' % int(subsessionid)
        fieldnames, rows = self.__readCSVFromUrl(url)
        
        finposIdx = fieldnames.index('Fin Pos')
        caridIdx= fieldnames.index('Car ID')
        carIdx = fieldnames.index('Car')
        carclassidIdx = fieldnames.index('Car Class ID')
        carclassIdx = fieldnames.index('Car Class')
        custidIdx = fieldnames.index('Custid')
        driverIdx = fieldnames.index('Driver')
        startposIdx = fieldnames.index('Start Pos')
        carnumIdx = fieldnames.index('Car #')
        outidIdx = fieldnames.index('Out ID')
        outIdx = fieldnames.index('Out')
        intervalIdx = fieldnames.index('Interval')
        lapsledIdx = fieldnames.index('Laps Led')
        averagelaptimeIdx = fieldnames.index('Average Lap Time')
        fastestlaptimeIdx = fieldnames.index('Fastest Lap Time')
        fastlapnumIdx = fieldnames.index('Fast Lap#')
        lapscompIdx = fieldnames.index('Laps Comp')
        incIdx = fieldnames.index('Inc')
        ptsIdx = fieldnames.index('Pts')
        clubptsIdx = fieldnames.index('Club Pts')
        divIdx = fieldnames.index('Div')
        clubidIdx = fieldnames.index('Club ID')
        clubIdx = fieldnames.index('Club')
        oldiratingIdx = fieldnames.index('Old iRating')
        newiratingIdx = fieldnames.index('New iRating')
        oldlicenselevelIdx = fieldnames.index('Old License Level')
        oldlicensesublevelIdx = fieldnames.index('Old License Sub-Level')
        newlicenselevelIdx = fieldnames.index('New License Level')
        newlicensesublevelIdx = fieldnames.index('New License Sub-Level')
        seriesnameIdx = fieldnames.index('Series Name')
        
        raceResults = list()
        
        for row in rows:
            finpos = int(row[finposIdx])
            carid = int(row[caridIdx])
            car = row[carIdx]
            carclassid = int(row[carclassidIdx])
            carclass = row[carclassIdx]
            custid = int(row[custidIdx])
            driver = row[driverIdx]
            startpos = int(row[startposIdx])
            carnum = int(row[carnumIdx])
            outid = int(row[outidIdx])
            out = row[outIdx]
            interval = row[intervalIdx]
            lapsled = int(row[lapsledIdx])
            averagelaptime = iRacingUtils.getTimeDelta(row[averagelaptimeIdx])
            fastestlaptime = iRacingUtils.getTimeDelta(row[fastestlaptimeIdx])
            
            fastlapnumStr = row[fastlapnumIdx]
            if len(fastlapnumStr) == 0:
                fastlapnum = -1
            else:
                fastlapnum = int(fastlapnumStr)
            lapscomp = int(row[lapscompIdx])
            inc = int(row[incIdx])
            pts = int(row[ptsIdx])
            clubpts = int(row[clubptsIdx])
            if row[divIdx].isdigit():
                div = int(row[divIdx])
            else:
                div = 0
            
            clubid = int(row[clubidIdx])
            club = row[clubIdx]
            oldirating = int(row[oldiratingIdx])
            newirating = int(row[newiratingIdx])
            oldlicenselevel = int(row[oldlicenselevelIdx])
            oldlicensesublevel = int(row[oldlicensesublevelIdx])
            newlicenselevel = int(row[newlicenselevelIdx])
            newlicensesublevel = int(row[newlicensesublevelIdx])
            seriesname = row[seriesnameIdx]
            raceResults.append(RaceResult(subsessionid, finpos, carid, car, carclassid, carclass, custid, driver, startpos, carnum, outid, out, interval, lapsled, averagelaptime, fastestlaptime, fastlapnum, lapscomp, inc, pts, clubpts, div, clubid, club, oldirating, newirating, oldlicenselevel, oldlicensesublevel, newlicenselevel, newlicensesublevel, seriesname))
        
        return raceResults
    
    def getSeasonRaces(self, season, week = 0):
        self.__logger.debug("Retrieving races for season %s week %s" % ( str(season), str(week) ) )
        
        Races = []
        
        # Get json data for the races in the season
        try:
            url = "http://members.iracing.com/memberstats/member/GetSeriesRaceResults?raceweek=%s&seasonid=%s" % ( str(week), str(season) )
            response = self.__readUrl(url)
            txt = response.read()
            
            racedata = json.loads(txt)
            if len(racedata) == 0:
                self.__logger.warn("iRacing returned no races for season %s week %s" % ( len(races), str(season), str(week) ) )
                return []
            
            races = racedata['d']
            self.__logger.debug("iRacing returned %d races for season %s week %s" % ( len(races), str(season), str(week) ) )
            

            # Make a dictionary of the lookup keys. For some reason the json is keyed by the field number, rather than
            # the field description

            jsonkeys = dict()

            for tpl in racedata['m'].items():
                jsonkeys[tpl[1]] = tpl[0]

            # Populate a list of Race objects from the json source data

            [Races.append(self.__makeRace(jsonracedata, jsonkeys)) for jsonracedata in races]
            
        except BaseException as e:
            self.__logger.error("Failed do retrieve races for season %s week %s: %s" % ( str(season), str(week), str(e) ) )
            
        return Races
    
    def getSeasonStandings(self, season):
        """
        Returns a populated SeasonStandings object for the specified season
        """

        url = "http://members.iracing.com/memberstats/member/GetSeasonStandings?format=csv&seasonid=%d&carclassid=-1&clubid=-1&raceweek=-1&division=-1&start=1&end=25&sort=points&order=desc" % season
        fieldnames, rows = self.__readCSVFromUrl(url)
                
        positionIdx = fieldnames.index('position')
        nameIdx = fieldnames.index('name')
        pointsIdx = fieldnames.index('points')
        droppedIdx = fieldnames.index('dropped')
        clubnameIdx = fieldnames.index('clubname')
        countrycodeIdx = fieldnames.index('countrycode')
        iratingIdx = fieldnames.index('irating')
        avgfinishIdx = fieldnames.index('avgfinish')
        topfiveIdx = fieldnames.index('topfive')
        startsIdx = fieldnames.index('starts')
        lapsleadIdx = fieldnames.index('lapslead')
        winsIdx = fieldnames.index('wins')
        incidentsIdx = fieldnames.index('incidents')
        divisionIdx = fieldnames.index('division')
        weekscountedIdx = fieldnames.index('weekscounted')
        lapsIdx = fieldnames.index('laps')
        polesIdx = fieldnames.index('poles')
        avgstartIdx = fieldnames.index('avgstart')
        
        # custidIdx = fieldnames[0].index('custid') --- this is not available yet
        
        standings = list()
        for row in rows:
            position = int(row[positionIdx])
            name = row[nameIdx]
            points = int(row[pointsIdx])
            dropped = int(row[droppedIdx])
            clubname = row[clubnameIdx]
            countrycode = row[countrycodeIdx]
            irating = int(row[iratingIdx])
            avgfinish = int(row[avgfinishIdx])
            topfive = int(row[topfiveIdx])
            starts = int(row[startsIdx])
            lapslead = int(row[lapsleadIdx])
            wins = int(row[winsIdx])
            incidents = int(row[incidentsIdx])
            division = int(row[divisionIdx])
            weekscounted = int(row[weekscountedIdx])
            laps = int(row[lapsIdx])
            poles = int(row[polesIdx])
            avgstart = int(row[avgstartIdx])
            standings.append(SeasonStanding(position, name, points, dropped, clubname, countrycode, irating, avgfinish, topfive, starts, lapslead, wins, incidents, division, weekscounted, laps, poles, avgstart))
                    
        s = SeasonStandings(season, standings)
        return s
        
    def searchForDrivers(self, driverName):
        self.__logger.info("Getting driver status for %s" % driverName)
        
        url = "http://members.iracing.com/membersite/member/GetDriverStatus"
        params = urllib.urlencode({"searchTerms":driverName})
        #params = params.encode('utf-8')
        response = self.__readUrl(url, params)
        data = json.loads(response.read())
        driversjson = data.get(u'searchRacers', None)
        drivers = list()
        if driversjson is None:
            return list()
        
        for driverjson in driversjson:
            name = driverjson[u'name']
            name = urllib.unquote_plus(name)
            custid = driverjson[u'custid']
            drivers.append(Driver(name, custid))
        
        return drivers
    
    def getPersonalBests(self, carid, custid):
        """
        Returns a list of personal bests for the specified car and driver
        """
        self.__logger.info("Getting personal bests for %d" % custid)
        url = "http://members.iracing.com/memberstats/member/GetPersonalBests"
        params = urllib.urlencode({"carid":carid, "custid":custid})
        params = params.encode('utf-8')

        response = self.__readUrl(url, params)
        jsondata = json.loads(response.read())
        
        laps = []
        
        for jsonlaptime in jsondata:
            trackid = jsonlaptime['trackid']
#            trackname = urllib.unquote(jsonlaptime['trackname']).replace("+"," ")
#            trackconfigname = urllib.unquote(jsonlaptime['trackconfigname']).replace("+"," ")

            bestlaptimeformatted = urllib.unquote(jsonlaptime['bestlaptimeformatted'])
            besttime = iRacingUtils.getTimeDelta(bestlaptimeformatted)
            
            eventtypename = urllib.unquote(jsonlaptime['eventtypename']).replace("+"," ")
            
            eventtype = Driver.EVENT_TYPES.get(eventtypename, None)
            if eventtype is None:
                pass
            
            assert(eventtype is not None)
            laps.append(Laptime(trackid, eventtype, besttime))
            
        return laps

