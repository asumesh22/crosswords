import sys; args = sys.argv[1:]
import re
import time
import random

global stats; stats = {}
global psblsCache; psblsCache = {}
global freq; freq = {}


def update(s, v):
    if s not in stats:
        stats[s] = v
    else:
        stats[s] += v

def parseArgs():
    w = 0; h = 0; nbs = 0; ss = []
    global EMPTYCHAR; EMPTYCHAR = '-'; global BLOCKINGSQUARE; BLOCKINGSQUARE = '#'

    for arg in args:
        if re.search('^\d+x\d+$', arg, re.IGNORECASE):
            h, w = [int(i) for i in arg.lower().split('x')]
        elif re.search('^\d+$', arg):
            nbs = int(arg)
        elif a:=re.findall('^((H|V)\d+x\d+).*$', arg, re.IGNORECASE):
            ss.append((a[0][1], [int(i) for i in (a[0][0])[1:].lower().split('x') if i!=''], arg[len(a[0][0]):]))
        
    pzl = EMPTYCHAR*w*h

    if nbs%2 and w%2 and h%2:
        pzl, nbs = placeBS(pzl, nbs, w*h//2, w, h)

    for seed in ss:
        pos = seed[1][0]*w+seed[1][1]
        if seed[2] == BLOCKINGSQUARE or seed[2] == '': 
            pzl, nbs = placeBS(pzl, nbs, pos, w, h)
        else:
            pzl = placeWord(pzl, pos, seed[0], seed[2], w)
            nbs -= seed[2].count(BLOCKINGSQUARE)
    
    init_hc = pzl.count(BLOCKINGSQUARE)
    bsLocs = [i for i, val in enumerate(pzl) if val == BLOCKINGSQUARE]
    for loc in bsLocs:
        if w*h - loc not in bsLocs:
            pzl, nbs = placeBS(pzl, nbs, loc, w, h)
    
    return (pzl, nbs, w, h)

def placeBS(pzl, nbs, pos, w, h):
    init_hc = pzl.count(BLOCKINGSQUARE)
    pzl = placeWord(pzl, pos, 'H', BLOCKINGSQUARE, w)
    pzl = placeWord(pzl, h*w-pos-1, 'H', BLOCKINGSQUARE, w)
    return (pzl, nbs+(init_hc-pzl.count(BLOCKINGSQUARE)))

def placeWord(pzl, pos, direction, wrd, w):
    wLen = len(wrd)
    newPzl = [*pzl]
    stepSize = 0
    if direction in {'H', 'h'}: stepSize = 1
    else: stepSize = w

    change = True
    for wi in range(wLen):
        if (val:=newPzl[pos+stepSize*wi]) == '-' or val.lower() == wrd[wi].lower():
            newPzl[pos+stepSize*wi] = wrd[wi]
        else:
            change = False; break
    
    if change: return ''.join(newPzl)
    return pzl

def show(pzl, w):
    print('\n'.join(pzl[rs:rs+w] for rs in range(0, len(pzl), w)))

# ------------ xwords 1 ------------ #

def isValidSlice(slice, ri):
    if EMPTYCHAR not in slice: return [[], True][ri]
    if BLOCKINGSQUARE not in slice: return [[], True][ri]

    invalid = []; seen = set()
    for idx, val in enumerate(slice):
        if val == BLOCKINGSQUARE: continue
        if idx in seen: continue

        wLen = 1; tmp = [idx]
        while idx+wLen < len(slice) and slice[idx+wLen] != BLOCKINGSQUARE:
            seen.add(idx+wLen); tmp.append(idx+wLen); wLen += 1

        if wLen < 3 and not ri: invalid += tmp
        if wLen < 3 and ri: return False
    
    if not ri: return invalid
    return True

def isValidCwStruct(pzl, w, ri):
    newPzl = ''.join(x if x==BLOCKINGSQUARE else EMPTYCHAR for x in pzl)
    
    # symmetry
    if newPzl != newPzl[::-1]: return [[], False][ri]

    # flood fill
    connections = []
    new = [newPzl.find(EMPTYCHAR)]
    if new == [-1]: return [[], True][ri]
    while new:
        connections += new
        nNew = []
        for idx in new:
            nbrs = [x for x in [idx-w, idx-1, idx+1, idx+w] if 0<=x<len(pzl) and newPzl[x]!=BLOCKINGSQUARE and (x//w == idx//w or x%w == idx%w) and x not in connections and x not in nNew]
            nNew += nbrs
        new = nNew
    connections = {*connections}
    emptySquares = set()
    for idx, val in enumerate(newPzl):
        if val == '-':
            emptySquares.add(idx)
    if emptySquares != connections:
        a = [*(emptySquares-connections)]
        t = sorted([(len(a), a), (len(connections), [*connections])])
        return [t[0][1], False][ri]

    # min word len = 3
    invalid = []
    for idx in range(len(pzl)//w):
        row = newPzl[idx*w:idx*w+w]
        cs = isValidSlice(row, ri)

        if not cs and ri: return [[], False][ri]
        if not ri:
            for val in cs: invalid.append(idx*w + val)
    
    for idx in range(w):
        col = newPzl[idx::w]
        cs = isValidSlice(col, ri)
        
        if not cs and ri: return [[], False][ri]
        if not ri:
            for val in cs: invalid.append(idx + val*w)
    
    if not ri: return invalid
    return [[], True][ri]

def fix(pzl, w, nbs):
    invalid = isValidCwStruct(pzl, w, False)
    if len(invalid) <= nbs:
        for idx in invalid:
            pzl, nbs = placeBS(pzl, nbs, idx, w, len(pzl)//w)
    return pzl, nbs

def bruteForce1(pzl, w, nbs, INV):
    if nbs < 0: return ''
    if pzl in INV: return ''
    if nbs == 0 and isValidCwStruct(pzl, w, True): return pzl
    if not isValidCwStruct(pzl, w, True):
        newPzl, newNbs = fix(pzl, w, nbs)

        if newPzl != pzl:
            bF = bruteForce1(newPzl, w, newNbs, INV)
            if bF: return bF
        return ''
    
    choices = [x for x in range(len(pzl)//2) if pzl[x] == EMPTYCHAR and pzl[len(pzl)-x-1] != BLOCKINGSQUARE][::-1]

    for ch in choices:
        newPzl, newNbs = placeBS(pzl, nbs, ch, w, len(pzl)//w)
        bF = bruteForce1(newPzl, w, newNbs, INV)
        if bF: return bF
    return ''

# ------------ xwords 2 ------------ #

def transpose(pzl, w):
    return ''.join([pzl[cs::w] for cs in range(w)]), len(pzl)//w

def augment(pzl, w):
    return '#'*(w+2) + ''.join('#'+pzl[rs:rs+w]+'#' for rs in range(0, len(pzl), w)) + '#'*(w+2), w+2

def deAugment(pzl, w):
    return ''.join(x for idx, x in enumerate(pzl) if idx//(w+2) not in {0, len(pzl)//(w+2)-1} and idx%(w+2) not in {0, w+1})

def findWordStarts(pzl, w):
    return [idx for idx, val in enumerate(pzl) if idx>0 and pzl[idx-1]==BLOCKINGSQUARE and pzl[idx]!=BLOCKINGSQUARE]

def importDictionary():
    wordList = open(args[0]).read().splitlines()

    total = 0
    dct = {}
    for wrd in wordList:
        wLen = len(wrd)
        if wLen not in dct:
            dct[wLen] = {wrd}
        else:
            dct[wLen].add(wrd)

        for le in wrd:
            total+=1
            if le not in freq: freq[le] = 1
            else: freq[le] += 1

    for key in freq:
        freq[key] = freq[key]/total

    return dct

def findWordsFromSpec(spec, dct, l=0):
    a = 0
    if l != 0: a = l
    else: a = len(spec)
    possibleWrds = dct[a]
    reString = spec.replace('-', '.')

    return {wrd for wrd in possibleWrds if re.search(f'^{reString}$', wrd, re.IGNORECASE)}

def findWordStartLens(aP, aW, ws):
    wsLens = []
    for idx in ws:
        row = aP[idx//aW*aW:idx//aW*aW + aW]
        i = idx%aW
        wLen = 0
        while i+wLen < aW and row[i+wLen]!=BLOCKINGSQUARE:
            wLen += 1
        
        wsLens.append((idx, wLen))
    return wsLens

def fromTransposePos(transposePos, aW, pzl):
    return transposePos//aW + transposePos%aW*(len(pzl)//aW)

def main():
    t1 = time.time()
    pzl, nbs, w, h = parseArgs()
    dct = importDictionary()

    update('total', time.time()-t1)
    print(stats)

def initglbls(tW, tP, aW, aP):
    hWs = findWordStartLens(aP, aW, findWordStarts(aP, aW))
    vWs = findWordStartLens(tP, tW, findWordStarts(tP, tW))
    global HLOCS1; global HLOCS2; global VLOCS1; global VLOCS2
    HLOCS1 = {
        (ws,wLen):[*range(ws, ws+wLen)] for ws,wLen in hWs
    }

    VLOCS1 = {
        (ws,wLen):[fromTransposePos(x, tW, tP) for x in range(ws, ws+wLen)] for ws,wLen in vWs
    }

    HLOCS2 = {
        idx:[key for key in HLOCS1 if idx in HLOCS1[key]][0] for idx in range(len(aP)) if aP[idx] != '#'
    }

    VLOCS2 = {
        idx:[key for key in VLOCS1 if idx in VLOCS1[key]][0] for idx in range(len(aP)) if aP[idx] != '#'
    }

if __name__ == '__main__': main()
# Aaryan Sumesh, Pd. 2, Class of 25