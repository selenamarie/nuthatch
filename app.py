#!/usr/bin/env python

import boto
from celery import Celery
from celery.signals import task_prerun
from flask import Flask, request, jsonify, g
from flask.ext.sqlalchemy import SQLAlchemy
import os
import requests

app = Flask(__name__)

# Set up Postgres database connection
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

from models import *

# Set up Celery
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379',
    CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml'],
)

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    celery.app = app
    return celery

celery = make_celery(app)
#print celery.app

@task_prerun.connect
def celery_prerun(*args, **kwargs):
    #print g
    with celery.app.app_context():
    #   # use g.db
       print g


@app.route('/')
def index():
    return "Hello, World!"


@app.route('/database/queries/new', methods=['POST'])
def new_query_source():
    uuid = ''
    if request.method == 'POST':
        # pick up the query the user submitted
        user_query = request.json['query']
        # TODO ensure this is a RO transaction
        try:
            newquery = QuerySource(query_text=user_query,)
            db.session.add(newquery)
            db.session.commit()
            # TODO change this to uuid
            id = newquery.id
            # add this thing to a queue?
        except Exception as e:
            return jsonify({
                'status': 'not ok',
                'error': 'Unable to add query to system',
                'exception': str(e)
            }), 401

        return jsonify({'status': 'ok', 'id': id}), 201


@app.route('/database/queries/<int:query_id>', methods=['GET'])
def get_query(query_id):
    if request.method == 'GET':
        try:
            user_query = QuerySource.query.filter_by(id=query_id).first()
            return jsonify({'status': 'ok', 'query': user_query.query_text})
        # TODO more interesting e handling
        except Exception as e:
            return jsonify({
                'status': 'not ok',
                'error': 'Could not find query',
                'exception': str(e)
            }), 401


@app.route('/database/queries/<int:query_id>/run', methods=['GET'])
def queue_query(query_id):
    if request.method == 'GET':
        try:
            run_query.delay(query_id)
            return jsonify({'status': 'ok', 'enqueued': 'yes', 'id': query_id}), 201
        except Exception as e:
            return jsonify({
                'status': 'not ok',
                'error': 'Unable to add query to system',
                'exception': str(e)
            }), 401


@app.route('/database/queries/<int:query_id>/latest_result', methods=['GET'])
def query_result(query_id):
        myresult = Results.query.filter_by(id=query_id).ordery_by(id).last()
        return jsonify({'results': myresult.result_all}), 201


@celery.task
def run_query(query_id):
    try:
        user_query = QuerySource.query.filter_by(id=query_id).first()
        results = db.session.execute(user_query.query_text)
        # http://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json
        # need to store the result, and then make it available at the DB url - so we need a mapping of s3 to query id s
        newresult = Result(query_id=query_id, result_all=jsonify(results))
        db.session.add(newresult)
        db.session.commit()
    except Exception as e:
        print e
        #return {
            #'status': 'not ok',
            #'error': 'Could not run specified query',
            #'exception': str(e)
        #}


if __name__ == '__main__':
    app.run(debug=True)
