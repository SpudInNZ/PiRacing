import datetime
import logging
import pickle
import os
import ConfigParser

PICKLE_FILE = "../racecache/racedata.txt"

def getConfigDir():
    
    # 
    curdir = os.getcwd()
    conf = os.path.join(curdir, "../config")
    assert(os.path.exists(conf))
    return conf
    
def getConfigFileName():

    confDir = getConfigDir()
    confFile = os.path.join(confDir, "PiRacing.cfg")
    assert(os.path.exists(confFile))
    return confFile
    
    ACCOUNT_CONFIG_FILE = os.path.join(CONFIG_DIR, "Account.cfg")
#
#    assert(os.path.exists(CONFIG_FILE))
#    return CONFIG_FILE

def getAccountDetails(configFileName = None):
    """
    Reads a username and password combination from the specified configuration file and returns them in a 2-tuple
    """
    
    if configFileName is None:
        configFileName = os.path.join(getConfigDir(), "Account.cfg")
        
    assert(os.path.exists(configFileName))
    config = ConfigParser.ConfigParser()
    config.read(configFileName)
    username = config.get("login","username", 0)
    password = config.get("login","password", 0)
    # quick sanity check
    if password == "your_password":
        raise Exception("You must edit the Account.cfg file in the 'cache' folder and set your iRacing username and password.")
    return username, password

def getTimeDelta(string_time):
    """
    Returns a timedelta representing the input string, which must be in the format mm:ss.ssss. Minutes are optional.
    """
    index = string_time.find(".")
    if index == -1 or len(string_time) < 5:    # s.sss
        return datetime.timedelta()
    
    millis = int (string_time[index + 1: ])
    secs = int (string_time[index - 2: index])
    
    index = string_time.find(":")
    if index != -1:
        mins = int(string_time[: index ])
    else:
        mins = 0
    
    result = datetime.timedelta(minutes=mins, seconds = secs, milliseconds = millis) 
    return result

def writeCacheToPickle(cache, fileName=PICKLE_FILE):

    backupFileName = "backup_" + fileName
    if os.path.exists(fileName):
        if os.path.exists(backupFileName):
            os.remove(backupFileName)
        os.rename(fileName, backupFileName)
        
    with open(fileName,"w") as file:
        logging.getLogger().info("Writing cached data to %s" % fileName)
        try:
            pickle.dump(cache, file)
            logging.getLogger().info("Cached data saved successfully")
        except BaseException as e:
            logging.getLogger().error("Error saving cache: %s" % e)
            

def loadCacheFromPickle(fileName = PICKLE_FILE):
    cache = None
    if os.path.exists(fileName):
        with open(fileName,"r") as file:
            logging.getLogger().info("Loading cached data from %s" % fileName)
            try:
                cache = pickle.load(file)
                logging.getLogger().info("Cached data loaded successfully")
            except BaseException as e:
                cache = None
                logging.getLogger().error("Error loading data from cache: %s" % e)
    else:
        raise Exception("Cache %s not found" % fileName)
    return cache