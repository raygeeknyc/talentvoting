from typing import List, Dict

# For now an Act is a JSON object with no stricter definition
Act = Dict[str, any]

# Any number of Acts are often referenced as a group
Acts = List[Act]

# This is a helper stub to use until we define backing storage services for Acts
def exampleActs() ->Acts:
    acts  =  Acts(
        {"season": 1, "act": "S01A001", "name": "Crazy good rock", "voting_eligible": True},
        {"season": 1, "act": "S01A002", "name": "Serious Wizardry", "voting_eligible": True},
        {"season": 1, "act": "S01A004", "name": "Acrobatic comedy", "voting_eligible": False}
        )
    return acts