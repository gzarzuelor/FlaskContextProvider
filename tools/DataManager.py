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

__author__ = 'b.gzr'
import warnings
import logging
import inspect
import os


def data_manager_error(message):
    cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
    print cmd_folder
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='%s/../etc/log/error.log' % cmd_folder, level=logging.WARNING)
    warnings.warn(message)
    logging.warning(message)


class Metadata():

    def __init__(self):
        """
        Manage a metadata list in order to add it
        to one or several attributes
        """
        self._metadata_list = []

    def get_metadata_list(self):
        """
        Returns the metadata_list
            :rtype : list
        """
        return self._metadata_list

    def metadata_add(self, name, meta_type, value):
        """
        Adds a new metadata to metadata_list.
            :param name: metadata name
            :param meta_type: metadata type
            :param value: metadata value
            :rtype : list
        """
        metadata_dict = {'name': name, 'type': meta_type, 'value': value}
        for i in self.get_metadata_list():
            if i['name'] == name:
                msg = "Metadata.metadata_add(): Metadata name %s is already in use" % name
                data_manager_error(msg)
                return self.get_metadata_list()[:]

        self.get_metadata_list().append(metadata_dict)

        return self.get_metadata_list()[:]

    def metadata_list_add(self, metadata_list):
        """
        Adds a new metadata list if it is valid.
            :param metadata_list: metadata list
            :rtype : list
        """
        for i in range(len(metadata_list)):
            z = 0
            for element in metadata_list[i]:
                if element not in ['name', 'type', 'value']:
                    z += 1
                    msg = "Metadata.metadata_list_add(): List was not added due to an incorrect format."
                    data_manager_error(msg)
            if z == 0:
                self._metadata_list.append(metadata_list[i])

        return self.get_metadata_list()[:]

    def metadata_purge(self, metadata_name):
        """
        Removes metadata of metadata_list.
            :param metadata_name: metadata name
            :rtype : list
        """
        z = 0
        for i in self.get_metadata_list():
            if i['name'] == metadata_name:
                self.get_metadata_list().remove(i)
                z += 1
        if z == 0:
            msg = "Metadata.metadata_purge(): Metadata name %s do not exist" % metadata_name
            data_manager_error(msg)

        return self.get_metadata_list()[:]

    def metadata_list_purge(self):
        """
        Sets the metadata_list to an empty list.
        """
        self._metadata_list = []


class Attributes():

    def __init__(self):
        """
        Manage an attribute list in order to add it
        to one or several entities
        """
        self._attribute_list = []
        self.metadata = Metadata()

    def get_attribute_list(self):
        """
        Returns the attribute_list.
            :rtype : list
        """
        for i in self._attribute_list:
            if 'metadatas' in i and len(i['metadatas']) == 0:
                    del i['metadatas']
        return self._attribute_list

    def attribute_add(self, name, attrib_type, value='', is_domain=''):
        """
        Adds a new attribute to metadata_list.
            :param name: attribute name
            :param attrib_type: attribute type
            :param value: attribute value
            :rtype : list
        """
        if value == '' and is_domain != '':
            attribute_dict = {'name': name, 'type': attrib_type, 'isDomain': is_domain}
        else:
            attribute_dict = {'name': name, 'type': attrib_type, 'value': value}

        for i in self.get_attribute_list():
            if i['name'] == name:
                msg = "Attributes.attribute_add(): Attribute name %s is already in use" % name
                data_manager_error(msg)
                return self.get_attribute_list()[:]

        self.get_attribute_list().append(attribute_dict)

        return self.get_attribute_list()[:]

    def attribute_list_add(self, attribute_list):
        """
        Adds a new attribute list if it is valid.
            :param attribute_list: attribute list
            :rtype : list
        """
        for i in range(len(attribute_list)):
            z = 0
            for element in attribute_list[i]:
                if element not in ['name', 'type', 'value', 'metadatas', 'isDomain']:
                    z += 1
                    msg = "Attribute.attribute_list_add(): Element %s is not part of an attribute list." % element
                    data_manager_error(msg)
            if z == 0:
                self._attribute_list.append(attribute_list[i])

        return self.get_attribute_list()[:]

    def attribute_purge(self, attribute_name):
        """
        Removes attribute of attribute_list.
            :param attribute_name: attribute name
            :rtype : list
        """
        z = 0
        for i in self.get_attribute_list():
            if i['name'] == attribute_name:
                self.get_attribute_list().remove(i)
                z += 1
        if z == 0:
            msg = "Attributes.attribute_purge(): Attribute name %s do not exist" % attribute_name
            data_manager_error(msg)

        return self.get_attribute_list()[:]

    def attribute_list_purge(self):
        """
        Sets the attribute_list to empty.
        """
        self._attribute_list = []

    def add_metadatas_to_attrib(self, attribute_name):
        """
            Adds the metadata list saved to one attribute.
                :param attribute_name: attribute name
                :rtype : list
        """
        if len(self.metadata.get_metadata_list()) == 0:
            msg = "Attributes.add_metadatas_to_attrib(): Empty metadata_list was passed to the function."
            data_manager_error(msg)

        else:
            z = 0
            for i in self.get_attribute_list():
                if i['name'] == attribute_name:
                    i['metadatas'] = self.metadata.get_metadata_list()[:]
                    z += 1
            if z == 0:
                msg = "Attributes.add_metadatas_to_attrib(): Attribute name %s do not exist" % attribute_name
                data_manager_error(msg)

            return self.get_attribute_list()[:]


