from talentvoting.common.acts import Act, Acts, exampleActs

MAX_VOTES_PER_ROUND = 6

class VotingPolicyEngine(object):
    def __init__(self):
        self._acts = exampleActs()

    def getAllActs(self) ->Acts:
        return self._acts
    
    def isEligibleVote(self, user, act:Act) ->bool:
        if user and act:
            return True
        else:
            return False