from abc import ABC, abstractmethod
from talentvoting.common.acts import Act, Acts

class VoteIngester(ABC):
    "Currently unused."
    def __init__(self):
        pass
    
    @abstractmethod
    def _getActs() ->Acts:
        "Return a json array of all acts in the current round."
        pass

    @abstractmethod
    def cast(self, userId:str, act:Act) ->any:
        "Cast a vote for the given act on behalf of the given user."
        pass

    @abstractmethod
    def getClientVotePolicyImpl(clientLang:str) ->str:
        "Return a policy engine for a set of acts in the specified client language."
        pass