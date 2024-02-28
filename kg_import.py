from neo4j import GraphDatabase, Driver, AsyncGraphDatabase, AsyncDriver
import re
from similarity_util import getIptcMediaTopic

URI = "<write uri to neo4j database>"
AUTH = ("neo4j", "<write your api key here>")

def update_IPTC_MediaTopics_level_info(label_name, level):
    _get_connection().execute_query("MATCH (t:IPTC_Media_Topic) WHERE t.name = $label_name SET t.level = $level RETURN elementId(t);", label_name=label_name, level = level )


def update_IPTC_MediaTopics_relationships(label_names, level):
    if level > 1:
        child_name = label_names[level]
        parent_name = label_names[level-1]
        _get_connection().execute_query("MATCH (parent:IPTC_Media_Topic) MATCH (child:IPTC_Media_Topic) WHERE parent.name = $parent_name and child.name = $child_name MERGE (child)-[:HAS_PARENT]->(parent);", parent_name=parent_name, child_name = child_name )


def update_DB_forIPTC_MediaTopics(label_names, level):
    print("Inside update()...")
    if level == 1:
        print("Inside update() level == 1 ...")
        try:
            _get_connection().execute_query("MATCH (t:IPTC_MediaTopic) where t.name=$name SET t.level = $level RETURN elementId(t);", name=label_names[1], level=level)[0][0][0]
        except Exception as e:
            _get_connection().execute_query("MERGE (t:IPTC_MediaTopic {name: $name, level: $level}) RETURN elementId(t);", name=label_names[1], level=level)
    

    elif level > 1:
        print("Inside update() level > 1 ...")
        c_name = label_names[level]
        p_name = label_names[level-1]
        c_id = [0]
        print("calling _get_connection() c_id[0] = ...")
        try:
            c_id[0] = _get_connection().execute_query("MATCH (t:IPTC_MediaTopic) where t.name=$name SET t.level = $level RETURN elementId(t);", name=c_name, level = level)
        except Exception as e:
          print("child not exists", str(e))
          _get_connection().execute_query("MERGE (c:IPTC_MediaTopic {name: $name, level: $level}) RETURN elementId(c);", name=c_name, level=level)
    

        print("calling _get_connection() parent rel... ...")
        _get_connection().execute_query("MATCH (pt:IPTC_MediaTopic) where pt.name=$p_name MATCH (ct:IPTC_MediaTopic) WHERE  ct.name=$c_name MERGE (ct)-[:HAS_PARENT]->(pt);", p_name=p_name, c_name=c_name )



def prepare_DB_forIPTC_MediaTopics(label_names, level):
    if level == 1:
        _get_connection().execute_query("MERGE (t:IPTC_MediaTopic {name: $name, level: $level}) RETURN elementId(t);", name=label_names[1], level=level)[0][0][0]
    
    elif level > 1:
        c_name = label_names[level]
        p_name = label_names[level-1]
        c_id = [0]
        c_id[0] = _get_connection().execute_query("MERGE (t:IPTC_MediaTopic {name: $name, level: $level}) RETURN elementId(t);", name=c_name, level = level)[0][0][0]
        _get_connection().execute_query("MATCH (pt:IPTC_MediaTopic) where pt.name=$p_name MATCH (ct:IPTC_MediaTopic) WHERE  elementId(ct) in $c_id MERGE (ct)-[:HAS_PARENT]->(pt);", p_name=p_name, c_id=c_id )


def _get_connection() -> Driver:
    driver = GraphDatabase.driver(URI, auth=AUTH)
    driver.verify_connectivity()

    return driver

def findEventByArticleUrl(url):
    return _get_connection().execute_query("MATCH (a:Article)-[r1]->(e:Event) where a.url = $url RETURN elementId(e);", url=url)[0][0][0]


def createCSVFILENAMEInDB(name):
    print("CSV-FILE-NAME::    "+name)
    return _get_connection().execute_query("MERGE (n:DataFile {name: $name}) RETURN elementId(n);", name=name)[0][0][0]

def findCSVFILENAMEInDB():
    print("Looking for data file name in KG")
    return _get_connection().execute_query("MATCH (p:DataFile) RETURN p.name;")

def updateCSVFileNameInDB(name):
    print("Updated file name: " + name)
    return _get_connection().execute_query("MATCH (p:DataFile) SET p.name = $name RETURN elementId(p);", name=name)[0][0][0]

def findArticleWithUrl(url):
    print("Looking for article by URL")
    return _get_connection().execute_query("MATCH (a:Article) where a.url = $url RETURN elementId(a);", url=url)[0]


def updateArticleSummaryInDB(url,summary):
    print("Calling neo4j..method to set new summary...")
    return _get_connection().execute_query("MATCH (a:Article) where a.url=$url SET a.summary = $summary RETURN elementId(a);", url=url, summary=summary)[0][0][0]



def createArticleInDB(url, title, publicationDate, publisher, summary):
    return _get_connection().execute_query("MERGE (a:Article {url: $url, title: $title, publicationDate: $publicationDate, publisher: $publisher, summary: $summary}) RETURN elementId(a);", url=url, title=title, publicationDate= publicationDate, publisher=publisher, summary=summary)[0][0][0]





