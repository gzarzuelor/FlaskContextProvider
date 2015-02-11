# FlaskContextProvider

The FlaskContextProvider is a python software that creates a [Flask](http://flask.pocoo.org/) server which 
allows to link a ContextBroker with another service. 

It is thought to provide real time data from sources which might have problems with the 
traffic that a periodical [uptateContext](https://forge.fiware.org/plugins/mediawiki/wiki/fiware/index.php/Publish/Subscribe_Broker_-_Orion_Context_Broker_-_User_and_Programmers_Guide#Update_context_elements) suppose, and even so be able to work as a ContextProvider, for instance a web service. 

The software includes the [DataManager](https://github.com/gzarrub/FlaskContextProvider/blob/master/tools/DataManager.py), a library that makes easier to work with ContextBroker responses, so it's relatively accessible to adapt any type of data source to be a ContextProvider. 

Links
-------------------------
1. [Installing the software](https://github.com/gzarrub/FlaskContextProvider/blob/master/etc/FlaskContextProvider/Installing-the-software.md)
2. [How it works?](https://github.com/gzarrub/FlaskContextProvider/blob/master/etc/FlaskContextProvider/How-it-works.md)
