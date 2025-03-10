import json
import sys
from typing import List, Tuple

from talentvoting.common.acts import Act, Acts, parseAct
from talentvoting.common.policy.votingpolicyengine import DefaultPolicyEngine
from talentvoting.common.interfaces.voteingester import VoteIngester
from talentvoting.common.interfaces.responses import FrontendError, IneligibleVote, InvalidUser, InvalidLogin, MalformedRequest, VoteCastError
from talentvoting.common.interfaces.servicelocations import VOTE_WEB_CLIENT_DOMAIN, VOTE_QUEUE_TOPIC, PROJECT_ID
from talentvoting.cloud.common.votingdatabaseutils import get_database

import firebase_admin
from firebase_admin import credentials, auth
from google.cloud import pubsub_v1

from flask import Flask, request, jsonify, Response, make_response
from werkzeug.exceptions import BadRequestKeyError

app = Flask(__name__)

cred = credentials.Certificate('private/serviceAccountKey.json')
firebase_admin.initialize_app(cred)

publisher = pubsub_v1.PublisherClient()
# Create a path to the votes topic
topic_path = publisher.topic_path(PROJECT_ID, VOTE_QUEUE_TOPIC )

def log(message:str):
     print(message, file=sys.stderr)
  
def logError(e:Exception, payload:str):
     print("Error: {}, Data: {}".format(str(e.__class__) + ":" + str(e), str(payload)), file=sys.stderr)
  
def _fixResponseHeaders(response):
    response.headers['Access-Control-Allow-Origin'] = VOTE_WEB_CLIENT_DOMAIN
    response.headers['Content-Type'] = 'text/json'

def _isLoggedInUser(user) ->bool:
     if user:
         return True
     else:
         return False

def __getUserVoteHistory(db_connection, user_id:str, round_id:int)->Tuple[int,List[str]]:
    result_rows = db_connection.execute_sql(
        "SELECT Total_votes_cast, voted_acts from Votebudget "+
        "WHERE Userid = '{}' and Round_id = {}".format(user_id, round_id)
    )
    result = result_rows.one_or_none()
    if result:
        log("votebudget(total,history):{} [1]:{}".format(result[0], result[1]))
    if result:
        prev_total = result[0]
        prev_votes = result[1]

    return (prev_total, prev_votes)

def _getActs(vote_history:List[str]) ->Acts:
     "Return the current JSON map of acts, each marked as eligible or not eligible for voting."
     acts = DefaultPolicyEngine.getAllActs()
     for act in acts:
         round_id, act_number = parseAct(act["act"])
         log("checking round,act: {},{}".format(round_id, act_number))
         if DefaultPolicyEngine.isEligibleVote(round_id, act_number, vote_history):
             log("voting_eligible")
             act["voting_eligible"] = True
         else:
             log("not voting_eligible")
             act["voting_eligible"] = False
     return acts
 
def __validateUser(form) -> str:
     uid = None
     id_token = None
     try:
         id_token = form['idToken']
 
         decoded_token = auth.verify_id_token(id_token)
         # Get user information from the decoded token
         uid = decoded_token['uid']
         # Do something with the user information
         log("validateUser({})".format(uid))

         if not _isLoggedInUser(uid):
             raise  InvalidUser(uid)

         return uid

     except BadRequestKeyError:
         raise MalformedRequest("idToken")

     except InvalidUser as e:
         raise e
     
     except auth.InvalidIdTokenError:
         raise InvalidLogin(str(id_token))
     
def _recordVote(act:Act) ->any:
     try:
         log("_recordVote({})".format(act))
         # Message data must be a bytestring
         message_data = act.encode("utf-8")
         future = publisher.publish(topic_path, message_data)
         _ = future.result()

     except Exception as e:
         logError(e, "_recordVote()")
         raise VoteCastError(str(act))

@app.route('/', methods=['POST','GET'])
def root():
     log("root {}".format(request.method))
     return "<html><body>voting front end service</body></html>"

@app.route('/vote', methods=['POST'])
def vote():
     form = request.form
     uid = __validateUser(form)

     try:
         actId = form['votedAct']
         vote = {"user": uid, "act": actId}
         vote = json.dumps(vote)
         log("vote({}".format(vote))
         _recordVote(vote)
         response = make_response(vote, 200)
         _fixResponseHeaders(response)
         log("response data: {}".format(str(response.get_data())))
         log("response headers: {}".format(str(response.headers)))
         return response
     except BadRequestKeyError:
         error = {"error" : str(MalformedRequest("votedAct").response()[0])}    
         error = json.dumps(error)
         logError(error, "error:vote()")
         response = make_response(error, error.response()[1])
         _fixResponseHeaders(response)
         log("response data: {}".format(str(response.get_data())))
         log("response headers: {}".format(str(response.headers)))
         return response
     
     except FrontendError as e:
         error = {"error" : str(e.response()[0])}    
         error = json.dumps(error)
         logError(error, "error:vote()")
         response = make_response(error, e.response()[1])
         _fixResponseHeaders(response)
         log("response data: {}".format(str(response.get_data())))
         log("response headers: {}".format(str(response.headers)))
         return response


@app.route('/getActs', methods=['POST'])
def getEligibleActs() ->any:
     try:
         form = request.form
         uid = __validateUser(form)
         vote_history = []
         round_id = DefaultPolicyEngine.getCurrentRoundId()
         with get_database().snapshot() as db_connection:
             _, fetched_vote_history = __getUserVoteHistory(db_connection, uid, round_id)
         candidate_acts = _getActs(fetched_vote_history)

         acts = {"acts" : candidate_acts}
         acts = json.dumps(acts)

         vote_history = json.dumps(fetched_vote_history)
         log("vote_history: {}".format(vote_history))

         acts_bundle = {"acts_bundle" : {"acts" : candidate_acts, "vote_history" : vote_history}}
         acts_bundle = json.dumps(acts_bundle)

         log("getActs({})".format((acts_bundle)))
         response = make_response(acts_bundle, 200)
         _fixResponseHeaders(response)
         log("response data: {}".format(str(response.get_data())))
         log("response headers: {}".format(str(response.headers)))
         return response
     
     except FrontendError as e:
         error = {"error" : str(e.response()[0])}    
         error = json.dumps(error)
         logError(error, "error:getActs()")
         response = make_response(error, e.response()[1])
         _fixResponseHeaders(response)
         log("response data: {}".format(str(response.get_data())))
         log("response headers: {}".format(str(response.headers)))
         return response