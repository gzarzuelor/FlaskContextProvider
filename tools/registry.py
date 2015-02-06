__author__ = 'b.gzr'
import DataManager as DM
import requests
import json
import re

def make_registry_json():
    entities = []
    for i in range(1, 261):
        entities.append('urn::Sevilla:Sevici%s' % str(i))

    registry = {'sevici':entities}
    registry['tipodeprueba']=['a','b']

    with open('./etc/FlaskContextProvider/registry.json', 'w') as jsonfile:
        jregistry = json.dumps(registry)
        jsonfile.write(jregistry)


def load_registry_json():
    try:
        with open('./etc/FlaskContextProvider/registry.json', 'r') as registry_file:
            registry = json.loads(registry_file.read())
        return registry
    except IOError:
        return 0


def check_entity_registration(entity_type,_id):
    entity_list = []
    registry = load_registry_json()
    entities = registry[entity_type]
    for i in range(len(entities)):
        pattern_id = "%s$" % _id
        match = re.match(pattern_id, entities[i])
        if match is not None:
            entity_list.append(entities[i])

    return entity_list


def get_registered_entities(cb_url, token=''):
        try:
            url = cb_url+'/v1/registry/discoverContextAvailability'
            if len(token) != 0:
                headers = {'Content-Type': 'application/json', "X-Auth-Token": token, 'Accept': 'application/json'}
            else:
                headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

            registry = load_registry_json()
            payload = DM.Entity()

            reg_entities = {}
            for entity_type in registry:
                reg_entities[entity_type] = []
                payload.entity_add('.*',entity_type, ispattern='true')
                data = json.dumps({'entities': payload.get_entity_list()})
                response = requests.post(url, headers=headers, data=data)
                if 'contextRegistrationResponses' in response.json():
                    responses = response.json()['contextRegistrationResponses']
                    for i in range(len(responses)):
                        entities = responses[i]['contextRegistration']['entities']
                        for e in range(len(entities)):
                            reg_entities[entity_type].append(entities[e]['id'])
                else:
                    reg_entities[entity_type] = None
                payload.entity_list_purge()
            print reg_entities

        except requests.RequestException as e:
            print "%s" % e.message
            return -1