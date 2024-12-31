from talentvoting.common.acts import Act, Acts
from talentvoting.common.policy.votingpolicyengine import VotingPolicyEngine
from talentvoting.common.interfaces.voteingester import VoteIngester
from talentvoting.common.interfaces.responses import IneligibleVote

class VotingFrontEnd(VoteIngester):
    def __init__(self):
        super().__init__()
        self._policy_engine = VotingPolicyEngine()

    def _getActs(self) ->Acts:
        return self._policy_engine.getAllActs()
   
    def getAllActs(self, requesting_user) ->Acts:
        return self._getActs()
    
    def cast(self, requesting_user, act:Act) ->any:
        if not self._policy_engine.isEligibleVote(requesting_user, act):
            return IneligibleVote(requesting_user, act).response()
    
    def getEligibleActs(self, requesting_user) ->Acts:
        candidate_acts = self._getActs()
        eligible_acts = []
        for act in candidate_acts:
            # TODO add filtering for acts currently open for voting
            eligible_acts.append(act)