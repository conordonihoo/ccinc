# jobs.py
import uuid
from hotqueue import HotQueue
from redis import StrictRedis
import os
import time
import json
from datetime import datetime

redis_ip = os.environ.get('REDIS_IP')
redis_port = os.environ.get('REDIS_PORT')
if not redis_ip:
    pass
    #raise Exception()
q = HotQueue("queue", host='localhost', port=6387, db=0) # queue
rd1 = StrictRedis(host='localhost', port=6387, db=1, decode_responses=True) # jobs
rd2 = StrictRedis(host='localhost', port=6387, db=2, decode_responses=True) # accounts

def _generate_bid():
    """Create a unique banking ID (account number)."""
    bid = str(uuid.uuid1().int)
    bid = bid[:12] # banking ID/account number is 12 digits long
    return bid

def _generate_jid():
    """Create a unique job ID."""
    return str(uuid.uuid4())

def _save_account(bid, account_dict):
    """Save an account object in second Redis database."""
    rd2.hmset(bid, account_dict)

def _save_job(jid, job_dict):
    """Save a job object in the first Redis database."""
    rd1.hmset(jid, job_dict)

def _queue_job(jid):
    """Add a job to the redis queue."""
    q.put(jid)

def _update_account(bid, balance, history='[]'):
    """Update the account dictionary."""
    return {'bid': bid,
            'balance': balance,
            'history': history}

def _update_job(jid, bid, timestamp, balance, amount, status):
    """Update the job dictionary."""
    return {'jid': jid,
            'bid': bid,
            'timestamp': timestamp,
            'balance': balance,
            'amount': amount,
            'status': status}

def can_withdraw(bid, amount):
    """Check if an account holder can withdraw a certain amount."""
    current_balance = float(rd2.hget(bid, 'balance'))
    if current_balance + amount < 0: # amount is negative
        return False
    else:
        return True

def bid_exists(bid):
    """Check if a BID exists."""
    if bid in rd2.keys():
        return True
    else:
        return False

def create_account():
    """Create a new account."""
    bid = _generate_bid()
    account_dict = _update_account(bid, 0, history=json.dumps([[str(datetime.now()), 0]]))
    _save_account(bid, account_dict)
    return bid

def create_job(bid, amount):
    """Create a new job."""
    jid = _generate_jid()
    # CAMERON PLEASE MAKE THE TIMESTAMP - minutes would work best (type = int)
    # ex: 1am = 60min, 5:30am = 330min, 8:27pm = 1227min
    timestamp = str(datetime.now())
    balance = float(rd2.hget(bid, 'balance'))
    job_dict = _update_job(jid, bid, timestamp, balance, amount, 'submitted')
    _save_job(jid, job_dict)
    _queue_job(jid)

def apply_change(jid):
    """Deposits/Withdraws a certain amount (communicates with worker)."""
    bid = rd1.hget(jid,'bid')
    timestamp = str(rd1.hget(jid, 'timestamp'))
    balance = float(rd1.hget(jid, 'balance'))
    amount = float(rd1.hget(jid, 'amount'))
    history = json.loads(rd2.hget(bid, 'history'))
    new_balance = balance + amount
    history.append([timestamp, new_balance])
    _save_job(jid, _update_job(jid, bid, timestamp, balance, amount, 'pending'))
    time.sleep(20)
    _save_account = (bid, _update_account(bid, new_balance, history=json.dumps(history)))
    _save_job(jid, _update_job(jid, bid, timestamp, balance, amount, 'complete'))


