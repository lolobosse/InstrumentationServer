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

from flask import Flask, render_template, copy_current_request_context
import ntpath
from subprocess import call
import os
from thread import start_new_thread
from flask_socketio import SocketIO, emit
import socketio
import time
from threading import Thread


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

app = Flask(__name__)
#app.debug = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)

# Run that in the InstrumentationPEP Repository

JavaPath = "/Library/Java/JavaVirtualMachines/jdk1.7.0_79.jdk/Contents/Home/bin/java";
EncodingOption = "-Dfile.encoding=UTF-8"
Classpath = "-classpath"
InstrumentationPepDirectory = "/Users/laurentmeyer/Documents/Uni/3.Semester/DroidForce/Instrumentation-PEP/"
NeededFromPEP = ["bin", "libs/android.jar", "libs/axml-2.0.jar", "libs/slf4j-api-1.7.5.jar",
                 "libs/slf4j-simple-1.7.5.jar"]
SootDirectory = "/Users/laurentmeyer/Documents/Uni/3.Semester/soot/"
NeededFromSoot = ["testclasses", "classes", "libs/polyglot.jar", "libs/AXMLPrinter2.jar", "libs/hamcrest-all-1.3.jar",
                  "libs/junit-4.11.jar", "libs/asm-debug-all-5.0.3.jar", "libs/cglib-nodep-2.2.2.jar",
                  "libs/java_cup.jar", "libs/javassist-3.18.2-GA.jar", "libs/mockito-all-1.10.8.jar",
                  "libs/powermock-mockito-1.6.1-full.jar", "libs/jboss-common-core-2.5.0.Final.jar",
                  "libs/dexlib2-2.1.0-dev.jar", "libs/util-2.1.0-dev.jar"]
JasminDirectory = "/Users/laurentmeyer/Documents/Uni/3.Semester/jasmin/"
NeededFromJasmin = ["classes", "libs/java_cup.jar"]
HerosDirectory = "/Users/laurentmeyer/Documents/Uni/3.Semester/heros/"
NeededFromHeros = ["target/classes", "target/test-classes", "slf4j-api-1.7.5.jar", "slf4j-simple-1.7.5.jar",
                   "junit.jar", "org.hamcrest.core_1.3.0.jar", "mockito-all-1.9.5.jar", "guava-18.0.jar"]
PathToFunctional = "/Users/laurentmeyer/.m2/repository/org/functionaljava/functionaljava/4.2/functionaljava-4.2.jar"
PathSootInfoflow = "/Users/laurentmeyer/Documents/Uni/3.Semester/soot-infoflow/"
NeededFromSootInfoflow = ["bin", "lib/cos.jar", "lib/j2ee.jar", "lib/slf4j-api-1.7.5.jar", "lib/slf4j-simple-1.7.5.jar"]
PathSootInfoflowAndroid = "/Users/laurentmeyer/Documents/Uni/3.Semester/soot-infoflow-android/"
NeededFromSootInfoflowAndroid = ["bin", "lib/AXMLPrinter2.jar", "lib/axml-2.0.jar"]

MainMethodName = "de.ecspride.Main"

AndroidPlatformsCommand = "-androidPlatforms"
PlatformsPath = "~/ASDK/platforms"

sourceFileCommand = "-sourceFile"
sourceFilePath = "./files/catSources_Short.txt"

sinkFileCommand = "-sinkFile"
sinkFilePath = "./files/catSinks_Short.txt"

taintWrapperCommand = "-taintWrapper"
taintWrapperPath = "./files/EasyTaintWrapperSource.txt"

apkFileCommand = "-apkFile"
apkFilePath = "/Users/laurentmeyer/NetworkOutput/app-debug.apk"
# Get the app-debug.apk to be able to retrieve the path to the newly created apk
apkName = path_leaf(apkFilePath)

outputDirectoryCommand = "-o"
outputDirectoryPath = "./sootOutput/"

androidJarCommand = "-androidJar"
androidJarPath = "./libs/android.jar"

# Check if jarsigner is present
jarsigner = "jarsigner"
keystoreOption = "-keystore"
keyStorePath = "~/keystore"
storePassOption = "-storepass"
storePass = "laurent"
signedJarOption = "-signedJar"
alias = "mykeystore"
outputDirectoryAndFileName = outputDirectoryPath+"apk-instrumented-signed.apk"

def createStringFromList(path, subelements, addTwoPointsAtTheEnd=True):
    toBeReturned = ':'.join([path + a for a in subelements])
    if addTwoPointsAtTheEnd:
        toBeReturned += ":"
    return toBeReturned


def createClassPath():
    return createStringFromList(
        InstrumentationPepDirectory, NeededFromPEP) + createStringFromList(SootDirectory,
                                                                           NeededFromSoot) + createStringFromList(
        JasminDirectory, NeededFromJasmin) + createStringFromList(HerosDirectory,
                                                                  NeededFromHeros) + PathToFunctional + ":" + createStringFromList(
        PathSootInfoflow, NeededFromSootInfoflow) + createStringFromList(PathSootInfoflowAndroid, NeededFromSootInfoflowAndroid, False)


def createCommand():
        commandInstru = " ".join(
            [JavaPath, EncodingOption, Classpath, createClassPath(), MainMethodName, AndroidPlatformsCommand,
             PlatformsPath,
             sourceFileCommand, sourceFilePath, sinkFileCommand, sinkFilePath, taintWrapperCommand, taintWrapperPath,
             apkFileCommand, apkFilePath, outputDirectoryCommand, outputDirectoryPath, androidJarCommand,
             androidJarPath])
        return commandInstru


def createCommandSign():
    return " ".join([jarsigner, keystoreOption, keyStorePath, storePassOption, storePass, signedJarOption,
                     outputDirectoryAndFileName, outputDirectoryPath + apkName, alias])
