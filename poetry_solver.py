#!/usr/bin/env python

import argparse
from collections import Counter,defaultdict
import random
import re
import math

def loadCmuDict(fn):
    zap = re.compile('[^a-z ]+')
    cmudict = defaultdict(list)
    with open(fn) as fh:
        for l in fh:
            if l[0].isalpha():
                fields = l[:-1].split(" ")
                word = zap.sub("",fields[0].split("(")[0].lower())
                cmudict[word].append(fields[2:])
    return dict(cmudict)

def loadCorpus(fn):
    zap = re.compile('[^a-z ]+')
    tokens = []
    with open(fn) as fh:
        for l in fh:
            tokens.extend(zap.sub("",l.replace("--"," ").lower()).split())
    return tokens

def buildNgrams(corpus,maxn=3):
    raw = defaultdict(Counter)
    for i in xrange(len(corpus)):
        for n in xrange(maxn+1):
            go = True
            for w in corpus[i-n:i+1]:
                if w not in cmudict:
                    go = False
                    break
            if go:
                raw[tuple(corpus[i-n:i])][corpus[i]] += 1
    out = {}
    for tup, rawcounter in raw.iteritems():
        total_count = sum(rawcounter.values())
        out[tup] = [(word, math.log(float(count)/total_count)) for word,count in rawcounter.most_common()]
    return out

def loadSchema(fn):
    with open(fn) as fh:
        return compileSchema(fh.read())

def compileSchema(raw):
    return [{'syl':l[:-1],'rhyme':l[-1]} for l in raw.split()]

class SolutionSpace:
    def __init__(self,cmudict,ngrams,nmax):
        self.cmudict = cmudict
        self.ngrams = ngrams
        self.nmax = nmax
        self.cand = []
    
    def forward(self):
        for lookback in reversed(xrange(self.nmax)):
            searchwords = [x[0][0] for x in self.cand[max(0,len(self.cand)-lookback):]]
            if tuple(searchwords) in ngrams:
                break
        new = [(x[0],x[1],[y for y in cmudict[x[0]]]) for x in random.sample(ngrams[tuple(searchwords)],len(ngrams[tuple(searchwords)]))]
        # new = [(x[0],x[1],[y for y in cmudict[x[0]]]) for x in ngrams[tuple(searchwords)]]
        self.cand.append(new)
    
    def back(self):
        self.cand[-1][0][2].pop(0)
        if len(self.cand[-1][0][2]) == 0:
            self.cand[-1].pop(0)
        if len(self.cand[-1]) == 0:
            self.cand.pop()
            self.back()
            
    def total_ll(self):
        return sum([x[0][1] for x in self.cand])
    
    def sofar(self):
        return [(x[0][0],x[0][2][0]) for x in self.cand]

def testAgainstSchema(cand,schema):
    def getStresses(word):
        out = ''
        for p in word[1]:
            if '0' in p:
                out += '-'
            if '1' in p or '2' in p:
                out += '/'
        return out
    def getRhymeBit(word):
        out = []
        for p in reversed(word):
            out.append(p)
            if '0' in p or '1' in p or '2' in p:
                break
        return out
    def checkRhyme(letter,word):
        if letter in rhymes:
            if getRhymeBit(word[1])==rhymes[letter]['bit']:
                if word[0] not in rhymes[letter]['words']:
                    rhymes[letter]['words'].add(word[0])
                    return True
            return False
        else:
            rhymes[letter] = {'bit':getRhymeBit(word[1]),'words':set([word[0]])}
            return True
    linewords = []
    rhymes = {}
    for line in schema:
        linewords.append([])
        stresses = ''
        while len(stresses) < len(line['syl']):
            if not cand:
                return ("MORE", "/".join([" ".join(x) for x in linewords]))
            new_word = cand.pop(0)
            linewords[-1].append(new_word[0])
            stresses += getStresses(new_word)
            if not line['syl'].startswith(stresses):
                return ("FAIL",None)
        if len(stresses) < len(line['syl']):
            return ("FAIL",None)
        if not checkRhyme(line['rhyme'],new_word):
            return ("FAIL",None)
    return ("DONE","\n".join([" ".join(x) for x in linewords]))

def makePoem(cmudict,ngrams,schema):
    foo = SolutionSpace(cmudict,ngrams,args.lookback)
    teststate,linewords = testAgainstSchema(foo.sofar(),schema)
    while teststate != "DONE":
        if teststate == "MORE": # and foo.total_ll()>-150:
            if args.v:
                print linewords
            foo.forward()
        if teststate == "FAIL":
            foo.back()
        teststate,linewords = testAgainstSchema(foo.sofar(),schema)
    if args.v:
        print foo.total_ll()
    return linewords

def parseArgs():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", help="verbose",
                    action='store_true')
    ap.add_argument("--corpus", help="input corpus path",
                    default="data/md.txt")
    ap.add_argument("--pdict", help="pronunciation dictionary path",
                    default="data/cmudict.0.7a.txt")
    ap.add_argument("--schema", help="poem schema path")
    ap.add_argument("--lookback", help="number of words to look back",
                    type=int,default=2)
    ap.add_argument("-n", help="number of poems to generate",
                    type=int,default=1)
    return ap.parse_args()

if __name__ == "__main__":
    args = parseArgs()
    cmudict = loadCmuDict(args.pdict)
    corpus = loadCorpus(args.corpus)
    ngrams = buildNgrams(corpus,args.lookback)
    schema = loadSchema(args.schema)
    for i in xrange(args.n):
        print makePoem(cmudict,ngrams,schema)
        print
        