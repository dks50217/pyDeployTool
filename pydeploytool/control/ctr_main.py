from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QDir 
from pydeploytool.gui.gui import Ui_window
from pydeploytool.util.util import MyUtil
from pydeploytool.control.thread_exec_deploy import Thread_Exec_Deploy
from pydeploytool.control.thread_cancel_deploy import Thread_Cancel_Deploy
from pydeploytool.model.param_deployer import Param_Deployer
from pydeploytool.gui.file_dialog import FileDialog
from pathlib import Path
from os import walk
from os.path import join
import os
import re
import sys
import datetime


class Ctr_Main():
    def __init__(self):
        app = QtWidgets.QApplication(sys.argv)
        window = QtWidgets.QMainWindow()
        self.objGUI = Ui_window()
        self.objGUI.setupUi(window)
        self.__initGUI()
        window.setFixedSize(window.size())
        window.show()
        sys.exit(app.exec_())

    def __initGUI(self):
        self.__listenerProgress("", 0)
        #userHome = Path.home()
        #pathOutputFolder = userHome / 'inetpub' / 'wwwroot'
        pathOutputFolder = r'C:\Users\User\Desktop\output'

        if not os.path.exists(pathOutputFolder):
            os.makedirs(pathOutputFolder)
            
        self.objGUI.qleOutputFolder.setText(str(pathOutputFolder))

        self.objGUI.bRemoveFile.setEnabled(False)
        
        self.objGUI.bCancel.hide()

        #button listeners
        self.objGUI.bConvert.clicked.connect(self.__listenerBExec)
        self.objGUI.bCancel.clicked.connect(self.__listenerBCancel)
        self.objGUI.bRemoveFile.clicked.connect(self.__listenerBRemove)
        self.objGUI.bSelectOutputFolder.clicked.connect(self.__listenerBSelectOuputFolder)
        self.objGUI.bOpenOutputFolder.clicked.connect(self.__listenerBOpenOutputFolder)
        self.objGUI.bSelectMedia.clicked.connect(self.__listenerBSelectMedia)
        self.objGUI.actionLicense.triggered.connect(self.__listenerBLicense)
        self.objGUI.actionAbout_pyTranscriber.triggered.connect(self.__listenerBAboutpyTranscriber)

        self.objGUI.bConvert.setEnabled(True)
        self.objGUI.bRemoveFile.setEnabled(True)

    def __resetGUIAfterSuccess(self):
        self.__resetGUIAfterCancel()

        self.objGUI.qlwListFilesSelected.clear()
        self.objGUI.bConvert.setEnabled(False)
        self.objGUI.bRemoveFile.setEnabled(False)

    def __resetGUIAfterCancel(self):

        self.__resetProgressBar()

        self.objGUI.bSelectMedia.setEnabled(True)
        self.objGUI.bSelectOutputFolder.setEnabled(True)
        self.objGUI.cbSelectLang.setEnabled(True)
        self.objGUI.chbxOpenOutputFilesAuto.setEnabled(True)

        self.objGUI.bCancel.hide()
        self.objGUI.bConvert.setEnabled(True)
        self.objGUI.bRemoveFile.setEnabled(True)

    def __lockButtonsDuringOperation(self):
        self.objGUI.bConvert.setEnabled(False)
        self.objGUI.bRemoveFile.setEnabled(False)
        self.objGUI.bSelectMedia.setEnabled(False)
        self.objGUI.bSelectOutputFolder.setEnabled(False)
        self.objGUI.cbSelectLang.setEnabled(False)
        self.objGUI.chbxOpenOutputFilesAuto.setEnabled(False)
        QtCore.QCoreApplication.processEvents()

    def __listenerProgress(self, str, percent):
        self.objGUI.labelCurrentOperation.setText(str)
        self.objGUI.progressBar.setProperty("value", percent)
        QtCore.QCoreApplication.processEvents()

    def __setProgressBarIndefinite(self):
        self.objGUI.progressBar.setMinimum(0)
        self.objGUI.progressBar.setMaximum(0)
        self.objGUI.progressBar.setValue(0)

    def __resetProgressBar(self):
        self.objGUI.progressBar.setMinimum(0)
        self.objGUI.progressBar.setMaximum(100)
        self.objGUI.progressBar.setValue(0)
        self.__listenerProgress("", 0)

    def __updateProgressFileYofN(self, str):
        self.objGUI.labelProgressFileIndex.setText(str)
        QtCore.QCoreApplication.processEvents()

    def __listenerBSelectOuputFolder(self):
        fSelectDir = QFileDialog.getExistingDirectory(self.objGUI.centralwidget)
        if fSelectDir:
            self.objGUI.qleOutputFolder.setText(fSelectDir)

    def __listenerBSelectMedia(self):
        file_dialog = FileDialog()
        files, _ = file_dialog.getOpenFileNames(self.objGUI.centralwidget, "選擇換版資料夾", "","All Files (*)")
        print(files)
        
        #options = QFileDialog.Options()
        # options = QFileDialog.DontUseNativeDialog
        # files, _ = QFileDialog.getOpenFileNames(self.objGUI.centralwidget, "選擇換版資料夾", "","All Files (*)")

        # if files:
        #     self.objGUI.qlwListFilesSelected.addItems(files)
        #     self.objGUI.bConvert.setEnabled(True)
        #     self.objGUI.bRemoveFile.setEnabled(True)


    def __listenerBExec(self):
        if not MyUtil.is_internet_connected():
            self.__showErrorMessage("必須要有網路連線!")
        else:
            #extracts the two letter lang_code from the string on language selection
            #selectedLanguage = self.objGUI.cbSelectLang.currentText()
            #indexSpace = selectedLanguage.index(" ")
            #langCode = selectedLanguage[:indexSpace]

            listFiles = []

            for i in range(self.objGUI.qlwListFilesSelected.count()):
                filePath = str(self.objGUI.qlwListFilesSelected.item(i).text()) 
                listFiles.append(filePath)

            outputFolder = self.objGUI.qleOutputFolder.text()

            if self.objGUI.chbxOpenOutputFilesAuto.checkState() == Qt.Checked:
                boolOpenOutputFilesAuto = True
            else:
                boolOpenOutputFilesAuto = False

            objParamDeploy = Param_Deployer(listFiles, outputFolder, boolOpenOutputFilesAuto)

            #execute the main process in separate thread to avoid gui lock
            self.thread_exec = Thread_Exec_Deploy(objParamDeploy)

            #connect signals from work thread to gui controls
            self.thread_exec.signalLockGUI.connect(self.__lockButtonsDuringOperation)
            self.thread_exec.signalResetGUIAfterSuccess.connect(self.__resetGUIAfterSuccess)
            self.thread_exec.signalResetGUIAfterCancel.connect(self.__resetGUIAfterCancel)
            self.thread_exec.signalProgress.connect(self.__listenerProgress)
            self.thread_exec.signalProgressFileYofN.connect(self.__updateProgressFileYofN)
            self.thread_exec.signalErrorMsg.connect(self.__showErrorMessage)
            self.thread_exec.signalFinished.connect(self.__finishProcess)

            self.thread_exec.start()

            #Show the cancel button
            self.objGUI.bCancel.show()
            self.objGUI.bCancel.setEnabled(True)

    def __listenerBCancel(self):
        self.objGUI.bCancel.setEnabled(False)
        self.thread_cancel = Thread_Cancel_Deploy(self.thread_exec)

        if self.thread_exec and self.thread_exec.isRunning():
            self.__listenerProgress("Cancelling", 0)
            self.__setProgressBarIndefinite()
            self.__updateProgressFileYofN("")
            self.thread_cancel.signalTerminated.connect(self.__resetGUIAfterCancel)
            self.thread_cancel.start()
            self.thread_exec = None

    def __listenerBRemove(self):
        indexSelected = self.objGUI.qlwListFilesSelected.currentRow()
        if indexSelected >= 0:
            self.objGUI.qlwListFilesSelected.takeItem(indexSelected)

        if self.objGUI.qlwListFilesSelected.count() == 0:
            self.objGUI.bRemoveFile.setEnabled(False)
            self.objGUI.bConvert.setEnabled(False)

    def __listenerBOpenOutputFolder(self):
        pathOutputFolder = Path(self.objGUI.qleOutputFolder.text())

        #if folder exists and is valid directory
        if os.path.exists(pathOutputFolder) and os.path.isdir(pathOutputFolder):
            MyUtil.open_file(pathOutputFolder)
        else:
            self.__showErrorMessage("Error! Invalid output folder.")

    def __listenerBLicense(self):
        self.__showInfoMessage("","測試")

    def __listenerBAboutpyTranscriber(self):
        self.__showInfoMessage("","測試")


    def __showInfoMessage(self, info_msg, title):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setWindowTitle(title)
        msg.setText(info_msg)
        msg.exec()

    def __showErrorMessage(self, errorMsg):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)

        msg.setWindowTitle("Error!")
        msg.setText(errorMsg)
        msg.exec()

    def __finishProcess(self):
        sys.exit()