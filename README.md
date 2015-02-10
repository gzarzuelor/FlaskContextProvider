# FlaskContextProvider

The FlaskContextProvider is a python software that creates a server which allows to link a 
ContextBroker with another service. 

It is thought to provide real time data from sources which might have problems with the 
traffic that a periodical uptateContext suppose, and even so be able to work as a 
ContextProvider, for instance a web service. 

The software includes the DataManager, a library that makes easier to work with ContextBroker
responses, so it's relatively accessible to adapt any type of data source e to be a 
ContextProvider. 

The FlaskContextProvider is based on the microframework for Python [Flask](http://flask.pocoo.org/) and 
a python memcached client so it's important that a [memcached](http://memcached.org/)server was 
installed before the FlaskContextProvider start.

