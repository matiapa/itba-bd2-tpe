# Flask SetUp

```bash
pip install -r requirements.txt
flask run
```

# Neo4j SetUp

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
