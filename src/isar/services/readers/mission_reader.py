import logging
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional

from isar.config import config
from isar.models.mission import Mission
from isar.services.readers.base_reader import BaseReader
from models.geometry.frame import Frame
from models.planning.step import STEPS

logger = logging.getLogger("state_machine")


class MissionReader(BaseReader):
    def __init__(
        self,
        predefined_mission_folder: Path = Path(
            config.get("mission", "eqrobot_pre_defined_missions_folder")
        ),
    ):
        self.predefined_mission_folder = predefined_mission_folder

    def get_mission(self, mission_path: Path) -> Optional[Mission]:
        mission_dict: dict = self.read_json(mission_path)
        mission: Mission = self.dict_to_dataclass(
            dataclass_dict=mission_dict,
            target_dataclass=Mission,
            cast_config=[Frame],
        )
        if mission is None:
            logger.error(f"Could not read mission from {mission_path.as_posix()} ")
            return None
        return mission

    def get_predefined_missions(self) -> Optional[dict]:
        missions: dict = {}
        invalid_mission_ids: list = []
        try:
            json_files = self.predefined_mission_folder.glob("*.json")
            for file in json_files:
                mission_name = file.stem
                path_to_file = self.predefined_mission_folder.joinpath(file.name)
                mission: Mission = self.get_mission(path_to_file)
                if mission is None:
                    logger.warning(
                        f"File {path_to_file.as_posix()} could not be parsed to a mission"
                    )
                elif mission.mission_id in invalid_mission_ids:
                    logger.warning(
                        f"Duplicate mission_id {mission.mission_id} : {path_to_file.as_posix()}"
                    )
                elif mission.mission_id in missions:
                    conflicting_file_path = missions[mission.mission_id]["file"]
                    logger.warning(
                        f"Duplicate mission_id {mission.mission_id} : {path_to_file.as_posix()}"
                        + f" and {conflicting_file_path}"
                    )
                    invalid_mission_ids.append(mission.mission_id)
                    missions.pop(mission.mission_id)
                else:
                    missions[mission.mission_id] = {
                        "name": mission_name,
                        "file": path_to_file.as_posix(),
                        "mission": mission,
                    }
            return missions
        except Exception as e:
            logger.error(f"Error in reading of files {e}")
            return None

    def list_predefined_missions(self) -> Optional[dict]:
        mission_list_dict = self.get_predefined_missions()
        if mission_list_dict is None:
            return None
        predefined_mission_list = []
        for mission_id, current_mission in mission_list_dict.items():
            predefined_mission_list.append(
                {
                    "id": mission_id,
                    "name": current_mission["name"],
                    "file": current_mission["file"],
                    "mission_steps": asdict(current_mission["mission"])[
                        "mission_steps"
                    ],
                }
            )
        return {"missions": predefined_mission_list}

    def get_mission_by_id(self, mission_id) -> Optional[Mission]:
        mission_list_dict = self.get_predefined_missions()
        if mission_list_dict is None:
            logger.error(f"Found no missions")
            return None
        try:
            return mission_list_dict[mission_id]["mission"]
        except Exception as e:
            logger.error(f"Could not get mission : {mission_id} - does not exist {e}")
            return None

    def mission_id_valid(self, mission_id: int) -> bool:
        mission_list_dict = self.get_predefined_missions()
        try:
            if mission_id in mission_list_dict:
                return True
            else:
                logger.error(f"Mission ID: {mission_id} does not exist")
                return False
        except Exception as e:
            logger.error(f"Mission ID: {mission_id} not readable {e}")
            return False
