import json

class MyJson:
    
    def __init__(self, json_path):
        self.json_path = json_path
    
    # open the json file
    def open_json(self):
        with open (self.json_path, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)

    # dump json dict
    def dump(self, json_dict:dict):
        json.dump(json_dict, open(self.json_path,'w', encoding='utf-8'), indent=4)
        
lang_path = "lang.json"
lang_json = MyJson(lang_path)
