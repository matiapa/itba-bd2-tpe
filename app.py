from flask import Flask
from flask import request
from neo4j import GraphDatabase
from elasticsearch import Elasticsearch

app = Flask(__name__)

STOP_WORDS = ['and','or','a','of']

neo = GraphDatabase.driver('neo4j://localhost:7687')
els = Elasticsearch()

@app.route("/search")
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

    session = neo.session()
    relatedLabels = session.write_transaction(getRelatedLabels, labels, depth, useClassOf, useParentOf)

    # Search document collection

    mapQuery = lambda label : els.search(index="docs", query={
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
    relations = ':CLASS_OF|PARENT_OF' if useClassOf and useParentOf else ':CLASS_OF' if useClassOf else ':PARENT_OF'
    result = tx.run(
        f'MATCH (e1:Entity)-[{relations}*0..{depth}]->(e2:Entity) '
        'WHERE toLower(e1.label) IN $labels '
        'RETURN e2.label;',
        labels=labels
    )
    return list(map(lambda l : l[0], result.values()))