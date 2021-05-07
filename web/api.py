# api.py
import json
from flask import Flask, render_template, request, send_from_directory
import jobs
import os
import os.path as path

app = Flask(__name__)
flask_ip = os.environ.get('FLASK_IP')
flask_port = os.environ.get('FLASK_PORT')
app.config['UPLOAD_FOLDER'] = "."


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


@app.route('/create', methods=['GET'])
def create():
  bid = jobs.create_account()
  return jobs.rd2.hgetall(bid)


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


@app.route('/jobs', methods=['GET'])
def get_jobs():
  job_list = []
  for key in jobs.rd4.keys():
    job_list.append(jobs.rd4.hgetall(key))
  jobs.rd4.flushdb()
  return json.dumps(job_list)


@app.route('/graph/spending', methods=['GET'])
def get_spending_graph():
  bid = request.args.get('id', default='', type=str)
  # Extra random data for clearing the cache
  rand = request.args.get('rand', default='', type=str)
  file_path = jobs.get_spending_graph(bid)
  uploads = path.join(app.root_path, app.config['UPLOAD_FOLDER'])
  ret = send_from_directory(directory=uploads, filename=file_path)
  return ret


@app.route('/graph/histogram', methods=['GET'])
def get_hourly_histogram():
  bid = request.args.get('id', default='', type=str)
  # Extra random data for clearing the cache
  rand = request.args.get('rand', default='', type=str)
  file_path = jobs.get_hrly_histogram(bid)
  uploads = path.join(app.root_path, app.config['UPLOAD_FOLDER'])
  ret = send_from_directory(directory=uploads, filename=file_path)
  return ret


@app.route('/generate_accounts', methods=['GET'])
def gen_accts():
  bid = request.args.get('id', default='', type=str)
  jobs.q1.put("generate random accounts")
  return "Confirmed"


@app.route('/nuke', methods=['GET'])
def clear_db():
  jobs.rd1.flushdb()
  jobs.rd2.flushdb()
  jobs.rd3.flushdb()
  jobs.rd4.flushdb()
  jobs.q1.clear()
  jobs.q2.clear()
  return "Nuked"


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
