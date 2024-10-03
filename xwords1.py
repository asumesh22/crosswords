import sys; args = sys.argv[1:]
import re

global stats; stats = {'brute force' : 0, 'quick fix' : 0}

def update(v):
    stats[v] += 1

def parse_args():
    global width, height, num_blocking_squares, file_name, seed_strings
    width = 0; height = 0; num_blocking_squares = 0; file_name = ''; seed_strings = []

    for arg in args:
        if re.search('^\d+x\d+$', arg, re.IGNORECASE): height, width = [int(i) for i in arg.lower().split('x')]
        elif re.search('^\d+$', arg): num_blocking_squares = int(arg)
        elif re.search('^.+\.txt$', arg): file_name = arg
        elif a:=re.findall('^((H|V)\d+x\d+).*$', arg, re.IGNORECASE): seed_strings.append((a[0][1], [int(i) for i in (a[0][0])[1:].lower().split('x') if i!=''], arg[len(a[0][0]):]))
    
    board = '-'*width*height

    if num_blocking_squares%2:
        if width%2 and height%2:
            center = width*height//2
            board = place_hash(board, center)
            num_blocking_squares -= 1
        else:
            print('impossible'); exit()

    for seed in seed_strings:
        pos = seed[1][0]*width+seed[1][1] 
        init = board.count('#')  
        if seed[2] == '#' or seed[2] == '': board = place_hash(board, pos); num_blocking_squares -= board.count('#')-init
        else: board = place_word(board, seed[0], pos, seed[2]); num_blocking_squares -= seed[2].count('#')

    if num_blocking_squares == width * height: board = '#' * width * height; display_board(board); exit()

    # fix
    init = board.count('#')
    locs = [idx for idx, val in enumerate(board) if val == '#']
    for lc in locs:
        if width*height - lc not in locs:
            board = place_hash(board, lc)

    fin = board.count('#')
    num_blocking_squares -= fin-init

    return board

def display_board(board):
    for row_num in range(height): print(''.join([*board[row_num*width:(row_num+1)*width]]))

def place_word(board, direction, position, word):
    word_len = len(word)

    changed_board = [*board]

    step_size = 0
    if direction == 'H' or direction == 'h': step_size = 1
    elif direction == 'V' or direction == 'v': step_size = width

    use_changed = True
    for word_idx in range(word_len):
        if (val:=changed_board[position + step_size*word_idx]) == '-' or val.lower() == word[word_idx].lower(): changed_board[position + step_size*word_idx] = word[word_idx]
        else: use_changed = False; break
            
    if use_changed: return ''.join(changed_board)
    return board

def place_hash(board, position):
    board = place_word(board, 'H', position, '#')
    board = place_word(board, 'H', width*height-position-1, '#')
    return board

def bruteForce(board, num_blocks):
    print(board, num_blocks)
    if num_blocks <= 0 and is_valid(board): return board
    if not is_valid(board):
        newBoard, nb = initial_fix(board, num_blocks)

        if newBoard != board:
            bF = bruteForce(newBoard, nb)
            if bF: 
                update('quick fix')
                return bF
        return ''

    choices = [x for x in range(int(len(board)/2)) if board[x]=='-']

    init = board.count('#')
    update('brute force')

    for ch in choices:
        newBoard = place_hash(board, ch)
        fin = newBoard.count('#')

        diff = fin-init
        bF = bruteForce(newBoard, num_blocks-diff)
        if bF: return bF
    return ''

def checkslice(slc, v):
    if '-' not in slc: return [[], True][v]
    if '#' not in slc: return [[], True][v]

    ret = []; seen = set()
    for idx, val in enumerate(slc):
        if val == '#': continue
        if idx in seen: continue

        wl = 1; tmp = [idx]
        while idx+wl < len(slc) and slc[idx+wl] != '#':
            seen.add(idx+wl); tmp.append(idx+wl); wl += 1

        if wl < 3 and not v: ret += tmp
        elif wl < 3 and v: return False

    if not v: return ret
    return True

def is_valid(board, v = True):
    #print('cp0')

    newBoard = ''.join([x if x == '#' else '-' for x in board])
    if newBoard != newBoard[::-1]: return [[], False][v]
    
    #print('cp1')

    connections = []
    new = [newBoard.find('-')]
    if new == [-1]: return [[], True][v]
    while new:
        connections += new
        new_new = []

        for idx in new:
            nbrs = [x for x in [idx-width, idx-1, idx+1, idx+width] if 0<=x<width*height and newBoard[x] != '#' and (x//width == idx//width or x%width == idx%width) and x not in connections and x not in new_new]
            new_new += nbrs

        new = new_new

    connections = {*connections}

    emptysquares = set()
    for idx, val in enumerate(newBoard):
        if val == '-': emptysquares.add(idx)

    if emptysquares!=connections:
        a = [*(emptysquares-connections)]
        toret = sorted([(len(a), a), (len(connections), [*connections])])
        return [toret[0][1], False][v]

    invalid = []
    for idx in range(height):
        row = newBoard[idx*width:idx*width+width]
        checkSlice = checkslice(row, v)
        if not checkSlice and v: return [[], False][v]

        if not v:
            for val in checkSlice: invalid.append(idx*width + val)
        
    for idx in range(width):
        col = newBoard[idx::width]
        checkSlice = checkslice(col, v)
        if not checkSlice and v: return [[], False][v]

        if not v:
            for val in checkSlice: invalid.append(idx + val*width)

    if not v: return invalid
    return [[], True][v]

def initial_fix(board, numbs):
    invalid = is_valid(board, v = False)
    if len(invalid) <= numbs:
        initcount = board.count('#')
        for idx in invalid:
            board = place_hash(board, idx)
        fincount = board.count('#')
        numbs-=fincount-initcount

    return board, numbs

def main(board):
    board = bruteForce(board, num_blocking_squares)
    display_board(board)
    print(stats)

board = parse_args()
if __name__ == '__main__': main(board)
# Aaryan Sumesh, Period 2, Class of 2025