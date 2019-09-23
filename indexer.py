from Corpus import Corpus
from Tokenizer import Tokenizer
import mysql.connector
from math import log10
from math import sqrt
from bs4 import BeautifulSoup
'''
    This model performs as an indexer, it includes all the index
    building processes by transfering data to the mysql database.
    We have 5 tables:
    
    Doc - [doc_id], [url], [brief website description]
    TokenT - [unique tokens]
    Web_index - [token], [doc_id], [tf], [wt]
    Ranking - [token], [doc_id], [tf-idf]
    Normalize - [token], [doc_id], [normalized tf-idf]
'''
    
class Indexer():
    def __init__(self):
        self.mydb = mysql.connector.connect(
               host="localhost",
               user="root",
               password="mf15837165780",
               database="web",
               buffered=True,
               auth_plugin='mysql_native_password'
               )
        self.mycursor = self.mydb.cursor()
        self.total = 36265
        

    def build_index(self):
        '''
        This function build the inverted index, it inserts the url to the
        doc Table with a doc_id, and insert each token to tokenT table
        and insert token, doc_id, term frequency and weight into the web_index
        Table
        '''
        
        c = Corpus()
        t = Tokenizer()
    
        for url,name in c.get_file_name():
            if len(url)>1000:
                continue
            result = t.tokenize(name)
            if len(result)==0:
                continue
            print(url)
            doc_id=1
            
            
            #Insert URL to table DOC
            sql="INSERT INTO web.doc(url) values (%s)"
            val=(url,)
            self.mycursor.execute(sql,val)
            self.mydb.commit()
            
            print(self.mycursor.rowcount, "was inserted in URL.")

            print(url)
            s_sql="select id from doc where url=%s"
            self.mycursor.execute(s_sql,val)
            myresult = self.mycursor.fetchone()
            doc_id = myresult[0]
            print ("DOC_ID IS "+ str(doc_id))

            #Insert token, doc_id, tf into web_index
            t_sql="INSERT INTO web.web_index(token, doc_id, tf, wt) values (%s,%s,%s,%s)"
            
            t_val=[]
            for token in result.keys():
               t_val.append((token, doc_id, result[token][0], result[token][1]))

            #print(t_val)
            

            self.mycursor.executemany(t_sql,t_val)

            self.mydb.commit()
            print(self.mycursor.rowcount, "was inserted in WEB_INDEX.")


            #insert into TokenT table
            count=0
            for token in result.keys():
                tq="Insert ignore into tokenT values (%s)"
                tv=(token,)
                self.mycursor.execute(tq,tv)
                self.mydb.commit()
                count+=1

            print("inserted "+ str(count) +" Tokens")
            

    def calculate(self, tf, df):
        '''
        This function calculate the tf-idf value with tf and df given
        in the parameter
        '''
        
        result = 1.0 + log10(float(tf))
        result *= log10(self.total/df)
        return result           

    def update(self):
        '''
        This function took all the token and document id pair and
        calculate the tf-idf and update them into the ranking Table
        '''
        
        #take all the tokens out of database
        self.mycursor.execute("Select token from tokenT")
        myresult = self.mycursor.fetchall()
        count=0
        for token in myresult:
            print("**********Token is "+ str(token)+"  ***********")
            c_sql="select count(*) from web_index where token=%s"
            c_val=token
            self.mycursor.execute(c_sql,c_val)
            c_result= self.mycursor.fetchone()
            df=c_result[0]
            print("************* DF IS "+str(df))

            t_sql="select token, doc_id, tf from web_index where token=%s"
            self.mycursor.execute(t_sql, c_val)
            t_list= self.mycursor.fetchall()
            u_val=[]
            for toke, doc_id, tf in t_list:
                #print ("Token is "+ str(token)+"  doc_id is "+ str(doc_id) + "  tf is "+ str(tf))
                tfidf = self.calculate(tf, df)
                #print("TF-IDF is "+ str(tfidf))

                u_val.append((toke,doc_id,tfidf))
                count+=1
                
            u_sql="insert into ranking(token, doc_id, tf_idf) values (%s, %s, %s)"

            self.mycursor.executemany(u_sql, u_val)
            self.mydb.commit()
            print(self.mycursor.rowcount, "was inserted in RANKING.")
                
    def normalize(self):
        '''
        This function calculates the normalized tf-idf and insert
        them into a new table normaliza
        '''
        #get all tf-idf of a dic_id
        #select doc_id
        self.mycursor.execute("select id from doc")
        myresult= self.mycursor.fetchall()
        for doc_id in myresult:
            print("**********Doc ID is "+str(doc_id)+" ********")
            #get all tf-idf
            tf_sql="select * from ranking where doc_id = %s"
            tf_val=doc_id
            self.mycursor.execute(tf_sql, tf_val)
            tf_result=self.mycursor.fetchall()

            sqrsum=0
            for tf_idf in tf_result:
                sqrsum+=tf_idf[2]**2

            doc_length= sqrt(sqrsum)
            i_val=[]
            for toke,doc_id, tf_idf in tf_result:
                norm = tf_idf/doc_length
                i_val.append((toke, doc_id, norm))         
     
            i_sql ="insert into normalize(token, doc_id, nmlz) values(%s, %s, %s)"
            self.mycursor.executemany(i_sql, i_val)
            self.mydb.commit()
            print(self.mycursor.rowcount, "was inserted in Normalize")
                       

    def get_description(self):
        '''
        This function gets all the url, finds their description text
        and update them to the database
        '''
        #get doc_id
        self.mycursor.execute("select id,url from doc")
        myresult= self.mycursor.fetchall()
        for doc_id, url in myresult:
            #print("**********Doc ID is "+str(doc_id)+" ********")
            c= Corpus()
            name = c.url_to_dir(url)
            #print("Name is "+ name)
            with open (name,"rb") as file:
                content = file.read()
                soup = BeautifulSoup(content, "lxml")
                metas = soup.find_all("meta")
                result = ''
                for meta in metas:
                    if ('content' in meta.attrs) and ('name' in meta.attrs) and \
                       ((meta.attrs['name'] == 'description') or (meta.attrs['name'] == 'keywords')):
                        result = " ".join(meta.attrs['content'].split())
  
                    
                #if html doesn't have description tag
                if result == '':
                    script = soup.find(["h1", "h2", "h3","h4","h5", "strong", "title","b"])
                    if script:
                        temp = " ".join(script.text.split())
                        result += temp if len(temp) < 200 else ""
                print(result)
                i_sql ="update doc set description =%s where id = %s"
                i_val=(result, doc_id)
                self.mycursor.execute(i_sql, i_val)
                self.mydb.commit()
                print(self.mycursor.rowcount, "was inserted in DOC , DOC ID IS "+str(doc_id))
        

if __name__ == "__main__":
    i= Indexer()
    i.get_description()
    

