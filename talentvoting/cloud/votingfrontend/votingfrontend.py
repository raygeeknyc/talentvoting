from talentvoting.common.acts import Act, Acts
from talentvoting.common.interfaces.voteingester import VoteIngester

class VotingFrontEnd(VoteIngester):
    def __init__(self):
        super().__init__()
        self.__setExampleActs()

# This is a stub for use until we define backing storage services for Acts
def __setExampleActs(self):
    self._acts  =  Acts(
        {"season": 1, "act": "S01A001", "name": "Crazy good rock"},
        {"season": 1, "act": "S01A002", "name": "Serious Wizardry"},
        {"season": 1, "act": "S01A004", "name": "Acrobatic comedy"}
    )