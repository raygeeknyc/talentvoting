from talentvoting.common.acts import Act, Acts

class VotingPolicyEngine(object):
    def __init__(self):
        self.__acts = []
        self.__setExampleActs()

    # This is a helper stub to use until we define backing storage services for Acts
    def __setExampleActs(self):
        self._acts  =  Acts(
            {"season": 1, "act": "S01A001", "name": "Crazy good rock"},
            {"season": 1, "act": "S01A002", "name": "Serious Wizardry"},
            {"season": 1, "act": "S01A004", "name": "Acrobatic comedy"}
            )

    def getAllActs(self) ->Acts:
        return self.__acts
    
    def isEligibleVote(self, user, act:Act) ->bool:
        return True