def createEventInDB(eventName, articleRef):
    return _get_connection().execute_query("MERGE (e:Event {name: $name, articleRef: $articleRef}) RETURN elementId(e);", name=eventName, articleRef=articleRef)[0][0][0]


def createIPTC_MediaTopic_InDB(eventType):
    iptcMediaTopc = getIptcMediaTopic(eventType)
    print("IPTC_MediaTopic_InDB::    "+iptcMediaTopc)
    return _get_connection().execute_query("MERGE (iptc:IPTC_MediaTopic {name: $name}) RETURN elementId(iptc);", name=iptcMediaTopc)[0][0][0]


def createEventTypeInDB(name):
    name =cleanupString(name).lower()
    print("EventTypeInDB::    "+name)
    if len(name) == 0:
        name = "None"
    return _get_connection().execute_query("MERGE (et:EventType {name: $name}) RETURN elementId(et);", name=name)[0][0][0]

def createArticle_to_Event_relation(a_id,e_id):
    _get_connection().execute_query("MATCH (a:Article) WHERE elementId(a) in $a_id MATCH (e:Event) WHERE elementId(e) in $e_id  MERGE (a)-[:HAS_EVENT]->(e);", a_id=a_id,e_id=e_id )

def createEvent_to_EventType_relation(e_id,et_id):
    _get_connection().execute_query("MATCH (e:Event) WHERE elementId(e) in $e_id MATCH (et:EventType) WHERE elementId(et) in $et_id  MERGE (e)-[:HAS_TYPE]->(et);", e_id=e_id,et_id=et_id )

def deleteEvent_to_EventType_relation(e_id):
    _get_connection().execute_query("MATCH (e:Event)-[r]->(et:EventType) WHERE elementId(e) in $e_id delete r;", e_id=e_id )

def deleteEvent_to_IPTC_relation(e_id):
    _get_connection().execute_query("MATCH (e:Event)-[r]->(iptc:IPTC_MediaTopic) WHERE elementId(e) in $e_id delete r;", e_id=e_id )

def createEvent_to_IPTC_relationByName(e_id,name):
    _get_connection().execute_query("MATCH (e:Event) WHERE elementId(e) in $e_id MATCH (t:IPTC_MediaTopic) WHERE t.name = $name  MERGE (e)-[:HAS_IPTC_MEDIA_TOPIC]->(t);", e_id=e_id,name=name )


def createEvent_to_IPTC_relation(e_id,iptc_id):
    _get_connection().execute_query("MATCH (e:Event) WHERE elementId(e) in $e_id MATCH (iptc:IPTC_MediaTopic) WHERE elementId(iptc) in $iptc_id  MERGE (e)-[:HAS_IPTC_MEDIA_TOPIC]->(iptc);", e_id=e_id,iptc_id=iptc_id )

def createEvent_to_InvolvedCountry_relation(e_id,loc_id):
    _get_connection().execute_query("MATCH (e:Event) WHERE elementId(e) in $e_id MATCH (loc:Location) WHERE elementId(loc) in $loc_id  MERGE (e)-[:INVOLVED_COUNTRY]->(loc);", e_id=e_id,loc_id=loc_id )


def createEvent_to_Location_relation(e_id,loc_id):
    _get_connection().execute_query("MATCH (e:Event) WHERE elementId(e) in $e_id MATCH (loc:Location) WHERE elementId(loc) in $loc_id  MERGE (e)-[:HAPPENED_IN]->(loc);", e_id=e_id,loc_id=loc_id )

def createEvent_to_Person_relation(e_id,p_id):
    _get_connection().execute_query("MATCH (e:Event) WHERE elementId(e) in $e_id MATCH (p:Person) WHERE elementId(p) in $p_id  MERGE (e)-[:INVOLVED_PERSON]->(p);", e_id=e_id,p_id=p_id )

def createLocationInDB(name):
    name = cleanupString(name)
    print("LocationInDB::    "+name)
    if len(name) == 0:
        name = "None"
    return _get_connection().execute_query("MERGE (n:Location {name: $name}) RETURN elementId(n);", name=name)[0][0][0]




def createPersonInDB(name):
    name = cleanupString(name)
    print("PersonInDB::    "+name)
    if len(name) == 0:
        name = "None"
    return _get_connection().execute_query("MERGE (n:Person {name: $name}) RETURN elementId(n);", name=name)[0][0][0]

def cleanupString(text):
    print("cleaning text: "+text)
    text = re.sub(r'"', '', text)
    text = re.sub(r',', '', text)
    text = re.sub(r'\[|\]', '', text)
    text = re.sub(r':', '', text)
    text = text.strip()
    text = re.sub(r'\[.*?\]|\{.*?\}|\(.*?\)|\<.*?\>', '', text)
    
    if text.endswith(","):
        text = text[:-1]
    if text.endswith('-'):
        text = text[:-1]
    if text.endswith("\\"):
        text = text[:-1]
    if text.startswith('-'):
        text = text[1:]
    if text.startswith("IPTC -"):
        text = text[6:]
    if text.startswith("IPTC news code: "):
        text = text[16:]
    if text.startswith("IPTC news code"):
        text = text[14:]
    if text.startswith("IPTC code"):
        text = text[9:]
    if text.startswith("IPTC"):
        text = text[4:]
        
    text = text.strip()
    return text