# jobs.py
import uuid
from hotqueue import HotQueue
from redis import StrictRedis
import os
import time

redis_ip = os.environ.get('REDIS_IP')
if not redis_ip:
    raise Exception()
q = HotQueue("queue", host=redis_ip, port=6379, db=1)
rd = StrictRedis(host=redis_ip, port=6379, db=0)

def _generate_bid():
    """Create a unique banking ID (account number)."""
    bid = str(uuid.uuid1().int)
    bid = bid[:12] # banking ID is 12 digits long
    return bid

def _save_account(bid, account_dict):
    """Save an account object in the Redis database."""
    rd.hmset(bid, account_dict)

def _queue_job(bid):
    """Add a job to the redis queue."""
    q.put(bid)

def _update_dict(bid, balance, status='complete', amount=0):
    """Update the account dictionary."""
    return {'bid': bid,
            'balance': balance,
            'status': status,
            'amount': amount}

def can_withdraw(bid, amount):
    """Check if an account holder can withdraw a certain amount."""
    current_balance = float(rd.hget(bid, 'balance'))
    if current_balance - amount < 0:
        return False
    else:
        return True

def bid_exists(bid):
    """Check if a BID exists."""
    if rd.hgetall(bid) == {}:
        return True
    else:
        return False

def create():
    """Create a new account."""
    bid = _generate_bid()
    account_dict = _update_dict(bid, 100)
    _save_account(bid, account_dict)

def deposit(bid, amount):
    """Deposits a given amount."""
    current_balance = float(rd.hget(bid, 'balance'))
    _update_dict(bid, current_balance, 'submitted', amount)
    _queue_job(bid)

def withdraw(bid, amount):
    """Withdraws a given amount."""
    current_balance = float(rd.hget(bid, 'balance'))
    amount *= -1 # needs to be negative
    _update_dict(bid, current_balance, 'submitted', amount)
    _queue_job(bid)

def apply_change(bid):
    """Deposits/Withdraws a certain amount (communicates with worker)."""
    current_balance = float(rd.hget(bid, 'balance'))
    # amount: positive if deposit, negative if withdrawal
    amount = float(rd.hget(bid, 'amount'))
    new_balance = current_balance + amount
    _update_dict(bid, new_balance, 'pending')
    time.sleep(10)
    _update_dict(bid, new_balance, 'complete')


