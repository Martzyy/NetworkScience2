from lxml import etree
import pickle
import sys
import itertools
import math
import time

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
                    #print(nod.name,item,i,tupl[0])
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
                elif elem.tag == 'genre':
                    lst = elem.text.split(":")
                    try:
                        previous.attributes[lst[0]]
                    except Exception:
                        previous.attributes[lst[0]] = []
                    previous.attributes[lst[0]].append(lst[1])
                elif elem.tag == 'relation':
                    try:
                        lst1 = elem.text.split(":",1)
                    except:
                        continue
                    try: 
                        previous.relations[lst1[0]]
                    except Exception:
                        previous.relations[lst1[0]] = []
                    previous.relations[lst1[0]].append((lst1[1],0)) #(relation,1) is inverse of (relation,0)
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
        return metaPaths2
    
    def findMetaPath3(self, metaPaths2):
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

    def calculatePc3(self, path):
        count = 1
        for i in range(1,len(path)-1):
            count *= len(path[i])
        return  count
        

    def generativeMetaPathWeighting(self, metaPaths, S, metaPathWeight, metaPaths1, pathNum):
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
        likelihood = []
        for path in metaPaths1:
            len1 = len(path[0])
            len2 = len(path[len(path)-1])
            for i in range(len1*len2):
                likelihood.append(self.calculatePc3(path))
        #print(likelihood)
        for i in range(len(likelihood)):
            pathNum.append(likelihood[i])
        pc_apc = []
        for i in range(len(metaPaths)):
            if (len(metaPaths[i]) <= 2):
                pc_apc.append(self.calculatePc2(metaPaths[i],1))
            else:
                pc_apc.append(prior_final[i])
        #print(pc_apc)
        for i in range(len(likelihood)):
            likelihood[i] = likelihood[i]/pc_apc[i]
        for i in range(len(prior_final)):
            metaPathWeight.append(prior_final[i] * likelihood[i])
        return
       
        
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

    def metaPathRelevance(self, q, v, Pi):
        #set limit to be 3 to prevent highly skewed values
        path = []
        temp = []
        m1 = []
        m2 = []
        count = 0
        self.findMetaPath(q, v, len(Pi)+1, path, temp)
        m1 = self.findMetaPath2(path)
        m2 = self.findMetaPath3(m1)
        for i in range(len(m2)):
            if m2[i] == Pi:
                count += 1
        return min(count, 3)
        
    def propertyRelevance(self, v):
        #set aprop to be 1
        count = 0
        for item in self.network:
            if item.name == v:
                v_attribute = item.attributes
        for item in self.network:
            if item.attributes == v_attribute:
                count += 1
        return count

    def grease(self,S,L,m, q):
        L += 1
        #line 1 of pseudocode
        #find all meta-paths of graph
        #connects source to target entity in some user-provided example
        metaPaths = []
        for source in S:
            temp = []
            self.findMetaPath(source, S[source], L, metaPaths, temp)
        metaPaths1 = []
        metaPaths1 = self.findMetaPath2(metaPaths)
        metaPaths2 = self.findMetaPath3(metaPaths1)
        #print(metaPaths)
        #print(metaPaths1)
        #print(metaPaths2)
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
        pathNum = []
        self.generativeMetaPathWeighting(metaPaths2, S, metaPathWeight, metaPaths1, pathNum)
        #print(metaPathWeight)
        propertyWeight = []
        for prop in properties:
            self.generativePropertyWeighting(prop, propertyWeight)
        #print(propertyWeight)
        #line 7 of pseudocode
        #return m metapaths with largest meta-path weight
        top_path = []
        for i in range(len(metaPathWeight)-1):
            if metaPathWeight[i] < metaPathWeight[i+1]:
                temp = metaPathWeight[i]
                metaPathWeight[i] = metaPathWeight[i+1]
                metaPathWeight[i+1] = temp
                temp1 = metaPaths2[i]
                metaPaths2[i] = metaPaths2[i+1]
                metaPaths2[i+1] = temp1 
                temp2 = pathNum[i]
                pathNum[i] = pathNum[i+1]
                pathNum[i+1] = temp2
        #print(metaPaths2) 
        #print(pathNum) 
        for i in range(m):
            top_path.append(metaPaths2[i])
        #print(top_path)
        #line 8 of pseudocode
        #return entities connected from query with meta-paths from line 7
        entities = []
        for i in range(len(top_path)):
            for j in range(len(metaPaths1)):
                for i1 in range(len(top_path[i])):
                    for j1 in range(len(metaPaths1[j])):
                        if top_path[i][i1] in metaPaths1[j][j1]:
                            if i1 == len(top_path[i])-1:
                                entities.append(metaPaths[j][-1])
        entities= list(dict.fromkeys(entities))
        #print(entities)
        #line 9-11 of pseudocode
        #compute extended relevance for line 8
        relevance = []
        #set limit to 
        #set decay factor to be 0.1
        rel = 0
        #print(metaPathWeight)
        #print(metaPaths2)
        for i in range(len(entities)):
            for j in range(len(metaPaths2)):
                rel += (metaPathWeight[j] * math.exp(-0.1*len(metaPaths2[i])) * self.metaPathRelevance(q, entities[i], metaPaths2[j]))
            for k in range(len(properties)):
                rel += (self.propertyRelevance(entities[i]) * propertyWeight[k])
            relevance.append(rel)
            rel = 0
        #print(relevance)
        #line 12 of pseudocode
        #return k top-ranked ones
        #set k to be 2
        k = 2
        for i in range(len(relevance)-1):
            if relevance[i] < relevance[i+1]:
                temp = relevance[i]
                relevance[i] = relevance[i+1]
                relevance[i+1] = temp
                temp1 = entities[i]
                entities[i] = entities[i+1]
                entities[i+1] = temp1 
        # this is suppose to print out the answers
        for i in range(min(2, len(entities))):
            print(entities[i])
        return


#datapath = 'database.xml'
datapath = './NetworkScience2/PythonApplication1/kek_db.xml'

S2 = { "Elijah Wood" : "Rainn Wilson","Jonah Hill" : "Channing Tatum"}

S3 = { "Jake Johnson":"Hailee Steinfield", "James Franco":"Seth Rogen", \
        "Elijah Wood" : "Rainn Wilson"}

S4 = { "Jack Black" : "Bryan Cranston", "James Franco":"Seth Rogen", \
        "Elijah Wood" : "Rainn Wilson","Jonah Hill" : "Channing Tatum"}

S5 = { "Jack Black" : "Bryan Cranston", "Jake Johnson":"Hailee Steinfield", \
        "Keanu Reeves":"Micahel Nyqvist", \
        "Mila Kunis" : "Channing Tatum", "Johnny Depp" : "Javier Bardem"}

L = 3
m = 2
q = "Javier Bardem"
kgraph = kg()
kgraph.parseData(datapath)
kgraph.generateInversePath()
#kgraph.show()
kgraph.grease(S2, L, m, q)
kgraph.grease(S3, L, m, q)
kgraph.grease(S4, L, m, q)
kgraph.grease(S5, L, m, q)