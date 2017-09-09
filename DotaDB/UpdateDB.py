import DotaDB
import DotaAPI
import time
import pickle

'''
Returns batch of matches in json format
Updates pickle file to newest seqeuence #
'''
def get_matches():
	lastMatchSeq = pickle.load(open('.lastMatchSeq.pkl','rb'))
	prop = {'start_at_match_seq_num': str(lastMatchSeq+1),'matches_requested':'500'}
	apiURL = DotaAPI.form_api_url(prop)
	[matchJSON,errCode,errReason] = DotaAPI.api_match_call(apiURL)
	if errCode == 0:
		#TO DO: Update pickle file to newest seq #
		return matchJSON
	else:
		errorlog = open('Log\errlog.txt','a')
		errMSG = time.strftime('%m-%d-%y-%H:%M:%S') + ',' + str(errCode) + ',' + errReason
		errorlog.write(errMSG)
		errorlog.close()
		return -1

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

	matchJSON = get_matches()
	matchDF = DotaDB.json_to_df(matchJSON)
	matchDF.to_sql('dota_matches',psql,if_exists='replace',index=False,index_label='match_id')

if __name__ == '__main__':
	main()


[_,pswd] = pickle.load(open('../.credentials.pkl','rb'))
user = 'kevin'
host = 'localhost'
database = 'dota'
psql = DotaDB.connect_to_psql(user,pswd,host,database)

matchJSON = get_matches()