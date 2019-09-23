from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import re

#
#scale for metadata weight[0,1]
#Title 1
#H1 0.8
#H2 0.6
#H3 0.4
#Strong 0.9
#bold 0.4

class Tokenizer():
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        
    def stemming(self, text):
        "stem the given string and return a list"
        result = []
        pat = re.compile(r'[a-zA-Z0-9]+')
        pat2 = re.compile(r"^.*[0-9]{4,}.*$")
        words = pat.findall(text)
        for word in words:
            #check for long words
            if (len(word) >= 100):
                continue
            
            word = word.lower()
            #remove stop words
            if word in self.stop_words:
                continue
            # Remove any token with more than 4 digits anywhere inside
            elif pat2.match(word):
                continue
            else:
                result.append(self.stemmer.stem(word))
        return result
                

    
    def tokenize(self,name):
        """takes a document directory and return a list of words with frequency"""
        #result return {tokens: (tf, weight)}
        result = {}
        with open (name,"rb") as file:
            content = file.read()
        soup = BeautifulSoup(content, "lxml")
        [x.extract() for x in soup.find_all('script')]
        [x.extract() for x in soup.find_all('style')]
        text = soup.get_text()
        words = self.stemming(text)
        for word in words:
            if word not in result:
                result[word] = [0,0]
            result[word][0] +=1
        
        #calculate weight by tags
        h1_list = []
        h2_list = []
        h3_list = []
        strong_list = []
        bold_list = []
        
        for i in soup.find_all("h1"):
            h1_list.extend(self.stemming(i.text))
        for i in soup.find_all("h2", text = True):
            h2_list.extend(self.stemming(i.text))
        for i in soup.find_all("h3", text = True):
            h3_list.extend(self.stemming(i.text))
        for i in soup.find_all("strong", text = True):
            strong_list.extend(self.stemming(i.text))
        for i in soup.find_all("b",text = True):
            bold_list.extend(self.stemming(i.text))

        #sum weight and store
        for i in h1_list:
            if i in result:
                result[i][1] += 0.8
        for i in h2_list:
            if i in result:
                result[i][1] += 0.6
        for i in h3_list:
            if i in result:
                result[i][1] += 0.4
        for i in strong_list:
            if i in result:
                result[i][1] += 0.9
        for i in bold_list:
            if i in result:
                result[i][1] += 0.4
        
        return result




"""
if __name__ == "__main__":
    i = Tokenizer()
    print(i.tokenize("./1.html"))
"""
