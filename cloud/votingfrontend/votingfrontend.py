from talentvoting.common.acts import Act, Acts
from talentvoting.common.policy.votingpolicyengine import VotingPolicyEngine
from talentvoting.common.interfaces.voteingester import VoteIngester
from talentvoting.common.interfaces.responses import FrontendError, IneligibleVote, InvalidUser, InvalidLogin, MalformedRequest
from talentvoting.common.interfaces.servicelocations import VOTE_WEB_CLIENT_DOMAIN

import firebase_admin
from firebase_admin import credentials, auth

from flask import Flask, request, jsonify, Response, make_response

import json

app = Flask(__name__)

from werkzeug.exceptions import BadRequestKeyError

import sys

cred = credentials.Certificate('private/serviceAccountKey.json')
firebase_admin.initialize_app(cred)

_policy_engine = VotingPolicyEngine()

def log(e:Exception, payload:str):
     print("Message: {}, Data: {}".format(str(e.__class__) + ":" + str(e), str(payload)), file=sys.stderr)
  
def _fixResponseHeaders(response):
    response.headers['Access-Control-Allow-Origin'] = VOTE_WEB_CLIENT_DOMAIN
    response.headers['Content-Type'] = 'text/json'

def _isLoggedInUser(user) ->bool:
     if user:
         return True
     else:
         return False
    
def _getActs() ->Acts:
     return _policy_engine.getAllActs()
 
def validateUser(form) -> str:
     uid = None
     id_token = None
     try:
         id_token = form['idToken']
 
         decoded_token = auth.verify_id_token(id_token)
         # Get user information from the decoded token
         uid = decoded_token['uid']
         # Do something with the user information
         log({'success': True, 'uid': uid},"validateUser()")

         if not _isLoggedInUser(uid):
             raise  InvalidUser(uid)

         return uid

     except BadRequestKeyError:
         raise MalformedRequest("idToken")

     except InvalidUser as e:
         raise e
     
     except auth.InvalidIdTokenError:
         raise InvalidLogin(str(id_token))
     
@app.route('/', methods=['POST','GET'])
def root():
     log(str(request.form), "root" )
     return "<html><body>voting front end service</body></html>"

@app.route('/vote', methods=['POST'])
def vote():
     form = request.form
     uid = "unknown"
     pass

@app.route('/getActs', methods=['POST'])
def getEligibleActs() ->any:
     try:
         form = request.form
         uid = validateUser(form)

         candidate_acts = _getActs()
         eligible_acts = []
         for act in candidate_acts:
             if act["voting_eligible"]:
                 eligible_acts.append(act)
         acts = {"acts" : eligible_acts}
         acts = json.dumps(acts)
        
         log(acts, "getActs()")
         response = make_response(acts, 200)
         _fixResponseHeaders(response)
         print(str(response), file=sys.stderr)
         return response
     
     except FrontendError as e:
         error = {"error" : str(e.response()[0])}    
         error = json.dumps(error)
         log(error, "error:getActs()")
         response = make_response(error, e.response()[1])
         _fixResponseHeaders(response)
         print(str(response), file=sys.stderr)
         return response
