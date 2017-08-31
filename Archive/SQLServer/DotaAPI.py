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
        details['Match_ID'] = matchDict['match_id']
        details['Match_Seq'] = matchDict['match_seq_num']
        details['Game_Mode'] = matchDict['game_mode']
        details['Lobby_Type'] = matchDict['lobby_type']
        details['Start_Time'] = matchDict['start_time']
        details['Duration'] = matchDict['duration']
        details['Tower_Rad'] = matchDict['tower_status_radiant']
        details['Tower_Dir'] = matchDict['tower_status_dire']
        details['Barracks_Rad'] = matchDict['barracks_status_radiant']
        details['Barracks_Dir'] = matchDict['barracks_status_dire']
        details['FB_Time'] = matchDict['first_blood_time']
        details['Humans'] = matchDict['human_players']
        details['Cluster'] = matchDict['cluster']
        if matchDict['radiant_win']:
            details['Rad_Win'] = 1
        else:
            details['Rad_Win'] = 0
        teamName = ['Rad','Dir']
        teamOffset = 128
        leaverCount = 0


        for ind in range(len(matchDict['players'])):   # Run through all players
            playerSlot = matchDict['players'][ind]['player_slot']
            playerLabel = teamName[int(playerSlot/teamOffset)] + '_Hero' + str(playerSlot%teamOffset+1)  
            details[playerLabel] = matchDict['players'][ind]['hero_id']
            if matchDict['players'][ind]['leaver_status'] > 2:
                leaverCount += 1 
        details['Leavers'] = leaverCount
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
    print(url)
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
    print(parsed_json)
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
    url = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/V001/?match_id=1892354235&key=DFD1061664AEAC307766E3BD4C824B83'
    print(matchDetails(1892354235,0))
    pass