import DotaDB
import pandas as pd

def query_new_matches(psql):
	query = '''
	SELECT
		dota_matches.match_id,
		dota_matches.match_seq_num,
		dota_matches.radiant_win,
		dota_matches.duration,
		dota_matches.p0_hero_id,
		dota_matches.p1_hero_id,
		dota_matches.p2_hero_id,
		dota_matches.p3_hero_id,
		dota_matches.p4_hero_id,
		dota_matches.p5_hero_id,
		dota_matches.p6_hero_id,
		dota_matches.p7_hero_id,
		dota_matches.p8_hero_id,
		dota_matches.p9_hero_id
	FROM dota_matches
	LEFT JOIN clean_matches
	ON dota_matches.match_id = clean_matches.match_id
	WHERE clean_matches.match_id IS NULL
	LIMIT 10
	'''

	return pd.read_sql_query(query,psql)

def rad_lineup(row):
	return [row['p0_hero_id'],
			row['p1_hero_id'],
			row['p2_hero_id'],
			row['p3_hero_id'],
			row['p4_hero_id']]

def dire_lineup(row):
	return [row['p5_hero_id'],
			row['p6_hero_id'],
			row['p7_hero_id'],
			row['p8_hero_id'],
			row['p9_hero_id']]

def transform_match_df(match_df):
	match_df['rad_lineup'] = match_df.apply(rad_lineup,axis=1)
	match_df['dire_lineup'] = match_df.apply(dire_lineup,axis=1)
	
	del match_df['p0_hero_id']
	del match_df['p1_hero_id']
	del match_df['p2_hero_id']
	del match_df['p3_hero_id']
	del match_df['p4_hero_id']
	del match_df['p5_hero_id']
	del match_df['p6_hero_id']
	del match_df['p7_hero_id']
	del match_df['p8_hero_id']
	del match_df['p9_hero_id']

	return match_df

def main():
	psql = DotaDB.psql()
	match_df = query_new_matches(psql)
	clean_df = transform_match_df(match_df)
	clean_df.to_sql('clean_matches',psql,index=False)

if __name__ == '__main__':
	main()
