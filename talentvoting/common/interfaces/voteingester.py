from abc import ABC, abstractmethod
from talentvoting.common.acts import Act, Acts

class VoteIngester(ABC):
    @abstractmethod
    def cast(self, act):
        pass

    def getActs(self) ->Acts:
        return self._acts
    
    def __init__(self):
        self._acts : Acts = []