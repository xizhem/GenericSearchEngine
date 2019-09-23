from bs4 import BeautifulSoup
import re
from collections import defaultdict
from Corpus import Corpus
from urllib.parse import urljoin
from lxml import html
from urllib.parse import urlparse

class Edge:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst
        
    def __print__(self):
        print("[{}-{}]".format())

    def reverse(self):
        return Edge(dst, src)
        
class Vertex:
    def __init__(self, url):
        self.id = url
        self.in_edges = []
        self.out_edges = []
        self.num_out_edges = 0
        self.num_in_edges = 0
        
    def add_in_edge(self, Edge):
        self.in_edges.append(Edge)
        self.num_in_edges += 1

    def add_out_edge(self, Edge):
        self.out_edges.append(Edge)
        self.num_out_edges += 1

    def contain(self, Edge):
        for i in self.in_edges:
            if i.src == Edge.src and i.dst == Edge.dst:
                return True
        return False

    def contain_out(self, Edge):
        for i in self.out_edges:
            if i.src == Edge.src and i.dst == Edge.dst:
                return True
        return False

class Graph:
    def __init__(self):
        self.corpus = Corpus()
        self.Vertices = []
        self.total_vertex = 0
        self.total_edge = 0
        self.score  = defaultdict(lambda: 1)

    def load_vertex(self):
        for url, adr in self.corpus.get_file_name():
            target = self.find(url)
            if target == None:
                self.add_vertex(url)
                target = self.find(url)
            with open(adr, "rb") as file:
                content = file.read()
            htmlElem = html.fromstring(content)
            links = htmlElem.xpath('//a/@href')
            outputLinks = []
            for link in links:
                outputLinks.append(urljoin(url, link))
            for i in outputLinks:
                self.add_edge(Edge(url, i))
            
    def print_score(self):
        count = 0
        for i in self.score:
            if count ==100:
                break
            print("url: ", i, "\n", "score:",self.score[i])
            count += 1

        

    def add_vertex(self, url):
        self.Vertices.append(Vertex(url))
        self.total_vertex += 1
        print("# of Vertex added: ", self.total_vertex, "url: ", url)

    def add_edge(self, edge):
        s = edge.src
        d = edge.dst
        target = self.find(edge.dst)
        if target == None:
            self.add_vertex(edge.dst)
            target = self.find(edge.dst)
        if not self.Vertices[target].contain(edge):
            self.Vertices[target].add_in_edge(edge)
        target2 = self.find(edge.src)
        if target2 == None:
            self.add_vertex(edge.src)
            target2 = self.find(edge.src)
        if not self.Vertices[target2].contain_out(edge):
            self.Vertices[target2].add_out_edge(edge)
            

    def find(self,id):
        for i in range(len(self.Vertices)):
            if self.Vertices[i].id == id:
                return i
        return None

    def page_rank(self, d = 0.85, max_iteration = 2):
        for n in range(max_iteration):
            new_score = defaultdict(int)
            for i in range(self.total_vertex):
                new_score[self.Vertices[i].id] = 1-d
                for x in range(self.Vertices[i].num_in_edges):
                    new_score[self.Vertices[i].id] += d * (self.score[self.Vertices[i].in_edges[x].src] / self.Vertices[self.find(self.Vertices[i].in_edges[x].src)].num_out_edges)
            print("url: ", self.Vertices[i].id, "\n", "score:", new_score[self.Vertices[i].id])
            self.score = new_score

if __name__ == "__main__":
    g = Graph()
    g.load_vertex()
    g.page_rank(0.85, 5)
    #g.print_score()

