'''
Created on Sep 29, 2015

@author: Kevin
'''
import time
import json
import urllib.request
import sys

key = 'DFD1061664AEAC307766E3BD4C824B83'
maxAttempts = 100


# Writes error message to log file
def logError(error_msg):
    errorlog = open('Log\errlog' + time.strftime('%m-%d-%y') + '.txt','a')
    errorlog.write(error_msg)
    errorlog.close()
    
# throttles next command
# sleeps until throttleTime is met
def throttle(lastRequest,throttleTime):
    
    sinceLast = time.time()-lastRequest
    if sinceLast<throttleTime:
        time.sleep(throttleTime-sinceLast)

# Match Generator
def realMatches(matches):
    for mm in matches:
        if mm['lobby_type'] == 0:
            yield mm['match_id']

# Gets Match IDs based on properties listed
def getMatches(prop, lastRequest):
    global key
    global maxAttempts
    
    throttle(lastRequest,1)
    apiURL = historyAPI(prop)
    #print(apiURL)
    for count in range(maxAttempts):
        try:
            page = urllib.request.urlopen(apiURL)
            content = page.read().decode('utf-8')
            thisRequest = time.time()
            break
        except:
            error = sys.exc_info()
            error_msg = 'Error in getMatches): ' + str(error[0]) + ',' + str(error[1]) + '\n'
            logError(error_msg)
            time.sleep(10)
    else:
        logError('Max Attempts reached in getMatches\n')
        return ({}, thisRequest, 1)
    
    parsed_json = json.loads(content)
    idGEN = realMatches(parsed_json['result']['matches'])
    return ([x for x in idGEN],time.time(),0)

# Gets Match Details for specific Match ID
def matchDetails(matchID, lastRequest):
    global key
    global maxAttempts
    
    throttle(lastRequest,1)
    url = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/V001/?match_id=' + str(matchID) + '&key=' + key
    thisRequest = time.time()
    #print(url)
    for count in range(maxAttempts):
        try:
            page = urllib.request.urlopen(url)
            content = page.read().decode('utf-8')
            thisRequest = time.time()
            break
        except:
            error = sys.exc_info()
            error_msg = 'Error in matchDetails(' + str(matchID) + '): ' + str(error[0]) + ',' + str(error[1]) + '\n'
            logError(error_msg)
            time.sleep(2)
    else:
        logError('Max Attempts reached in matchDetails(' + str(matchID) + ')\n')
        return ({}, thisRequest, 1)
    
    parsed_json = json.loads(content)
    
    details = {}
    
    try:
        details['MatchID'] = parsed_json['result']['match_id']
        details['Mode'] = parsed_json['result']['game_mode']
        if details['Mode'] in [1,2,3,4,5,16,22]:
            if parsed_json['result']['radiant_win']:
                details['RadWin'] = 1
            else:
                details['RadWin'] = 0
            teamName = ['Rad','Dir']
            teamOffset = [0,128]
            for ind in range(10):
                if parsed_json['result']['players'][ind]['player_slot'] == teamOffset[int(ind/5)]+ind%5:
                    details[teamName[int(ind/5)] + 'Hero' + str(ind%5+1)] = parsed_json['result']['players'][ind]['hero_id']
                else:
                    logError('Error in matchDetails(' + str(matchID) + '): ' + 'player mismatch\n')
                    return ({},thisRequest,2)
        else:
            return ({},thisRequest,2)
        return (details,thisRequest,0)
    except KeyError:
        return ({},thisRequest,2)
    
# Formats URL for Match History lookup using dota web API
def historyAPI(prop):
    global key
    
    url = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/V001/?'
    
    first = 1   # Flag used to check if this is first parameter set
                # For all parameters after first, precede with '&'
                
    for item in iter(prop):    # Adds each property onto URL
        if first == 1:
            first = 0
        else:
            url +='&'
        url += item + '=' + str(prop[item])
    if first ==0:
        url += '&'
    url += 'key=' + key     # Adds key onto URL
    
    return url
    
if __name__ == '__main__':
    
    pass