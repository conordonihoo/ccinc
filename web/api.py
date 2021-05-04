# api.py
import json
from flask import Flask, render_template, request
import jobs

app = Flask(__name__)

@app.route('/')
def main():
  # We use the HTML file as the template
  return render_template("page.html")

@app.route('/login?id=ID_STRING_HERE', methods=['GET'])
def login():
  bid = request.args.get('id', default='', type=str)
  if jobs.bid_exists(bid): # make bid_exists() method in jobs.py
    return json.dumps(jobs.rd.hgetall(bid))
  else:
    return 'ACCOUNT NUMBER NOT FOUND'

@app.route('/create', methods=['GET'])
def create():
  bid = request.args.get('id', default='', type=str)
  jobs.create() # make create() method in jobs.py
  return json.dumps(jobs.rd.hget('bid'))

@app.route('/ids', methods=['GET'])
def ids():
  return json.dumps(jobs.rd.keys())

@app.route('/delete?id=ID_STRING_HERE', methods=['GET'])
def delete():
  bid = request.args.get('id', default='', type=str)
  if jobs.bid_exists(bid): # make bid_exists() method in jobs.py
    jobs.rd.delete(bid)
    return 'completed'
  else:
    return 'ACCOUNT NUMBER NOT FOUND'

@app.route('/transaction/deposit?id=ID_STRING_HERE&amount=AMOUNT_INT_HERE', methods=['GET'])
def deposit():
  bid = request.args.get('id', default='', type=str)
  amount = request.args.get('amount', default=0, type=float)
  if jobs.bid_exists(bid): # make bid_exists() method in jobs.py
    jobs.deposit(bid,amount) # make deposit() method in jobs.py
    return ('Balance: ' + jobs.rd.hget(bid,'balance'))
  else:
    return 'ACCOUNT NUMBER NOT FOUND'

@app.route('/transaction/withdraw?id=ID_STRING_HERE&amount=AMOUNT_INT_HERE', methods=['GET'])
def withdraw():
  bid = request.args.get('id', default='', type=str)
  amount = request.args.get('amount', default=0, type=float)
  if jobs.bid_exists(bid): # make bid_exists() method in jobs.py
    if jobs.can_withdraw(bid,amount): # make can_withdraw() method in jobs.py
      jobs.withdraw(bid,amount) # make withdraw() method in jobs.py
      return ('Balance: ' + jobs.rd.hget(bid,'balance'))
    else:
      return 'NOT ENOUGH BALANCE'
  else:
    return 'ACCOUNT NUMBER NOT FOUND'



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
