from random import randint, random, choice
from math import log, pi, sin, cos

import sys

sys.setrecursionlimit(100000)

####################
#   world legend   #
# ---------------- #
#     0 = water    #
#     1 = land	   #
#     2 = tree     #
#     3 = sand     #
####################

# process
# 1. fill board with water
# 2. place random island starting points
# 3. expand each island with a decreasing possibility of expansion per expansion step

map_size = 300

# random terrain gen
world = [[0 for x in range(map_size)] for y in range(map_size)]


def print_board(board):
    for row in board:
        print(" ".join([(" ", "X", "O", "*")[cell] for cell in row]))


# distance takes the coordinates between two points and returns the euclidean distance
def distance(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


# get_neighbors takes the position of a starting point and the dimensions of the board and returns a list of all valid points a given distance from that starting point
def get_near(pos, dist):
    x1, y1 = pos
    near = []

    for y2 in range(y1 - dist, y1 + dist):
        for x2 in range(x1 - dist, x1 + dist + 1):
            if abs(distance((x1, y1), (x2, y2)) - dist) < 0.5:
                if 0 <= x2 < map_size and 0 <= y2 < map_size:
                    near.append((x2, y2))
    return near


def get_neighbors_2(pos):
    neighbors = [(pos[0] + dx, pos[1] + dy) for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2)]
    neighbors.remove(pos)
    neighbors = filter(in_bounds, neighbors)
    return neighbors

def get_neighbors(pos):
    neighbors = [(pos[0] + dx, pos[1] + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    neighbors.remove(pos)
    neighbors = filter(in_bounds, neighbors)
    return neighbors


def in_bounds(pos):
    return min(pos) >= 0 and max(pos) < map_size


def gen_line(a, b, board, land):
    "Bresenham's line algorithm"
    dx = abs(b[0] - a[0])
    offset = abs(b[1] - a[1])
    x_, y_ = a
    sx = -1 if a[0] > b[0] else 1
    sy = -1 if a[1] > b[1] else 1
    if dx > offset:
        err = dx / 2.0
        while x_ != b[0]:
            if in_bounds((x_, y_)):
                board[y_][x_] = 1
                land.append((x_, y_))
            err -= offset
            if err < 0:
                y_ += sy
                err += dx
            x_ += sx
    else:
        err = offset / 2.0
        while y_ != b[1]:
            if in_bounds((x_, y_)):
                board[y_][x_] = 1
                land.append((x_, y_))
            err -= dx
            if err < 0:
                x_ += sx
                err += offset
            y_ += sy
    if in_bounds((x_, y_)):
        board[y_][x_] = 1
    land.append((x_, y_))


# gen_islands takes an empty board and returns a board populated with random islands
def gen_islands(board, islands=(map_size // 15)):
    print("Generating Islands...")
    # islands = 1  # Terrain Gen Testing ONLY
    max_radius = 2 * int(map_size ** 0.5)
    height = len(board)
    width = len(board[0])

    land = []
    centers = []
    for i in range(int(islands)):
        # island center point
        x = randint(0, width - 1)
        y = randint(0, height - 1)
        centers.append((x, y))

        num_vertices = 15
        d_theta = 2 * pi / num_vertices
        vertices = []
        angle = 0
        for i in range(num_vertices):
            # TODO: change distance in a smooth way, and connect back to start smoothly
            dist = randint(int(max_radius * 0.75), max_radius)
            vertices.append((x + cos(angle) * dist, y + sin(angle) * dist))
            angle += d_theta

        # Draw Vertices
        for v in vertices:
            x_, y_ = v
            if min(v) >= 0 and max(v) < map_size:
                board[int(y_)][int(x_)] = 1
                land.append((int(x_), int(y_)))

        # Draw Perimeter
        for i in range(-1, num_vertices - 1):
            a = vertices[i]
            b = vertices[i + 1]

            a = (int(a[0]), int(a[1]))
            b = (int(b[0]), int(b[1]))

            gen_line(a, b, board, land)

        # Fill Polygon
        # TODO: split segment in half with drawn line and then fill halves
        def flood_fill(pos):
            # print(pos)
            if in_bounds(pos):
                if board[pos[1]][pos[0]] == 0:
                    board[pos[1]][pos[0]] = 1
                    land.append(pos)
                    flood_fill((pos[0] - 1, pos[1]))
                    flood_fill((pos[0] + 1, pos[1]))
                    flood_fill((pos[0], pos[1] - 1))
                    flood_fill((pos[0], pos[1] + 1))

                    return True
            return False

        if not flood_fill((x, y)):  # if unable to seed at center, try a lot of other points
            # Seed the flood fill algorithm with many points adjacent to vertices
            for v in vertices:
                if int(v[0]) < x:
                    dx = 1
                elif int(v[0]) > x:
                    dx = -1
                else:
                    dx = 0
                if int(v[1]) < y:
                    dy = 1
                elif int(v[1]) > y:
                    dy = -1
                else:
                    dy = 0
                offset = 1
                flood_fill((int(v[0]) + dx * offset, int(v[1]) + dy * offset))

    return board, land, centers


def gen_land_bridge(a, b, board, land, centers):
    width = randint(10, 15)

    for dy in range(-width // 2, width // 2):
        for dx in range(-width // 2, width // 2):
            gen_line((a[0] + dx, a[1] + dy), (b[0] + dx, b[1] + dy), board, land)

    disp = (b[0] - a[0], b[1] - a[1])
    length = (disp[0] ** 2 + disp[1] ** 2) ** 0.5
    vect = (disp[0] / length, disp[1] / length)
    perp_vect = (vect[1], vect[0] * -1)
    for offset in range(-2, 2):
        offset_vect = (round(perp_vect[0] * offset), round(perp_vect[1] * offset))
        gen_line((a[0] + offset_vect[0], a[1] + offset_vect[1]), (b[0] + offset_vect[0], b[1] + offset_vect[1]), board,
                 land)

    return board, land, centers


def gen_land_bridges(world):
    print("Generating land bridges...")
    board, land, centers = world
    for center in centers:
        if random() < 0.5:  # 50% chance of connecting to at least 1 other center
            sorted_centers = sorted(centers, key=lambda c: (center[0] - c[0]) ** 2 + (center[1] - c[1]) ** 2)
            for i in range(1, randint(1, 5)):
                gen_land_bridge(center, sorted_centers[i], board, land, centers)

    return board, land, centers


def add_sand(world):
    print("Adding sand...")
    board, land, centers = world
    land = list(filter(in_bounds, land))
    for pos in land:
        for x, y in get_neighbors_2(pos):
            if board[y][x] == 0:
                if random() < 1.0:
                    board[pos[1]][pos[0]] = 3
                    # TODO: add random chance of extending sand by 1 additional block for varied beach thickness
                    if random() < 0.1:
                        pass

    return board, land, centers


def gen_trees(world):
    print("Generating shrubbery...")
    board, land, centers = world
    for _ in range(100):  # gen 100 trees
        x, y = choice(land)
        if board[y][x] == 1:
            board[y][x] = 2

    return board, land, centers


def gen_world():
    return gen_trees(add_sand(gen_land_bridges(gen_islands(world))))

# print_board(world)
