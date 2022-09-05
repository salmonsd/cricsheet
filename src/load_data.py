import urllib.request
import zipfile
import json
from utils.config import ZIP_URL
from utils.db_utils import get_db_connection
from typing import Dict
from datetime import date


def run():

    db_con = get_db_connection()

    zip_object = get_zip(ZIP_URL)

    json_file_list = [file for file in zip_object.namelist() if ".json" in file]

    for file in json_file_list:
        file_name = str(file)
        file_number = int(file.split(".")[0])
        # get file data
        file_json = get_json_elements(file, zip_object)

        # separate three main dicts
        file_meta = file_json.get("meta")
        file_info = file_json.get("info")
        file_innings = file_json.get("innings")

        # files_proccessed table
        file_processed_data = tuple(
            map(file_meta.get, ["data_version", "created", "revision"])
        )

        # parse player registry and combine with file_info players
        player_registry = file_info.get("registry").get("people")
        player_data = [
            (id, name, team, file_info.get("gender"))
            for name, id in player_registry.items()
            for team, name_list in file_info.get("players").items()
            for _ in name_list
            if _ == name
        ]

        outcome_type = None
        outcome_margin = None
        outcome_dict = file_info.get("outcome").get("by", None)
        if outcome_dict is not None:
            outcome_type = list(outcome_dict.keys())[0]
            outcome_margin = list(outcome_dict.values())[0]
        # match_outcome table
        match_outcome_data = (
            file_info.get("match_type"),
            file_info.get("match_type_number"),
            file_info.get("season"),
            date.fromisoformat(file_info.get("dates")[0]),
            file_info.get("gender"),
            file_info.get("teams")[0],
            file_info.get("teams")[1],
            file_info.get("outcome").get("winner"),
            outcome_type,
            outcome_margin,
        )

        # parse match info
        match_info_data = [
            (
                side_dict.get("team"),
                overs_dict.get("over"),
                delivery,
                delivery_dict.get("batter"),
                delivery_dict.get("bowler"),
                delivery_dict.get("non_striker"),
                delivery_dict.get("runs").get("batter"),
                delivery_dict.get("runs").get("extras"),
                delivery_dict.get("runs").get("total"),
            )
            for side_dict in file_innings
            for overs_dict in side_dict.get("overs")
            for delivery, delivery_dict in enumerate(overs_dict.get("deliveries"))
        ]

        with db_con:
            db_con.executemany(
                """
                INSERT INTO players(id, name, team, gender) 
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO NOTHING
                """,
                player_data,
            )

            db_con.execute(
                f"""
                INSERT INTO match_outcome(
                    file_number,
                    match_type,
                    match_type_number,
                    season,
                    match_date,
                    gender,
                    team_1,
                    team_2,
                    winner,
                    outcome_type,
                    outcome_by
                    )
                VALUES ({file_number}, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(file_number) DO NOTHING
                """,
                match_outcome_data,
            )

            db_con.executemany(
                f"""
                INSERT INTO innings(
                    file_number,
                    team,
                    over,
                    delivery,
                    batter,
                    bowler,
                    non_striker,
                    batter_runs,
                    extras_runs,
                    total_runs
                    )
                VALUES ({file_number}, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                match_info_data,
            )

            db_con.execute(
                f"""
                INSERT INTO file_processed(
                    file_number,
                    data_version,
                    created,
                    revision
                    )
                VALUES ({file_number}, ?, ?, ?)
                """,
                file_processed_data,
            )


def get_zip(url: str):
    """
    Given a URL link, return a ZipFile object.
    """
    filehandle, _ = urllib.request.urlretrieve(url)
    zip_file_object = zipfile.ZipFile(filehandle, "r")
    return zip_file_object


def get_json_elements(file: str, zip_file_object: object) -> Dict:
    """
    Takes in a file from a ZipFile object and open, reads,
    and loads it as json/Dict.
    """
    opened_file = zip_file_object.open(file)
    file_content = opened_file.read()
    json_content = json.loads(file_content.decode("utf-8"))
    return json_content


if __name__ == "__main__":
    run()
