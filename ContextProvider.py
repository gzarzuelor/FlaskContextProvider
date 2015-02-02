from flask import Flask, request
import xml.etree.ElementTree as ET
import ConfigParser
import memcache


class ContextProvider():
    def __init__(self):
        config = ConfigParser.ConfigParser()
        config.read("./config.ini")

        self.provider_url = config.get('PROVIDER', 'provider_url')
        self.provider_port = int(config.get('PROVIDER', 'provider_port'))


        self.cache_server_url = config.get('CACHE', 'cache_server_ip')
        self.cache_server_port = config.get('CACHE', 'cache_server_port')
        self.max_cache_time = int(config.get('CACHE', 'max_cache_time'))


        self.c_type = None
        self.route = None
        self.function = None
        self.orion_data = None
        self.app = None


        self.cache = self.start_cache()

    def run(self, route, funct):
        self.route = route
        self.function = funct

        self.app = Flask('ContextProvider')

        @self.app.route(self.route, methods=['POST'])
        def __provider_task__():
            self.c_type = request.headers['Content-Type']
            self.orion_data = self.__get_orion_data__(request)
            service_provider_response = self.function()
            response = self.__parse_response__(service_provider_response)
            return response

        self.app.run(host=self.provider_url, port=self.provider_port)

    def __get_orion_data__(self, cb_request):

        if self.c_type == 'application/json':
            orion_data = cb_request.json

        else:
            try:
                query_context_request = ET.fromstring(cb_request.data)
                entity_ids = query_context_request.findall('.//entityIdList//entityId')
                orion_id = []
                for entity_id in entity_ids:
                    entity_dict = entity_id.attrib
                    entity_dict['id'] = entity_id.find('.//id').text
                    orion_id.append(entity_dict)
                query_context_request = ET.fromstring(cb_request.data)
                attributes = query_context_request.findall('.//attributeList//attribute')
                if len(attributes) != 0:
                    attribute_list = []
                    for attribute in attributes:
                        attribute_list.append(attribute.text)
                    orion_data = {'entities': orion_id, 'attributes': attribute_list}
                else:
                    orion_data = {'entities': orion_id}

            except ET.ParseError:
                return 0

        return orion_data

    def __parse_response__(self, dm_entity_list):
        try:
            if len(dm_entity_list) != 0:
                query_context_response = ET.Element('queryContextResponse')
                context_response_list = ET.SubElement(query_context_response, 'contextResponseList')
                for entity in dm_entity_list:
                    context_element_response = ET.SubElement(context_response_list, 'contextElementResponse')
                    context_element = ET.SubElement(context_element_response, 'contextElement')
                    entity_id = ET.SubElement(context_element, 'entityId', {"type": entity['type'], 'isPattern': entity['isPattern']})
                    id_element = ET.SubElement(entity_id, 'id')
                    id_element.text = entity['id']
                    if 'attributes' in entity:
                        context_attribute_list = ET.SubElement(context_element, 'contextAttributeList')
                        for attribute in entity['attributes']:
                            if not 'attributes' in self.orion_data or ('attributes' in self.orion_data and attribute['name'] in self.orion_data['attributes']):
                                context_attribute = ET.SubElement(context_attribute_list, 'contextAttribute')
                                name = ET.SubElement(context_attribute, 'name')
                                name.text = attribute['name']
                                type_element = ET.SubElement(context_attribute, 'type')
                                type_element.text = attribute['type']
                                context_value = ET.SubElement(context_attribute, 'contextValue')
                                context_value.text = attribute['value']
                                if 'metadatas' in attribute:
                                    for metadata in attribute['metadatas']:
                                        meta_data = ET.SubElement(context_attribute, 'metadata')
                                        context_metadata = ET.SubElement(meta_data, 'contextMetadata')
                                        name = ET.SubElement(context_metadata, 'name')
                                        name.text = metadata['name']
                                        type_element = ET.SubElement(context_metadata, 'type')
                                        type_element.text = metadata['type']
                                        value = ET.SubElement(context_metadata, 'value')
                                        value.text = metadata['value']

                    status_code = ET.SubElement(context_element_response, 'statusCode')
                    code = ET.SubElement(status_code, 'code')
                    code.text = '200'
                    reason_phrase = ET.SubElement(status_code, 'reasonPhrase')
                    reason_phrase.text = 'OK'

            else:
                query_context_response = ET.Element('queryContextResponse')
                error_code = ET.SubElement(query_context_response, 'errorCode')
                code = ET.SubElement(error_code, 'code')
                code.text = '404'
                reason_phrase = ET.SubElement(error_code, 'reasonPhrase')
                reason_phrase.text = 'No context elements found'

        except (Exception, ET.ParseError):

            query_context_response = ET.Element('queryContextResponse')
            error_code = ET.SubElement(query_context_response, 'errorCode')
            code = ET.SubElement(error_code, 'code')
            code.text = '404'
            reason_phrase = ET.SubElement(error_code, 'reasonPhrase')
            reason_phrase.text = 'No context elements found'

        return ET.tostring(query_context_response, 'utf-8')

    def start_cache(self):
        try:
            route = '%s:%s' % (self.cache_server_ip, self.cache_server_port)
            return memcache.Client([route], debug=0)
        except:
            return None

    def check_cache(self, key):
        try:
            if self.cache is not None:
                return self.cache.get(key)
            else:
                return None
        except:
            return None

    def update_cache(self, key, data, life_time):
        try:
            if self.cache is not None:
                if len(key) > 250:
                    raise SyntaxError('Key too long')

                self.cache.set(key, data, time=int(life_time))
            else:
                return None
        except:
            return None