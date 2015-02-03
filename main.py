import ContextProvider as CP
import DataManager as DM
import functions as f

cp = CP.ContextProvider()

def get_data_function():
    ############################################
    entities = cp.orion_data['entities']
    if 'attributes' in cp.orion_data:
        attributes = cp.orion_data['attributes']
    ############################################

    response_data = DM.Entity()
    entity_id_list = []

    for i in range(len(entities)):
        entity_id_list.append(entities[i]['id'])

    for e in range(len(entity_id_list)):
        cached_response = cp.check_cache(entity_id_list[e])
        if cached_response is None:
            sevici_response = f.request_sevici(entity_id_list[e], max_time=cp.max_cache_time)
            if len(sevici_response[0]) != 0:
                response_data.entity_list_add(sevici_response[0])
                cp.update_cache(entity_id_list[e], sevici_response[0], sevici_response[1])
        else:
            response_data.entity_list_add(cached_response)

    return response_data.get_entity_list()


cp.run('/v1/queryContext',get_data_function)