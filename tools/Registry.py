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

                payload = DM.Entity()
                regs, reg_id, reg_types, reg_attrb, reg_attrb_type = self.load_registry_file()

                for i in range(len(reg_id)):
                    for e in range(len(reg_id[i])):
                        payload.entity_add(reg_id[i][e], reg_types[i])
                    data = json.dumps({'entities': payload.get_entity_list()})
                    response = requests.post(url, headers=headers, data=data)
                    z = 0
                    if 'contextRegistrationResponses' in response.json():
                        responses = response.json()['contextRegistrationResponses']
                        for e in range(len(responses)):
                            entities = responses[e]['contextRegistration']['entities']
                            for t in range(len(entities)):
                                if entities[t]['id'] not in reg_id[i]:
                                    z += 1
                            attributes = responses[e]['contextRegistration']['attributes']
                            for t in range(len(attributes)):
                                if (attributes[t]['name'] not in reg_attrb[i]
                                        or attributes[t]['type'] not in reg_attrb_type[i]):
                                    z += 1
                        if z != 0:
                            print "%s has changed at registry.ini update registration, (registration ID)" % regs[i]
                    else:
                        print "%s it's not registered, new registry or expired one?" % regs[i]
                    payload.entity_list_purge()


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
        attribute_list_types = []

        for i in range(len(sections)):
            entity_list.append('')
            entities_type.append('')
            attribute_list.append('')
            attribute_list_types.append('')
            entity_list[i] = config.get(sections[i], 'entity_ids').replace(" ", "").split(",")
            entities_type[i] = config.get(sections[i], 'entity_type')
            attribute_list[i] = config.get(sections[i], 'attributes').replace(" ", "").split(",")
            attribute_list_types[i] = config.get(sections[i], 'attrb_type').replace(" ", "").split(",")

        return sections, entity_list, entities_type, attribute_list, attribute_list_types
