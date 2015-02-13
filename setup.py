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


from setuptools import setup, find_packages

setup(
    name='FlaskContextProvider',
    version='0.1',
    packages=find_packages(),
    url='https://github.com/gzarrub/FlaskContextProvider',
    license='',
    author='Guillermo Zarzuelo',
    author_email='gzarrub@gmail.com',
    description="""The FlaskContextProvider is a python software that creates a Flask server
    which allows to link a ContextBroker with another service. It is thought to provide real
    time data from sources which might have problems with the traffic that a periodical
    uptateContext suppose, and even so be able to work as a ContextProvider, for instance a
    web service. The software includes the DataManager, a library that makes easier to work
    with ContextBroker responses, so it's relatively accessible to adapt any type of data
    source e to be a ContextProvider.""",
    install_requires=['flask', 'python-memcached', 'requests']
)