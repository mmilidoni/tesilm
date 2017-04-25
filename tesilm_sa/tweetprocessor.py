from politician import Politician
from nbclassifier import NBClassifier
from etl import Etl
import json

class TweetProcessor:
    politicianList = []
    
    def __init__(self):
        t = Politician()
        self.politicianList = t.getList()
        self.classifier = NBClassifier()
        self.e = Etl()
        
    def process(self, jsonString):
        jsonData = json.loads(jsonString)
        if "lang" in jsonData and jsonData["lang"] == "en":
            output = []
            for politician in self.politicianList:
                givenName = politician["givenName"]
                familyName = politician["familyName"]
                if familyName in jsonString and givenName in jsonString:
                    if "text" in jsonData:
                        sentiment = self.classifier.classify(jsonData["text"])
                        self.e.put(jsonData, politician, sentiment)
                        output.append([politician, sentiment])
                    else:
                        raise Exception("No text in jsonData")
            return output
        else:
            raise Exception("Not an English tweet")

