from SPARQLWrapper import JSON
from SPARQLWrapper import SPARQLWrapper
import csv

class Politician:
    path = ""
    fileData = ""

    def __init__(self):
        self.fileData = "dbpedia_politicians_complete.csv"

    def getList(self):
        politicians = []
        with open(self.path + self.fileData, "r") as fin:
            reader = csv.DictReader(fin)
            politicians = [row for row in reader]
        return politicians

    def add(self, politicianDbpediaUri):
        sparql = SPARQLWrapper("http://localhost:8890/sparql")
        
        for r in self.getList():
            if politicianDbpediaUri == r["dbpediaURI"]:
                print "resource already there"
                return False        
        
        q = "SELECT * WHERE { ?politician owl:sameAs <" + politicianDbpediaUri + "> . ?politician yago-res:hasGivenName ?givenName . ?politician yago-res:hasFamilyName ?familyName . ?politician yago-res:hasGender ?gender . ?politician yago-res:isAffiliatedTo ?affiliatedTo . }"
        sparql.setQuery(q)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        if len(results["results"]["bindings"]) > 0:
            bind = results["results"]["bindings"][0]
            with open(self.fileData, "a") as fileout:
                fileout.write(bind["familyName"]["value"] + "," 
                    + bind["givenName"]["value"] + "," 
                    + bind["gender"]["value"] + "," 
                    + bind["affiliatedTo"]["value"] + "," 
                    + politicianDbpediaUri + "," 
                    + bind["politician"]["value"] + "\n"
                    )
            return True
        print "record not found"
        return False

#obj = Politician()
#l = obj.getList()
#
#for i in range(10):
#    print l[i]["dbpediaURI"]
#    
#obj.add("http://dbpedia.org/resource/Bill_Clinton")