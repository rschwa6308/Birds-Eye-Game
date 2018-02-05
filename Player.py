import pygame as pg
import math

from Game_Variables import *
from Reference import *
from Items import *


class Player():
    width = 0.5
    height = 0.5
    image = pg.Surface((width * block_size, height * block_size))
    image.fill(yellow)

    orientation = 0  # values 0-7, 45 degree increments

    speed = 2
    xvel = 0
    yvel = 0

    inventory = []
    inventory_index = 0
    inventory_open = True

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 0.5
        self.height = 0.5
        self.image = pg.Surface((self.width * block_size, self.height * block_size))
        self.image.fill(yellow)
        self.xvel = 0
        self.yvel = 0

        self.inventory = [[4, 10], [3, 15], [5, 20]]

    def update_orientation(self):
        self.orientation = int(-1 * math.degrees(math.atan2(self.yvel, self.xvel)) / 45) % 8
        # print self.orientation

    def get_image(self):
        img = self.image.copy()
        img_rect = img.get_rect()

        arrow = pg.Surface((15, 15))
        arrow_rect = arrow.get_rect()
        arrow.fill(yellow)

        # pg.draw.line(arrow, black, arrow_rect.midtop, arrow_rect.midright, 2)
        # pg.draw.line(arrow, black, arrow_rect.midbottom, arrow_rect.midright, 2)

        pg.draw.line(arrow, black, arrow_rect.midleft, arrow_rect.midright, 2)
        pg.draw.lines(arrow, black, False,
                      [arrow_rect.midtop, [arrow_rect.width - 2, arrow_rect.height / 2], arrow_rect.midbottom], 2)

        arrow = pg.transform.rotate(arrow, self.orientation * 45)

        img.blit(arrow, (img_rect.centerx - arrow.get_width() / 2, img_rect.centery - arrow.get_height() / 2))

        return img

    def move(self, board):
        world_width = len(board[0])
        world_height = len(board)
        unwalkable = [0, 2]
        newx = self.x + self.xvel * 0.1
        if newx < 0.01 or (newx + self.width) > (world_width - 0.01):
            newx = self.x
        newy = self.y
        top_left = board[int(newy)][int(newx)]
        top_right = board[int(newy)][int(newx + self.width)]
        bottom_left = board[int(newy + self.height)][int(newx)]
        bottom_right = board[int(newy + self.height)][int(newx + self.width)]

        if self.xvel > 0:
            if top_right not in unwalkable and bottom_right not in unwalkable:
                self.x = newx
            else:
                self.x = int(newx + self.width) - self.width - 0.00001
        elif self.xvel < 0:
            if top_left not in unwalkable and bottom_left not in unwalkable:
                self.x = newx
            else:
                self.x = int(newx) + 1 + 0.00001

        newx = self.x
        newy = self.y + self.yvel * 0.1
        if newy < 0.01 or (newy + self.height) > (world_height - 0.01):
            newy = self.y
        top_left = board[int(newy)][int(newx)]
        top_right = board[int(newy)][int(newx + self.width)]
        bottom_left = board[int(newy + self.height)][int(newx)]
        bottom_right = board[int(newy + self.height)][int(newx + self.width)]

        if self.yvel < 0:
            if top_left not in unwalkable and top_right not in unwalkable:
                self.y = newy
            else:
                self.y = int(newy) + 1 + 0.00001
        elif self.yvel > 0:
            if bottom_left not in unwalkable and bottom_right not in unwalkable:
                self.y = newy
            else:
                self.y = int(newy + self.height) - self.height - 0.00001

                # print (self.x, self.y)

    def get_facing(self):
        offs = [
            (1, 0),
            (1, -1),
            (0, -1),
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, 1),
            (1, 1)
        ]
        xoff, yoff = offs[self.orientation]
        # print (xoff, yoff)
        facing = (int(self.x + self.width / 2) + xoff, int(self.y + self.height / 2) + yoff)
        return facing

    def attack(self, board, target):
        target_id = board[target[1]][target[0]]
        breaks = items[target_id]["breaks"]
        if breaks is not None:
            board[target[1]][target[0]] = 1
            self.add_inventory(breaks["id"], breaks["quantity"])

    def place(self, board, target, item_id):
        if self.get_quantity(item_id) > 0:
            places = items[item_id]["places"]
            if places is not None:  # check if item is placable
                if board[target[1]][target[0]] is 1:  # check if target is empty (land)
                    # print places
                    board[target[1]][target[0]] = places
                    self.add_inventory(item_id, -1)

    def add_inventory(self, item_id, quantity):
        ids = [a for a, b in self.inventory]
        if item_id in ids:
            i = ids.index(item_id)
            self.inventory[i][1] += quantity
            if self.inventory[i][1] == 0:
                self.inventory.pop(i)
        else:
            self.inventory.append([item_id, quantity])

    def get_quantity(self, item_id):
        ids = [a for a, b in self.inventory]
        return self.inventory[ids.index(item_id)][1]

    def get_holding(self):
        return self.inventory[self.inventory_index][0]
