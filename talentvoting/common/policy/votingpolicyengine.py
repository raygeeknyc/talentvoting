from talentvoting.common.acts import Act, Acts, exampleActs, parseAct
from typing import List


class VotingPolicyEngine(object):
    "This is meant to be used through its provided instance (see bottom of file)."
    MAX_VOTES_PER_ROUND = 6

    DEFAULT_VOTE_HISTORY = ['N','N','N','N','N','N','N','N','N','N','N','N']

    def __init__(self):
        self._acts = exampleActs()

    def getAllActs(self) ->Acts:
        "Return all current acts as retrieved."
        return self._acts
    
    def getCurrentRoundId(self)->int:
        "Parse out the round_id from the first act in the current round."
        first_act = self._acts[0]["act"]
        return parseAct(first_act)[0]

    @staticmethod
    def getClientJSVotePolicyImpl() ->str:
        """
        Return the Javascript source for a policuy rules enforcement function
        to be used as a client-side equivalent of isEligibleVote(...) in this class.
        """
        return """ 
        // If we have reached the limit on votes, disable all vote buttons
        // After a vote has been cast for an act, disable its vote button
        console.log(voted_act, vote_tally_element, vote_limit, acts_table); // required method signature
        let voted_count = parseInt(vote_tally_element.value);
        voted_count = voted_count + 1;
        vote_tally_element.value = voted_count;
        const rows = acts_table.rows
        for (let i = 0; i < rows.length; i++) {
             const row = rows[i];
             if (i > 0) {  // The first row is a TH
                 const rowActId = row.cells[0].children[0].value;
                 if (rowActId == voted_act || voted_count >= vote_limit) {
                     row.cells[1].innerHTML = '';  // Removes all children
                     row.cells[1].innerHTML = '--';                  
                 }
             }
         }
             """


    @staticmethod
    def isEligibleVote(round_id:int, act_number:int,
                        prev_votes:List[str]) ->bool:
        """"
        Determine if this vote is within the vote budget.
        The vote history is 0 indexed, act numbers start at 1 so adjust the index 
        into the history array.
        """

        if not round_id or not act_number or not prev_votes:
            return False
        prev_total = prev_votes.count('Y')
        if prev_votes[act_number-1] == 'Y':
            return False
        if prev_total >= DefaultPolicyEngine.MAX_VOTES_PER_ROUND:
            return False
        return True
    

# Provide a singleton for clients to use
DefaultPolicyEngine = VotingPolicyEngine()