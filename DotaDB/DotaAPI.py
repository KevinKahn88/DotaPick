'''
DotaAPI controls calls to Valve's API

'''

from urllib.request import urlopen
from urllib.error import HTTPError
from http.client import IncompleteRead
import json
import pickle

url = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchHistoryBySequenceNum/V001/?start_at_match_seq_num=2900000002&key=DFD1061664AEAC307766E3BD4C824B83'
[APIKEY,_] = pickle.load(open('../.credentials.pkl','rb'))

'''
Makes a call to the DotaAPI and returns the matchinfo in json format
Input: url fr API call
Output: 
		matchData - json format, None if unsuccessful
		type - error type, None if successful
		error - None if successful
		errormsg - None if successful
'''
def api_match_call(apiCall):
	try:
		apiResponse = urlopen(apiCall)
		rawData = apiResponse.read().decode('utf-8')
		jsonData = json.loads(rawData)
		matchData = jsonData['result']['matches']
		return [matchData,None,None,None]
	except HTTPError as err:
		print(err)
		return [None,'HTTP',err.code,err.reason]
	except IncompleteRead as err:
		print(err)
		return [None,'IncompleteRead','','']

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


