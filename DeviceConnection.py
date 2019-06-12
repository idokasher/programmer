import os
import sys
import subprocess

from PyQt5.QtCore import QThread, pyqtSignal, QObject

from Settings import Settings

class Worker(QObject):

    finished = pyqtSignal(int)
    output   = pyqtSignal(str)
    
    def __init__(self, cmds):
        super(QObject, self).__init__()
        self.cmds = cmds

    def doWork(self):
        try:
            for cmd in self.cmds:
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
                for line in iter(p.stdout.readline, b''):
                    self.output.emit((str(line.strip(), 'utf-8')))
                p.communicate()
                retcode = p.returncode
                if (retcode != 0): break
        except Exception as e:
            print(e)
            retcode = 1

        # Command execution done, now inform the main thread with the output
        self.finished.emit(retcode)

class DeviceConnection(QObject):

    def __init__(self, parent, configuration, workarea):
        super(DeviceConnection, self).__init__(parent)
        
        self.deviceName         = Settings.getElement(configuration, 'device_name')
        self.repositoryName     = Settings.getElement(configuration, 'repository_name')
        self.repositoryUrl      = Settings.getElement(configuration, 'repository_url')
        self.buildCmd           = Settings.getElement(configuration, 'build_cmd')
        self.programCmd         = Settings.getElement(configuration, 'program_cmd')
        self.reposWorkDir       = Settings.getElement(configuration, 'repository_work_dir')
        self.masterBranch       = Settings.getElement(configuration, 'master_branch')
        self.buildParams        = Settings.getListElement(configuration, 'build_params')

        self.workareaDirectory  =  workarea

        self.repositorySuffix   = "work"
        
        self.currentCommitHash  = None

        self.workerThread       = None
        self.workerObject       = None

    def name(self):
        return self.deviceName

    def getBuildParameters(self):
        return self.buildParams

    def str(self):
        textElements = ["Repository : %s" % self.repositoryName,
                        "Location   : %s" % self.getRepositoryPath(),
                        "Build      : %s" % self.buildCmd,
                        "Program    : %s" % self.programCmd]
        text = '\n'.join(textElements)
        return text

    def send_os_command(self, command):
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        stdout_data, stderr_data = p.communicate()
        retcode = p.returncode
        if (retcode == 0 or stdout_data):
            raw_data = str(stdout_data, 'utf-8')
            raw_data_list = raw_data.split('\n')
            return (retcode, raw_data_list)
        else:
            if stderr_data:
                return (retcode, [str(stderr_data, 'utf-8')])
            else:
                return (retcode, ["None"])

    def getRepositoryPath(self):
        reposFullname = self.getRepositoryFullname()
        reposPath = os.path.join(self.workareaDirectory, reposFullname)
        return reposPath

    def getRepositoryFullname(self):
        reposFullname  = "%s.%s" % (self.repositoryName, self.repositorySuffix)
        return reposFullname

    def removeRepository(self, finishedSlot, appendLineSlot):
        reposFullname = self.getRepositoryFullname()

        cmds = ["cd %s && rm -rf %s" % (self.workareaDirectory, reposFullname)]

        self.runCommands(cmds, finishedSlot, appendLineSlot)
    
    def updateRepository(self, finishedSlot, appendLineSlot):
        # If repository does not exist, create one, if it does, just get latest (remember to update submodule)
        reposPath     = self.getRepositoryPath()
        reposFullname = self.getRepositoryFullname()

        if (os.path.exists(reposPath)):
            cmds = ["cd %s && git checkout %s && git pull && git submodule update && git checkout " % (reposPath, self.masterBranch)]
        else:
            cmds = ["cd %s && git clone --recurse-submodules %s %s" % (self.workareaDirectory, self.repositoryUrl, reposFullname)]

        self.runCommands(cmds, finishedSlot, appendLineSlot)

    def getActiveBranch(self):
        reposPath = self.getRepositoryPath()
        
        if (os.path.exists(reposPath)):    
            cmd = "cd %s && git branch -a | grep \* | cut -d ' ' -f2" % reposPath
            retcode, output = self.send_os_command(cmd)
            if (retcode == 0):
                return output

    def getCurrentLabels(self):
        reposPath = self.getRepositoryPath()
        
        if (os.path.exists(reposPath)):    
            cmd = "cd %s && git tag" % reposPath
            retcode, output = self.send_os_command(cmd)
            if (retcode == 0):
                labels = []
                labels.append('master')
                for line in output:
                    if (len(line) == 0): continue
                    labels.append(line.strip())
                return labels

        return []

    def getCurrentBranches(self):
        reposPath = self.getRepositoryPath()
        
        if (os.path.exists(reposPath)):    
            cmd = "cd %s && git branch -a" % reposPath
            retcode, output = self.send_os_command(cmd)
            if (retcode == 0):
                branches = []
                for line in output:
                    line = line[2:].strip()
                    if (len(line) == 0): continue
                    branches.append(line)
                return branches

        return []
    
    def buildImage(self, checkout, buildParamsValues, finishedSlot, appendLineSlot):        
        reposWorkPath = os.path.join(self.getRepositoryPath(), self.reposWorkDir)

        if (buildParamsValues != None):
            buildParamsList = []

            for idx, value in enumerate(buildParamsValues):
                buildParam = self.buildParams[idx]
                paramCommand   = buildParam['command']

                if (value == ''): continue
                
                if (paramCommand != ''):
                    buildParamsList.append("%s %s" % (paramCommand, value))
                else:
                    buildParamsList.append("%s" % value)
        
            buildParamsStr = ' '.join(buildParamsList)

        else:
            buildParamsStr = ''

        cmds = []
        cmds.append("cd %s && git checkout %s && git submodule update" % (reposWorkPath, checkout))
        cmds.append("cd %s && %s %s" % (reposWorkPath, self.buildCmd, buildParamsStr))

        self.runCommands(cmds, finishedSlot, appendLineSlot)
        
    def programImage(self, finishedSlot, appendLineSlot):
        reposWorkPath = os.path.join(self.getRepositoryPath(), self.reposWorkDir)

        cmds = ["cd %s && %s" % (reposWorkPath, self.programCmd)]
        self.runCommands(cmds, finishedSlot, appendLineSlot)

    def runCommands(self, cmds, finishedSlot = None, outputSlot = None):
        self.workerThread = QThread()
        self.workerObject = Worker(cmds)
        self.workerObject.moveToThread(self.workerThread)
        self.workerThread.started.connect(self.workerObject.doWork)
        if (finishedSlot): self.workerObject.finished.connect(finishedSlot)
        if (outputSlot):   self.workerObject.output.connect(outputSlot)
        self.workerObject.finished.connect(self.commandDone)
        self.workerThread.start()

    def commandDone(self):
        self.workerThread.quit()
        self.workerThread.wait()
        self.workerThread = None
        self.workerObject = None
        
    def cancelCommand(self):
        # TODO find a way to stop the thread
        try:
            self.workerThread.quit()
        except Exception:
            pass
