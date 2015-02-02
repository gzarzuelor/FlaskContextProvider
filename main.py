import ContextProvider as CP
import functions as f

cp = CP.ContextProvider()

def get_data_function():
########################################
    entities = cp.orion_data['entities']
    if 'attributes' in cp.orion_data:
        attributes = cp.orion_data['attributes']
########################################

    entity_id = []
    for i in range(len(entities)):
        entity_id.append(entities[i]['id'])
    _id = sorted(f.select_ids(entity_id))


    if _id == range(_id[0], _id[len(_id)-1]+1):
        key = "[range%s-%s]" % (str(_id[0]), str(_id[len(_id)-1]))
    else:
        key = "%s" % str(_id)

    if 'attributes' in cp.orion_data:
        key = "%s/%s" % (key, str(attributes))

    key = key.replace(" ", "").replace("'", "")
    cached_response = cp.check_cache(key)
    if cached_response is None:
        sevici_response = f.request_sevici(_id, max_time=cp.max_cache_time)
        cp.update_cache(key, sevici_response[0], sevici_response[1])
        return sevici_response[0]
    else:
        return cached_response

cp.run('/v1/queryContext',get_data_function)