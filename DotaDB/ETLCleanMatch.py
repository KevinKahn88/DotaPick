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

def main():
	pass

if __name__ == '__main__':
	main()
