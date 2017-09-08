
import pickle
import sqlalchemy
import pandas as pd
from getpass import getpass

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

ability_schema = []
for ind in range(19):	#19 is the highest ability level, valve ignores levels without upgrades
	ability_schema += ['ability' + str(ind) + '_id']
	ability_schema += ['ability' + str(ind) + '_time']
	ability_schema += ['ability' + str(ind) + '_level']
'''
Establishes connection to psql database
'''
def connect_to_psql(user,password,host,database):
	engine_str = 'postgresql://' + user + ':' + password + '@' + host + '/' + database
	engine = sqlalchemy.create_engine(engine_str)
	connection = engine.connect()
	return connection

'''
Separate out players info into distinct columns
Applied to players column in df
'''
def parse_players_info(players_list):
	global player_schema

	parsedCols = []
	for player in players_list:
		parsedCols += [player[x] for x in player_schema]
		parsedCols += parse_ability(player['ability_upgrades'])
	return parsedCols
'''
Converts json matches to dataframe that can export into psql
Input: array of dictionaries (should be jsonData['result']['matches'])
Output: dataframe
'''

'''
Separate out array upgrades into distinct columns
'''
def parse_ability(ability_upgrades):
	upgrade_num = len(ability_upgrades)
	abilityCols = []
	for ind in range(19):
		if ind < upgrade_num:
			upgrade = ability_upgrades[ind]
			abilityCols += [upgrade['ability'],upgrade['time'],upgrade['level']]
		else:
			abilityCols += [None,None,None]
	return abilityCols

'''
Transforms match information stored as json into a pandas DF
'''
def json_to_df(matchesJson):
	global player_schema
	team_schema = []
	for ind in range(10):
		temp_schema = ['p' + str(ind) + '_' + item for item in player_schema]
		temp_schema += ['p' + str(ind) + '_' + item for item in ability_schema]
		team_schema += temp_schema


	matchDF = pd.DataFrame(matchesJson)
	matchDF = matchDF[matchDF['human_players']==10]

	newcols = matchDF['players'].apply(lambda x: pd.Series(parse_players_info(x), index = team_schema))
	matchDF[team_schema] = newcols

	del matchDF['players']
	if 'picks_bans' in matchDF.keys():
		del matchDF['picks_bans']
	return matchDF

matchData = pickle.load(open('matchData.pkl','rb'))
matchDF = json_to_df(matchData)
pswd = getpass()
connection = connect_to_psql('kevin',pswd,'localhost','kevin')
matchDF.to_sql('dota_matches',connection,index=False,if_exists='replace',index_label='match_id')