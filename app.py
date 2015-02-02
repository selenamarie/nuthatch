#!/usr/bin/env python

import boto
from flask import Flask, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
import os
import requests

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

from models import *

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
def run_query(query_id):
    if request.method == 'GET':
        try:
            user_query = QuerySource.query.filter_by(id=query_id).first()
            results = db.session.execute(user_query.query_text)
            # http://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json
            return jsonify({'results': results}), 201
        # TODO more interesting e handling
        except Exception as e:
            return jsonify({
                'status': 'not ok',
                'error': 'Could not find specified query query',
                'exception': str(e)
            }), 401



if __name__ == '__main__':
    app.run(debug=True)
