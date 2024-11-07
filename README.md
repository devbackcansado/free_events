# free_events

## Warning

This docker is not running.

## Description

This is a simple web application that allows users to create, read, update, and delete events. The application is built using the Django web framework and uses the POSTGRES database.

## VS Code Extensions

https://marketplace.visualstudio.com/items?itemName=humao.rest-client

## Configuration

To run this application, you will need to have Python3 and Django installed on your machine. You can install Django by running the following command:

```
pip install -r requirements/prod.txt
```

## Create DB

Create a database in POSTGRES and update the database settings in the settings.py file.

## Run the application

To run the application, navigate to the root directory of the project and run the following command:

```
make migrate
```

To start the application, run the following command:

```
make start
```

## Run Celery

To run the celery worker, run the following command:

```
make worker
```

To run the celery beat, run the following command:

```
make beat
```

## Folder HTTP

This folder contains the HTTP requests that can be made to the application using the REST Client extension in VS Code.
