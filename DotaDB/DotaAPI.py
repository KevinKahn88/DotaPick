'''
DotaAPI controls calls to Valve's API

'''

from urllib.request import urlopen
from urllib.error import HTTPError
import json
import pickle

url = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchHistoryBySequenceNum/V001/?start_at_match_seq_num=2900000002&key=DFD1061664AEAC307766E3BD4C824B83'
[APIKEY,_] = pickle.load(open('../.credentials.pkl','rb'))

'''
Makes a call to the DotaAPI and returns the matchinfo in json format
Input: url fr API call
Output: 
		matchData - json format, None if unsuccessful
		error - 0 if successful
		errormsg - None if successful
'''
def api_match_call(apiCall):
	try:
		apiResponse = urlopen(apiCall)
		rawData = apiResponse.read().decode('utf-8')
		jsonData = json.loads(rawData)
		matchData = jsonData['result']['matches']
		return [matchData,0,None]
	except HTTPError as err:
		print(err)
		return [None,err.code,err.reason]

'''
Form DotaAPI url from a dictionary of properties
Key is already included
'''
def form_api_url(prop):
	global APIKEY
	url = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchHistoryBySequenceNum/V001/?key=' + APIKEY

	for [key, value] in prop.items():
		url += '&' + key + '=' + value
	return url

prop = {'start_at_match_seq_num':'2900000002'}
test = api_match_call(form_api_url(prop))

def get_match_batch():
