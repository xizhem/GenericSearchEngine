import json
import os



class Corpus:
    """
    This class is responsible for handling corpus related
    functionalities like getting the url from bookkeeping.json
    and mapping a url to its local file name
    
    """

    # The corpus directory name
    WEBPAGES_RAW_NAME = "WEBPAGES_RAW"
    # The corpus JSON mapping file
    JSON_FILE_NAME = os.path.join(".", WEBPAGES_RAW_NAME, "bookkeeping.json")

    def __init__(self):
        self.file_url_map = json.load(open(self.JSON_FILE_NAME), encoding="utf-8")
        self.url_file_map = dict()
        for key in self.file_url_map:
            self.url_file_map[self.file_url_map[key]] = key
    

    def get_file_name(self):
        for file,url in self.file_url_map.items():
            addr = file.split("/")
            dir = addr[0]
            file = addr[1]
            yield (url, os.path.join(".", self.WEBPAGES_RAW_NAME, dir, file))
    

    def url_to_dir(self,url):
        if url in self.url_file_map:
            addr = self.url_file_map[url].split("/")
            dir = addr[0]
            file = addr[1]
            return os.path.join(".", self.WEBPAGES_RAW_NAME, dir, file)
        else:
            return None
