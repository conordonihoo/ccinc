# api.py
import json
from flask import Flask, render_template
import jobs
import redis

app = Flask(__name__)
rd = redis.StrictRedis(host="10.102.92.99", port=6379, db=1)


@app.route('/')
def main():
    # We use the HTML file as the template
    return render_template("page.html")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
