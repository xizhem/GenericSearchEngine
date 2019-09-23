import mysql.connector
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from math import log2
from math import log10
from math import sqrt
from collections import defaultdict
import re

'''
    This model performs the search and retrieve function of the search engine
'''

class Search():
    def __init__(self):
        self.stemmer = PorterStemmer()
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
        
    def search(self,query):
        '''
        This function performs the overall searching process including
        tokenize and normalize the query, getting all candidate document id
        and ranking them by score
        '''
        #tokenize the query
        q_dict = {}
        stop_words = set(stopwords.words('english'))
        pat = re.compile(r'[a-zA-Z0-9]+')
        words = pat.findall(query)
        for i in words:
            # Remove any token with more than 4 digits anywhere inside
            if re.match(r"^.*[0-9]{4,}.*$",i):
                continue
            i=i.lower()
            if i not in stop_words and len(i)<100:
                word = self.stemmer.stem(i)
                if word not in q_dict:
                    q_dict[word] = 0
                q_dict[word] +=1
                
                    
        print(q_dict)
        
        #normalize query dictionary
        q_dict= self.normalize(q_dict)
        
        #calculates the number of words the document at least have
        select = int(log2(len(q_dict)))+1

        # get a list of candidate document id
        id_dict=defaultdict(int)
        for word in q_dict.keys():
            for doc_id in self.getid(word):
                id_dict[doc_id[0]]+=1

        print("***before limt len is "+str(len(id_dict)))              



        # filtering the document id using the At Least Have number
        #log2(query length)+1
        result_list=[]
        for doc_id in id_dict.keys():
            if id_dict[doc_id]>=select:
                result_list.append(doc_id)
        print("****after limit len is "+ str(len(result_list)))

        # get the score of all the documents in the doc_id list
        # score_list is a list of (doc_id, score)
        score_list = self.get_score(result_list, q_dict)


        # sort score list get top 20 or less
        print("******sorting**********")
        score_list.sort(key = lambda x: x[1], reverse = True)
        result_list=[]

        print(score_list[:20])
        
        for i in range(20):
            doc_sql="select url, description from doc where id=%s"
            doc_val =(score_list[i][0],)
            #result_list.append(score_list[i][0])
 
            self.mycursor.execute(doc_sql, doc_val)
            doc_result = self.mycursor.fetchone()
            result_list.append((doc_result[0], doc_result[1]))
            
        '''
        for i in range(20):
            result_list.append(score_list[i][0])

        '''
        print(result_list)    
        return result_list

    def get_score(self, id_list, query_dict):
        '''
        Get a list of all the candidate doc_id, and a query dictionary with
        each query item as the key as there weight (tf-idf) as the value,
        the calculate all the cosine simliarity of the documents, then return a
        list of tuple (doc_id, score) 
        '''
        print("********************calculating score******")
        score_list=[]
        for doc_id in id_list:
            # get all query terms
            score = 0
            for term in query_dict.keys():
                # get all the normalize values
                n_sql="select nmlz from normalize where doc_id=%s and token = %s"
                n_val=(doc_id, term)
                self.mycursor.execute(n_sql, n_val)
                n_result = self.mycursor.fetchone()
                if n_result == None:
                    continue
                else:
                    #print(n_result[0])
                    score += n_result[0]*query_dict[term]
            score_list.append((doc_id,score))
        
        

        return score_list
                       
           
                        
    def normalize(self, query_dict):
        '''
            Get a query dictionary with term frequency and
            return a query dictionary with normalized value
        '''
        print("******Normalizing querys ********")
        #get df of term
        sqrsum=0
        for term in query_dict.keys():
            print("**********Token is "+ str(term)+"  ***********")
            c_sql="select count(*) from web_index where token=%s"
            c_val=(term,)
            self.mycursor.execute(c_sql,c_val)
            c_result= self.mycursor.fetchone()
            df=c_result[0]
            print("************* DF IS "+str(df))
            wt = self.calculate(query_dict[term], df)
            print ("TF-IDF IS "+str(wt))
            query_dict[term]=wt
            sqrsum += wt**2 
                             
        query_length= sqrt(sqrsum)

        for q in query_dict.keys():
            query_dict[q] = query_dict[q]/query_length
            print("normalize is "+ str(query_dict[q]))
        
        return query_dict


    def calculate(self, tf, df):
        '''
        This function calculates the tf-idf by using tf and df given
        in the parameter
        '''
        result = 1.0 + log10(float(tf))
        result *= log10(self.total/df)
        return result


    
    def getid(self, word):
        '''
        Select the top 4000 candidate doc_id which contains the token
        '''
        
        qd_list=[]
        sql="select doc_id from web_index where web_index.token=%s\
        order by tf desc, wt desc limit 4000"
        val=(word,)
        self.mycursor.execute(sql, val)
        myresult= self.mycursor.fetchall()

        return myresult
        
        
if __name__ == "__main__":
    
    s=Search()
    s.search("comput scienc")
    
     
        
        

