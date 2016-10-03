# tinywebdb
These are the files necessary for running a custom TinyWebDB for the MIT AppInventor 2.


## Requirements


These files do not run on a normal webserver. You would need to have a python framework running like Django and other dependencies.
They are specifically intended to run on a Google WebEngine Server, just like the original code from MIT.

You will also need the Google App Engine SDK for python and a Google Cloud Console account. That's because you have to edit it according to your needs and then upload the files with the SDK. For a tutorial visit http://appinventor.mit.edu/explore/content/custom-tinywebdb-service.html .


#### Python version: 2.7 (latest compatible version)

#### Django version: 1.5 (latest compatible version)

-------------------------
## Hint

```TinyWebDB``` let's you run the service with a web interface, but be careful! Everyone knowing the URL could easily alter your data.

```TinyWebDB no_interface``` let's you run the same service, but without any web interface. That means everything has to be done over the Google Cloud Console. The advantage is that you don't have to care about the web frontend.
