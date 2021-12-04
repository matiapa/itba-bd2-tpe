from flask import Flask
from flask import request
from neo4j import GraphDatabase
from elasticsearch import Elasticsearch, helpers
import csv
import io

app = Flask(__name__)

STOP_WORDS = ['and','or','a','of']

neo = GraphDatabase.driver('neo4j://localhost:7687')
es = Elasticsearch(host = "localhost", port = 9200)

@app.route("/search")
def search():
    depth = int(request.args.get('depth') or '1')
    useClassOf = bool(int(request.args.get('useClassOf') or '1'))
    useParentOf = bool(int(request.args.get('useParentOf') or '1'))
    searchStr = request.args.get('query')

    if not useClassOf and not useParentOf:
        return "At least one relationship must be used", 404
    if searchStr == None:
        return "Missing query parameter", 404

    # Prepare labels and find related ones

    searchStr = searchStr.lower()
    words = searchStr.split(" ")
    words = list(filter(lambda l : l not in STOP_WORDS, words))
    labels = words + [searchStr]

    session = neo.session(database = "bd2")
    relatedLabels = session.write_transaction(getRelatedLabels, labels, depth, useClassOf, useParentOf)

    # Search document collection

    mapQuery = lambda label : es.search(index="body", query={
        "fuzzy": {
            "description": {"value": label}
        }
    })
    results = list(map(mapQuery, relatedLabels))

    docs = []
    for res in results:
        for hit in res['hits']['hits']:
            docs.append(hit["_source"])

    return {
        'labels': relatedLabels,
        'docs': docs
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


@app.route("/data", methods=['POST'])
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
        return "Invalid file extension", 404

    # rename csv header to id_field and body_field
    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    reader = csv.DictReader(stream)
    header = reader.fieldnames

    # check that header contains id_field and body_field
    if id_field not in header or body_field not in header:
        return "Invalid header", 404
    # check that id_field and body_field are not the same
    if id_field == body_field:
        return "Headers can't be equal", 404
    
    # rename id_field header to 'id'
    header[header.index(id_field)] = 'id'
    # rename body_field header to 'body'
    header[header.index(body_field)] = 'body'

    # load data to elasticsearch
    helpers.bulk(es, reader, index='body')
    
    return "Succesfully Uploaded", 201