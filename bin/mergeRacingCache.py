import MemoryCache
import iRacingUtils
import os

def doFile(masterCache, dr, files):
    
    i = 1
    for fileName in files:
        assert(isinstance(masterCache, MemoryCache.MemoryCache))
        print "Loading %d of %d: %s" % (i, len(files), fileName)
        i += 1
        newCache = iRacingUtils.loadCacheFromPickle(dr+fileName)
        print "Merging..."
        masterCache.mergeWith(newCache)
        
def main():
        
    masterCache = MemoryCache.MemoryCache()
    try:
        os.path.walk("racecache/", doFile, masterCache)
    except Exception as e:
        print e
        exit(1)
        
    iRacingUtils.writeCacheToPickle(masterCache, "racecache/Allraces.txt")
        
if __name__ == '__main__':
    main()