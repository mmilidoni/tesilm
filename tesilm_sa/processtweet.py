from politician import Politician
from nbclassifier import NBClassifier
from etl import Etl

class ProcessTweet:
    politicianList = []
    
    def __init__(self):
        t = Politician()
        self.politicianList = t.getList()
        self.classifier = NBClassifier()
        
    def process(self, jsonString):
        if "lang" in jsonString and jsonString["lang"] == "en":
            for politician in self.politicianList:
                givenName = politician["givenName"]
                familyName = politician["familyName"]
                if familyName in line and givenName in line:
                    jsonData = eval(jsonString)
                    if "text" in jsonData:
                        jsonData["sentiment_analysis"] = self.classifier.classify(jsonData["text"])
                        e = Etl()
                        e.put(jsonData)
                    else:
                        raise Exception("No text in jsonData")
                else:
                    raise Exception("Polician not found")
        else:
            raise Exception("Not an English tweet")

