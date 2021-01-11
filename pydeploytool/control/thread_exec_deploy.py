from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
from pathlib import Path
from pydeploytool.util.util import MyUtil
from pydeploytool.control.ctr_deploy import Ctr_Deploy
import os


class Thread_Exec_Deploy(QThread):
    signalLockGUI = pyqtSignal()
    signalResetGUIAfterCancel = pyqtSignal()
    signalResetGUIAfterSuccess = pyqtSignal()
    signalProgress = pyqtSignal(str, int)
    signalProgressFileYofN = pyqtSignal(str)
    signalErrorMsg = pyqtSignal(str)

    def __init__(self, objParamDeploy):
        self.objParamDeploy = objParamDeploy
        self.running = True
        QThread.__init__(self)

    def __updateProgressFileYofN(self, currentIndex, countFiles ):
        self.signalProgressFileYofN.emit("File " + str(currentIndex+1) + " of " +str(countFiles))

    def listenerProgress(self, string, percent):
        self.signalProgress.emit(string, percent)

    def __generatePathOutputFile(self, sourceFile):
        base = os.path.basename(sourceFile)
        fileName = os.path.splitext(base)[0]
        pathOutputFolder = Path(self.objParamDeploy.outputFolder)
        outputFileSRT = pathOutputFolder / (fileName + ".xxx")
        return outputFileSRT

    def __runDeployForMedia(self, index, langCode):
        sourceFile = self.objParamDeploy.listFiles[index]
        outputFiles = self.__generatePathOutputFile(sourceFile)
        outputFile = outputFiles[0]

        fOutput = Ctr_Deploy.start_deploy(source_path = sourceFile,
                                    output = outputFile,
                                    listener_progress = self.listenerProgress)
        if not fOutput:
            self.signalErrorMsg.emit("Error! Unable to generate subtitles for file " + sourceFile + ".")
        elif fOutput != -1:
            self.listenerProgress("Finished", 100)

            if self.objParamDeploy.boolOpenOutputFilesAuto:
                print('123')

    def __loopSelectedFiles(self):
        self.signalLockGUI.emit()

        langCode = self.objParamDeploy.langCode

        pathOutputFolder = Path(self.objParamDeploy.outputFolder)

        if not os.path.exists(pathOutputFolder):
            os.mkdir(pathOutputFolder)

        if not os.path.isdir(pathOutputFolder):
            self.signalErrorMsg.emit("Error! Invalid output folder. Please choose another one.")
        else:
            nFiles = len(self.objParamDeploy.listFiles)
            for i in range(nFiles):
                if not Ctr_Deploy.is_operation_canceled():
                    self.__updateProgressFileYofN(i, nFiles)
                    self.__runDeployForMedia(i, langCode)

            if Ctr_Deploy.is_operation_canceled():
                self.signalResetGUIAfterCancel.emit()
            else:
                self.signalResetGUIAfterSuccess.emit()


    def run(self):
        Ctr_Deploy.init()
        self.__loopSelectedFiles()
        self.running = False

    def cancel(self):
       Ctr_Deploy.cancel_operation()
