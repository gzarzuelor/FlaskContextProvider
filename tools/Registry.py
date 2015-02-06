__author__ = 'b.gzr'
import DataManager as DM
import ConfigParser
import requests
import json
import re


class Registry():
    def __init__(self):
        self.path = './etc/Registry/registry.json'
        self.registration_path = './etc/Registry/registry.ini'

    def add_registry_json(self, _type, entity_id_list):
        registry = self.load_registry_json()

        if _type in registry:
            for i in range(len(entity_id_list)):
                if entity_id_list[i] not in registry[_type]:
                    registry[_type].append(entity_id_list[i])
        else:
            registry[_type] = entity_id_list


        with open(self.path, 'w') as jsonfile:
            jregistry = json.dumps(registry)
            jsonfile.write(jregistry)

    def load_registry_json(self):
        try:
            with open(self.path, 'r') as registry_file:
                registry = json.loads(registry_file.read())
            return registry
        except IOError:
            return 0

    def check_entity_registration(self, entity_type, _id):
        entity_list = []
        registry = self.load_registry_json()
        entities = registry[entity_type]
        for i in range(len(entities)):
            pattern_id = "%s$" % _id
            match = re.match(pattern_id, entities[i])
            if match is not None:
                entity_list.append(entities[i])

        return entity_list

    def get_registered_entities(self, cb_url, token=''):
            try:
                url = cb_url+'/v1/registry/discoverContextAvailability'
                if len(token) != 0:
                    headers = {'Content-Type': 'application/json', "X-Auth-Token": token, 'Accept': 'application/json'}
                else:
                    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

                registry = self.load_registry_json()
                payload = DM.Entity()
                reg_id, reg_types, reg_attrb ,reg_attrb_val, reg_attrb_type = self.load_registry_file()

                reg_entities = {}
                for i in range(len(reg_id)):
                    for e in range(len(reg_id[i])):
                        payload.entity_add(reg_id[i][e], reg_types[i])
                    data = json.dumps({'entities': payload.get_entity_list()})
                    response = requests.post(url, headers=headers, data=data)

                    if 'contextRegistrationResponses' in response.json():
                        responses = response.json()['contextRegistrationResponses']
                        for i in range(len(responses)):
                            entities = responses[i]['contextRegistration']['entities']
                            for e in range(len(entities)):
                                reg_entities[reg_types[i]].append(entities[e]['id'])
                    else:
                        reg_entities[reg_types[i]] = None
                    payload.entity_list_purge()
                print reg_entities

            except requests.RequestException as e:
                print "%s" % e.message
                return -1

    def load_registry_file(self):
        config = ConfigParser.ConfigParser()
        config.read(self.registration_path)

        sections = config.sections()
        entity_list = []
        entities_type = []
        attribute_list = []
        attribute_list_values = []
        attribute_list_types = []

        for i in range(len(sections)):
            entity_list.append('')
            entities_type.append('')
            attribute_list.append('')
            attribute_list_values.append('')
            attribute_list_types.append('')
            entity_list[i] =  config.get(sections[i], 'entity_ids').replace(" ","").split(",")
            entities_type[i] =  config.get(sections[i], 'entity_type')
            attribute_list[i] = config.get(sections[i], 'attributes').replace(" ","").split(",")
            attribute_list_values[i] = config.get(sections[i], 'attrib_val').replace(" ","").split(",")
            attribute_list_types[i] = config.get(sections[i], 'attrib_type').replace(" ","").split(",")

        return entity_list, entities_type, attribute_list, attribute_list_values, attribute_list_types

