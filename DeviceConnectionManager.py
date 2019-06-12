from PyQt5.QtCore import QAbstractListModel, QStringListModel, Qt, QObject

from DeviceConnection import DeviceConnection

class DeviceConnectionListModel(QAbstractListModel):

    DeviceConnectionRole = Qt.UserRole + 1

    def __init__(self, connectionsList):
        super(DeviceConnectionListModel, self).__init__()
        self.connectionsList = connectionsList

    def rowCount(self, parent = None):
        return len(self.connectionsList)

    def data(self, index, role):
        if (role == Qt.DisplayRole):
            return self.connectionsList[index.row()].name()
        elif (role == self.DeviceConnectionRole):
            return self.connectionsList[index.row()]

class DeviceConnectionManager(QObject):

    def __init__(self, parent, configurations, workareaDirectory):
        super(DeviceConnectionManager, self).__init__(parent)
        
        self.populateConnections(configurations, workareaDirectory)
        self.currentConnection = self.model.data(self.model.index(0, 0),
                                                 DeviceConnectionListModel.DeviceConnectionRole)

    def setConnection(self, connection):
        self.currentConnection = connection
        
    def getCurrentConnection(self):
        return self.currentConnection

    def populateConnections(self, configurations, workareaDirectory):
        connections = []

        for config in configurations:        
            connection = DeviceConnection(self, config, workareaDirectory)
            connections.append(connection)

        self.model = DeviceConnectionListModel(connections)

    def getModel(self):
        return self.model
