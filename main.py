#!/usr/bin/env python
#-*- coding:utf-8 -*-

import random
import hashlib
import copy

a = [1,1,5,1,1,1, 5]
b = [2,2,2,4,2,2, 7]
q = [8,8,8,8,8,8, 2]

NumIndividuals = 200
NumElite       = 10
symbols = ['a', 'b','add', 'mul', 'sub', 'and', 'or', 'not']
terminals = ['a', 'b']
MaxTreeDepth  = 10
mutationRate = 0.05
crossoverRate = 1.0
delim = ','

class Tree:
    def __init__(self):
        self.value    = ""
        self.children = None
        self.parent   = None
        self.depth    = 0
        self.score    = 0
        self.trav     = ""
    def clone(self):
        s = Tree()
        s.value    = self.value
        s.children = self.children
        s.parent = self.parent
        s.depth = self.depth
        s.score = self.score
        return s
    def generateGraph(self):
        p = id(self)
        print str(p)+' [label="'+self.value+'"]'
        print str(p) + ";"
        for c in self.children:
            cc = id(c)
            print str(cc)+' [label="'+c.value+'"]'
            print str(p) + " -> " + str(cc) +";"
            c.generateGraph()
    def getNodeArray(self):
        s = [self]
        for c in self.children:
            s.extend(c.getNodeArray())
        return s
    def traverse(self):
        s = self.value
        for c in self.children:
            s += delim + c.traverse()
        self.trav = s;
        return s
    def make(self, depth):
        if depth == 0:
            self.value = 'p'
        else:
            random.shuffle(symbols)
            self.value = symbols[0];
        self.depth = depth
        if self.depth >= MaxTreeDepth:
            random.shuffle(terminals)
            self.value = terminals[0]
        if   self.value == 'add' : self.children = [None] * 2
        elif self.value == 'mul' : self.children = [None] * 2
        elif self.value == 'sub' : self.children = [None] * 2
        elif self.value == 'and' : self.children = [None] * 2
        elif self.value == 'or' : self.children = [None] * 2
        elif self.value == 'xor' : self.children = [None] * 2
        elif self.value == 'not' : self.children = [None] * 1
        elif self.value == 'p' : self.children = [None] * 1
        else                   : self.children = [None] * 0
        for c in xrange(len(self.children)):
            self.children[c] = Tree()
            self.children[c].parent = self
            self.children[c].make(depth+1)
    def calc(self, qq):
        z = [0] * len(qq)
        if self.value in terminals:
            idx = terminals.index(self.value)
            z = [i for i in eval(terminals[idx])]
        elif self.value == 'not' :
            c0 = self.children[0].calc(qq)
            z = [~i for i in c0] # 正しい？ NOT
        elif self.value == 'p' :
            c0 = self.children[0].calc(qq)
            z = [i for i in c0] # through
        else :
            c0 = self.children[0].calc(qq)
            c1 = self.children[1].calc(qq)
            if   self.value == 'add' :
                z = [i+j for i,j in zip(c0, c1)]
            elif self.value == 'mul' :
                z = [i*j for i,j in zip(c0, c1)]
            elif self.value == 'sub' :
                z = [i-j for i,j in zip(c0, c1)]
            elif self.value == 'and' :
                z = [i&j for i,j in zip(c0, c1)]
            elif self.value == 'or' :
                z = [i|j for i,j in zip(c0, c1)]
            elif self.value == 'xor' :
                z = [i^j for i,j in zip(c0, c1)]
        self.score = sum([abs(i-j) for i,j in zip(qq,z)])
        return z

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
print "..... Start ....."

tarray = [0] * NumIndividuals
elites = [0] * NumElite

for j in xrange(len(elites)):
    elites[j] = Tree()
    elites[j].make(0)

for j in xrange(len(tarray)):
    tarray[j] = Tree()
    tarray[j].make(0)
    #print "======= "+ str(j) + " ========="
    #print tarray[j].traverse()

generation = 0
while True:
    pa = elites + tarray
    for p in pa:
        p.traverse()
        p.calc(q)
    pa.sort(key=lambda pa: (pa.score, len(pa.traverse().split(delim))), reverse=False)

    sp = pa
    output = []
    j = 0
    for i in sp:
        if not i.trav in output:
            output.append(i.trav)
            elites[j] = copy.deepcopy(i)
            print str(elites[j].score), len(elites[j].traverse().split(delim)),elites[j].trav
            j=j+1
            if j == len(elites):
                break
    determ = 0
    """
    print "Length : "+str(len(sp))
    for j in xrange(len(elites)):
        elites[j] = copy.deepcopy(sp[j])
        tq = elites[j].calc(q)
        print str(elites[j].score), tq,elites[j].traverse()
        if elites[j].score == 0:
            determ = j
    """

    if determ != 0:
        print "find."
        print elites[j].traverse()
        break
    for j in xrange(len(tarray)):
        tarray[j] = pa[j]

    # 交叉
    random.shuffle(tarray)
    for j in xrange(len(tarray)/2):
        ind0   = tarray[2*j+0]
        nodes0 = ind0.traverse().split(delim)
        nid0   = random.randint(1, len(nodes0)-1)
        nodelist0 = ind0.getNodeArray()
    
        ind1   = tarray[2*j+1]
        nodes1 = ind1.traverse().split(delim)
        nid1   = random.randint(1, len(nodes1)-1)
        nodelist1 = ind1.getNodeArray()

        #ind0.generateGraph()
        #ind1.generateGraph()
        #print "t["+str(2*j+0)+"("+str(nid0)+"), "+\
        #    str(2*j+1)+"("+str(nid1)+")] : "
        #print "pA "+str(ind0.traverse())+" : "+nodelist0[nid0].value
        #print "pB "+str(ind1.traverse())+" : "+nodelist1[nid1].value
        if random.random() < crossoverRate:

            p0 = nodelist0[nid0].parent
            p1 = nodelist1[nid1].parent
            if p0 != None:
                p0idx = p0.children.index(nodelist0[nid0])
                p0.children[p0idx] = nodelist1[nid1]
            if p1 != None:
                p1idx = p1.children.index(nodelist1[nid1])
                p1.children[p1idx] = nodelist0[nid0]
            tmp = nodelist0[nid0].parent
            nodelist0[nid0].parent = nodelist1[nid1].parent
            nodelist1[nid1].parent = tmp
        #print "nA "+str(ind0.traverse())
        #print "nB "+str(ind1.traverse())
        #print ""
        #ind0.generateGraph()
        #ind1.generateGraph()

    # 突然変異
    for j in xrange(len(tarray)):
        if random.random() < mutationRate:
            nodes = tarray[j].traverse().split(delim)
            nid   = random.randint(0, len(nodes)-1)
            nodelist = tarray[j].getNodeArray()
            #print "m ["+str(nid)+"] in "+\
            #    str(len(nodes))+str(nodelist[nid])
            #print tarray[j].traverse()
            #tarray[j].generateGraph()
            nodelist[nid].make(nodelist[nid].depth)
            #print tarray[j].traverse()
            #tarray[j].generateGraph()
    print ".....  End "+ str(generation)+"  ....."
    generation = generation + 1

    #for j in xrange(len(tarray)):
    #    tq = tarray[j].calc(q)
    #    print str(tarray[j].score) + " "+str(tq)

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""



