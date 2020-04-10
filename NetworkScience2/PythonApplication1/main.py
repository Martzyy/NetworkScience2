from lxml import etree
import pickle
import sys

metaPaths = []

class node:
    name:str #name of node
    attributes:dict #attributes in form of dict of strings
    relations:dict #relations in form of <connectednode object>:<types of relations in a list>

    #init function
    def __init__(self,name,attributes,relations):
        self.name = name
        self.attributes = attributes
        self.relations = relations
        return

    def __init__(self):
        self.name = ''
        self.attributes = {}
        self.relations = {}
        return

class kg:
    network:list

    #init methods
    def __init__(self,network):
        self.network = network
        return

    def __init__(self):
        self.network = []

    #critical methods
    def generateInversePath(self):
        for nod in self.network:
            for item in nod.relations:
                for i,tupl in enumerate(nod.relations[item]):
                    print(nod.name,item,i,tupl[0])
                    try:
                        self.search(item).relations[nod.name]
                    except Exception:
                        self.search(item).relations[nod.name] = []
                    self.search(item).relations[nod.name].append((tupl[0],1))
        return

    def search(self,name):
        for item in self.network:
            if item.name == name:
                return item
    
    def show(self):
        for item in self.network:
            print('name : '+item.name)
            print('attributes : '+str(item.attributes))
            print('relations : '+str(item.relations))
            print('')
        return

    def parseData(self,datapath):
        xmlp = etree.XMLParser(recover = True)
        itertree = etree.iterparse(datapath, load_dtd = True, events=("start", "end"))
        itertree = iter(itertree)
        previous = None #same as proj1
        for event, elem in itertree:
            if event == 'start':
                if elem.tag == 'node':
                    previous = node()
                elif elem.tag == 'name':
                    previous.name = elem.text
                elif elem.tag == 'attribute':
                    lst = elem.text.split(":")
                    try: 
                        previous.attributes[lst[0]]
                    except Exception:
                        previous.attributes[lst[0]] = []
                    previous.attributes[lst[0]].append(lst[1])
                elif elem.tag == 'relation':
                    lst = elem.text.split(":",1)
                    try: 
                        previous.relations[lst[0]]
                    except Exception:
                        previous.relations[lst[0]] = []
                    previous.relations[lst[0]].append((lst[1],0)) #(relation,1) is inverse of (relation,0)
            elif event == 'end' and elem.tag == 'node':
                self.network.append(previous)
                previous = None
            elem.clear()
        return

    def findMetaPath(self, source, dest, L, metaPaths, temp):
        #find all meta-paths of graph
        #connects source to target entity in some user-provided example
        if len(temp) < L:
            if source == dest:
                temp.append(source)
                metaPaths.append(temp)
                return
            else:
                for item in self.network:
                    if source == item.name:
                        temp.append(source)
                        for relation in item.relations:
                            self.findMetaPath(relation, dest, L, metaPaths, temp)
        return 

    def grease(self,S,L):
        metaPaths = []
        for source in S:
            temp = []
            self.findMetaPath(source, S[source], L, metaPaths, temp)
        print(metaPaths)
        #find all properties that constrain target entity in some user-provided example
        properties = {"query" : {}, "answer" : {}}
        dicts_q = []
        dicts_a = []
        for key in S:
            for item in self.network:
                if key == item.name:
                    dicts_q.append(item.attributes)
        for d in dicts_q:
            for k, v in d.items():
                try:
                    properties["query"].setdefault(k, []).extend(v)
                except TypeError:
                    properties["query"][k].append(v)
        for value in S.values():
            for item in self.network:
                if value == item.name:
                    dicts_a.append(item.attributes)
        for d in dicts_a:
            for k, v in d.items():
                try:
                    properties["answer"].setdefault(k, []).extend(v)
                except TypeError:
                    properties["answer"][k].append(v)
        

#datapath = 'database.xml'
datapath = 'PythonApplication1/database.xml'
S1 = {"Dave Chappelle" : "Lady Gaga", "Matt Damon" : "Julia Roberts"}
S2 = {"Dave Chappelle" : "Bradley Cooper", "Matt Damon" : "George Clooney"}
L = 4
kgraph = kg()
kgraph.parseData(datapath)
kgraph.generateInversePath()
kgraph.show()
kgraph.grease(S1, L)

