import csv
from nltk.classify import NaiveBayesClassifier
import nltk.classify.util
import os
import os.path
import pickle
import re

class NBClassifier:
    # This class implements a Naive Bayes Classifier
    # It uses a pickle previously created
    trainfeats = []
    testfeats = []
    classifierPickleFile = ""
    classifier = ""

    def __init__(self, classifierPickleFile="nbclassifier.pickle"):
        self.classifierPickleFile = os.path.dirname(__file__) + "/" + classifierPickleFile
        if os.path.isfile(self.classifierPickleFile):
            self.openClassifier()
        else:
            raise Exception("Pickle not found")

    def openClassifier(self):
        f = open(self.classifierPickleFile, 'rb')
        self.classifier = pickle.load(f)
        f.close()
        self.classifier.show_most_informative_features(3)

    def buildClassifier(self, neutral, annotatedCorpus):
        posSet = []
        negSet = []
        neuSet = []
        with open(annotatedCorpus, "r") as csvfile:
            r = csv.reader(csvfile, delimiter=",", quotechar="\"")
            for row in r:
                if len(row) > 4:
                    if row[1] == "positive":
                        posSet.append([self.cleanQuote(word) for word in row[4].split()])
                    elif row[1] == "negative":
                        negSet.append([self.cleanQuote(word) for word in row[4].split()])
                    elif row[1] == "neutral" and neutral:
                        neuSet.append([self.cleanQuote(word) for word in row[4].split()])

        posfeats = [(self.wordFeats(f), 'positive') for f in posSet]
        negfeats = [(self.wordFeats(f), 'negative') for f in negSet]
        neufeats = [(self.wordFeats(f), 'neutral') for f in neuSet]

        negcutoff = len(negfeats) * 3 / 4
        neucutoff = len(neufeats) * 3 / 4
        poscutoff = len(posfeats) * 3 / 4

        self.trainfeats = negfeats[:negcutoff] + posfeats[:poscutoff] + neufeats[:neucutoff]
        self.testfeats = negfeats[negcutoff:] + posfeats[poscutoff:] + neufeats[neucutoff:]
        print 'train on %d instances, test on %d instances' % (len(self.trainfeats), len(self.testfeats))

        self.classifier = NaiveBayesClassifier.train(self.trainfeats)
        print 'accuracy:', nltk.classify.util.accuracy(self.classifier, self.testfeats)
        self.classifier.show_most_informative_features(3)

        f = open(self.classifierPickleFile, 'wb')
        pickle.dump(self.classifier, f)
        f.close()

    def classify(self, text):
        return self.classifier.classify(self.wordFeats([self.cleanQuote(word) for word in text.split()]))

    def cleanQuote(self, w):
        return "".join(re.findall("[a-zA-Z]+", w.lower()))

    def wordFeats(self, words):
        return dict([(word, True) for word in words if word])
