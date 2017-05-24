import mysql.connector
import datetime

class Etl:
    # This class manages OLAP database
    
    # constants
    GENDER_MALE = 1
    GENDER_FEMA = 2
    PARTY_REPUB = 1
    PARTY_DEMOC = 2

    def __init__(self):
        self.cnx = mysql.connector.connect(user='olap_test', password='olap_test', database='olap_test')
        self.cursor = self.cnx.cursor()

    def put(self, tweet, politician, sentiment):
        # This method records the sentiment 
        # into the OLAP database
        
        # processing data
        dTemp = tweet["created_at"][4:10]+" "+tweet["created_at"][-4:]
        saDate = self.__putDate(datetime.datetime.strptime(dTemp, "%b %d %Y").strftime('%Y-%m-%d'))
        saParty = self.PARTY_DEMOC if politician["affiliatedTo"][35:45] == "Democratic" else self.PARTY_REPUB
        saGender = self.GENDER_FEMA if politician["gender"][-6:] == "female" else self.GENDER_MALE
        
        # politician dimension
        saPolitician = self.__putPolitician({
                "name": politician["familyName"]+" "+politician["givenName"], 
                "dbpedia_resource": politician["dbpediaURI"],
                "gender_id": saGender,
                "party_id": saParty
                })["id"]
        
        # date dimension
        sa1 = {"date_id": saDate,
                "politician_id": saPolitician,
                }
        
        # sentiment analysis fact
        return self.__putSentimentAnalysis(sa1, sentiment)
        
    def __putDate(self, date):
        # This method manages the date dimension
        # If date doesn't exists, it will be created
        year = date[0:4]
        month = date[5:7]
        self.cursor.execute("SELECT count(*) FROM dim_date WHERE date = %s ", [date])
        res = self.cursor.fetchone()
        if res[0] == 0:
            self.cursor.execute("INSERT INTO dim_date (date, month, year) VALUES (%s, %s, %s)", [date, month, year])
            self.cnx.commit()
        return date

    def __putPolitician(self, politician):
        # This method manages the politician dimension
        # If politician doesn't exists, it will be created

        self.cursor.execute("SELECT id FROM dim_politician WHERE dbpedia_resource = %s ", 
                [politician["dbpedia_resource"]])
        res = self.cursor.fetchone()
        if not res:
            self.cursor.execute("INSERT INTO dim_politician (name, dbpedia_resource, gender_id, party_id) "
                   "VALUES (%s, %s, %s, %s)", 
                   [politician["name"], politician["dbpedia_resource"], politician["gender_id"], politician["party_id"]])
            self.cnx.commit()
            politician["id"] = self.cursor.lastrowid
        else:
            politician["id"] = res[0]
        return politician

    def exportGephi(self, filename):
        self.cursor.execute("SELECT SA.positive, SA.negative, SA.neutral,\
                SA.date_id date,\
                P.id politician_id, P.name politician_name, P.gender, P.party\
                FROM fact_sentiment_analysis SA \
                JOIN dim_politician P ON SA.politician_id = P.id \
                ")
        rows = self.cursor.fetchall()

        import xml.etree.cElementTree as ET

        root = ET.Element("gexf")
        root.attrib["xmlns"] = "http://www.gexf.net/1.1draft"
        root.attrib["xmlns:xsi"] = "http://www.w3.org/2001/XMLSchema-instance"
        root.attrib["xsi:schemaLocation"] = "http://www.gexf.net/1.1draft http://www.gexf.net/1.1draft/gexf.xsd"
        root.attrib["version"] = "1.3"

        graph = ET.Element("graph", mode="static", defaultedgetype="undirected")
        
        graphAttribs = ET.Element("attributes")
        graphAttribs.attrib["class"] = "node"
        graphAttribs.attrib["mode"] = "dynamic"
        graphAttribs.append(ET.Element("attribute", title="Appreciation", type="float", id="appreciation"))
        graphAttribs.append(ET.Element("attribute", title="TotalSentiment", type="int", id="total_sentiment"))
        graphAttribs.append(ET.Element("attribute", title="Gender", type="string", id="gender"))
        #graphAttribs.append(ET.Element("attribute", title="Party", type="string", id="party"))
        graph.append(graphAttribs)

        nodes = ET.Element("nodes")
        edges = ET.Element("edges")
        nodesDict = {}
        edgesList = []

        for row in rows:
            saPositive = float(row[0])
            saNegative = float(row[1])
            saNeutral  = float(row[2])
            totalSentiment = int(saPositive + saNeutral + saNegative)
            appr = str(round(float(saPositive / float(totalSentiment)), 4))
            date = str(row[3].isoformat()).replace("-", "")
            politicianId = str(row[4])
            politicianName = str(row[5])
            politicianGender = str(row[6])
            politicianParty = str(row[7])

            if not politicianId in nodesDict.keys():
                node = ET.Element("node", id=politicianId, label=politicianName)
                attvalues = ET.Element("attvalues")
                attvalueGender = ET.Element("attvalue")
                attvalueGender.attrib["for"] = "gender"
                attvalueGender.attrib["value"] = politicianGender
                attvalueParty = ET.Element("attvalue")
                attvalues.append(attvalueGender)
                attvalueTotalSentiment = ET.Element("attvalue")
                attvalueTotalSentiment.attrib["for"] = "total_sentiment"
                attvalueTotalSentiment.attrib["value"] = str(totalSentiment)
                attvalues.append(attvalueTotalSentiment)

                node.append(attvalues)
                #edgesList.append(ET.Element("edge", source=politicianId, target=politicianGender))
                edgesList.append(ET.Element("edge", source=politicianId, target=politicianParty))
            else:
                node = nodesDict[politicianId]

            attvalues = node.find("attvalues")
            value = ET.Element("attvalue", value=appr, start=date, end=date)
            value.attrib["for"] = "appreciation"
            attvalues.append(value)

            nodesDict[politicianId] = node

            if not politicianParty in nodesDict.keys():
                nodesDict[politicianParty] = ET.Element("node", id=politicianParty, label=politicianParty)
                attvaluesPol = ET.Element("attvalues")
                valuePol = ET.Element("attvalue", value="3000")
                valuePol.attrib["for"] = "total_sentiment"
                attvaluesPol.append(valuePol)
                valuePol = ET.Element("attvalue", value="neutral")
                valuePol.attrib["for"] = "gender"
                attvaluesPol.append(valuePol)
                valuePol = ET.Element("attvalue", value="1")
                valuePol.attrib["for"] = "appreciation"
                attvaluesPol.append(valuePol)
                nodesDict[politicianParty].append(attvaluesPol)


            #if not politicianGender in nodesDict.keys():
            #    nodesDict[politicianGender] = ET.Element("node", id=politicianGender, label=politicianGender)

        for k in nodesDict.keys():
            nodes.append(nodesDict[k])

        for edge in edgesList:
            edges.append(edge)

        graph.append(nodes)
        graph.append(edges)
        root.append(graph)
        tree = ET.ElementTree(root)
        if filename.endswith(".gexf"):
            tree.write(filename)
        else:
            tree.write(filename + ".gexf")

        return True


    def __putSentimentAnalysis(self, keys, sa):
        # This method manages the sentiment analysis fact
        # If record doesn't exist, it will be created, 
        # otherwise it will increase the scoring points
        
        self.cursor.execute("SELECT id FROM fact_sentiment_analysis " 
                " WHERE date_id = %s AND politician_id = %s ", 
                [keys["date_id"], keys["politician_id"]])
        res = self.cursor.fetchone()
        if not res:
            self.cursor.execute("INSERT INTO fact_sentiment_analysis "
                "(date_id, politician_id, "+sa+") "
                "values (%s, %s, %s)",
                [keys["date_id"], keys["politician_id"], 1])
            self.cnx.commit()
            return self.cursor.lastrowid
        else:
            self.cursor.execute("UPDATE fact_sentiment_analysis SET " + sa + " = " + sa + " + 1 "
                    " WHERE id = %s",
                [res[0]])
            self.cnx.commit()
            return res[0]
        return False
    
