from setuptools import setup, find_packages

setup(
    name='FlaskContextProvider',
    version='0.1',
    packages=find_packages(),
    url='https://github.com/gzarrub/FlaskContextProvider',
    license='',
    author='Guillermo',
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