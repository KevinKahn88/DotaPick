'''
DotaAPI controls calls to Valve's API

'''


from urllib.request import urlopen
import json
import pickle

url = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchHistoryBySequenceNum/V001/?start_at_match_seq_num=2900000002&key=DFD1061664AEAC307766E3BD4C824B83'

apiResponse = urlopen(url)
rawData = apiResponse.read().decode('utf-8')
jsonData = json.loads(rawData)
matchData = jsonData['result']['matches']

pickle.dump(matchData,open('matchData.pkl','wb'))