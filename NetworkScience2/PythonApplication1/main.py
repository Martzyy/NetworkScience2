from lxml import etree
import pickle
import sys
import itertools

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
        return 

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
        if len(temp) < L:
            if source == dest:
                temp.append(source)
                metaPaths.append(temp[:])
                temp.pop()
                return
            else:
                if (len(temp) == L-1):
                    return
                for item in self.network:
                    if source == item.name:
                        temp.append(source)
                        for relation in item.relations:
                            self.findMetaPath(relation, dest, L, metaPaths, temp)
                        temp.pop()
        return
    
    def findMetaPath2(self, metaPaths):
        metaPaths2 = []
        temp = []
        for path in metaPaths:
            for i in range(len(path)-1):
                for item in self.network:
                    if path[i] == item.name:
                        for relation in item.relations:
                            if path[i+1] == relation:
                                temp.append(item.relations[relation])
            metaPaths2.append(temp[:])
            temp = []
        #print(metaPaths2)
        metaPaths3 = []
        for i in range(len(metaPaths2)):
            new_list = list(itertools.product(*metaPaths2[i]))
            for i in new_list:
                metaPaths3.append(i)
        return metaPaths3
    

    def calculatePc(self, path, nodeNo):
        #calculate number of paths in the KG that follow meta-path P for a relation type
        r1 = path[nodeNo-1]
        pc = 0
        for item in self.network:
            for relation in item.relations:
                for i in range(len(item.relations[relation])):
                    if item.relations[relation][i] == r1:
                        pc += 1
        return pc

    def calculatePc2(self, path, nodeNo):
        #calculate number of paths in the KG that follow meta-path P for 2 consecutive relation type
        r1 = path[nodeNo-1]
        r2 = path[nodeNo]
        pc = 0
        for item in self.network:
            for relation in item.relations:
                for i in range(len(item.relations[relation])):
                    if item.relations[relation][i] == r1:
                        for item1 in self.network:
                            if item1.name == relation:
                                for relation1 in item1.relations:
                                    if r1[0] == r2[0]:
                                        if relation1 != item.name:
                                            for j in range(len(item1.relations[relation1])):
                                                if item1.relations[relation1][j] == r2:
                                                    pc += 1
                                    else:
                                        for j in range(len(item1.relations[relation1])):
                                                if item1.relations[relation1][j] == r2:
                                                    pc += 1

        return pc

    def calculatePc3(self, source, dest, path):
       
        return

    def generativeMetaPathWeighting(self, metaPaths, S, metaPathWeight):
        #compute prior
        prior1 = []
        prior2 = []
        prior_final = []
        for path in metaPaths:
            pc1 = self.calculatePc(path,1)
            #print(pc1)
            pc2 = 1
            for i in range(2,len(path)+1,1):
                num = self.calculatePc2(path,i-1)
                den = self.calculatePc(path,i-1)
                pc2 *= (num/den)
            prior = pc1 * pc2
            prior1.append(prior)
            prior = 0
        #print(prior1)
        for path in metaPaths:
            pc1 = self.calculatePc(path,1)
            #print(pc1)
            pc2 = 1
            for i in range(1,len(path)-1,1):
                num = self.calculatePc2(path,i)
                den = self.calculatePc(path,i+1)
                pc2 *= (num/den)
            prior = pc1 * pc2
            prior2.append(prior)
            prior = 0
        #print(prior2)
        for i in range(len(prior1)):
            prior_final.append((prior1[i] + prior2[i])/2)
        #print(prior_final)
        #compute likelihood
        for key in S:
            for path in metaPaths:
                prob = self.calculatePc3(key, S[key], path)

    def generativePropertyWeighting(self, prop, propertyWeight):
        #compute prior
        count = 0
        for item in self.network:
            if prop == item.attributes:
                count += 1
        prior = count/len(self.network) 
        #print(prior)
        #compute likelihood
        likelihood = 1
        count1  = 0
        for item in self.network:
            if item.attributes == prop:
                count1 += 1
        if count1 == 0:
            count1 = len(self.network)
        likelihood *= 1/count1
        propertyWeight.append(prior*likelihood)
        return

    def grease(self,S,L):
        #line 1 of pseudocode
        #find all meta-paths of graph
        #connects source to target entity in some user-provided example
        metaPaths = []
        for source in S:
            temp = []
            self.findMetaPath(source, S[source], L, metaPaths, temp)
        metaPaths1 = []
        metaPaths1 = self.findMetaPath2(metaPaths)
        #print(metaPaths)
        print(metaPaths1)
        #line 2 of pseudocode
        #find all properties that constrain target entities in some user-provided example
        properties = []
        for value in S.values():
            for item in self.network:
                if value == item.name:
                    properties.append(item.attributes)
        #print(properties)
        #lines 4-6 of pseudocode
        #generative meta-path weightage
        metaPathWeight = []
        self.generativeMetaPathWeighting(metaPaths1, S, metaPathWeight)
        #print(metaPathWeight)
        propertyWeight = []
        for prop in properties:
            self.generativePropertyWeighting(prop, propertyWeight)
        #print(propertyWeight)
        #line 7 of pseudocode
        #return m metapaths with largest meta-path weight


        return

#datapath = 'database.xml'
datapath = '/Users/charlottechng/Desktop/NetworkScience2/NetworkScience2/PythonApplication1/database.xml'
S1 = {"Dave Chappelle" : "Lady Gaga", "Matt Damon" : "Julia Roberts"}
S2 = { "Dave Chappelle" : "Bradley Cooper","Matt Damon" : "George Clooney"}
L = 3
kgraph = kg()
kgraph.parseData(datapath)
kgraph.generateInversePath()
kgraph.show()
kgraph.grease(S2, L)

