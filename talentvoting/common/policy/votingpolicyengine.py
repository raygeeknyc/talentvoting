from talentvoting.common.acts import Act, Acts, exampleActs

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