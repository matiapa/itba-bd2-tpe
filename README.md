# Searchtastic

Searchtastic is a Polyglot Database Solution that combines the power of graph based data structures along with search efficient indexing to search for conceptual relationships in your datasets. Powered by both Neo4j and Elasticsearch, this database is incredibly Flexible. By simply editing the information stored in the Neo4j instance, the conceptual search engine can be tailored to suit any organization's needs.


# Documentation

You may find the API specification in docs/api.yaml, it's on the OpenAPI 3.0 format and can be visualized
with many online free tools.

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


### Import Neo4j Data
The following script will read RDF data from the WikiData dump and load it into Neo4J

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
# Configure Environment

Copy and Rename the .env-template file

```bash
cp .env-template .env
```
And fill all information fields in the newly created file to configure the Database

# Flask SetUp
Linux install of pip and requirements

```bash
sudo apt install python3-pip
pip install -r requirements.txt
```
Once installed, run the following commands

(Warning: both database instances must be running for the following commands to take effect properly)

```bash
flask run
```
# Frontend SetUp
## Project setup

Install Vue and Vue CLI from https://vue.js

On the webapp/ folder run the following commands

```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

NOTE: The production build will be generated on the webapp/dist folder and is served
statically by the Flask server

# Examples of API use

## Search for technology

The following request will search for the term 'technology' using the relations 'useClassOf' and 'useParentOf'
with a maximum relation depth of 1.

```
curl --location --request GET 'http://localhost:5000/api/search?query=technology&depth=1&useClassOf=1&useParentOf=1'
```

## Search for organisms

The following request will search for the term 'organisms' using the relations 'useClassOf' and 'useParentOf'
with a maximum relation depth of 2.

```
curl --location --request GET 'http://localhost:5000/api/search?query=technology&depth=2&useClassOf=1&useParentOf=1'
```
