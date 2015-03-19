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


from providers.sevici import sevici as sevici
from providers.tusbic import tusbic as tusbic
from providers.villo import villo as villo
from providers.valenbisi import valenbisi as valenvisi



def get_data(_id, _type, max_time=1):
    if _id.find('Sevici.') != -1:
        return sevici.get_data(_id,_type,max_time=max_time)
    elif _id.find('Tusbic.') != -1:
        return tusbic.get_data(_id,_type,max_time=max_time)
    elif _id.find('Villo.') != -1:
        return villo.get_data(_id,_type,max_time=max_time)
    elif _id.find('Valenvisi.') != -1:
        return valenvisi.get_data(_id,_type,max_time=max_time)
    else:
        return [[], 1]