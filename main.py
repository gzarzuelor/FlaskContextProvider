import ContextProvider as CP
import functions as f

cp = CP.ContextProvider()

def get_data_function():
    response_format = 'xml'
    max_cache_time = 360

########################################
    entities = cp.orion_data['entities']
    attributes = cp.orion_data['attributes']
########################################

    entitiy_id = []
    for i in range(len(entities)):
        entitiy_id.append(entities[i]['id'])
    _id = sorted(f.select_ids(entitiy_id))

    sevici_response = f.request_sevici(_id, max_time=max_cache_time)

    return sevici_response

cp.run('/v1/queryContext',get_data_function)