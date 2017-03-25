from random import randint, random, choice
from math import log

####################
#    world legend  #
#------------------#
#     0 = water    #
#     1 = land	   #
#     2 = tree     #
####################

#process
#1. fill board with water
#2. place random island starting points
#3. expand each island with a decreasing possibility of expansion per expansion step

map_size = 200


#random terrain gen
world = [[0 for x in range(map_size)] for y in range(map_size)]

def print_board(board):
    for row in board:
        print " ".join([(" ", "X", "O")[cell] for cell in row])


#distance takes the coordinates between two points and returns the euclidean distance
def distance((x1, y1), (x2, y2)):
    return ((x2-x1)**2 + (y2-y1)**2)**0.5




#get_neighbors takes the position of a starting point and the dimensions of the board and returns a list of all valid points a given distance from that starting point
def get_near(x1, y1, dist, height, width):
    near = []
    
    for y2 in range(height):
        for x2 in range(width):
            if abs(distance((x1, y1), (x2, y2)) - dist) < 0.5:
                near.append((x2, y2))
    
    return near



#gen_islands takes an empty board and returns a board populated with random islands
def gen_islands(board, islands=(map_size/10)):
    max_radius = 2 * int(map_size**0.5)
    height = len(board)
    width = len(board[0])

    land = []
    centers = []
    print "Generating Islands..."
    for i in range(int(islands)):
        #island center point
        x = randint(0, width-1)
        y = randint(0, height-1)
##        print x
##        print y
        board[y][x] = 1
        land.append((x,y))
        centers.append((x,y))
        
        #spread island
        for dist in range(1, max_radius):
            for point in get_near(x, y, dist, height, width):
                prob = log((-float(dist)) + max_radius)                             #1.0/distance**0.5		#detirmines island generation spread pattern
                if random() <= prob:
                    board[point[1]][point[0]] = 1
                    land.append(point)

    print "Creating Land Bridges..."
    #make land bridges
    for a in centers:
        #print "a: " + str(a)
        for b in centers:
            #print "b: " + str(b)
            if 2*max_radius < distance(a, b) < 3*max_radius:
                
                if random() < 0.5:
                    try:
                        delta_y = b[1] - a[1]
                        delta_x = b[0] - a[0]
                        slope = float(delta_y) / float(delta_x)

                        width = randint(2, int(max_radius/3))

                        if a[0] < b[0]:
                            for shift in range(width):
                                for x in range(abs(delta_x)):
                                    pos = (a[0] + x, a[1]+int(slope*x) + shift)
                                    board[pos[1]][pos[0]] = 1
                        else:
                            for shift in range(width):
                                for x in range(abs(delta_x)):
                                    pos = (b[0] + x, b[1]+int(slope*x) + shift)
                                    board[pos[1]][pos[0]] = 1
                    except:
                        print "land bridges generator threw an error"


    
    return (board, land)





def gen_trees((board, land)):

    for x in range(100):        #gen 100 trees
        pos = choice(land)
        board[pos[1]][pos[0]] = 2
    
    return (board, land)






world, land = gen_trees(gen_islands(world))




print_board(world)









