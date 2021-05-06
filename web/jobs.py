# jobs.py
import time
import uuid
from hotqueue import HotQueue
from redis import StrictRedis
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import json
from datetime import datetime
redis_ip = os.environ.get('REDIS_IP')
redis_port = os.environ.get('REDIS_PORT')
if not redis_ip:
    pass
    #raise Exception()
rd1 = StrictRedis(host='localhost', port=6387, db=1, decode_responses=True) # transaction jobs
rd2 = StrictRedis(host='localhost', port=6387, db=2, decode_responses=True) # accounts
rd3 = StrictRedis(host='localhost', port=6387, db=3, decode_responses=True) # graphing jobs
rd4 = StrictRedis(host='localhost', port=6387, db=5, decode_responses=True) # for displaying jobs
q1 = HotQueue("queue", host='localhost', port=6387, db=4) # transaction queue
q2 = HotQueue("queue", host='localhost', port=6387, db=5) # graph queue

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
    job_dict["type"] = "transaction"


def _queue_job(jid):
    """Add a transaction job to the redis queue."""
    q1.put(jid)


def _queue_graph_job(jid):
    """Add a graphing job to the redis queue."""
    q2.put(jid)


def _update_account(bid, balance, history='[]'):
    """Update the account dictionary."""
    return {'bid': bid,
            'balance': balance,
            'transaction_history': history}


def _update_job(jid, bid, timestamp, balance, amount, status):
    """Update the job dictionary."""
    return {'jid': jid,
            'bid': bid,
            'timestamp': timestamp,
            'balance': balance,
            'amount': amount,
            'status': status,
            'type': "transaction"}


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
    account_dict = _update_account(bid, 0, history=json.dumps([{'ts': str(datetime.now()), 'balance': 0}]))
    _save_account(bid, account_dict)
    return bid


def create_job(bid, amount):
    """Create a new job."""
    jid = _generate_jid()
    timestamp = str(datetime.now())
    balance = float(rd2.hget(bid, 'balance'))
    job_dict = _update_job(jid, bid, timestamp, balance, amount, 'submitted')
    rd4.hmset(jid, job_dict)
    _save_job(jid, job_dict)
    _queue_job(jid)


def transaction_change(jid):
    """Deposits/Withdraws a certain amount (communicates with worker)."""
    bid = rd1.hget(jid, 'bid')
    timestamp = str(rd1.hget(jid, 'timestamp'))
    balance = float(rd1.hget(jid, 'balance'))
    amount = float(rd1.hget(jid, 'amount'))
    history = json.loads(rd2.hget(bid, 'transaction_history'))
    new_balance = balance + amount
    history.append({'ts': timestamp, 'balance': new_balance})
    job_dict = _update_job(jid, bid, timestamp, balance, amount, 'pending')
    rd4.hmset(jid, job_dict)
    _save_job(jid, job_dict)
    print("Updating account information for {}".format(bid))
    _save_account(bid, _update_account(bid, new_balance, history=json.dumps(history)))
    job_dict = _update_job(jid, bid, timestamp, balance, amount, 'complete')
    _save_job(jid, job_dict)
    rd4.hmset(jid, job_dict)

def generate_spending_graph(jid):
    """Adds a data point and adjusts the prediction function on the graph (communicates with worker)."""
    bid = rd3.hget(jid, 'bid')
    jid = rd3.hget(jid, 'jid')

    job_dict = {"jid": jid, "bid": bid, "image": b'', "status": 'pending'}
    rd3.hmset(jid, job_dict)
    rd4.hmset(jid, job_dict)
    history = json.loads(rd2.hget(bid, 'transaction_history'))
    figure, figure_axis = plt.subplots()
    figure_axis.set_xlabel("Date")
    h = figure_axis.set_ylabel("Balance")
    x = []
    y = []
    # Iterate through timestamps
    for ts_bal in history:
        timestamp = datetime.strptime(ts_bal["ts"], '%Y-%m-%d %H:%M:%S.%f')
        time = timestamp
        balance = ts_bal["balance"]
        x.append(time)
        y.append(balance)
    figure_axis.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    formatter = ticker.FormatStrFormatter('$%1.2f')
    figure_axis.yaxis.set_major_formatter(formatter)
    figure_axis.grid(True)
    figure_axis.plot(x, y)
    path_to_image = "tmp/" + jid + ".png"
    figure.autofmt_xdate()
    figure.savefig(path_to_image)
    job_dict = {"jid": jid, "bid": bid, "image": path_to_image, "status": 'complete'}
    rd3.hmset(jid, job_dict)
    rd4.hmset(jid, job_dict)


def get_spending_graph(bid):
    """Returns Matplotlib image file for graph for specified account"""
    jid = _generate_jid()
    job_dict = {"jid": jid, "bid": bid, "image": "", "status": 'submitted', "type": "graphing"}
    rd3.hmset(jid, job_dict)
    rd4.hmset(jid, job_dict)

    _queue_graph_job(jid)
    time.sleep(2)
    return rd3.hget(jid, "image")