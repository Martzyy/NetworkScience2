from lxml import etree
import pickle
import sys

class node:
    name:str #name of node
    attributes:dict #attributes in form of dict of strings
    relations:dict #relations in form of <connectednode object>:<types of relations in a list>

    #init function
    def __init__(self,name,attributes,connectednodes):
        self.name = name
        self.attributes = attributes
        self.connected = connected
        return

    def __init__(self):
        self.name = ''
        self.attributes = {}
        self.relations = {}
        return

    def init(self):
        self.attributes = {}
        self.connected = {}
        return

class kg:
    network:list

    def __init__(self,network):
        self.network = network
        return

    def __init__(self):
        self.network = []

    def parsedata(self,datapath):
        xmlp = etree.XMLParser(recover = True)
        itertree = etree.iterparse(datapath, load_dtd = True, events=("start", "end"))
        itertree = iter(itertree)
        previous = None #same as proj1
        for event, elem in itertree:
            print(event,elem.tag,elem.text)
            if event == 'start':
                if elem.tag == 'node':
                    previous = node()
                elif elem.tag == 'name':
                    previous.name = elem.text
                elif elem.tag == 'attribute':
                    previous.attributes = elem.text
                elif elem.tag == 'relation':
                    lst = elem.text.split(":",1)
                    previous.relations[lst[0]] = (lst[1],0) #(relation,1) is inverse of (relation,0)
            elif event == 'end' and elem.tag == 'node':
                self.network.append(previous)
                previous = None
            elem.clear()
        return

datapath = 'database.xml'
kgraph = kg()
kgraph.parsedata(datapath)
for item in kgraph.network:
    print(item.name)