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
    
