class IneligibleVote(object):
    def __init__(self, user, act):
        self.__user = user
        self.__act = act

    def response(self) ->any:
        return [
            {"error": "Ineligible vote"},
            {"user": str(self.__user)},
            {"act": str(self.__act)}
        ]