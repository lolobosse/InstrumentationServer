#Instrumentation Server for DroidForce

##Introduction

[Droid Force](https://github.com/secure-software-engineering/DroidForce) is a solution designed by some researchers of the Darmstadt University allowing you to instrument and analyse Android Applications. They used to launch their instrumentation software with [Eclipse](link to Eclipse) which is kind of inflexible when you want to instrument the app on a server.

Paper [here](https://www.informatik.tu-darmstadt.de/fileadmin/user_upload/Group_EC-Spride/Publikationen/droidforce_ares2014.pdf)

Therefore, I created this project (thanks to a suggestion of [Enrico Lovat](https://www22.in.tum.de/en/people/enrico-lovat/x)) which will allow you to drag and drop an android app + source & sinks file + tain wrapper (you've to look in the original project to see what I mean) and receive the instrumented application.

##Roadmap

Currently this project does very few: it only allow the user to go on the `0.0.0.0:5000` and then run a instrumentation following the config defined in [config.ini](config.ini)

At the end, we hope having few cool features:
* Drag and drop APK
* Define custom source, sinks and taint wrapper for instrumentation
* Hash and store instrumented APK to save resources
* Possibility to have users which will have their own custom apps
* Instrumentation via an Android App (which would call our server)

##How to use it yet

There is currently no `setup.py` so you have to do all manually (but I'll do that in few days).
* The server is running `Python 2.7.x`, so first, be sure you have it.
* Clone this repo (`git clone https://github.com/lolobosse/InstrumentationServer.git`)
* Then install following dependencies:
  * [Flask](http://flask.pocoo.org/) (`pip install Flask`)
  * [Flask SocketIO](https://flask-socketio.readthedocs.org/en/latest/) (`pip install flask-socketio`)
  * [Eventlet](http://eventlet.net/) (`pip install eventlet`)
  * [Gevent](https://pypi.python.org/pypi/gevent/1.1rc1) (`pip install gevent`)
* Clone the [DroidForce Repo](https://github.com/secure-software-engineering/DroidForce.git) and configure the [config file](config.ini).

###Known issues

I'm a Mac user and I had these problems:
* It can be that you have to use `sudo` to install pip packages
* `Gevent` can have an issue at installation and I solved it with `CFLAGS='-std=c99' pip install gevent` and it works (with a lot of warnings).
