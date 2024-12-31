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
    
class InvalidUser(object):
    def __init__(self, user):
        self.__user = user

    def response(self) ->any:
        return [
            {"error": "Not logged in user"},
            {"user": str(self.__user)}
        ]