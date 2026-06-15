import sqlite3
import pandas as pd

CSV_FILE = "fifa_world_cup_2026_player_performance.csv"
DB_FILE = "fifa_tracker.db"

df = pd.read_csv(CSV_FILE)

con = sqlite3.connect(DB_FILE)
df.to_sql("player_stats", con, if_exists="replace", index=False)

con.execute("""
    CREATE VIEW IF NOT EXISTS top_scorers AS
    SELECT
        player_name,
        nationality,
        team,
        position,
        SUM(goals) AS total_goals,
        SUM(assists) AS total_assists,
        SUM(shots_on_target) AS total_shots_on_target,
        COUNT(DISTINCT match_id) AS matches_played
    FROM player_stats
    GROUP BY player_id
    ORDER BY total_goals DESC, total_assists DESC
""")

con.execute("""
    CREATE VIEW IF NOT EXISTS team_stats AS
    SELECT
        team,
        COUNT(DISTINCT match_id) AS matches_played,
        SUM(CASE WHEN match_result = 'W' THEN 1 ELSE 0 END) AS wins,
        SUM(CASE WHEN match_result = 'D' THEN 1 ELSE 0 END) AS draws,
        SUM(CASE WHEN match_result = 'L' THEN 1 ELSE 0 END) AS losses,
        SUM(goals) AS goals_scored,
        ROUND(AVG(player_rating), 2) AS avg_player_rating
    FROM player_stats
    GROUP BY team
    ORDER BY wins DESC, goals_scored DESC
""")

con.execute("""
    CREATE VIEW IF NOT EXISTS match_results AS
    SELECT DISTINCT
        match_id,
        match_date,
        tournament_stage,
        team,
        opponent_team,
        match_result,
        goals_team,
        goals_opponent,
        stadium,
        city
    FROM player_stats
    ORDER BY match_date
""")

con.commit()
con.close()
print("Database created successfully: fifa_tracker.db")
