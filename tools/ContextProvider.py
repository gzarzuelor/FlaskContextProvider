#!/usr/bin/python
# Copyright 2015 Telefonica Investigacion y Desarrollo, S.A.U
#
# This file is part of FlaskContextProvider.
#
# FlaskContextProvider is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# FlaskContextProvider is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Orion Context Broker. If not, see http://www.gnu.org/licenses/.


import xml.etree.ElementTree as ET
from flask import Flask, request
import tools.DataManager as DM
import tools.Registry as R
import ConfigParser
import warnings
import memcache
import inspect
import logging
import re
import os


class ContextProvider():
    def __init__(self, **kwargs):

        self.file_path = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
        self.__start_log__('FlaskContextProvider')
        config = ConfigParser.ConfigParser()
        config.read("%s/../etc/FlaskContextProvider/FlaskContextProvider.ini" % self.file_path)
        try:
            self.provider_url = config.get('PROVIDER', 'provider_url')
            self.provider_port = int(config.get('PROVIDER', 'provider_port'))
            self.public_provider_url = config.get('PROVIDER', 'public_provider_url')

            self.cache_server_url = config.get('CACHE', 'cache_server_ip')
            self.cache_server_port = config.get('CACHE', 'cache_server_port')
            self.max_cache_time = int(config.get('CACHE', 'max_cache_time'))

        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError) as e:
            warnings.warn("%sat FlaskContextProvider.ini" % e, stacklevel=2)
            exit(-1)

        route = self.__get_route__()
        self.orion_data = None
        self.c_type = None
        self.cache = self.__start_cache__()

        self.reg = R.Registry(self.public_provider_url)
        self.reg.get_registered_entities()

        app = Flask('ContextProvider')
        @app.route(route, methods=['POST'])
        def __provider_task__():
            """
            Defines the process which is going to be done every time
            a post access is detected.
                :rtype : str
            """
            self.c_type = request.headers['Content-Type']
            self.orion_data = self.__get_cb_data__(request)

            entities = self.orion_data['entities']
            response_data = DM.Entity()

            entity_id_list = []
            entity_type_list = []

            for i in range(len(entities)):
                entity_id_list.append(entities[i]['id'])
                entity_type_list.append(entities[i]['type'])

            for i in range(len(entity_id_list)):
                key = "%s/%s" % (entity_id_list[i], entity_type_list[i])
                cached_response = self.__check_cache__(key)

                if cached_response is None:
                    response = [[], 1]
                    for k, f in kwargs.iteritems():
                        if entity_type_list[i] == k:
                            response = f(entity_id_list[i], entity_type_list[i], self.max_cache_time)

                    if len(response[0]) != 0:
                        response_data.entity_list_add(response[0])
                        if response[1] < 1:
                            response[1] = 1
                        self.__update_cache__(key, response[0], response[1])

                else:
                    response_data.entity_list_add(cached_response)

            response = self.__parse_response__(response_data.get_entity_list())
            return response

        app.run(host=self.provider_url, port=self.provider_port)

    def __get_route__(self):
        if len(re.findall("http[s]?://", self.public_provider_url)) == 0:
            msg = "Please, add http:// or https:// to your public_provider_url field at FlaskContextProvider.ini"
            warnings.warn(msg, stacklevel=2)
            exit(-1)

        url_pattern = 'http[s]?://(?:[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        if len(re.findall(url_pattern, self.public_provider_url)) != 0:
            find_port = ':%s' % str(self.provider_port)
            port_pos = self.public_provider_url.find(find_port)
            if port_pos != -1:
                sub_route = self.public_provider_url[port_pos+len(find_port):]
                if sub_route[len(sub_route)-1] == '/':
                    provider_route = sub_route+'queryContext'
                else:
                    provider_route = sub_route+'/queryContext'

                return provider_route
            else:
                msg = "Your provider_port and public_provider port doesn't match"
                warnings.warn(msg, stacklevel=2)
                exit(-1)
        else:
            msg = "Incorrect url, try something like http://example_url:provider_port/directory"
            warnings.warn(msg, stacklevel=2)
            exit(-1)

    def __get_cb_data__(self, cb_request):
        """
        Gets the ContextBroker request data and parses it to a json dict.
            :param cb_request: ContextBroker request
            :rtype : dict
        """

        try:
            offset = int(cb_request.args.get('offset'))
        except TypeError:
            offset = 0
        try:
            limit = int(cb_request.args.get('limit'))
        except TypeError:
            limit = 0

        entity_list = []
        if self.c_type == 'application/json':
            entities = cb_request.json['entities']
            for i in range(len(entities)):
                entity = entities[i]
                if entity['isPattern'] == 'true':
                    entities_list = self.reg.check_entity_registration(entity['type'], entity['id'])
                    for e in range(len(entities_list)):
                        entity_list.append({'id': entities_list[e], 'type': entity['type'], 'isPattern': 'false'})
                else:
                    entity_list.append({'id': entity['id'], 'type': entity['type'], 'isPattern': 'false'})

            if offset != 0 and limit != 0:
                cb_request.json['entities'] = entity_list[offset:offset+limit]
            elif offset == 0 and limit != 0:
                cb_request.json['entities'] = entity_list[:limit]
            elif offset != 0 and limit == 0:
                cb_request.json['entities'] = entity_list[offset:]
            else:
                cb_request.json['entities'] = entity_list[:]

            return cb_request.json

        else:
            try:
                query_context_request = ET.fromstring(cb_request.data)
                entity_ids = query_context_request.findall('.//entityIdList//entityId')

                orion_id = []
                for entity_id in entity_ids:
                    entity_dict = entity_id.attrib
                    entity_dict['id'] = entity_id.find('.//id').text
                    if entity_dict['isPattern'] == 'true':
                        entities = self.reg.check_entity_registration(entity_dict['type'], entity_dict['id'])
                        for i in range(len(entities)):
                            orion_id.append({'id': entities[i], 'type': entity_dict['type'], 'isPattern': 'false'})
                    else:
                        orion_id.append(entity_dict)

                if offset != 0 and limit != 0:
                    orion_id = orion_id[offset:offset+limit]
                elif offset == 0 and limit != 0:
                    orion_id = orion_id[:limit]
                elif offset != 0 and limit == 0:
                    orion_id = orion_id[offset:]
                else:
                    orion_id = orion_id[:]

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
        """
        Parses the data of a DataManager List to xml.
            :param dm_entity_list: response list
            :rtype : str
        """
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
                            # This "if" checks the attributes that the user has requested, if user doesn't specify
                            # any attribute, the "for" makes the if at each loop, on the contrary, if user requests
                            # an "attribute-filtered" response, the attribute only will be added if it is on the
                            # requested attribute list.
                            if 'attributes'not in self.orion_data or ('attributes' in self.orion_data and attribute['name'] in self.orion_data['attributes']):
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

    def __start_cache__(self):
        """
        Starts a memcache client.
        """
        try:
            route = '%s:%s' % (self.cache_server_url, self.cache_server_port)
            return memcache.Client([route], debug=0)

        except Exception as e:
            warnings.warn("%s" % e, stacklevel=1)
            return None

    def __check_cache__(self, key):
        """
        checks if it exists a cache entry of the key param.
            :param key: cache response id
            :rtype : list
        """
        try:
            if self.cache is not None:
                return self.cache.get(str(key))
            else:
                return None
        except Exception as e:
            warnings.warn("%s" % e, stacklevel=1)
            return None

    def __update_cache__(self, key, data, life_time):
        """
        Adds a new cache entry.
            :param key: cache response id
            :param data: response
            :param life_time: time at cache
            :rtype : bool
        """
        try:
            if self.cache is not None:
                if len(key) > 250:
                    raise SyntaxError("%s it's a too long key, check your entity ids" % key)

                return self.cache.set(str(key), data, time=life_time)
            else:
                return False

        except SyntaxError as e:
            warnings.warn("%s" % e, stacklevel=1)
            return False

    def __start_log__(self, log_name):

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh = logging.FileHandler('%s/../etc/log/%s.log' % (self.file_path, log_name))
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)