import sys; args = sys.argv[1:]
import re
import time
import random

def parse_arguments():
    w = 0; h = 0; nbs = 0; ss = []
    global EC; EC = '-'
    global BS; BS = '#'

    for arg in args:
        if re.search('^\d+x\d+$', arg, re.IGNORECASE):
            h, w = [int(i) for i in arg.lower().split('x')]
        elif re.search('^\d+$', arg):
            nbs = int(arg)
        elif a:=re.findall('^((H|V)\d+x\d+).*$', arg, re.IGNORECASE):
            ss.append((a[0][1], [int(i) for i in (a[0][0])[1:].lower().split('x') if i!=''], arg[len(a[0][0]):]))
    
    pzl = EC * w * h

    # middle parity
    if nbs%2 and w%2 and h%2:
        pzl, nbs = place_bs(pzl, nbs, w*h//2, w)

    for st in ss:
        idx = st[1][0]*w + st[1][1]
        if st[2] == BS or st[2] == '':
            pzl, nbs = place_bs(pzl, nbs, idx, w)
        else:
            pzl = place_wrd(pzl, idx, st[0], st[2], w)
            nbs -= st[2].count(BS)
    
    # make symmetric
    bs_locs = [i for i,v in enumerate(pzl) if v==BS]
    for idx in bs_locs:
        if w*h - idx not in bs_locs:
            pzl, nbs = place_bs(pzl, nbs, idx, w)
    
    return pzl, nbs, w

def place_bs(pzl, nbs, idx, pw):
    init_ct = pzl.count(BS)
    pzl = place_wrd(pzl, idx, 'H', BS, pw)
    pzl = place_wrd(pzl, len(pzl)-idx-1, 'H', BS, pw)
    return pzl, nbs-(pzl.count(BS)-init_ct)

def place_wrd(pzl, idx, d, word, w):
    word_len = len(word)
    new_pzl = [*pzl]
    step_size = 0

    if d in {'H', 'h'}: step_size = 1
    else: step_size = w

    changed = True
    for wi in range(word_len):
        if ((val:=new_pzl[idx+step_size*wi]) == EC or val.lower() == word[wi].lower()):
            new_pzl[idx+step_size*wi] = word[wi]
        else:
            changed = False; break
        
    if changed: return ''.join(new_pzl)
    else: return pzl

def show(pzl, w):
    print('\n'.join(pzl[rs:rs+w] for rs in range(0, len(pzl), w)))
    print()

def valid_cw_struct(pzl, w, ri):
    newPzl = ''.join(x if x==BS else EC for x in pzl)
    
    # symmetry
    if newPzl != newPzl[::-1]:
        asd = []
        for idx, val in enumerate(newPzl):
            if val != newPzl[-1-idx] and val == EC: asd.append(idx)

        return [asd, False][ri]

    # flood fill
    connections = []
    new = [newPzl.find(EC)]
    if new == [-1]: return [[], True][ri]
    while new:
        connections += new
        nNew = []
        for idx in new:
            nbrs = [x for x in [idx-w, idx-1, idx+1, idx+w] if 0<=x<len(pzl) and newPzl[x]!=BS and (x//w == idx//w or x%w == idx%w) and x not in connections and x not in nNew]
            nNew += nbrs
        new = nNew
    connections = {*connections}
    emptySquares = set()
    for idx, val in enumerate(newPzl):
        if val == EC:
            emptySquares.add(idx)
    if emptySquares != connections:
        a = [*(emptySquares-connections)]
        t = sorted([(len(a), a), (len(connections), [*connections])])
        return [t[0][1], False][ri]

    # min word len = 3
    invalid = []
    for idx in range(len(pzl)//w):
        row = newPzl[idx*w:idx*w+w]
        cs = valid_slice(row, ri)

        if not cs and ri: return [[], False][ri]
        if not ri:
            for val in cs: invalid.append(idx*w + val)
    
    for idx in range(w):
        col = newPzl[idx::w]
        cs = valid_slice(col, ri)
        
        if not cs and ri: return [[], False][ri]
        if not ri:
            for val in cs: invalid.append(idx + val*w)
    
    if not ri: return invalid
    return [[], True][ri]

def valid_slice(slice, ri):
    if EC not in slice: return [[], True][ri]
    if BS not in slice: return [[], True][ri]

    invalid = []; seen = set()
    for idx, val in enumerate(slice):
        if val == BS: continue
        if idx in seen: continue

        wLen = 1; tmp = [idx]
        while idx+wLen < len(slice) and slice[idx+wLen] != BS:
            seen.add(idx+wLen); tmp.append(idx+wLen); wLen += 1

        if wLen < 3 and not ri: invalid += tmp
        if wLen < 3 and ri: return False
    
    if not ri: return invalid
    return True

def fix(pzl, w, nbs):
    invalid = valid_cw_struct(pzl, w, False)
    #print(invalid)
    if len(invalid) <= nbs:
        for idx in invalid:
            pzl, nbs = place_bs(pzl, nbs, idx, w)

    #print(pzl)
    return pzl, nbs

def arrange(choices, pzl, w):
    return [x[1] for x in sorted([(-h(ch, pzl, w), ch) for ch in choices])]

def h(c, pzl, w):
    brs = [n for n in [c-w, c-1, c+1, c+w] if 0<=n<len(pzl) and n//w == c//w or n%w == c%w]
    nbrs = [pzl[n] for n in brs]

    sides = 0
    for idx in brs:
        if idx//w in {0, len(pzl)//w-1} or idx%w in {0, w-1}:
            sides += 1

    letterct = 0
    for x in nbrs:
        if x!=BS and x!=EC:
            letterct += 1

    return nbrs.count(EC)*50 - nbrs.count(BS)*10 + 150*letterct + c%(w//2-1) * 4 - sides * 10

def gen_cw_struct(pzl, w, nbs, dnp):
    #print(pzl, nbs)
    if pzl in dnp: return ''
    if nbs < -1: return ''
    if nbs <= 0 and valid_cw_struct(pzl, w, True): return pzl
    if not valid_cw_struct(pzl, w, True):
        npzl, nnbs = fix(pzl, w, nbs)

        if npzl != pzl:
            bF = gen_cw_struct(npzl, w, nnbs, dnp)
            if bF: return bF
        return ''
    
    choices = [x for x in range(len(pzl)//2) if pzl[x] == EC]

    for ch in arrange(choices, pzl, w):
        npzl, nnbs = place_bs(pzl, nbs, ch, w)
        bF = gen_cw_struct(npzl, w, nnbs, dnp)
        if bF: return bF
    return ''

def read_dictionary():
    global FREQ; FREQ = {}
    word_list = open(args[0]).read().splitlines()
    total = 0
    dct = {}
    for word in word_list:
        word_len = len(word)
        spec = EC * word_len

        if spec in dct:
            dct[spec].add(word)
        else:
            dct[spec] = {word}

        for i,v in enumerate(word):
            spec = EC * word_len
            spec = spec[:i] + v + spec[i+1:]

            if spec in dct:
                dct[spec].add(word)
            else:
                dct[spec] = {word}

            if v not in FREQ: FREQ[v] = 1
            else: FREQ[v] += 1

            total += 1
    
    for key in FREQ:
        FREQ[key] = FREQ[key]/total

    return dct

def transpose(pzl, w):
    return ''.join([pzl[cs::w] for cs in range(w)]), len(pzl)//w

def augment(pzl, w):
    return '#'*(w+2) + ''.join('#'+pzl[rs:rs+w]+'#' for rs in range(0, len(pzl), w)) + '#'*(w+2), w+2

def find_words_from_spec(spec, dct):
    word_len = len(spec)
    words = dct[EC*word_len]

    for i,v in enumerate(spec):
        s = EC * word_len
        s = s[:i] + v + s[i+1:]

        if s not in dct: return set()
        words = words.intersection(dct[s])

    return words

def transposePos(transpose_idx, aw, ap):
    return transpose_idx//aw + transpose_idx%aw * (len(ap)//aw)

def get_locs(ap, aw):
    global LOCS1; LOCS1 = []
    global LOCS2; LOCS2 = []
    global LOCS3; LOCS3 = []
    global LOCS4; LOCS4 = []
    global HWS; HWS = []
    global VWS; VWS = []

    starts = [idx for idx,val in enumerate(ap) if idx>0 and ap[idx-1]==BS and val!=BS]
    ws_lens = []
    for idx in starts:
        row = ap[idx//aw*aw:idx//aw*aw + aw]
        i = idx%aw
        word_len = 0

        while i + word_len < aw and row[i+word_len]!=BS:
            word_len += 1

        ws_lens.append((idx, word_len))

    HWS = ws_lens

    for idx,word_len in ws_lens:
        LOCS1.append([*range(idx, idx+aw*word_len, aw)])

    tp, tw = transpose(ap, aw)
    starts = [idx for idx,val in enumerate(tp) if idx>0 and tp[idx-1]==BS and val!=BS]
    ws_lens = []
    for idx in starts:
        row = tp[idx//tw*tw:idx//tw*tw + tw]
        i = idx%tw
        word_len = 0

        while i + word_len < tw and row[i+word_len]!=BS:
            word_len += 1

        ws_lens.append((idx, word_len))

    VWS = ws_lens

    for idx,word_len in ws_lens:
        LOCS2.append([transposePos(x, tw, tp) for x in range(idx, idx+aw*word_len, aw)])

    LOCS3 = {x:bs for bs in LOCS1 for x in bs}
    LOCS4 = {x:bs for bs in LOCS2 for x in bs}

def get_psbls(ap, aw, tp, tw, dct):
    h_psbls = [v if v != EC else set() for v in ap]
    v_psbls = [v if v != EC else set() for v in ap]

    for ws,wLen in HWS:
        spec = ap[ws:ws+wLen]

        if EC not in spec: continue

        words = find_words_from_spec(spec, dct)

        for w in words:
            for i,v in enumerate(w):
                if type(h_psbls[ws+i]) is set:
                    h_psbls[ws+i].add(v)
    
    if set() in h_psbls:
        return h_psbls
    
    for ws,wLen in VWS:
        spec = tp[ws:ws+wLen]
        if EC not in spec: continue

        words = find_words_from_spec(spec, dct)
        for w in words:
            for i,v in enumerate(w):
                if type(v_psbls[transposePos(ws+i, tw, tp)]) is set:
                    v_psbls[transposePos(ws+i, tw, tp)].add(v)

    if set() in v_psbls:
        return v_psbls
    
    psbls = [x if type(x) is str else x.intersection(v_psbls[i]) for i,x in enumerate(h_psbls)]
    return psbls

def checkDupes(aP, aW, tP, tW):
    hwords = [a for rs, wLen in HWS if '-' not in (a:=aP[rs:rs+wLen])]

    vwords = [a for rs, wLen in VWS if '-' not in (a:=tP[rs:rs+wLen])]
    return len(z:=(hwords+vwords)) == len({*z})

def sortOptions(options):
    a = sorted([(-hu(w), w) for w in options])
    return [x[1] for x in a]

def hu(wrd):
    a = sum(FREQ[le] for le in wrd)
    return a

def solve(ap, aw, tp, tw, dct, psbls):
    #show(ap, aw)
    tp, tw = transpose(ap, aw)

    if not checkDupes(ap, aw, tp, tw): return ''
    if EC not in ap: return ap
    if set() in psbls: return ''

    minlen = 27
    minidx = -1

    for i,v in enumerate(psbls):
        if type(v) is not set: continue
        if len(v) < minlen:
            minlen = len(v); minidx = i

    for ch in psbls[minidx]:
        n_pzl = place_wrd(ap, minidx, 'H', ch, aw)
        n_tp, n_tw = transpose(n_pzl, aw)
        n_psbls = get_psbls(n_pzl, aw, n_tp, n_tw, dct)
        bF = solve(n_pzl, aw, n_tp, n_tw, dct, n_psbls)
        if bF: return bF
    return ''
    
def deAugment(pzl, w):
    return ''.join(x for idx, x in enumerate(pzl) if idx//(w+2) not in {0, len(pzl)//(w+2)-1} and idx%(w+2) not in {0, w+1})

def dumbSolve(ap, aw, dct):
    LOW = []
    for ws,wLen in HWS:
        wrds = find_words_from_spec(ap[ws:ws+wLen], dct)

        w = ''
        for wr in wrds:
            if wr not in LOW:
                w = wr; LOW.append(wr); break
        
        ap = place_wrd(ap, ws, 'H', w, aw)

    return ap

def main():
    t1 = time.time()
    dnp = []
    pzl, nbs, w = parse_arguments()
    # show(struct, w) # cw struct from xword1
    while True:
        struct = gen_cw_struct(pzl, w, nbs, dnp)
        if not struct: exit()
        struct = struct.lower()
        dct = read_dictionary()
        ap, aw = augment(struct, w)
        tp, tw = transpose(ap, aw)
        # show(ap, aw) # augmented
        get_locs(ap, aw)
        psbls = get_psbls(ap, aw, tp, tw, dct)
        #print(psbls)
        dS = dumbSolve(ap, aw, dct)
        dS = deAugment(dS, w)
        show(dS, w)
        bF = solve(ap, aw, tp, tw, dct, psbls)
        if not bF:
            dnp.append(struct)
        # show(bF, aw)
        soln = deAugment(bF, w)
        show(soln, w)
        print(time.time()-t1)
        exit()

if __name__ == '__main__': main()
# Aaryan Sumesh, P2, Class of 25