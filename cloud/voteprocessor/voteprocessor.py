import json
from flask import Flask, request
from talentvoting.common.policy.votingpolicyengine import MAX_VOTES_PER_ROUND
from talentvoting.common.interfaces.servicelocations import SPANNER_INSTANCE, SPANNER_DATABASE

from google.cloud import spanner

app = Flask(__name__)
def __get_database():
    "Create a database connection - this is per request for now"
    spanner_client = spanner.Client()
    instance = spanner_client.instance(SPANNER_INSTANCE)
    database = instance.database(SPANNER_DATABASE)
    print("Created database connection")
    return database

def __is_vote_in_budget(transaction, user_id, round_id, act_number):
    """Return votes array if this user has remaining votes in their budget and has not voted for this act.
    Insert a new Votebudget for this user and round if no Votebudget exists.
    returns: Array of string if a Vote can be cast for this act, False otherwise
    """
    print("__is_vote_in_budget()")
    result_rows = transaction.execute_sql(
        "SELECT Total_votes_cast, voted_acts from Votebudget "+
        "WHERE Round_id = {} AND Userid = '{}'".format(round_id, user_id)
    )
    result = result_rows.one_or_none()
    print("result: {}".format(result))
    if result:
        print("[0]:{} [1]:{}".format(result[0], result[1]))
    if result:
        prev_total = result[0]
        prev_votes = result[1]
        if prev_votes[act_number] != 'Y' and prev_total < MAX_VOTES_PER_ROUND:
            return prev_votes
        else:
            return False
    else:
        new_votes = ['N','N','N','N','N','N','N','N','N','N','N','N']
        print("creating votebudget for user {} round {}".format(user_id, round_id))
        print("new_votebudget: {}" .format(str(new_votes)))
        sql= "INSERT INTO Votebudget "+\
            "(Userid, Round_id, Last_voted_at, Total_votes_cast, Voted_acts) "+\
            "VALUES('{}',{},NULL,0,ARRAY{})".format(user_id, round_id,str(new_votes))
        print("INSERT: '{}'".format(sql))
        row_ct = transaction.execute_update(sql)

        if row_ct != 1:
            raise ValueError("Updated unexpected number of rows {} inserted for round {} act {}".
                             format(row_ct, round_id, act_number))

        return new_votes

def __update_vote(transaction, act_number, round_id):
    print("__update_vote()")
    row_ct = transaction.execute_update(
        "UPDATE Votes "
        "SET Total = Total + 1 "
        "WHERE Act_number = {} ".format(act_number) +
        "AND Round_id = {}".format(round_id)
    )
    if row_ct != 1:
        raise ValueError("Updated unexpected number of rows {} for round {} act {}".
                         format(row_ct, round_id, act_number))

def __update_votebudget(transaction, user_id, round_id, act_number, vote_budget):
    print("__update_votebudget()")
    vote_budget[act_number] = 'Y'
    print("vote_budget set to: {}".format(str(vote_budget)))
    sql= "UPDATE Votebudget "+ \
    "SET voted_acts = ARRAY{}, ".format(str(vote_budget)) + \
        "Total_votes_cast = Total_votes_cast + 1, " +\
        "Last_voted_at = CURRENT_TIMESTAMP " +\
        "WHERE Round_id = {} AND Userid = '{}'".format(round_id, user_id)
    print("UPDATE '{}'".format(sql))
    row_ct = transaction.execute_update(sql)

    if row_ct != 1:
        raise ValueError("Updated unexpected number of rows {} updated for round {} user {}"
                         .format(len(row_ct), round_id, user_id))

def _apply_vote_if_allowed(transaction, user_id, round_id, act_number):
    print("_apply_vote_if_allowed()")
    vote_budget = __is_vote_in_budget(transaction, user_id, round_id, act_number)
    print("vote_budget: {}".format(vote_budget))
    if not vote_budget:
        print("vote out of budget for user {} round {} act {}".format(user_id, round_id, act_number))
        return
    __update_vote(transaction, act_number, round_id)
    __update_votebudget(transaction, user_id, round_id, act_number, vote_budget)
    return        

def _processVote(message:json) -> bool:
    """
    Process a JSON message containing a vote.
    args:
        message: A JSON dict
    Returns:
        True if a message was processed, False otherwise
    """
    if not message:
        return False
    if not isinstance(message, dict):
        return False
    if "user" not in message or "act" not in message:
        return False
    round = int(message["act"][1:3])
    act = int(message["act"][4:])
    __get_database().run_in_transaction(_apply_vote_if_allowed, user_id=message["user"], round_id=round, act_number=act)
    return True


@app.route("/", methods=["POST"])
def index():
    """Receive a Pub/Sub message which should contain valid JSON and issue HTTP response."""
    message = request.data
   
    print("incoming message!")
    if message:
        print("data: {}".format(message))
    try:
        vote = json.loads(message)
    except ValueError as e:
        print("Invalid JSON received: {}".format(e))
        return ("Invalid JSON", 400)
    try:
        if _processVote(vote):
            print("Processed vote: {}".format(vote))
        else:
            print("Invalid vote: {}".format(vote))
            return ("Invalid vote", 400)  # Invalid content error status  
    except Exception as e:
        print("error: {}".format(e))
        return ("", 500)  # Internal server error status
    return ("", 204)  # No content OK status
