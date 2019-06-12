# Imports
import sys
import os

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDir, QModelIndex, Qt, QItemSelectionModel
from PyQt5 import QtSql, QtCore
from PyQt5.QtGui import QIcon, QColor, QFont

from DeviceConnectionManager import DeviceConnectionManager, DeviceConnectionListModel
from DeviceConnection import DeviceConnection
from Settings import Settings

class App(QMainWindow):

    def __init__(self, parent = None):
        super(App, self).__init__(parent)
        
        self.title  = "Programmer"
        self.left   = 0
        self.top    = 0
        self.width  = 900
        self.height = 800

        self.fontSize = 12

        self.settings = Settings()
        self.settings.load('settings.json')

        self.successAction = None
        self.successMessage = None
        self.failureMessage = None

        self.workareaDirectory = self.settings.getGeneralSettings()['workarea']
        if (not os.path.exists(self.workareaDirectory)):
            os.makedirs(self.workareaDirectory)

        self.deviceConnectionManager = DeviceConnectionManager(self, self.settings.getConfigurations(), self.workareaDirectory)
        
        self.initUI()

        self.updateConnection()

    def appendConsoleMessages(self, text):
        self.logTextEdit.append(text)

    ### This set of functions should invoke a GUI-independent functionality layer
    def removeRepository(self):
        reply = QMessageBox.question(self, "Programmer", "Are you sure you want to remove the repository?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if (reply == QMessageBox.No):
            return
        
        self.setEnabled(False)
        self.successAction = lambda : self.populateLabels()
        self.failureAction = lambda : self.commandFailureMessage("Error removing repository.\nPlease check console logs.\nYou can try to remove it manually from %s." % "Where am I?")
        self.deviceConnectionManager.getCurrentConnection().removeRepository(self.commandFinished,
                                                                             self.addLogLine)
        
    def updateRepository(self):
        self.setEnabled(False)
        self.successAction = lambda : self.populateLabels()
        self.failureAction = lambda : self.commandFailureMessage("Failed updating repository.\nPlease check console logs.\n")
        self.deviceConnectionManager.getCurrentConnection().updateRepository(self.commandFinished,
                                                                             self.addLogLine)

    def checkoutLabel(self):
        reposLabel = self.reposLabelsSelectionComboBox.currentText()
        self.successAction = lambda : self.null
        self.failureAction = lambda : self.commandFailureMessage("Failed checking out label.\nPlease check console logs.\n")
        self.deviceConnectionManager.getCurrentConnection().checkoutLabel(reposLabel,
                                                                          self.commandFinished,
                                                                          self.addLogLine)

    def checkoutBranch(self):
        reposBranch = self.reposBranchSelectionComboBox.currentText()
        self.successAction = lambda : self.populateLabels()
        self.failureAction = lambda : self.commandFailureMessage("Failed checking out branch.\nPlease check console logs.\n")
        self.deviceConnectionManager.getCurrentConnection().checkoutBranch(reposBranch,
                                                                          self.commandFinished,
                                                                          self.addLogLine)        
        
    def populateLabels(self):
        labels = self.deviceConnectionManager.getCurrentConnection().getCurrentLabels()
        self.reposLabelsSelectionComboBox.clear()
        self.reposLabelsSelectionComboBox.addItems(labels)

    def populateBranches(self):
        branches = self.deviceConnectionManager.getCurrentConnection().getCurrentBranches()
        self.reposBranchSelectionComboBox.clear()
        self.reposBranchSelectionComboBox.addItems(branches)

    def getBuildParametersValues(self):
        paramsWidget = self.buildParamsWidget        
        layout = paramsWidget.layout()

        values = []
        for i in range(layout.count()):
            layoutItem = layout.itemAt(i)
            widget     = layoutItem.widget()
            widgetType = type(widget)
            if (widgetType == QComboBox):
                values.append(widget.currentText())
            elif (widgetType == QLineEdit):
                values.append(widget.text())

        return values

    def buildImage(self):
        # Retrieve selections
        if (self.labelRadioButton.isChecked()):
            checkout = self.reposLabelsSelectionComboBox.currentText()
        elif (self.branchRadioButton.isChecked()):
            checkout = self.reposBranchSelectionComboBox.currentText()
        elif (self.commitRadioButton.isChecked()):
            checkout = self.commitLineEdit.text()

        self.setEnabled(False)
        self.successAction = lambda : self.commandSuccessMessage("Build completed successfully.")
        self.failureAction = lambda : self.commandFailureMessage("Error while building the image.\nPlease check console logs.")
        self.deviceConnectionManager.getCurrentConnection().buildImage(checkout,
                                                                       self.getBuildParametersValues(),
                                                                       self.commandFinished,
                                                                       self.addLogLine)
                        
    def programImage(self):
        self.setEnabled(False)
        self.successAction = lambda : self.commandSuccessMessage("Image updated successfully.")
        self.failureAcyion = lambda : self.commandFailureMessage("Error while programming the image.\nPlease check console logs.")
        self.deviceConnectionManager.getCurrentConnection().programImage(self.commandFinished,
                                                                         self.addLogLine)

    def cancelCommand(self):
        QMessageBox.information(self, "Programmer", "Cancelling an operation is not supported yet")
        # self.deviceConnectionManager.getCurrentConnection().cancelCommand()
            
    def updateConnection(self):
        connection = self.deviceSelectionComboBox.currentData(DeviceConnectionListModel.DeviceConnectionRole)
        self.deviceConnectionManager.setConnection(connection)
        self.infoTextEdit.setText(connection.str())
        self.populateLabels()
        self.populateBranches()
        self.updateUI_buildParams()

    def setEnabled(self, value):
        self.updateRepositoryButton.setEnabled(value)
        self.removeRepositoryButton.setEnabled(value)
        self.buildButton.setEnabled(value)
        self.programButton.setEnabled(value)
        self.deviceSelectionComboBox.setEnabled(value)
        self.reposBranchSelectionComboBox.setEnabled(value)
        self.reposLabelsSelectionComboBox.setEnabled(value)
        self.commitLineEdit.setEnabled(value)
        self.reposRadioGroupBox.setEnabled(value)

        for i in range(self.buildParamsWidget.layout().count()):
            self.buildParamsWidget.layout().itemAt(i).widget().setEnabled(value)

    def commandSuccessMessage(self, message):
        QMessageBox.information(self, "Programmer", message)

    def commandFailureMessage(self, message):
        QMessageBox.critical(self, "Programmer", message)

    def null(self):
        pass
        
    @QtCore.pyqtSlot(int)
    def commandFinished(self, retcode):
        if (retcode == 0):
            self.successAction()
        else:
            self.failureAction()            
        
        self.setEnabled(True)

    @QtCore.pyqtSlot(str)
    def addLogLine(self, line):
        self.logTextEdit.append(line)

    def on_updateRepository_click(self):
        self.updateRepository()

    def on_removeRepository_click(self):
        self.removeRepository()
        
    def on_buildButton_click(self):
        self.buildImage()

    def on_programButton_click(self):
        self.programImage()

    def on_cancelButton_click(self):
        self.cancelCommand()

    def on_clearLogsButton_click(self):
        self.logTextEdit.clear()

    def updateUI_buildParams(self):
        widget = self.buildParamsWidget
        layout = QHBoxLayout()

        # Replace the layout of the widget
        if (self.buildParamsWidget.layout() != None):
            QWidget().setLayout(self.buildParamsWidget.layout())
        self.buildParamsWidget.setLayout(layout)

        currentConnection = self.deviceConnectionManager.getCurrentConnection()
        buildParams       = currentConnection.getBuildParameters()

        for buildParam in buildParams:
            paramName      = buildParam['name']
            paramValueName = buildParam['value_name']
            if (len(paramValueName) == 0):
                lineEdit = QLineEdit()
                lineEdit.setPlaceholderText(paramName)
                lineEdit.setClearButtonEnabled(True)
                layout.addWidget(lineEdit)
            else:
                paramValues = self.settings.getParamValues(buildParam['value_name'])
                comboBox = QComboBox()
                comboBox.addItems(paramValues)
                layout.addWidget(comboBox)

    def initUI_centralWidget(self):
        self.layout = QVBoxLayout()

        # Device selection
        tempWidget = QWidget()
        tempLayout = QHBoxLayout()
        tempWidget.setLayout(tempLayout)
        self.layout.addWidget(tempWidget)

        self.deviceSelectionComboBox = QComboBox()
        self.deviceSelectionComboBox.setModel(self.deviceConnectionManager.getModel())
        self.deviceSelectionComboBox.currentIndexChanged.connect(self.updateConnection)
        tempLayout.addWidget(self.deviceSelectionComboBox)

        # Build parameters
        self.buildParamsWidget = QWidget()
        self.layout.addWidget(self.buildParamsWidget)

        # Repository control and selection
        tempWidget = QWidget()
        tempLayout = QHBoxLayout()
        tempWidget.setLayout(tempLayout)
        self.layout.addWidget(tempWidget)

        self.reposRadioGroupBox = QGroupBox()

        self.labelRadioButton  = QRadioButton("Label")
        self.reposLabelsSelectionComboBox = QComboBox()

        self.branchRadioButton = QRadioButton("Branch")
        self.reposBranchSelectionComboBox = QComboBox()

        self.commitRadioButton = QRadioButton("Commit")
        self.commitLineEdit = QLineEdit()
        self.commitLineEdit.setClearButtonEnabled(True)

        self.labelRadioButton.setChecked(True)

        tempRadioBoxLayout = QGridLayout()
        tempRadioBoxLayout.addWidget(self.labelRadioButton, 0, 0)
        tempRadioBoxLayout.addWidget(self.reposLabelsSelectionComboBox, 0, 1)
        
        tempRadioBoxLayout.addWidget(self.branchRadioButton, 1, 0)
        tempRadioBoxLayout.addWidget(self.reposBranchSelectionComboBox, 1, 1)
        
        tempRadioBoxLayout.addWidget(self.commitRadioButton, 2, 0)
        tempRadioBoxLayout.addWidget(self.commitLineEdit, 2, 1)
        
        self.reposRadioGroupBox.setLayout(tempRadioBoxLayout)

        tempLayout.addWidget(self.reposRadioGroupBox)

        tempWidget = QWidget()
        tempLayout = QHBoxLayout()
        tempWidget.setLayout(tempLayout)
        self.layout.addWidget(tempWidget)

        self.updateRepositoryButton = QPushButton("Update repository")
        self.updateRepositoryButton.clicked.connect(self.on_updateRepository_click)
        tempLayout.addWidget(self.updateRepositoryButton)

        self.removeRepositoryButton = QPushButton("Remove repository")
        self.removeRepositoryButton.clicked.connect(self.on_removeRepository_click)
        tempLayout.addWidget(self.removeRepositoryButton)
        
        # Build and program
        tempWidget = QWidget()
        tempLayout = QHBoxLayout()
        tempWidget.setLayout(tempLayout)
        self.layout.addWidget(tempWidget)

        self.buildButton = QPushButton("Build")
        self.buildButton.clicked.connect(self.on_buildButton_click)
        tempLayout.addWidget(self.buildButton)

        self.programButton = QPushButton("Program")
        self.programButton.clicked.connect(self.on_programButton_click)
        tempLayout.addWidget(self.programButton)

        self.cancelButton = QPushButton("Cancel", self)
        self.cancelButton.clicked.connect(self.on_cancelButton_click)
        tempLayout.addWidget(self.cancelButton)

        self.clearLogsButton = QPushButton("Clear Logs", self)
        self.clearLogsButton.clicked.connect(self.on_clearLogsButton_click)
        tempLayout.addWidget(self.clearLogsButton)
        
        self.textEditSplitter = QSplitter(Qt.Vertical, self)
        self.layout.addWidget(self.textEditSplitter)
        
        infoFont = QFont("Courier New", self.fontSize, QFont.Normal);
        infoFont.setStyleHint(QFont.Courier)

        self.infoTextEdit = QTextEdit()
        self.infoTextEdit.setFont(infoFont)
        self.infoTextEdit.setReadOnly(True)
        self.infoTextEdit.append("Information:")
        self.textEditSplitter.addWidget(self.infoTextEdit)        

        logFont = QFont("Courier New", self.fontSize, QFont.Normal);
        logFont.setStyleHint(QFont.Courier)

        self.logTextEdit = QTextEdit()
        self.logTextEdit.setFont(logFont)
        self.logTextEdit.setReadOnly(True)
        self.textEditSplitter.addWidget(self.logTextEdit)

        self.textEditSplitter.setStretchFactor(0, 0)
        self.textEditSplitter.setStretchFactor(1, 1)
                
        widget = QWidget()
        widget.setLayout(self.layout)
        return widget

    def initUI(self):

        self.setCentralWidget(self.initUI_centralWidget())
        
        # Main window settings
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()
        
        
if (__name__ == "__main__"):    

    app = QApplication(sys.argv)

    ex = App()
    
    sys.exit(app.exec_())

