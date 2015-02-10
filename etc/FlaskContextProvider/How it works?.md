
1.  First at all, you have to write your own function to get the data from the source, the
    function is different for every situation and depends on the data source.

    The function will be called one time for each entity that the Context Provider
    will be asked to, so take into account that this functions have to give response
    for just one entity, in addition to this, you don't have to take care about patterned
    ids, there are a previous method that processes them and returns non patterned ids.

2.  After that you have to include the entities that you want to give response at [registry.ini](https://github.com/gzarrub/FlaskContextProvider/blob/master/etc/Registry/registry.ini)
    That config file will be used to process the patterned ids and to make the registration at ContextBroker whether
    there is a new registry or the registration duration has finished. All the registration information as registration_id is
    storaged at [registration.log](https://github.com/gzarrub/FlaskContextProvider/blob/master/tools/registryUtils/registration.log).

    Owing to the complicated registration_id management, by now the update of a registration can't be done
    automatically. So to make a registration upload, the manual_register_context method must be used after
    look for the registration_id at the registration [registration log](https://github.com/gzarrub/FlaskContextProvider/blob/master/tools/registryUtils/registration.log) file and the
    registration label at [registry.ini](https://github.com/gzarrub/FlaskContextProvider/blob/master/etc/Registry/registry.ini). 
