from talentvoting.common.acts import Act, Acts
from talentvoting.common.policy.votingpolicyengine import VotingPolicyEngine
from talentvoting.common.interfaces.voteingester import VoteIngester
from talentvoting.common.interfaces.responses import IneligibleVote, InvalidUser, InvalidLogin

import firebase_admin
from firebase_admin import credentials, auth

from flask import Flask, request, jsonify, Response

app = Flask(__name__)

from werkzeug.exceptions import BadRequestKeyError

import sys

cred = credentials.Certificate('private/serviceAccountKey.json')
firebase_admin.initialize_app(cred)


@app.route('/', methods=['POST','GET'])
def root():
     print(str(request.form), file=sys.stderr)
     return "<html><body>voting front end service</body></html>"

def logError(e:Exception, payload:str):
     print("Error: {}, Data: {}".format(str(e.__class__), str(payload)), file=sys.stderr)

@app.route('/vote', methods=['POST'])
def vote():
     form = request.form
     uid = "unknown"
     try:
         id_token = request.form['idTokenz']

         decoded_token = auth.verify_id_token(id_token)
         # Get user information from the decoded token
         uid = decoded_token['uid']
         # Do something with the user information
         return jsonify({'success': True, 'uid': uid})

     except BadRequestKeyError as e:
         logError(e, 'idToken')
         return  InvalidLogin("none").response()

     except auth.InvalidIdTokenError:
         logError(e, uid)
         return  InvalidLogin(str(uid).response())

class VotingFrontEnd(VoteIngester):
     @staticmethod
     def _isLoggedInUser(user) ->bool:
         if user:
             return True
         else:
             return False
    
     def __init__(self):
         super().__init__()
         self._policy_engine = VotingPolicyEngine()
    
     def _getActs(self) ->Acts:
         return self._policy_engine.getAllActs()
   
     def getAllActs(self, requesting_user) ->any:
         if not self._isLoggedInUser(requesting_user):
             return  InvalidUser(requesting_user).response()

         return self._getActs()
    
     def cast(self, requesting_user, act:Act) ->any:
         if not self._isLoggedInUser(requesting_user):
             return  InvalidUser(requesting_user).response()

         if not self._policy_engine.isEligibleVote(requesting_user, act):
             return IneligibleVote(requesting_user, act).response()
    
     def getEligibleActs(self, requesting_user) ->Acts:
         if not self._isLoggedInUser(requesting_user):
             return  InvalidUser(requesting_user).response()

         candidate_acts = self._getActs()
         eligible_acts = []
         for act in candidate_acts:
             if act["voting_eligible"]:
                 eligible_acts.append(act)
        
         return eligible_acts 