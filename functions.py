__author__ = 'b.gzr'
import re
import time
import json
import urllib2
import requests
import unicodedata
from xml.dom import minidom
import xml.etree.ElementTree as ET
import DataManager as DM


def norm_data(s):
    """
    Normalizes data
        :param s: string to normalize
        :rtype : str
    """
    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))


def norm_time(s):
    """
    Parses time value to ISO8601 format
        :param s: time in seconds since the epoch
        :rtype : str
    """
    return time.strftime("%Y-%m-%dT%H:%M:%S.000000Z", time.localtime(float(s)))


def get_stations():
    """
    Obtains the stations xml provided by http://www.sevici.es
        :rtype : list
    """
    try:
        response = urllib2.urlopen('http://www.sevici.es/service/carto')
        xmldoc = minidom.parse(response)
        item_list = xmldoc.getElementsByTagName('marker')
        stations = []

        for s in item_list:
            station_dict = {
                'number': norm_data(s.attributes['number'].value),
                'name': norm_data(s.attributes['name'].value),
                'address': norm_data(s.attributes['address'].value),
                'fulladdress': norm_data(s.attributes['fullAddress'].value),
                'latitude': norm_data(s.attributes['lat'].value),
                'longitude': norm_data(s.attributes['lng'].value),
                'open': norm_data(s.attributes['open'].value),
                'bonus': norm_data(s.attributes['bonus'].value)
            }
            stations.append(station_dict)

        return stations
    except ValueError:
        return 0


def make_stations_jsonfile():
    """
    Creates a new stations json file
    """
    stations = get_stations()
    if stations != 0:
        with open('file/stations.json', 'w') as jsonfile:
            jstations = json.dumps(stations)
            jsonfile.write(jstations)


def load_stations():
    """
    Loads the stations list
        :rtype : list
    """
    try:
        with open('file/stations.json', 'r') as stations_file:
            stations = json.loads(stations_file.read())
        return stations
    except Exception:
        return 0


def select_ids(orion_ids):
    n = []
    for i in range(len(orion_ids)):
        pattern = "[urnSevilac:.*]*"
        a = len(re.match(pattern, orion_ids[i]).group())
        pattern_id = orion_ids[i][a:]+"$"
        clean_pattern = pattern_id.replace(".", "").replace("*", "")
        if len(clean_pattern) <= 4:
            for e in range(1, 261):
                if re.match(pattern_id, str(e)):
                    n.append(e)
    if len(n) == 0:
        n = [0]
    return n


def get_sevici_data(sevici_id):
    """
    Makes the sevici request
        :param sevici_id: sevici id number
        :rtype : list
    """
    url = 'http://www.sevici.es/service/stationdetails/seville/'+str(sevici_id)
    response = requests.get(url)
    response.raise_for_status()
    root = ET.fromstring(response.text)
    fields = root.findall("*")

    return fields


def request_sevici(id_, max_time=1):
    """
    Parses the response in xml format
        :param id_: entity id number
        :rtype : list
    """
    entity = DM.Entity()
    life_time = [time.time()]
    try:
        for i in range(len(id_)):
            fields = get_sevici_data(id_[i])
            _id = "urn::Sevilla:Sevici%s" % str(id_[i])

            entity.entity_add(_id, 'sevici', ispattern='false')
            for s in fields:
                if s.tag == "updated":
                    s.tag = "timeinstant"
                    life_time.append(float(s.text))
                    s.text = norm_time(s.text)
                    fieldtype = "urn:x-ogc:def:trs:IDAS:1.0:ISO8601"
                else:
                    fieldtype = "integer"

                entity.attribute.attribute_add(s.tag, fieldtype, s.text)

            stations = load_stations()
            if stations == 0:
                make_stations_jsonfile()
                stations = load_stations()

            if stations != 0:
                for station in stations:
                    if station['number'] == str(id_[i]):
                        pos = station['latitude']+","+station['longitude']
                        entity.attribute.attribute_add('position', 'coords', pos)
                        entity.attribute.metadata.metadata_add('location', 'string', 'WGS84')
                        entity.attribute.add_metadatas_to_attrib('position')
                        entity.attribute.metadata.metadata_list_purge()

            entity.add_attributes_to_entity(_id)
            entity.attribute.attribute_list_purge()

        response_data = entity.get_entity_list()[:]
        entity.entity_list_purge()
        l_time = (time.time() - max(life_time))

        if l_time < 1:
            l_time = 1
        else:
            l_time = max_time - l_time

        return [response_data, l_time]

    except:
        return [[], 1]