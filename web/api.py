# api.py
import json
from flask import Flask, render_template, request
import jobs
import os

app = Flask(__name__)
flask_ip = os.environ.get('FLASK_IP')
flask_port = os.environ.get('FLASK_PORT')


@app.route('/')
def main():
  return render_template("page.html")


@app.route('/login', methods=['GET'])
def login():
  bid = request.args.get('id', default='', type=str)
  if jobs.bid_exists(bid):
    print("ACCESSING ACCT: " , str(bid))
    return json.dumps(jobs.rd2.hgetall(bid))
  else:
    return 'ACCOUNT NUMBER NOT FOUND'

# MAKE GET ROUTE FOR JOBS SIMILAR TO THE GET ROUTE FOR ACCOUNTS ^^^^


@app.route('/create', methods=['GET'])
def create():
  bid = jobs.create_account()
  return json.dumps(jobs.rd2.hgetall(bid))


@app.route('/delete', methods=['GET'])
def delete():
  bid = request.args.get('id', default='', type=str)
  if jobs.bid_exists(bid):
    jobs.rd2.delete(bid)
    return 'completed'
  else:
    return 'ACCOUNT NUMBER NOT FOUND'


@app.route('/accountids', methods=['GET'])
def account_ids():
  return json.dumps(jobs.rd2.keys())


@app.route('/jobids', methods=['GET'])
def job_ids():
  return json.dumps(jobs.rd1.keys())


@app.route('/transaction/deposit', methods=['GET'])
def deposit():
  bid = request.args.get('id', default='', type=str)
  amount = request.args.get('amount', default=0, type=float)
  if jobs.bid_exists(bid):
    jobs.create_job(bid, amount)
    print("Depositing ${} into acct {}".format(amount, bid))
    return jobs.rd2.hget(bid, 'balance')
  else:
    print("Invalid acct# to deposit ${} to acct {}".format(amount, bid))
    return 'ACCOUNT NUMBER NOT FOUND'


@app.route('/transaction/withdraw', methods=['GET'])
def withdraw():
  bid = request.args.get('id', default='', type=str)
  amount = (request.args.get('amount', default=0, type=float))
  amount *= -1 # needs to be negative
  if jobs.bid_exists(bid):
    if jobs.can_withdraw(bid, amount):
      jobs.create_job(bid, amount)
      print("Withdrawing ${} from acct {}".format(amount, bid))
      return jobs.rd2.hget(bid, 'balance')
    else:
      print("Invalid funds to withdraw ${} from acct {}".format(amount, bid))
      return 'NOT ENOUGH BALANCE'
  else:
    print("Invalid acct# to withdraw ${} from acct {}".format(amount, bid))
    return 'ACCOUNT NUMBER NOT FOUND'


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
