'''
Created on Sep 29, 2015

@author: Kevin
'''
import time
import json
import urllib.request
import sys

key = 'DFD1061664AEAC307766E3BD4C824B83'
maxAttempts = 10


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

def parseMatch(matchDict):
    details = {}
    try:
        if (matchDict['human_players'] == 10) & (matchDict['game_mode'] in [1,2,3,4,5,16,22]) & (matchDict['lobby_type'] == 0):  # Only care about these modes and full 10 player games
            details['MatchID'] = matchDict['match_id']
            details['MatchSeq'] = matchDict['match_seq_num']
            details['Mode'] = matchDict['game_mode']
            if matchDict['radiant_win']:
                details['RadWin'] = 1
            else:
                details['RadWin'] = 0
            teamName = ['Rad','Dir']
            teamOffset = [0,128]
            okFlag = True   # Flag if player slot #s match correct value
            for ind in range(10):   # Run through all players
                if matchDict['players'][ind]['player_slot'] == teamOffset[int(ind/5)]+ind%5:
                    details[teamName[int(ind/5)] + 'Hero' + str(ind%5+1)] = matchDict['players'][ind]['hero_id']
                else:
                    okFlag = False
                    logError('Error in parseMatch(' + str(matchDict['match_id']) + '): ' + 'player mismatch for\n')
            if okFlag:
                return details
    except KeyError:
        return {}
    return {}

# Gets a Batch of Match Details using GetMAtchHistoryBySequenceNum
def batchDetails(prop, lastRequest):
    global key
    global maxAttempts
    
    throttle(lastRequest,1)
    apiURL = historyBySeqNumAPI(prop)
    print(apiURL)
    for count in range(maxAttempts):    # Attempt to grab match info from Web API
        try:
            page = urllib.request.urlopen(apiURL)
            content = page.read().decode('utf-8')
            thisRequest = time.time()
            break
        except:
            error = sys.exc_info()
            error_msg = 'Error in batchDetails(): ' + str(error[0]) + ',' + str(error[1]) + '\n'
            logError(error_msg)
            time.sleep(10)
    else:
        logError('Max Attempts reached in getMatches\n')
        return ({}, time.time(),0,1)
    
    parsed_json = json.loads(content)   # Parse JSON Format
    try:
        batchData = parsed_json['result']['matches']
    except KeyError:
        return({},thisRequest,0,1)
    
    details = []
    for matchDict in batchData:
        try:
            print(matchDict['match_id'])
            tempInfo = parseMatch(matchDict)
            if len(tempInfo) > 0:
                details.append(tempInfo)
        except KeyError:
            logError('Error in batchDetails(): ' + 'KeyError for ' + str(matchDict['match_id']) + '\n')
    return (details,batchData[-1]['match_seq_num'],thisRequest,0)
    

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
    details = parseMatch(parsed_json['result'])
    if len(details) > 0:
        return (details,thisRequest,0)
    else:
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

# Formats URL for Match History lookup using dota web API
def historyBySeqNumAPI(prop):
    global key
    
    url = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchHistoryBySequenceNum/V001/?'
    
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