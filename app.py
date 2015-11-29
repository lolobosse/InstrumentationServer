#!/usr/bin/env python

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

from flask import Flask, render_template, send_file, request, session
from flask_socketio import SocketIO, emit

import InstrumentationScripts as IS


# TODO Emit only to the client who asked for instrumentation: using that (warning maybe a bit qd):
# socketio.server._emit_internal(sid, 'my response', {'data': 'Only to you', 'count': 0}, '/test', 0)


app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

thread_map = {}


def background_thread(sid):
    time.sleep(1)
    socketio.emit('my response',
                  {'data': "Thread Started", 'count': 0},
                  namespace='/test')
    cb = IS.CommandBuilder()
    args = cb.createCommand().split()
    chdir(cb.InstrumentationPepDirectory)
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for out in iter(process.stdout.readline, b""):
        if thread_map[sid]:
            out = '<pre>' + out + '</pre>'
            socketio.emit('my response', {'data': out, 'count':0}, namespace='/test')
            time.sleep(0.001)
        else:
            os.kill(process.pid, signal.SIGUSR1)
            print 'Java Process was killed'
            break
    socketio.emit('my response',
                  {'data': "Thread Finished", 'count': 0},
                  namespace='/test')
    thread_map[sid] = False



@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect', namespace='/test')
def test_connect():
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


if __name__ == '__main__':
    socketio.run(app, debug=True)
