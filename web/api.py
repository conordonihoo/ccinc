# api.py
import json
from flask import Flask, request
import jobs

app = Flask(__name__)

@app.route('/status', methods=['GET'])
def get_status():
    status_list = []
    for key in jobs.rd.keys():
        status_list.append(str(jobs.rd.hgetall(key)))
    return (json.dumps(status_list) + '\n')

@app.route('/reset', methods=['GET'])
def reset():
  for key in jobs.rd.keys():
    jobs.rd.delete(key)
  return 'Completed\n'

@app.route('/jobs', methods=['POST'])
def jobs_api():
    try:
        job = request.get_json(force=True)
    except Exception as e:
        return True, json.dumps({'status': "Error", 'message': 'Invalid JSON: {}.'.format(e)})
    return (json.dumps(jobs.add_job(job['start'], job['end'])) + '\n')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
