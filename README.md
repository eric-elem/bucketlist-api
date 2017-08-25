[![Build Status](https://travis-ci.org/eric-elem/bucketlist-api.svg?branch=develop)](https://travis-ci.org/eric-elem/bucketlist-api)

# bucketlist-api

# Description
Bucketlist-api is a RESTFul web api that let's users create accounts, login and create, view, edit and delete bucketlists and items.

# Installation

Create a new directory and initialize git in it. Clone this repository by running
```sh
$ git clone https://github.com/eric-elem/bucketlist-api.git
```
Create a virtual environment. For example, with virtualenv, create a virtual environment named env using
```sh
$ virtualenv env
```
Activate the virtual environment
```sh
$ source env/bin/activate
```
Install the dependencies in the requirements.txt file using pip
```sh
$ pip install -r requirements.txt
```
Setup a database that the api will use and set the uri as an environment variable. For postgres on mac, use
```sh
$ export DB_URL='postgresql://dbusername:dbpassword@localhost/dbname'
```
Start the application by running
```sh
$ python manage.py runserver
```
Test your setup using a client app like postman
