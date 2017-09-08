import sqlalchemy
import pandas as pd

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
	parsedCols = []
	for player in enumerate(players_list):
		parsedCols.append(player['account_id'])
		parsedCols.append(player['player_slot'])
		parsedCols.append(player['hero_id'])
		parsedCols.append(player['item_0'])
		parsedCols.append(player['item_1'])
		parsedCols.append(player['item_2'])
		parsedCols.append(player['item_3'])
		parsedCols.append(player['item_4'])
		parsedCols.append(player['item_5'])
		parsedCols.append(player['kills'])
		parsedCols.append(player['deaths'])
		parsedCols.append(player['assists'])
		parsedCols.append(player['leaver_status'])
		parsedCols.append(player['gold'])
		parsedCols.append(player['last_hits'])
		parsedCols.append(player['denies'])
		parsedCols.append(player['gold_per_min'])
		parsedCols.append(player['xp_per_min'])
		parsedCols.append(player['gold_spent'])
		parsedCols.append(player['hero_damage'])
		parsedCols.append(player['tower_damage'])
		parsedCols.append(player['hero_healing'])
		parsedCols.append(player['level'])

'''
Converts json matches to dataframe that can export into psql
Input: array of dictionaries (should be jsonData['result']['matches'])
Output: dataframe
'''
def json_to_df(matchesJson):
	matchDF = pd.DataFrame(matchesJson)

	matchDF = matchDF[matchDF['human_players']==10]

	# remove columns to be restructured (with nested info)
	del matchDF['players']
	if 'picks_bans' in matchDF.keys():
		del matchDF['picks_bans']





