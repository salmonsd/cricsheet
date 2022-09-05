ZIP_URL = "https://cricsheet.org/downloads/odis_json.zip"

TABLE_CONFIG = {
    "file_processed": """
        CREATE TABLE IF NOT EXISTS file_processed (
                file_full_name
                , file_number INTEGER PRIMARY KEY
                , data_version
                , created DATE
                , revision INTEGER
                , create_dt_tm TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                , updt_cnt INTEGER DEFAULT 0
                , updt_dt_tm TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
    "players": """
        CREATE TABLE IF NOT EXISTS players (
                id PRIMARY KEY
                , name
                , gender
                , team
                , create_dt_tm TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                , updt_cnt INTEGER DEFAULT 0
                , updt_dt_tm TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
    "match_outcome": """
        CREATE TABLE IF NOT EXISTS match_outcome (
                file_number INTEGER PRIMARY KEY
                , match_type
                , match_type_number
                , season
                , match_date DATE
                , gender
                , team_1
                , team_2
                , winner
                , outcome_type
                , outcome_by
                , create_dt_tm TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                , updt_cnt INTEGER DEFAULT 0
                , updt_dt_tm TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
    "innings": """
        CREATE TABLE IF NOT EXISTS innings (
            file_number INTEGER
            , team
            , over INTEGER
            , delivery INTEGER
            , batter
            , bowler
            , non_striker
            , extras_type
            , extras_count INTEGER
            , wicket_type
            , wicket_player
            , wicket_fielder
            , batter_runs INTEGER DEFAULT 0
            , extras_runs INTEGER DEFAULT 0
            , total_runs INTEGER DEFAULT 0
            , create_dt_tm TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            , updt_cnt INTEGER DEFAULT 0
            , updt_dt_tm TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
}
