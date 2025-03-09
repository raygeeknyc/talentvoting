from typing import List, Dict

# For now an Act is a JSON object with no stricter definition enforced
Act = Dict[str, any]

# Any number of Acts are often referenced as a group
Acts = List[Act]

def parseAct(act:str)->tuple[int,int]:
    "Extract round ID and act number from act string."
    round = int(act[1:3])
    act = int(act[4:])
    return (round,act)

# This is a helper stub to use until we define backing storage services for Acts
def exampleActs() ->Acts:
    act1 = {"season": 1, "act": "S01A001", "name": "Crazy good rock", "voting_eligible": True}
    act2 = {"season": 1, "act": "S01A002", "name": "Serious Wizardry", "voting_eligible": True}
    act3 = {"season": 1, "act": "S01A003", "name": "Inspiring singer", "voting_eligible": True}
    act4 = {"season": 1, "act": "S01A004", "name": "Acrobatic comedy", "voting_eligible": True}

    acts  =  list(        
        [act1, act2, act3, act4]
        )
    return acts