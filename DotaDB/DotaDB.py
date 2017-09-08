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
	for ind, player in enumerate(players_list):

'''
Converts json matches to dataframe that can export into psql
Input: array of dictionaries (should be jsonData['result']['matches'])
Output: dataframe
'''
def json_to_df(matchesJson):
	matchDF = pd.DataFrame(matchesJson)

	# remove columns to be restructured (with nested info)
	del matchDF['players']
	if 'picks_bans' in matchDF.keys():
		del matchDF['picks_bans']





