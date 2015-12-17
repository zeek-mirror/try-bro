from flask import Flask, render_template, request, redirect
from flask.ext.jsonpify import jsonify
import hashlib

import backend
import metrics

from flask import Flask

class FlaskStaticCors(Flask):
    def send_static_file(self, filename):
        response = super(FlaskStaticCors, self).send_static_file(filename)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

app = FlaskStaticCors(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/metrics")
def bro_metrics():
    return render_template('metrics.html', metrics=metrics.get())

@app.route("/metrics.json")
def bro_metrics_json():
    return cors_jsonify(**metrics.get())

@app.route("/saved/<job>")
def saved(job):
    return backend.get_saved(job)

@app.route("/run", methods=['OPTIONS'])
def run_options_for_cors():
    return cors_jsonify(ok="ok")

@app.route("/run", methods=['POST'])
def run():
    sources = request.json.get('sources', '')
    pcap = request.json.get('pcap', '')
    version = request.json.get('version', '')
    if pcap and '--' in pcap:
        pcap = None

    job_id, stdout = backend.run_code(sources, pcap=pcap, version=version)
    return cors_jsonify(job=job_id, stdout=stdout)

@app.route("/run_simple", methods=['GET', 'POST'])
def run_simple():
    stdin = request.args.get("code") or request.form.get("code") or 'print "Huh?";'
    version = request.args.get("version") or request.form.get("version") or backend.BRO_VERSION

    files = backend.run_code_simple(stdin, version=version)
    return cors_jsonify(files=files)

@app.route("/stdout/<job>")
def stdout(job):
    txt = backend.get_stdout(job)
    if txt is None:
        return 'wait', 202
    return cors_jsonify(txt=txt)

@app.route("/files/<job>")
def files(job):
    files = backend.get_files(job)
    return cors_jsonify(files=files)

@app.route("/files/<job>.json")
def files_json(job):
    files = backend.get_files_json(job)
    return cors_jsonify(files=files)

@app.route("/versions.json")
def versions():
    return cors_jsonify(versions=backend.BRO_VERSIONS, default=backend.BRO_VERSION)

@app.route("/pcap/upload/<checksum>", methods=['POST'])
def pcap_upload(checksum):
    contents = request.files['pcap'].read()
    actual = md5(contents)
    ok = actual == checksum
    if ok:
        backend.save_pcap(checksum, contents)
    return cors_jsonify(status=ok, checksum=actual)

@app.route("/pcap/<checksum>")
def has_pcap(checksum):
    status = backend.check_pcap(checksum)
    return cors_jsonify(status=status)

@app.route("/example/<name>")
def example(name):
    return redirect("/#/trybro?example=%s" % name)

def md5(s):
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()

def cors_jsonify(**kwargs):
    response = jsonify(**kwargs)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

app.debug = False

if __name__ == "__main__":
    app.run(debug=True)
