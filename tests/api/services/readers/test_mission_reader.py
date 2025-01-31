from pathlib import Path
from typing import List

import pytest

from isar.config import config
from isar.models.mission import Mission
from tests.utilities import Utilities


@pytest.mark.parametrize(
    "mission_path ,expected_output",
    [
        (
            Path("./tests/test_data/test_mission_working_nosteps.json"),
            Mission,
        ),
        (Path("./tests/test_data/test_mission_working.json"), Mission),
        (Path("./tests/test_data/no_file.json"), None),
        (Path("./tests/test_data/test_mission_not_working.json"), None),
    ],
)
def test_get_mission(mission_reader, mission_path, expected_output):
    output = mission_reader.get_mission(mission_path)
    assert Utilities.compare_two_arguments(output, expected_output)


def test_get_predefined_mission_dict(mission_reader):
    mission_list_dict = mission_reader.get_predefined_missions()
    assert type(mission_list_dict) is dict


def test_list_predefined_missions(mission_reader):
    mission_list_dict = mission_reader.list_predefined_missions()
    assert type(mission_list_dict) is dict


@pytest.mark.parametrize(
    "mission_id ,expected_output",
    [(1, Mission), (12234, None), (None, None), (config, None)],
)
def test_get_mission_by_id(mission_reader, mission_id, expected_output):
    output = mission_reader.get_mission_by_id(mission_id)
    assert Utilities.compare_two_arguments(output, expected_output)


@pytest.mark.parametrize(
    "mission_id ,expected_output",
    [(1, True), (12234, False), (None, False), (config, False)],
)
def test_is_mission_id_valid(mission_reader, mission_id, expected_output):
    output = mission_reader.mission_id_valid(mission_id)
    assert output == expected_output


def test_valid_predefined_missions_files(mission_reader):
    # Checks that the predefined mission folder contains only valid missions!
    mission_list_dict = mission_reader.get_predefined_missions()
    predefined_mission_folder = Path(
        config.get("mission", "eqrobot_pre_defined_missions_folder")
    )
    assert len(list(predefined_mission_folder.glob("*.json"))) == len(
        list(mission_list_dict)
    )
    for file in predefined_mission_folder.glob("*.json"):
        path_to_file = predefined_mission_folder.joinpath(file.name)
        mission = mission_reader.get_mission(path_to_file)
        assert mission is not None
