class IneligibleVote(object):
    def __init__(self, user, act):
        self.__user = user
        self.__act = act

    def response(self) ->any:
     return ({"error": "Ineligible vote",
         "user": str(self.__user),
         "act": str(self.__act)},
     403)
        

class InvalidUser(object):
    def __init__(self, user):
        self.__user = user

    def response(self) ->any:
     return ({"error": "Unknown user",
         "user": str(self.__user)},
     401)
 

class InvalidLogin(object):
    def __init__(self, id):
        self.__id = id

    def response(self) ->any:
     return ({"error": "Invalid or missing user",
         "id": str(self.__id)},
     400)
