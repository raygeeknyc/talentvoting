from talentvoting.common.acts import Act, Acts, exampleActs, parseAct
from typing import List

MAX_VOTES_PER_ROUND = 6

class VotingPolicyEngine(object):

    def __init__(self):
        self._acts = exampleActs()

    def getAllActs(self) ->Acts:
        return self._acts
    
    def getCurrentRoundId(self)->int:
        first_act = self._acts[0]["act"]
        return parseAct(first_act)[0]
    
    @staticmethod
    def isEligibleVote(round_id:int, act_number:int, prev_votes:List[str]) ->bool:
        """"
        Determine if this vote is within the vote budget.
        The vote history is 0 indexed, act numbers start at 1 so adjust the index into the history array.
        """

        if not round_id or not act_number or not prev_votes:
            return False
        prev_total = prev_votes.count('Y')
        if prev_votes[act_number-1] == 'Y':
            return False
        if prev_total >= MAX_VOTES_PER_ROUND:
            return False
        return True
    
DefaultPolicyEngine = VotingPolicyEngine()