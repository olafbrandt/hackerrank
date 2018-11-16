#!/bin/python

import sys, copy

def getNeighbors(grid, x, y, match = None, mask = None):
    n = {}
    w = len(grid[0])
    h = len(grid)
    if (type(mask) == str and len(mask) == 9):
        mask = [mask[i:i+3] for i in range(0, len(mask), 3)]
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if (y+dy >= 0) and (y+dy < h):
                if (x+dx >= 0) and (x+dx < w):
                    if (mask is None) or (mask[1+dy][1+dx] != '0'):
                        if ((match is None and dx != 0 and dy != 0) or match == grid[y+dy][x+dx]):
                            #print (x, y, dx, dy, file=sys.stderr)
                            n[str([x+dx,y+dy])] = grid[y+dy][x+dx]
    return(n)

def segment(grid):
    total = 0
    singles = 0
    groups = {}
    cellToGroup = {}
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            g = None
            if (grid[r][c] == '-'):
                continue
            total += 1
            mn = getNeighbors(grid, c, r, grid[r][c], '010101010')
            for k in mn.keys():
                if k in cellToGroup:
                    if g is not None and cellToGroup[k] != g:
                        ng = cellToGroup[k]
                        for i in groups[g]:
                            cellToGroup[i] = ng
                        groups[ng].extend(groups[g])
                        del groups[g]
                        g = ng
     
                    g = cellToGroup[k]
            if g is None and len(mn):
                g = str([c,r])
                cellToGroup[g] = g
                groups[g] = [g]
            if g is None:
                singles += 1
            for k in mn.keys():
                if k not in cellToGroup:
                    cellToGroup[k] = g
                    groups[g].append(k)
    return (groups, singles, total)

def compactify(grid):
    for c in range(len(grid[0])):
        dr = len(grid)-1
        for r in range(len(grid)-1,-1,-1):
            grid[dr][c] = grid[r][c]
            if (grid[r][c] != '-'):
                dr -= 1
        while dr >= 0:
            grid[dr][c] = '-'
            dr -= 1
    #print('\n'.join([''.join(r) for r in grid]), file=sys.stderr)
    for c in range(len(grid[0])):
        if (''.join([r[c] for r in grid]) == '-'*len(grid)):
            #print ('empty column', c, file=sys.stderr)
            #print('before', file=sys.stderr)
            #print('\n'.join([''.join(r) for r in grid]), file=sys.stderr)
            for r in range(len(grid)):
                del grid[r][c]
                grid[r].append('-')
            #print('after', file=sys.stderr)
            #print('\n'.join([''.join(r) for r in grid]), file=sys.stderr)
    return (grid)
            
def removeGroup(grid, group):
    for c in group:
        c = eval(c)
        grid[c[1]][c[0]] = '-'
    #print('\n'.join([''.join(r) for r in grid]), file=sys.stderr)
    return (compactify(grid))

def singleScore(grid, group):
    new_grid = copy.deepcopy(grid)
    new_grid = removeGroup(new_grid, group)
    new_grid = compactify(new_grid)
    (groups, singles, total) = segment(new_grid)
    #print ('singles: {:2}, group #{:2}, group: {}'.format(singles, len(group), group), file=sys.stderr)
    return (singles)

def distance_from(group, col, row):
    total = sum([round(((eval(c)[0]-col)**2 + (eval(c)[1]-row)**2)**0.5,2) for c in group])
    avg100 = int((total * 100) // len(group))
    print ('dist: orig:[{},{}] avg:{} {} {}'.format(col, row, avg100, group, [round(((eval(c)[0]-col)**2 + (eval(c)[1]-row)**2)**0.5,2) for c in group]), file=sys.stderr)
    return (avg100)
    
def nextMove(cols, rows, color, grid):
    print('cols={}, rows={}, k={}, grid=\n{}'.format(cols, rows, color,
                                                   '\n'.join([''.join(r) for r in grid])), file=sys.stderr)
    (groups, singles, total) = segment(grid)
    print('total: {}, singles: {}, groups: {}'.format(total, singles, len(groups)), file=sys.stderr)
    best_group = None
    
    best_func = lambda arg: len(arg[1])
    best_func = lambda arg: 0 - max([(cols-1-eval(c)[0])**2 + (eval(c)[1]**2)**0.5 for c in arg])
    best_func = lambda arg: singleScore(grid, arg)
    
    best_val = 0
    best_dist = 0
    best_group = None
    for (k,v) in groups.items():
        #print ("K:",k,"V:",v, file=sys.stderr)
        val = best_func(v)
        dist = distance_from(v, len(grid[0]), len(grid))
        if best_group is None:
            best_group = k
            best_val = val
            best_dist = distance_from(v, len(grid[0]), len(grid))
        elif best_val > val or (best_val == val and best_dist > dist):
            best_group = k
            best_val = val
            best_dist = dist
            print ('new best: singles:{}, dist:{}'.format(best_val, best_dist), file=sys.stderr)
    print('best: {}, len:{}, {}'.format(best_val, len(groups[best_group]), best_group), file=sys.stderr)
    best_group = eval(best_group)
    print (best_group[1], best_group[0])

if True:
    rows,cols,k = [ int(i) for i in input().strip().split() ] 
    grid = [[i for i in str(input().strip())] for _ in range(rows)] 
    nextMove(cols, rows, k, grid)
