import sys
import json
import zipfile
import logging
import urllib.request

from typing import Dict
from datetime import date
from tqdm import tqdm

from utils.config import ZIP_URL
from utils.db_utils import get_db_connection
from utils.logger_utils import get_logger


# setup logging
py_file = __file__.split("/")[-1]
logger = get_logger(name=f"{py_file}:{__name__}")


def run():

    logger.info("Getting database connection")
    conn = get_db_connection()

    logger.info(f"Getting ZIP from: {ZIP_URL}")
    zip_object = get_zip(ZIP_URL)

    json_file_list = [file for file in zip_object.namelist() if ".json" in file]

    logger.info(f"Found {len(json_file_list)} files, processing now...")
    for file in tqdm(json_file_list):
        # get file data
        file_json = get_json_elements(file, zip_object)
        file_number = int(file.split(".")[0])

        # separate three main dicts
        file_meta = file_json.get("meta")
        file_info = file_json.get("info")
        file_innings = file_json.get("innings")

        # files_proccessed table
        file_processed_data = tuple(
            map(file_meta.get, ["data_version", "created", "revision"])
        )

        # players table - combine players and player_registry objects
        player_registry = file_info.get("registry").get("people")
        players_data = [
            (id, name, team, file_info.get("gender"))
            for name, id in player_registry.items()
            for team, name_list in file_info.get("players").items()
            for _ in name_list
            if _ == name
        ]

        # match_outcome table
        outcome_type = None
        outcome_margin = None
        outcome_dict = file_info.get("outcome").get("by", None)
        if outcome_dict is not None:
            outcome_type = list(outcome_dict.keys())[0]
            outcome_margin = list(outcome_dict.values())[0]

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

        # innings tables
        innings_data = [
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

        # *** DB INSERT ***
        try:
            with conn:
                conn.executemany(
                    """
                    INSERT INTO players(id, name, team, gender) 
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(id) DO NOTHING
                    """,
                    players_data,
                )

                conn.execute(
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

                conn.executemany(
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
                    innings_data,
                )

                conn.execute(
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

        except Exception as e:
            logger.error(e)
            conn.close()
            sys.exit(1)

    logger.info("Finished processing files, closing DB connection")
    conn.close()


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
