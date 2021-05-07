# jobs.py
import random
import time
import uuid
from hotqueue import HotQueue
from redis import StrictRedis
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib.dates import date2num
import json
import numpy as np
from polyreg import polyreg
from datetime import datetime
from datetime import timedelta
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
q2 = HotQueue("queue", host='localhost', port=6387, db=6) # graph queue

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

def generate_graph(jid):
    """Adds a data point and adjusts the prediction function on the graph (communicates with worker)."""
    bid = rd3.hget(jid, 'bid')
    jid = rd3.hget(jid, 'jid')
    if rd3.hget(jid, 'type') == "histo_graphing":
        job_dict = {"jid": jid, "bid": bid, "image": "", "type": "histo_graphing", "status": 'pending'}
        rd3.hmset(jid, job_dict)
        rd4.hmset(jid, job_dict)
        history = json.loads(rd2.hget(bid, 'transaction_history'))
        figure, figure_axis = plt.subplots()
        figure_axis.set_xlabel("Hour")
        h = figure_axis.set_ylabel("Number of Transactions")
        x = list(range(0, 24))
        y = [0]*24
        # Iterate through timestamps
        for ts_bal in history:
            timestamp = datetime.strptime(ts_bal["ts"], '%Y-%m-%d %H:%M:%S.%f')
            hour = timestamp.hour
            y[hour] += 1

        figure_axis.set_title("Spending Tracked Hourly")
        figure_axis.grid(True)
        figure_axis.bar(x, y, width=0.8, bottom=0 , align='center')
        path_to_image = "tmp/" + jid + ".png"
        figure.savefig(path_to_image)
        plt.close(figure)
        job_dict = {"jid": jid, "bid": bid, "image": path_to_image, "status": 'complete'}
        rd3.hmset(jid, job_dict)
        rd4.hmset(jid, job_dict)
    else:
        job_dict = {"jid": jid, "bid": bid, "image": "", "type": "graphing", "status": 'pending'}
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
        figure_axis.plot(x, y, label="Actual")

        x = date2num(x)
        # Linear regression
        c = polyreg(x, y, 7)
        # prediction function
        f = lambda v: c[0] + c[1] * (v) + c[2] * (v ** 2) + c[3] * (v ** 3) + c[4] * (v ** 4) + c[5] * (v ** 5) + c[
            6] * (v ** 6) + c[7] * (v ** 7)
        y_pred = f(np.array(x))
        figure_axis.plot(x, y_pred, color='red', linestyle='dashed', label="Predicted")

        figure_axis.legend()
        figure_axis.set_title("Spending Tracked and Predicted Over Time")
        path_to_image = "tmp/" + jid + ".png"
        figure.autofmt_xdate()
        figure.savefig(path_to_image, bbox_inches='tight')
        plt.close(figure)
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


def get_hrly_histogram(bid):
    """Returns Matplotlib image file for graph for specified account"""
    jid = _generate_jid()
    job_dict = {"jid": jid, "bid": bid, "image": "", "status": 'submitted', "type": "histo_graphing"}
    rd3.hmset(jid, job_dict)
    rd4.hmset(jid, job_dict)

    _queue_graph_job(jid)
    time.sleep(2)
    return rd3.hget(jid, "image")


def generate_random_accounts(num_accounts, min_trans, max_trans, min_date, max_date, trans_mean, trans_sd):
    """Generates a bunch of random accounts for analysis"""
    random.seed(time.time())
    for i in range(num_accounts):
        bid = _generate_bid()

        num_trans = random.randint(min_trans, max_trans)
        rand_history = [{}] * num_trans
        random_dates = []
        for ii in range(0, num_trans):
            rand_hour = random.randint(0, 24)
            random_number_of_days = random.randrange((max_date - min_date).days)
            random_date = datetime.strptime(min_date.strftime('%Y-%m-%d %H:%M:%S.%f'), '%Y-%m-%d %H:%M:%S.%f') + timedelta(days=random_number_of_days, hours=rand_hour)
            random_dates.append(random_date)
        random_dates = sorted(random_dates)

        balance = 0
        rand_history[0] = {'ts': random_dates[0].strftime('%Y-%m-%d %H:%M:%S.%f'), 'balance': balance}
        for ii in range(1, num_trans):
            rand_amount = np.random.normal(loc=trans_mean, scale=trans_sd, size=1).item()
            balance = rand_history[ii - 1]['balance'] + rand_amount
            if balance < 0:
                balance = 0
            balance = round(balance, 2)
            rand_history[ii] = {'ts': random_dates[ii].strftime('%Y-%m-%d %H:%M:%S.%f'), 'balance': balance}

        account_dict = _update_account(bid, balance, history=json.dumps(rand_history))
        _save_account(bid, account_dict)



