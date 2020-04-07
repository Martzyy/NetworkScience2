from lxml import etree
import pickle
import sys

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
                    previous.attributes = elem.text
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


datapath = 'database.xml'
kgraph = kg()
kgraph.parseData(datapath)
kgraph.generateInversePath()
kgraph.show()