import datetime

class Series:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.seasons = { } # season id, Season
        
class Season:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        
class Car:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        
        
class iRacingRefData:
    """
    Contains collections of (relatively) static data, like car types, race tracks, series and season numbers
    """
    
    lastUpdated = "2010-29-03"  # yyyy-mm-dd
    series = []
    cars = { }
    seasons = { }
    
    


class SeasonStanding:
        
    def __init__(self, position, name, points, dropped, clubname, countrycode, irating, avgfinish, topfive, starts, lapslead, wins, incidents, division, weekscounted, laps, poles, avgstart):
                        
        self.position=position
        self.name=name
        self.points=points
        self.dropped=dropped
        self.clubname=clubname
        self.countrycode=countrycode
        self.irating=irating
        self.avgfinish=avgfinish
        self.topfive=topfive
        self.starts=starts
        self.lapslead=lapslead
        self.wins=wins
        self.incidents=incidents
        self.division=division
        self.weekscounted=weekscounted
        self.laps=laps
        self.poles=poles
        self.avgstart=avgstart

class SeasonStandings:
           
    def __init__(self, season, standings = list()):
        
        self.season = season
        self.standings = standings

class Race:
    def __init__(self, session, subsession, racestarttime, isofficial):
        
        self.sessionid = session
        self.subsessionid = subsession
        self.isofficial = isofficial
        self.racestarttime = datetime.datetime.fromtimestamp(racestarttime / 1000)
        self.raceresults = None # {} custid, RaceResult objects
    
    def setResults(self, results):
	"""
	Associates a list of RaceResult objects with this race. 
	Results are stored in a dictionary keyed by custid
	"""
	self.raceresults = {}
	for result in results:
	    self.raceresults[result.custid] = result
    
    def getResults(self):
	return self.raceresults
	
    def  __str__(self):
        return 'Race: Subsession: %d, Start Time: %s' % (self.subsession, self.racestarttime)

    
class Laptime:
    """ Used to record personal bests """
    def __init__(self, trackid, eventtype, time):
        self.trackid = trackid
        self.eventtype = eventtype
        self.laptime = time #timedelta

class Driver:
    
    EVENT_TYPES = { 'Practice':1, 'Qualify':2, 'Race':3, 'Time Trial':4 }

    
    def __init__(self, name, custid = None):
        self.name = name
        self.custid = custid
        self.personalbests = {} # carid, list(Laptime)
       
class Lap:
    """ Used to record a single lap by a single driver for a race """
    FLAG_INVALID = 1
    FLAG_PITTED = 2
    FLAG_OFF_TRACK = 4
    FLAG_BLACK_FLAG = 8
    FLAG_CAR_RESET = 16
    FLAG_CONTACT = 32
    FLAG_CAR_CONTACT = 64
    FLAG_LOST_CONTROL = 128
    FLAG_DISCONTINUITY = 256
    FLAG_INTERPOLATED_CROSSING = 512
    FLAG_CLOCK_SMASH = 1024
    FLAG_TOW = 2048
		    
    def __init__(self, lapnum, time, flags):
        self.lapnum = lapnum

	assert(isinstance(time, datetime.timedelta))
        self.flags = flags
	if flags & Lap.FLAG_INVALID:
	    self.time = datetime.timedelta(0)
	else:
	    self.time = time #timedelta	    

    def isGoodLap(self):
        """
        Returns True if the lap was considered safe. That means not pitted, not out of control, no tow, not first lap (lap zero) 
        Off-tracks are OK, as are discontinuities.
        """
	if self.lapnum == 0: return False
	
	badflags = Lap.FLAG_INVALID + Lap.FLAG_PITTED + Lap.FLAG_BLACK_FLAG + Lap.FLAG_CAR_RESET + Lap.FLAG_CONTACT + Lap.FLAG_LOST_CONTROL + Lap.FLAG_DISCONTINUITY + Lap.FLAG_INTERPOLATED_CROSSING + Lap.FLAG_CLOCK_SMASH + Lap.FLAG_TOW
	badLap = self.flags & badflags
	
	return not badLap
	
    def isCleanLap(self):
	"""
	Returns true if there the lap has no incidents, discontinuities etc.
	"""
	return self.lapnum != 0 and self.flags == 0    	
    
class RaceResult:
    """
    The detailed results of a race
    """
    def __init__(self, subsessionid, finpos, carid, car, carclassid, carclass, custid, driver, startpos, carnum, outid, out, interval, lapsled, averagelaptime, fastestlaptime, fastlapnum, lapscomp, inc, pts, clubpts, div, clubid, club, oldirating, newirating, oldlicenselevel, oldlicensesublevel, newlicenselevel, newlicensesublevel, seriesname):
        """
        Creates a new race result. Parameters:
            
        """
        self.laps = None # list() of Lap
        
        self.subsessionid = subsessionid
        self.finpos = finpos
        self.carid = carid
        self.car = car
        self.carclassid = carclassid
        self.carclass = carclass
        self.custid = custid
        self.driver = driver
        self.startpos = startpos
        self.carnum = carnum
        self.outid = outid
        self.out = out
        self.interval = interval
        self.lapsled = lapsled
        self.averagelaptime = averagelaptime
        self.fastestlaptime = fastestlaptime
        self.fastlapnum = fastlapnum
        self.lapscomp = lapscomp
        self.inc = inc
        self.pts = pts
        self.clubpts = clubpts
        self.div = div
        self.clubid = clubid
        self.club = club
        self.oldirating = oldirating
        self.newirating = newirating
        self.oldlicenselevel = oldlicenselevel
        self.oldlicensesublevel = oldlicensesublevel
        self.newlicenselevel = newlicenselevel
        self.newlicensesublevel = newlicensesublevel
        self.seriesname = seriesname

    def setLaps(self, laps):
	"""
	Sets list of Laps associated with this race result
	"""
        self.laps = laps
	
    def getGoodLaps(self):
	"""
	Returns a list of Laps that are 'good' according to Lap.isGoodLap()
	"""
	goodLaps = []
	for lap in self.laps:
	    if lap.isGoodLap():
		goodLaps.append(lap)
		
	return goodLaps
    	
