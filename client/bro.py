#!/usr/bin/env python
import json
import requests
import sys
import time
HOST="http://brototype.ncsa.illinois.edu/"

def run_code(code):
    sources = [
        {"name": "main.bro", "content": code}
    ]
    req = {"sources": sources}
    data = json.dumps(req)
    headers = {'Content-type': 'application/json'}
    return requests.post(HOST  + "run", data=data, headers=headers).json()["job"]

def run_code_fn(fn):
    with open(fn) as f:
        code = f.read()
    
    return run_code(code)

def wait(job):
    while True:
        res = requests.get(HOST + "stdout/" + job)
        if res.status_code != 202:
            break
        print "waiting..."
        time.sleep(.1)
    res.raise_for_status()
    return res.json()

def run(fn):
    job =  run_code_fn(fn)
    print wait(job)['txt']

if __name__ == "__main__":
    fn = sys.argv[1]
    run(fn)
