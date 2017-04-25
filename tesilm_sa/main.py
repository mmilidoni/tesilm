from ScrolledText import ScrolledText
from Tkinter import *
from politician import Politician
from tweetprocessor import TweetProcessor

class App:

    def __init__(self, master):
        self.tweetProcessorObject = TweetProcessor()
        self.politicianObject = Politician()

        # tweet processor frame
        rowTweetProcessor = 0
        tweetProcessorFrame = LabelFrame(master, text="Tweet Processor")
        tweetProcessorFrame.grid(row=rowTweetProcessor, column=0)
        
        ## add tweet
        lblAddTweet = Label(tweetProcessorFrame, text="Add Tweet (json): ",
                            anchor='w', justify='left')
        self.txtAddTweet = Text(tweetProcessorFrame, height=10)
        lblAddTweet.grid(row=0, column=0)
        self.txtAddTweet.grid(row=1, column=0)
        btnAddTweet = Button(tweetProcessorFrame, text="Add", command=self.addTweet)
        btnAddTweet.grid(row=2, column=0)
        
        # politician frame
        rowPolitician = 1
        politicianFrame = LabelFrame(master, text="Politician")
        politicianFrame.grid(row=rowPolitician, column=0)
        
        ## add politician
        lblAddPolitican = Label(politicianFrame, text="Add Politician (dbpedia URI): ",
                                anchor='w', justify='left')
        self.entryAddPolitician = Entry(politicianFrame, width=40)
        lblAddPolitican.grid(row=0, column=0)
        self.entryAddPolitician.grid(row=0, column=1)
        btnAddPolitician = Button(politicianFrame, text="Add", command=self.addPolitician)
        btnAddPolitician.grid(row=0, column=2)
        ## list politicians
        btnListPoliticians = Button(politicianFrame, text="List", command=self.listPoliticians)
        btnListPoliticians.grid(row=1, column=0, columnspan=3)
        
        # output frame
        rowOutputFrame = 2
        outputFrame = LabelFrame(master, text="Output")
        outputFrame.grid(row=rowOutputFrame, column=0, sticky=W + E + N + S)
        self.txtOutputFrame = ScrolledText(outputFrame, width=160)
        self.txtOutputFrame.pack(fill=BOTH, expand=1)
        self.txtOutputFrame.config(wrap=NONE)
    
    def addTweet(self):
        try:
            output = self.tweetProcessorObject.process(self.txtAddTweet.get(1.0, END))
            if len(output) == 0:
                out = "Match politician <-> tweet not found"
            else:
                out = ""
                out += str(len(output)) + " sentiments added\n"
                out += "--------  DETAILS  ------------\n"
                for [politician, sentiment] in output:
                    out += "Politician: " + politician["familyName"] + " " + politician["givenName"] + "\n"
                    out += sentiment.upper() + " sentiment\n"
                    out += "-------------------------------\n"
            self.writeOutput(out)
        except Exception as eDetail:
            self.writeOutput(eDetail)
            raise
                
    def addPolitician(self):
        try:
            if self.politicianObject.add(self.entryAddPolitician.get()):
                self.writeOutput("Politician added")
            else:
                self.writeOutput("Internal error")
        except Exception as eDetail:
            self.writeOutput(eDetail)
            raise
            
    def listPoliticians(self):
        out = ""
        for politician in self.politicianObject.getRawList():
            out += politician
        self.writeOutput(out)
        
    def writeOutput(self, text):
        #self.txtOutputFrame.config(state=NORMAL)
        self.txtOutputFrame.delete(1.0, END)
        self.txtOutputFrame.insert(END, text)
        #self.txtOutputFrame.config(state=DISABLED)


def center(toplevel):
    toplevel.update_idletasks()
    w = toplevel.winfo_screenwidth()
    h = toplevel.winfo_screenheight()
    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = w / 2 - size[0] / 2
    y = h / 2 - size[1] / 2
    toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))
    
root = Tk()
root.title("Twitter Sentiment Analysis Manager")
#root.minsize(800, 400)
App(root)
center(root)
root.mainloop()

#if __name__ == "__main__":
#    pt = TweetProcessor()
#    pt.process('{"created_at":"Sat Aug 21 06:30:00 +0000 2015","id":627365646456623104,"id_str":"627365646456623104","text":"Bill Clinton is terrible!","truncated":false,"in_reply_to_status_id":null,"in_reply_to_status_id_str":null,"in_reply_to_user_id":null,"in_reply_to_user_id_str":null,"in_reply_to_screen_name":null,"user":{"id":2394398282,"id_str":"2394398282","name":"\u5c11\u5e74\u53f8\u4ee4\u5b98@\u30ea\u30af","screen_name":"lockon85193738","location":"","url":null,"description":"\u4e16\u754c\u6700\u5f31\u306e\u7537","protected":false,"verified":false,"followers_count":158,"friends_count":204,"listed_count":12,"favourites_count":2243,"statuses_count":13637,"created_at":"Mon Mar 17 13:28:08 +0000 2014","utc_offset":null,"time_zone":null,"geo_enabled":false,"lang":"en","contributors_enabled":false,"is_translator":false,"profile_background_color":"C0DEED","profile_background_image_url":"http:\/\/abs.twimg.com\/images\/themes\/theme1\/bg.png","profile_background_image_url_https":"https:\/\/abs.twimg.com\/images\/themes\/theme1\/bg.png","profile_background_tile":false,"profile_link_color":"0084B4","profile_sidebar_border_color":"C0DEED","profile_sidebar_fill_color":"DDEEF6","profile_text_color":"333333","profile_use_background_image":true,"profile_image_url":"http:\/\/pbs.twimg.com\/profile_images\/626315196970110976\/GDt0wiOG_normal.jpg","profile_image_url_https":"https:\/\/pbs.twimg.com\/profile_images\/626315196970110976\/GDt0wiOG_normal.jpg","profile_banner_url":"https:\/\/pbs.twimg.com\/profile_banners\/2394398282\/1438160154","default_profile":true,"default_profile_image":false,"following":null,"follow_request_sent":null,"notifications":null},"geo":null,"coordinates":null,"place":null,"contributors":null,"retweet_count":0,"favorite_count":0,"entities":{"hashtags":[],"trends":[],"urls":[],"user_mentions":[],"symbols":[]},"favorited":false,"retweeted":false,"possibly_sensitive":false,"filter_level":"low","lang":"en","timestamp_ms":"1438410600662"}')
