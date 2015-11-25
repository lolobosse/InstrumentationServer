#!/usr/bin/env python

# TODO: DO not use CDN, doesn't work in the train !!! Use `bower install --save`

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

from flask import Flask, render_template, send_file
from flask_socketio import SocketIO, emit

import InstrumentationScripts as IS


app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None


def background_thread():
    time.sleep(1)
    socketio.emit('my response',
                  {'data': "Thread Started", 'count': 0},
                  namespace='/test')
    cb = IS.CommandBuilder()
    args = cb.createCommand().split()
    chdir(cb.InstrumentationPepDirectory)
    process = subprocess.Popen(args, stdout=subprocess.PIPE)
    for out in iter(process.stdout.readline, b""):
        out = '<pre>' + out + '</pre>'
        socketio.emit('my response', {'data': out, 'count':0}, namespace='/test')
        time.sleep(0.001)
    socketio.emit('my response',
                  {'data': "Thread Finished", 'count': 0},
                  namespace='/test')


@app.route('/')
def index():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.daemon = True
        # thread.start()
    return render_template('index.html')


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    # Find the thread in the pool and cancel it if he is still active
    print('Client disconnected')

@app.route('/jquery')
def send_jquery():
    return send_file('bower_components/jquery/dist/jquery.min.js')

@app.route('/socketIo')
def send_socketio():
    return send_file('static/socketIo/socketio.js')


if __name__ == '__main__':
    socketio.run(app, debug=True)