class Entity():

    def __init__(self):
        """
        Manage an entity list in order to add it
        to one Context Broker method
        """
        self.__entity_list = []
        self.attribute = Attributes()

    def get_entity_list(self):
        """
        Returns the entity_list.
            :rtype : list
        """
        return self.__entity_list

    def entity_add(self, entity_id, entity_type, ispattern='false'):
        """
        Adds a new entity to entity_list.
            :param entity_id: entity id
            :param entity_type: entity type
            :param ispattern: isPattern[true/false]
            :rtype : list
        """
        entity_dict = {'id': entity_id, 'type': entity_type, 'isPattern': ispattern}
        for i in self.get_entity_list():
            if i['id'] == entity_id:
                msg = "Entity.entity_add(): Entity was not added, id %s already exists" % entity_id
                data_manager_error(msg)
                return self.get_entity_list()[:]

        self.get_entity_list().append(entity_dict)

        return self.get_entity_list()[:]

    def entity_list_add(self, entity_list):
        """
        Adds a new entity list if it is valid.
            :param entity_list: entity list
            :rtype : list
        """

        for i in range(len(entity_list)):
            z = 0
            for element in entity_list[i]:
                if element not in ['id', 'type', 'isPattern', 'attributes']:
                    msg = "Entity.entity_list_add(): Element %s is not part of an entity list." % element
                    data_manager_error(msg)
                    z += 1
            if z == 0:
                self.__entity_list.append(entity_list[i])

        return self.get_entity_list()[:]

    def entity_purge(self, entity_id):
        """
        Removes entity of entity_list.
            :param entity_id: entity id
            :rtype : list
        """
        z = 0
        for i in self.get_entity_list():
            if i['id'] == entity_id:
                self.get_entity_list().remove(i)
                z += 1
        if z == 0:
            msg = "Entity.entity_purge(): Entity %s do not exist" % entity_id
            data_manager_error(msg)

        return self.get_entity_list()[:]

    def entity_list_purge(self):
        """
        Sets the entity_list to an empty list.
        """
        self.__entity_list = []

    def add_attributes_to_entity(self, entity_id):
        """
            Adds the attribute list saved to one entity.
                :param entity_id: entity id
                :rtype : list
        """
        if len(self.attribute.get_attribute_list()) == 0:
            msg = "Element.add_entity_attrib(): Empty attribute_list passed to the function"
            data_manager_error(msg)

        else:
            z = 0
            for i in self.get_entity_list():
                if i['id'] == entity_id:
                    i['attributes'] = self.attribute.get_attribute_list()[:]
                    z += 1
            if z == 0:
                msg = "Entity.add_entity_attrib(): Entity %s do not exist" % entity_id
                data_manager_error(msg)

            return self.get_entity_list()[:]