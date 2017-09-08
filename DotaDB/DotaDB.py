
import pickle
import sqlalchemy
import pandas as pd

test_url = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchHistoryBySequenceNum/V001/?start_at_match_seq_num=2900000002&key=DFD1061664AEAC307766E3BD4C824B83'

player_schema = [
	'account_id',
	'player_slot',
	'item_0',
	'item_1',
	'item_2',
	'item_3',
	'item_4',
	'item_5',
	'kills',
	'deaths',
	'assists',
	'leaver_status',
	'gold',
	'last_hits',
	'denies',
	'xp_per_min',
	'gold_spent',
	'hero_damage',
	'tower_damage',
	'hero_healing',
	'level']
'''
Establishes connection to psql database
'''
def connect_to_psql(user,password,host,database):
	engine_str = 'postgresql://' + user + ':' + password + '@' + host + '/' + database
	engine = sqlalchemy.creat_engine(engine_str)
	connection = engine.connect()
	return connection

'''
Separate out players info into distinct columns
Applied to players column in df
'''
def parse_players_info(players_list):
	global player_schema

	parsedCols = []
	for player in enumerate(players_list):
		parsedCols.append([player[x] for x in player_schema])
'''
Converts json matches to dataframe that can export into psql
Input: array of dictionaries (should be jsonData['result']['matches'])
Output: dataframe
'''
def json_to_df(matchesJson):
	global player_schema
	team_schema = []
	for ind in range(10):
		temp_schema = ['p' + str(ind) + '_' + item for item in player_schema]
		team_schema.append(temp_schema)


	matchDF = pd.DataFrame(matchesJson)
	matchDF = matchDF[matchDF['human_players']==10]

	matchDF[team_schema] = matchDF['players'].apply(parse_players_info)
	return matchDF

matchData = pickle.load(open('matchData.pkl','rb'))
matchDF = pd.DataFrame(matchData)
matchDF = matchDF[matchDF['human_players']==10]
players_info = matchDF['players'][0]