import json

settings = {}

settings['general'] = {"workarea" : "repos"}

settings['param_values'] = {}

param_values = {'option1_values_list' : ["value1",
                                         "value2",
                                         "value3",
                                         "value4"]}

settings['param_values'].update(param_values)

build_params = [{"name" : "ComboBox Option",
                 "value_name" : "option1_value_list",
                 "command" : "-o1"},
                {"name" : "FreeText Named Option",
                 "value_name" : "",
                 "command" : "-o2"},
                {"name" : "FreeText Positional Option",
                 "value_name" : "",
                 "command" : ""}]

settings['configurations'] = []
config = {"device_name" : "Programmer",
          "repository_name" : "programmer",
          "repository_url" : "https://github.com/idokasher/programmer.git",
          "repository_work_dir" : "workdir",
          "build_cmd" : "scripts/build.sh",
          "build_params" : build_params,
          "program_cmd" : "scripts/program.sh",
          "master_branch" : "master"}

settings['configurations'].append(config)

with open('settings.json', 'wt') as outfile:  
    json.dump(settings, outfile, indent=4)


