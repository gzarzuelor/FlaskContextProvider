__author__ = 'b.gzr'
import DataManager as DM
import ConfigParser
import warnings
import requests
import json
import re


class Registry():
    def __init__(self, cp_url):
        self.path = './tools/registryUtils/registry.json'
        self.registration_path = './etc/Registry/registry.ini'

        self.cp_url = cp_url

        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        self.config = ConfigParser.ConfigParser()

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
            jsonfile.close()

    def clean_registry_json(self):
        registry = {}

        with open(self.path, 'w') as jsonfile:
            jregistry = json.dumps(registry)
            jsonfile.write(jregistry)
            jsonfile.close()

    def load_registry_json(self):
        try:
            with open(self.path, 'r') as registry_file:
                registry = json.loads(registry_file.read())
                registry_file.close()
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

    def get_registered_entities(self):
            try:

                self.config.read(self.registration_path)
                regs = self.config.sections()
                payload = DM.Entity()
                self.clean_registry_json()
                if len(regs) != 0:
                    for i in range(len(regs)):
                        reg = self.load_registry_file(regs[i])
                        if reg != 0:
                            for e in range(len(reg[0])):
                                payload.entity_add(reg[0][e], reg[1])

                            for e in range(len(reg[2])):
                                payload.attribute.attribute_add(reg[2][e], reg[3][e], is_domain='false')

                            data = json.dumps({'entities': payload.get_entity_list()})

                            url = reg[4]+'/v1/registry/discoverContextAvailability'
                            if reg[5] != 'None':
                                self.headers = {'Content-Type': 'application/json', 'X-Auth-Token': reg[5], 'Accept': 'application/json'}
                            else:
                                self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

                            response = requests.post(url, headers=self.headers, data=data)

                            z = 0
                            if 'contextRegistrationResponses' in response.json():
                                responses = response.json()['contextRegistrationResponses']
                                for e in range(len(responses)):
                                    if not responses[e]['contextRegistration']['providingApplication'] == self.cp_url:
                                        print "another provider has %s registered" % regs[i]

                                    else:
                                        entities = responses[e]['contextRegistration']['entities']
                                        for t in range(len(entities)):
                                            if (entities[t]['id'] not in reg[0]
                                                    or entities[t]['type'] != reg[1]):
                                                z += 1

                                        attributes = responses[e]['contextRegistration']['attributes']
                                        for t in range(len(attributes)):
                                            if (attributes[t]['name'] not in reg[2]
                                                    or attributes[t]['type'] not in reg[3]):
                                                z += 1

                                        if z != 0:
                                            print "%s has changed at registry.ini update registration, (registration ID)" % regs[i]
                                            # registration_id = search registration_id
                                            # reg_response = self.register_context(reg[4], payload.get_entity_list(),payload.attribute.get_attribute_list(), duration=reg[6], registration_id=registration_id)
                                            # if reg_response != -1:
                                            #     self.add_registry_json(reg[1],reg[0])
                                        else:
                                            self.add_registry_json(reg[1],reg[0])

                            else:
                                print "%s it's not registered, new registry or expired one?" % regs[i]
                                # registration_id = search registration_id
                                # reg_response = self.register_context(reg[4], payload.get_entity_list(),payload.attribute.get_attribute_list(), duration=reg[6], registration_id=registration_id)
                                # if reg_response != -1:
                                #     self.add_registry_json(reg[1],reg[0])

                            payload.entity_list_purge()
                            payload.attribute.attribute_list_purge()

            except requests.RequestException as e:
                print "%s" % e.message
                return -1

    def load_registry_file(self, reg):

        self.config.read(self.registration_path)
        try:
            entity_list = self.config.get(reg, 'entity_ids').replace(" ", "").split(",")
            entities_type = self.config.get(reg, 'entity_type')
            attribute_list = self.config.get(reg, 'attributes').replace(" ", "").split(",")
            attribute_list_types = self.config.get(reg, 'attrb_type').replace(" ", "").split(",")
            ContBroker = self.config.get(reg, 'ContBroker').replace(" ", "")
            token = self.config.get(reg, 'token').replace(" ", "")
            duration = self.config.get(reg, 'duration').replace(" ", "")

            if len(attribute_list) != len(attribute_list_types):
                warnings.warn("Registry %s has an incorrect definition" % reg)
                return 0

            return [entity_list, entities_type, attribute_list, attribute_list_types, ContBroker, token]

        except ConfigParser.Error:
            warnings.warn("Registry %s has an incorrect definition" % reg)
            return 0

    def register_context(self, cb_url, entities, attribute_list, duration='PT24H', registration_id=''):

        payload = {
            "contextRegistrations": [{
                'entities': entities,
                'attributes': attribute_list,
                'providingApplication': self.cp_url,
            }],
            "duration": duration
        }

        if registration_id != '':
            payload['registrationId'] = registration_id

        data = json.dumps(payload)
        url = cb_url+'/v1/registry/registerContext'

        try:
            response = requests.post(url, headers=self.headers, data=data)
            return response

        except requests.RequestException as e:
            print "%s" % e.message
            return -1

