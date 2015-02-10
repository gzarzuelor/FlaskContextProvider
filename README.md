# FlaskContextProvider

The FlaskContextProvider is a python software that creates a [Flask](http://flask.pocoo.org/) server which 
allows to link a ContextBroker with another service. 

It is thought to provide real time data from sources which might have problems with the 
traffic that a periodical uptateContext suppose, and even so be able to work as a 
ContextProvider, for instance a web service. 

The software includes the DataManager, a library that makes easier to work with ContextBroker
responses, so it's relatively accessible to adapt any type of data source e to be a 
ContextProvider. 

Links
-------------------------
1. [Installing the software](https://github.com/gzarrub/FlaskContextProvider/blob/master/etc/FlaskContextProvider/Installing-the-software.md)
2. [How it works?](https://github.com/gzarrub/FlaskContextProvider/blob/master/etc/FlaskContextProvider/How-it-works.md)
