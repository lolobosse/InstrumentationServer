#!/usr/bin/env python

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on available packages.
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
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import InstrumentationScripts as IS
import subprocess
from os import chdir

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None


# def background_thread():
#     """Example of how to send server generated events to clients."""
#     count = 0
#     while True:
#         time.sleep(10)
#         count += 1
#         socketio.emit('my response',
#                       {'data': IS.createCommand(), 'count': count},
#                       namespace='/test')

def background_thread():
    time.sleep(1)
    socketio.emit('my response',
                  {'data': "Thread Started", 'count': 0},
                  namespace='/test')
    args = IS.createCommand().split()
    chdir(IS.InstrumentationPepDirectory)
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
        thread.start()
    return render_template('index.html')


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


if __name__ == '__main__':
    socketio.run(app, debug=True)
