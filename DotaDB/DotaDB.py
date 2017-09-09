
import pickle
import sqlalchemy
import pandas as pd

GAME_SCHEMA = [
	'barracks_status_dire',
	'barracks_status_radiant',
	'cluster',
	'dire_score',
	'duration',
	'engine',
	'first_blood_time',
	'flags',
	'game_mode',
	'human_players',
	'leagueid',
	'lobby_type',
	'match_id',
	'match_seq_num',
	'negative_votes',
	'positive_votes',
	'pre_game_duration',
	'radiant_score',
	'radiant_win',
	'start_time',
	'tower_status_dire',
	'tower_status_radiant',
	'players'
]

PLAYER_SCHEMA = [
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

ABILITY_SCHEMA = []
for ind in range(19):	#19 is the highest ability level, valve ignores levels without upgrades
	ABILITY_SCHEMA += ['ability' + str(ind) + '_id']
	ABILITY_SCHEMA += ['ability' + str(ind) + '_time']
	ABILITY_SCHEMA += ['ability' + str(ind) + '_level']
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
	global PLAYER_SCHEMA

	parsedCols = []
	for player in players_list:
		parsedCols += [player[x] for x in PLAYER_SCHEMA]
		if 'ability_upgrades' in player.keys():
			parsedCols += parse_ability(player['ability_upgrades'])
		else:	#Entered if no abilities upgraded
			parsedCols += [None]*3*19
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
	global PLAYER_SCHEMA
	global GAME_SCHEMA

	team_schema = []
	for ind in range(10):
		temp_schema = ['p' + str(ind) + '_' + item for item in PLAYER_SCHEMA]
		temp_schema += ['p' + str(ind) + '_' + item for item in ABILITY_SCHEMA]
		team_schema += temp_schema


	matchDF = pd.DataFrame(matchesJson)
	matchDF = matchDF[matchDF['human_players']==10]
	for colName in matchDF.keys():
		if colName not in GAME_SCHEMA:
			del matchDF[colName]


	newcols = matchDF['players'].apply(lambda x: pd.Series(parse_players_info(x), index = team_schema))
	matchDF[team_schema] = newcols
	del matchDF['players']

	return matchDF