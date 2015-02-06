import tools.ContextProvider as CP
import tools.DataManager as DM
import sevici.sevici as f


def get_data_example(_id, _type, max_cache_time):
    """
        This is an example function which shows you how to manage the data in order
        to add it properly to the Context Provider response. This example uses the
        DataManager class but if you don't feel at ease with it and you prefer build
        the  response on your own, verify that your response matches with the example
        response.

        The function will be called one time for each entity that the Context Provider
        will being asked to, so take into account that  this functions have to make to
        give response for just one entity, in addition to this, you don't have to take
        care about patterned ids, there are a previous method that process them.

            :param _id: entity_id
            :param _type: entity_type
            :rtype : list
    """

    dm = DM.Entity()
    dm.entity_add(_id, _type)

    # CREATE AN ATTRIBUTE LIST
    dm.attribute.attribute_add('attrib_name_A', 'attrib_type_A', value='attrib_value_A')
    dm.attribute.attribute_add('attrib_name_B', 'attrib_type_B', value='attrib_value_B')

    # ADD A METADATA LIST TO AN ATTRIBUTE
    dm.attribute.metadata.metadata_add('metadata_name1', 'metadata_type1', value='metadata_value1')
    dm.attribute.metadata.metadata_add('metadata_name2', 'metadata_type2', value='metadata_value2')
    dm.attribute.add_metadatas_to_attrib('attrib_name_A')
    dm.attribute.metadata.metadata_list_purge()

    # ADD AN ATTRIBUTE LIST TO THE ENTITY
    data_response = dm.add_attributes_to_entity(_id)

    # SET THE ENTITY CACHE LIFETIME
    l_time = max_cache_time

    response = [data_response, l_time]

    return response

CP.ContextProvider('/v1/queryContext', f.get_data)
