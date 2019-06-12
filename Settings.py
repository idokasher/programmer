import json

class Settings:

    def __init__(self):
        self.settingsData = {}

    def load(self, filename = "settings.json"):
        with open(filename, 'rt') as json_file:  
            self.settingsData = json.load(json_file)

    def getConfigurations(self):
        return self.settingsData['configurations']

    def getParamValues(self, param_name):
        return sorted(Settings.getElement(self.settingsData['param_values'], param_name))

    def getGeneralSettings(self):
        return self.settingsData['general']

    def getElement(configuration, element):
        try:
            return configuration[element]
        except:
            return ''
        
    def getListElement(configuration, element):
        try:
            return configuration[element]
        except:
            return []
