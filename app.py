#!/usr/bin/env python
import json
from django.shortcuts import redirect

async_mode = None

if async_mode is None:
    try:
        import eventlet

        async_mode = 'eventlet'
    except ImportError:
        pass

    if async_mode is None:
        try:
            from gevent import monkey

            async_mode = 'gevent'
        except ImportError:
            pass

    if async_mode is None:
        async_mode = 'threading'

    print('async_mode is ' + async_mode)

# monkey patching is necessary because this application uses a background
# thread
if async_mode == 'eventlet':
    import eventlet

    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey

    monkey.patch_all()

import time
from threading import Thread
import subprocess
from os import chdir
import os
import signal
from uuid import uuid4

from flask import Flask, render_template, send_file, request, session, url_for
from flask_socketio import SocketIO, emit

import InstrumentationScripts as IS


# TODO Emit only to the client who asked for instrumentation: using that (warning maybe a bit qd):
# socketio.server._emit_internal(sid, 'my response', {'data': 'Only to you', 'count': 0}, '/test', 0)


app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

thread_map = {}
objects_for_thread = {}


def log(process, sid):
    for out in iter(process.stdout.readline, b""):
        if thread_map[sid]:
            out = '<pre>' + out + '</pre>'
            socketio.emit('my response', {'data': out, 'count': 0}, namespace='/test')
            time.sleep(0.001)
        else:
            os.kill(process.pid, signal.SIGUSR1)
            print 'Java Process was killed'
            break


def background_thread(sid):
    time.sleep(1)
    socketio.emit('my response',
                  {'data': "Thread Started", 'count': 0},
                  namespace='/test')
    cb = IS.CommandBuilder()
    # Replace the ini with the upload at runtime
    if 'Apk' in objects_for_thread[sid].keys():
        cb.apkFilePath = objects_for_thread[sid]['Apk']
    if 'Source' in objects_for_thread[sid].keys():
        cb.sourceFilePath = objects_for_thread[sid]['Source']
    if 'Sink' in objects_for_thread[sid].keys():
        cb.sinkFilePath = objects_for_thread[sid]['Sink']
    if 'TaintWrapper' in objects_for_thread[sid].keys():
        cb.taintWrapperPath = objects_for_thread[sid]['TaintWrapper']
    args = cb.createCommand().split()
    chdir(cb.InstrumentationPepDirectory)
    instrumentation = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log(instrumentation, sid)
    sign = subprocess.Popen(cb.createCommandSign().split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log(sign, sid)
    socketio.emit('my response',
                  {'data': "Thread Finished", 'count': 0},
                  namespace='/test')
    thread_map[sid] = False


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect', namespace='/test')
def test_connect():
    print("Client connected")
    emit('my response', {'data': 'Connected<br>', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    thread_map[request.sid] = False
    print('Client disconnected')


@socketio.on('startInstrumentation', namespace='/test')
def test_start_stop(message):
    if message['data']:
        thread = Thread(target=background_thread, args=(request.sid,))
        thread.daemon = True
        thread.setName(request.sid)
        thread_map[request.sid] = True
        thread.start()
    else:
        thread_map[request.sid] = False


@app.route('/jquery')
def send_jquery():
    return send_file('bower_components/jquery/dist/jquery.min.js')


@app.route('/socketIo')
def send_socketio():
    return send_file('static/socketIo/socketio.js')


def saveFile(target, upload):
    filename = upload.filename.rsplit("/")[0]
    destination = "/".join([target, filename])
    print "Accept incoming file:", filename
    print "Save it to:", destination
    upload.save(destination)
    return destination


@app.route('/upload', methods=["POST"])
def upload():
    form = request.form
    # Create a unique "session ID" for this particular batch of uploads.
    upload_key = str(uuid4())

    # Is the upload using Ajax, or a direct POST by the form?
    is_ajax = False
    if form.get("__ajax", None) == "true":
        is_ajax = True

    # Target folder for these uploads.
    target = '/'.join([os.path.dirname(os.path.realpath(__file__)), "static/uploads/{}".format(upload_key)])
    try:
        if not os.path.exists(target):
            os.makedirs(target)
    except OSError as e:
        print e
        if is_ajax:
            return ajax_response(False, "Couldn't create upload directory: {}".format(target))
        else:
            return "Couldn't create upload directory: {}".format(target)
    print(request.files.getlist("file"))
    if request.files.has_key("Apk"):
        upload = request.files.get("Apk")
        objects_for_thread[form['sid']] = {'Apk': saveFile(target, upload)}
        print(objects_for_thread)
    if request.files.has_key("Source"):
        upload = request.files.get("Source")
        objects_for_thread[form['sid']] = {'Source': saveFile(target, upload)}
    if request.files.has_key("Sink"):
        upload = request.files.get("Sink")
        objects_for_thread[form['sid']] = {'Sink': saveFile(target, upload)}
    if request.files.has_key("TaintWrapper"):
        upload = request.files.get("TaintWrapper")
        objects_for_thread[form['sid']] = {'TaintWrapper': saveFile(target, upload)}
    return ajax_response(True, upload_key)



def ajax_response(status, msg):
    status_code = "ok" if status else "error"
    return json.dumps(dict(
        status=status_code,
        msg=msg,
    ))


if __name__ == '__main__':
    socketio.run(app, debug=True)
