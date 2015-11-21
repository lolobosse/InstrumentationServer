import ntpath
import ConfigParser
import os


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


class CommandBuilder:
    def __init__(self):
        self.Config = ConfigParser.ConfigParser()
        self.Config.read(os.path.dirname(os.path.abspath(__file__))+"/config.ini")
        # Run that in the InstrumentationPEP Repository
        self.JavaPath = self.ConfigSectionMap("Global Java")["javapath"]
        self.EncodingOption = self.ConfigSectionMap("Global Java")["encodingoption"]
        self.Classpath = "-classpath"
        self.InstrumentationPepDirectory = self.ConfigSectionMap("InstrumentationPEP")["instrumentationpepdirectory"]
        self.NeededFromPEP = ["bin", "libs/android.jar", "libs/axml-2.0.jar", "libs/slf4j-api-1.7.5.jar",
                              "libs/slf4j-simple-1.7.5.jar"]
        self.SootDirectory = self.ConfigSectionMap("Soot")["sootdirectory"]
        self.NeededFromSoot = ["testclasses", "classes", "libs/polyglot.jar", "libs/AXMLPrinter2.jar",
                               "libs/hamcrest-all-1.3.jar",
                               "libs/junit-4.11.jar", "libs/asm-debug-all-5.0.3.jar", "libs/cglib-nodep-2.2.2.jar",
                               "libs/java_cup.jar", "libs/javassist-3.18.2-GA.jar", "libs/mockito-all-1.10.8.jar",
                               "libs/powermock-mockito-1.6.1-full.jar", "libs/jboss-common-core-2.5.0.Final.jar",
                               "libs/dexlib2-2.1.0-dev.jar", "libs/util-2.1.0-dev.jar"]
        self.JasminDirectory = self.ConfigSectionMap("Jasmin")["jasmindirectory"]
        self.NeededFromJasmin = ["classes", "libs/java_cup.jar"]
        self.HerosDirectory = self.ConfigSectionMap("Heros")["herosdirectory"]
        self.NeededFromHeros = ["target/classes", "target/test-classes", "slf4j-api-1.7.5.jar",
                                "slf4j-simple-1.7.5.jar",
                                "junit.jar", "org.hamcrest.core_1.3.0.jar", "mockito-all-1.9.5.jar", "guava-18.0.jar"]
        self.PathToFunctional = self.ConfigSectionMap("FunctionalJava")["pathtofunctional"]
        self.PathSootInfoflow = self.ConfigSectionMap("Infoflow")["pathsootinfoflow"]
        self.NeededFromSootInfoflow = ["bin", "lib/cos.jar", "lib/j2ee.jar", "lib/slf4j-api-1.7.5.jar",
                                       "lib/slf4j-simple-1.7.5.jar"]
        self.PathSootInfoflowAndroid = self.ConfigSectionMap("Infoflow Android")["pathsootinfoflowandroid"]
        self.NeededFromSootInfoflowAndroid = ["bin", "lib/AXMLPrinter2.jar", "lib/axml-2.0.jar"]

        self.MainMethodName = "de.ecspride.Main"

        self.AndroidPlatformsCommand = "-androidPlatforms"
        self.PlatformsPath = self.ConfigSectionMap("Android")["platformspath"]

        self.sourceFileCommand = "-sourceFile"
        self.sourceFilePath = self.ConfigSectionMap("Sources and Sinks")["sourcefilepath"]

        self.sinkFileCommand = "-sinkFile"
        self.sinkFilePath = self.ConfigSectionMap("Sources and Sinks")["sinkfilepath"]

        self.taintWrapperCommand = "-taintWrapper"
        self.taintWrapperPath = self.ConfigSectionMap("Sources and Sinks")["taintwrapperpath"]

        self.apkFileCommand = "-apkFile"
        self.apkFilePath = self.ConfigSectionMap("To be instrumented")["apkfilepath"]
        # Get the app-debug.apk to be able to retrieve the path to the newly created apk
        self.apkName = path_leaf(self.apkFilePath)

        self.outputDirectoryCommand = "-o"
        self.outputDirectoryPath = self.ConfigSectionMap("Output")["outputdirectorypath"]

        self.androidJarCommand = "-androidJar"
        self.androidJarPath = self.ConfigSectionMap("Android Jar")["androidjarpath"]

        # Check if jarsigner is present
        self.jarsigner = "jarsigner"
        self.keystoreOption = "-keystore"
        self.keyStorePath = self.ConfigSectionMap("Keystore")["keystorepath"]
        self.storePassOption = "-storepass"
        self.storePass = self.ConfigSectionMap("Keystore")["storepass"]
        self.signedJarOption = "-signedJar"
        self.alias = self.ConfigSectionMap("Keystore")["alias"]
        self.outputDirectoryAndFileName = self.outputDirectoryPath + "apk-instrumented-signed.apk"

    def createStringFromList(self, path, subelements, addTwoPointsAtTheEnd=True):
        toBeReturned = ':'.join([path + a for a in subelements])
        if addTwoPointsAtTheEnd:
            toBeReturned += ":"
        return toBeReturned


    def createClassPath(self):
        return self.createStringFromList(
            self.InstrumentationPepDirectory, self.NeededFromPEP) + self.createStringFromList(self.SootDirectory,
                                                                                              self.NeededFromSoot) + self.createStringFromList(
            self.JasminDirectory, self.NeededFromJasmin) + self.createStringFromList(self.HerosDirectory,
                                                                                     self.NeededFromHeros) + self.PathToFunctional + ":" + self.createStringFromList(
            self.PathSootInfoflow, self.NeededFromSootInfoflow) + self.createStringFromList(
            self.PathSootInfoflowAndroid, self.NeededFromSootInfoflowAndroid, False)


    def createCommand(self):
        commandInstru = " ".join(
            [self.JavaPath, self.EncodingOption, self.Classpath, self.createClassPath(), self.MainMethodName,
             self.AndroidPlatformsCommand,
             self.PlatformsPath,
             self.sourceFileCommand, self.sourceFilePath, self.sinkFileCommand, self.sinkFilePath,
             self.taintWrapperCommand, self.taintWrapperPath,
             self.apkFileCommand, self.apkFilePath, self.outputDirectoryCommand, self.outputDirectoryPath,
             self.androidJarCommand,
             self.androidJarPath])
        return commandInstru


    def createCommandSign(self):
        return " ".join([self.jarsigner, self.keystoreOption, self.keyStorePath, self.storePassOption, self.storePass,
                         self.signedJarOption,
                         self.outputDirectoryAndFileName, self.outputDirectoryPath + self.apkName, self.alias])

    def ConfigSectionMap(self, section):
        dict1 = {}
        options = self.Config.options(section)
        for option in options:
            try:
                dict1[option] = self.Config.get(section, option)
                if dict1[option] == -1:
                    print "skip"
            except:
                print("exception on %s!" % option)
                dict1[option] = None
        return dict1
