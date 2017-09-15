#!/usr/bin/env python

import DotaDB
import DotaAPI
import time
import pickle

'''
Returns batch of matches in json format
Original match_seq_num = 2500000000
'''
def get_matches():
	lastMatchSeq = pickle.load(open('.lastMatchSeq.pkl','rb'))
	prop = {'start_at_match_seq_num': str(lastMatchSeq+1),'matches_requested':'500'}
	apiURL = DotaAPI.form_api_url(prop)
	[matchJSON,errType,errCode,errReason] = DotaAPI.api_match_call(apiURL)
	if errType:
		errorlog = open('Log/errlog.txt','a')
		errMSG = time.strftime('%m-%d-%y-%H:%M:%S') + ', ' + str(errType) + ', ' + str(errCode) + ', ' + str(errReason) + '\n'
		errorlog.write(errMSG)
		errorlog.close()
		return -1
	else:
		return matchJSON

'''
Main function
Continuously makes calls to dota API for match information
uploads match data to DB
'''
def main():
	[_,pswd] = pickle.load(open('../.credentials.pkl','rb'))
	user = 'kevin'
	host = 'localhost'
	database = 'dota'
	psql = DotaDB.connect_to_psql(user,pswd,host,database)

	throttle = 5
	while True:
		time.sleep(throttle)
		matchJSON = get_matches()
		if matchJSON == -1:
			throttle = throttle * 2
		else:
			throttle = 5
			matchDF = DotaDB.json_to_df(matchJSON)
			matchDF.to_sql('dota_matches',psql,if_exists='append',index=False,index_label='match_id')
			lastMatchSeq = matchDF['match_seq_num'].max()
			pickle.dump(lastMatchSeq,open('.lastMatchSeq.pkl','wb'))

if __name__ == '__main__':
	main()