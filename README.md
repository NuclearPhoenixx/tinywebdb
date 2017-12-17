# tinywebdb
![GitHub last commit](https://img.shields.io/github/last-commit/phoenix1747/tinywebdb.svg?style=flat-square) ![open issues](https://img.shields.io/github/issues-raw/phoenix1747/tinywebdb.svg?style=flat-square) ![license](https://img.shields.io/github/license/phoenix1747/tinywebdb.svg?style=flat-square)

These are the files necessary for running a custom TinyWebDB for the MIT AppInventor 2.

## Requirements

These files do not run on a normal webserver - you would need to have a python framework with Django running. In additon they depend on some Google App Engine and Webapp libraries.

They are specifically intended to run on a Google App Engine Server, just like the original code by the App Inventor guys from MIT.

If you want to use Google App Engine's infrastructure, you will also need the Google App Engine SDK for python and a Google Cloud Console account. You'll have to edit the files according to your needs and then upload the files with the SDK software. You can find a tutorial here: [http://appinventor.mit.edu/explore/content/custom-tinywebdb-service.html](http://appinventor.mit.edu/explore/content/custom-tinywebdb-service.html).

**Python version: 2.7 (latest standard env version)**

---

## Directories

```TinyWebDB``` let's you run the service with a web interface, but be careful since everyone knowing the URL could easily alter your data!

```TinyWebDB no_interface``` let's you run the same service, but without any web interface at all. That means everything has to be done over the Google Cloud Console. The advantage is that you don't have to care about the web frontend.

---

## Branches

```master``` is the latest stable version of this custom TinyWebDB.

```dev``` is the unstable development branch for testing changes in the TinyWebDB.
