# Searchtastic

A brief description of what this project does and who it's for


# Neo4j SetUp

### Neo4j Installation (skip this step if you already have a working instance)

Follow the instructions from the link below to get the Desktop Version

https://neo4j.com/download/

Install also the following Plugins:

-APOC

-Neosemantics

You can access the control panel here:
http://localhost:7474/browser/

(Replace 7474 with whatever port your Database is listening on)

### Create Constraint
```bash
CREATE CONSTRAINT n10s_unique_uri ON (r:Resource)
ASSERT r.uri IS UNIQUE
```

### Create Graph Config
```bash
CALL n10s.graphconfig.init({
  handleVocabUris: 'MAP'
})
```

### Import Data
```bash
WITH 'PREFIX neo: <neo4j://voc#>
CONSTRUCT { 
  ?entity a neo:Entity . 
  ?instance a neo:Entity .
  ?subclass a neo:Entity .
  ?instance neo:classOf ?entity .  
  ?instance neo:label ?instanceLabel .
  ?subclass neo:parentOf ?entity .  
  ?subclass neo:label ?subclassLabel .
  ?entity neo:label ?label . 
}
WHERE
{
  ?entity wdt:P31 ?instance .
  ?instance rdfs:label ?instanceLabel filter (lang(?instanceLabel) = "en").
  ?entity wdt:P279 ?subclass .
  ?subclass rdfs:label ?subclassLabel filter (lang(?subclassLabel) = "en").
  ?entity rdfs:label ?label filter (lang(?label) = "en").
 } LIMIT 50000' AS sparql

CALL n10s.rdf.import.fetch(
  'https://query.wikidata.org/sparql?query='+ apoc.text.urlencode(sparql),
  'Turtle' ,
  { headerParams: { Accept: "application/x-turtle" } }
)
YIELD terminationStatus, triplesLoaded, triplesParsed
RETURN terminationStatus, triplesLoaded, triplesParsed
```

# ElasticSearch SetUp

### ElasticSearch Installation (skip this step if you already have a working instance)
```bash
docker pull elasticsearch:7.14.1
docker run --name Myelastic -p 9200:9200 -p 9300:9300 -e"discovery.type=single-node" elasticsearch:7.14.1
```
Other useful commands
```bash
docker start Myelastic
docker stop Myelastic
docker ps
```


# Flask SetUp
Linux install of pip and flask

```bash
sudo apt install python3-pip
sudo apt install python3-flask
```
Once installed, run the following commands

```bash
pip install -r requirements.txt
flask run
```
