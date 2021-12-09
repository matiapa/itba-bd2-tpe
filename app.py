import re
from flask import Flask, request, send_from_directory
from neo4j import GraphDatabase
from elasticsearch import Elasticsearch, helpers
import csv
import io

app = Flask(__name__)

NEO4J_URL = 'neo4j://localhost:7687'
NEO4J_USER = 'neo4j'
NEO4J_PASS = '1234'
NEO4J_DB_NAME = "neo4j"

ELASTIC_HOST = 'localhost'
ELASTIC_PORT = 9200
ELASTIC_INDEX_NAME = 'docs'

STOP_WORDS = ['and','or','a','of']
LABEL_LIMIT = 10

neo = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USER, NEO4J_PASS))
es = Elasticsearch(host = ELASTIC_HOST, port = ELASTIC_PORT)

@app.route("/api/search")
def search():
    depth = int(request.args.get('depth') or '1')
    useClassOf = bool(int(request.args.get('useClassOf') or '1'))
    useParentOf = bool(int(request.args.get('useParentOf') or '1'))
    searchStr = request.args.get('query')

    if not useClassOf and not useParentOf:
        return "At least one relationship must be used", 400
    if searchStr == None:
        return "Missing query parameter", 400

    # Prepare labels and find related ones

    searchStr = searchStr.lower()
    words = searchStr.split(" ")
    words = list(filter(lambda l : l not in STOP_WORDS, words))
    labels = words + [searchStr]

    print(f'> Labels from query string: {labels}')

    session = neo.session(database = NEO4J_DB_NAME)
    relatedLabels = session.write_transaction(getRelatedLabels, labels, depth, useClassOf, useParentOf)

    if len(relatedLabels) > LABEL_LIMIT:
        relatedLabels = relatedLabels[0:LABEL_LIMIT]

    print(f'> Related labels: {relatedLabels}')

    # Search document collection

    docs = {}

    for label in relatedLabels:

        response = es.search(index=ELASTIC_INDEX_NAME, query={
            "fuzzy": {
                "description": {"value": label}
            }
        })

        for doc in response['hits']['hits']:
            _id = doc['_id']

            if _id in docs:
                docs[_id]['labels'].append(label)
            else:
                docs[_id] = {
                    'description': doc['_source']['description'],
                    'labels': [label]
                }

    # Convert docs dict to docs list

    result = []

    for _id, doc in docs.items():
        result.append({
            'id': _id,
            'description': doc['description'],
            'labels': doc['labels']
        })

    return {
        'labels': relatedLabels,
        'docs': result
    }


def getRelatedLabels(tx, labels, depth, useClassOf, useParentOf):
    relations = ':classOf|parentOf' if useClassOf and useParentOf else ':classOf' if useClassOf else ':parentOf'
    result = tx.run(
        f'MATCH path=(e1:Entity)-[{relations}*0..{depth}]->(e2:Entity) '
        'WHERE toLower(e1.label) IN $labels '
        'RETURN e2.label order by length(path);',
        labels=labels
    )
    return list(map(lambda l : l[0], result.values()))


@app.route("/api/data", methods=['POST'])
def load_data():
    id_field = request.form['id_field']
    body_field = request.form['body_field']
    file = request.files['file']

    # if id_field is not present then use default 'id'
    if id_field == None:
        id_field = 'id'
    # if body_field is not present then use default 'body'
    if body_field == None:
        body_field = 'body'
    # validate file extension is csv
    if file.filename.split('.')[-1] != 'csv':
        return "Invalid file extension", 415

    # rename csv header to id_field and body_field
    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    reader = csv.DictReader(stream)
    header = reader.fieldnames

    # check that header contains id_field and body_field
    if id_field not in header or body_field not in header:
        return "Invalid body or id", 400
    # check that id_field and body_field are not the same
    if id_field == body_field:
        return "Body and id cannot be equal", 400
    
    # rename id_field header to 'id'
    header[header.index(id_field)] = 'id'
    # rename body_field header to 'body'
    header[header.index(body_field)] = 'body'

    # load data to elasticsearch
    helpers.bulk(es, reader, index=ELASTIC_INDEX_NAME)
    
    return "Succesfully uploaded", 201


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('webapp/dist/js', path)

@app.route('/img/<path:path>')
def send_img(path):
    return send_from_directory('webapp/dist/img', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('webapp/dist/css', path)

@app.route('/favicon.ico')
def send_favicon(path):
    return send_from_directory('webapp/dist/favicon.ico', path)

@app.route('/')
def send_index():
    return send_from_directory('webapp/dist/', 'index.html')

@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    header['Access-Control-Allow-Headers'] = 'Content-Type'
    return response