import pygame as pg

from Player import Player
from Game_Variables import *
from Reference import *
from Terrain_Gen import *
from Items import items

from time import sleep


class Camera():
    edge_buffer = 6

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.xvel = 0
        self.yvel = 0

    def move(self):
        newx = self.x + self.xvel * 0.1
        if 0 <= newx <= world_width - 0.0001 and 0 <= newx + grid_width <= world_width - 0.0001:
            self.x = newx

        newy = self.y + self.yvel * 0.1
        if 0 <= newy <= world_height - 0.0001 and 0 <= newy + grid_height <= world_height - 0.0001:
            self.y = newy

    def track(self, player):

        left_dist = player.x + player.xvel * 0.1 - cam.x
        right_dist = (cam.x + cam.width) - (player.x + player.xvel * 0.1 + player.width)
        top_dist = player.y + player.yvel * 0.1 - cam.y
        bottom_dist = (cam.y + cam.height) - (player.y + player.yvel * 0.1 + player.height)

        if left_dist < self.edge_buffer:
            if not cam.x < 0.2:
                self.xvel = player.xvel
        elif right_dist < self.edge_buffer:
            # print cam.x+cam.width
            if not (cam.x + cam.width) > (world_width - 0.2):
                self.xvel = player.xvel

        if top_dist < self.edge_buffer:
            if not cam.y < 0.2:
                self.yvel = player.yvel
        elif bottom_dist < self.edge_buffer:
            if not (cam.y + cam.height) > (world_height - 0.2):
                self.yvel = player.yvel

        self.move()
        self.xvel = 0
        self.yvel = 0

    def get_area(self):
        area = []

        for y in range(0, self.height):
            for x in range(0, self.width):
                area.append((x + int(self.x), y + int(self.y)))

        return area

    def get_perimeter(self):
        perimeter = []

        # top
        perimeter.extend([(x + int(self.x), int(self.y)) for x in range(self.width + 1)])

        for y in range(1, self.height):
            # left
            perimeter.append((int(self.x), y + int(self.y)))
            # right
            perimeter.append((int(self.x) + self.width, y + int(self.y)))

        # bottom
        perimeter.extend([(x + int(self.x), int(self.y) + self.height) for x in range(self.width + 1)])

        return perimeter


class Minimap():
    scale = int(200 / map_size + 1)
    draw_size = scale * map_size

    open = True

    def __init__(self):
        self.image = pg.Surface((map_size * self.scale, map_size * self.scale))
        self.image.set_alpha(63)  # quarter transparent
        self.blocks_seen = []

    def update(self, new_blocks, board):
        for new in new_blocks:
            # if new not in self.blocks_seen:
            draw_color = items[board[new[1]][new[0]]]["color"]
            for y in range(self.scale):
                for x in range(self.scale):
                    self.image.set_at((new[0] * self.scale + x, new[1] * self.scale + y), draw_color)

            self.blocks_seen.append(new)

    def refresh(self, new_blocks, board):
        # print new_blocks
        for block in new_blocks:
            if block in self.blocks_seen:
                self.blocks_seen.remove(block)
        self.update(new_blocks, board)

    def get_image(self, cam):
        img = self.image.copy()

        # draw cam rect
        pg.draw.rect(img, yellow,
                     pg.Rect((cam.x - 1) * self.scale, (cam.y - 1) * self.scale, (cam.width + 2) * self.scale,
                             (cam.height + 2) * self.scale), 1)

        # draw player point
        pg.draw.rect(img, yellow, pg.Rect(int(player.x) * self.scale, int(player.y) * self.scale, self.scale,
                                          self.scale))  # currently disabled - looks like garbage

        return img


def display_inventory(player):
    overlay_height = len(player.inventory) * 30 + 90
    overlay = pg.Surface((200, overlay_height), pg.SRCALPHA)
    fill_color = (0, 68, 135, 63)
    overlay.fill(fill_color)  # quarter transparent blue
    pg.draw.rect(overlay, black, overlay.get_rect(), 1)

    title_image = inventory_font.render(" Inventory ", True, black)
    # print title_image.get_height()
    title_image.set_alpha(255)
    title_x = overlay.get_width() / 2 - title_image.get_width() / 2
    overlay.blit(title_image, (title_x, 20))
    pg.draw.line(overlay, black, (title_x, 25 + title_image.get_height()),
                 (title_x + title_image.get_width(), 25 + title_image.get_height()), 3)

    row = 0
    for i in range(len(player.inventory)):
        item_id, quantity = player.inventory[i]
        if quantity is not 0:
            # print item_id
            item_name = items[item_id]["name"]
            text = item_name + ": " + str(quantity)
            if i == player.inventory_index:
                text = "> " + text
            else:
                text = "     " + text
            # print text
            text_image = inventory_font.render(text, True, black)
            text_image.set_alpha(255)
            # print text_image.get_size()
            overlay.blit(text_image, (20, row * 30 + 75))
            row += 1

    screen.blit(overlay, (screen_width - overlay.get_width() - 10, 10))


def display_crafting(player):
    overlay = pg.Surface((500, 300), pg.SRCALPHA)
    fill_color = (0, 68, 135, 63)
    overlay.fill(fill_color)  # quarter transparent blue
    pg.draw.rect(overlay, black, overlay.get_rect(), 1)

    screen.blit(overlay, (screen_width // 2 - overlay.get_width() // 2, screen_height // 2 - overlay.get_height() // 2))


# takes the board+player to print, the screen to be printed on, and a bounding camera object and updates the screen
def display_board(board, player, screen, cam, minimap):
    screen.fill(blue)
    # draw world
    for y in range(0, cam.height + 2):
        for x in range(0, cam.width + 2):
            gridx = x + int(cam.x)  # calculate board coordinates
            gridy = y + int(cam.y)
            drawx = (x - (cam.x - int(cam.x))) * block_size  # calculate screen coordinates
            drawy = (y - (cam.y - int(cam.y))) * block_size
            try:
                cell = board[gridy][gridx]
            except IndexError:
                pass

            draw_color = items[cell]["color"]  # select color for water, land, and trees

            pg.draw.rect(screen, draw_color, pg.Rect(drawx, drawy, block_size, block_size))

    # draw player
    drawx = (player.x - cam.x) * block_size
    drawy = (player.y - cam.y) * block_size
    screen.blit(pg.transform.scale(player.get_image(), (block_size // 2, block_size // 2)), (drawx, drawy))

    # draw minimap
    if minimap.open:
        screen.blit(minimap.get_image(cam), (10, 10))
        pg.draw.rect(screen, (0, 0, 0), pg.Rect(9, 9, minimap.draw_size + 2, minimap.draw_size + 2), 1)

    # draw inventory if open
    if player.inventory_open:
        display_inventory(player)

    # draw crafting screen if open
    if player.crafting_open:
        display_crafting(player)

    # flip display
    pg.display.update()


# Generate World
world, land, centers = gen_world()

# grid dimensions of screen
grid_width = int(12 * (128 / block_size))
grid_height = int(9 * (128 / block_size))

# pixel dimensions of screen
screen_width = grid_width * block_size
screen_height = grid_height * block_size

# grid dimensions of world
world_width = len(world[0])
world_height = len(world)

# pick island center within camera range to spawn on
spawn = choice([l for l in land if (grid_width / 2 < l[0] < world_width - grid_width / 2) and (
    grid_height / 2 < l[1] < world_height - grid_height / 2)])
# spawn = choice(centers)

# initialize player
player = Player(spawn[0], spawn[1])

# (floating_grid_value, floating_grid_value, int_grid_value, int_grid_value)
cam = Camera(player.x - grid_width / 2, player.y - grid_height / 2, grid_width, grid_height)

# initialize minimap
minimap = Minimap()
minimap.update(cam.get_area(), world)
minimap.update([(x, y) for x in range(map_size) for y in range(map_size)], world)  # Terrain Gen Testing ONLY

# Initialize I/O variables
shift_pressed = False
zoom_change = False

# initialize display
screen = pg.display.set_mode((grid_width * block_size, grid_height * block_size))  # 8 cells by 6 cells (block_sizepx)

# initialize screen
display_board(world, player, screen, cam, minimap)

clock = pg.time.Clock()

done = False
while not done:
    clock.tick(60)

    # user input
    for event in pg.event.get():

        if event.type == pg.QUIT:
            pg.quit()
            done = True
            break

        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_i:
                cam.yvel = -player.speed * 3
            elif event.key == pg.K_k:
                cam.yvel = player.speed * 3
            elif event.key == pg.K_j:
                cam.xvel = -player.speed * 3
            elif event.key == pg.K_l:
                cam.xvel = player.speed * 3
            elif event.key == pg.K_w:
                player.yvel = -player.speed
            elif event.key == pg.K_s:
                player.yvel = player.speed
            elif event.key == pg.K_a:
                player.xvel = -player.speed
            elif event.key == pg.K_d:
                player.xvel = player.speed
            elif event.key == pg.K_e:
                player.inventory_open = not player.inventory_open
                display_board(world, player, screen, cam, minimap)  # update display
            elif event.key == pg.K_m:
                minimap.open = not minimap.open
                display_board(world, player, screen, cam, minimap)  # update display
            elif event.key == pg.K_LSHIFT or event.key == pg.K_RSHIFT:
                shift_pressed = True
            elif event.key == pg.K_TAB:
                player.crafting_open = not player.crafting_open
                display_board(world, player, screen, cam, minimap)

        elif event.type == pg.KEYUP:
            if event.key == pg.K_i:
                cam.yvel = 0
            elif event.key == pg.K_k:
                cam.yvel = 0
            elif event.key == pg.K_j:
                cam.xvel = 0
            elif event.key == pg.K_l:
                cam.xvel = 0
            elif event.key == pg.K_w:
                player.yvel = 0
            elif event.key == pg.K_s:
                player.yvel = 0
            elif event.key == pg.K_a:
                player.xvel = 0
            elif event.key == pg.K_d:
                player.xvel = 0
            elif event.key == pg.K_e:
                pass
            elif event.key == pg.K_LSHIFT or event.key == pg.K_RSHIFT:
                shift_pressed = False

        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button is 1:
                target = player.get_facing()  # get coords of target
                if 0 <= target[0] < world_width and 0 <= target[1] < world_height:  # check if target is in world
                    player.attack(world, target)  # call player attack method
                    minimap.refresh([target], world)  # refresh minimap on target
                    display_board(world, player, screen, cam, minimap)  # update display
            elif event.button is 3:
                target = player.get_facing()  # get coords of target
                if 0 <= target[0] < world_width and 0 <= target[1] < world_height:  # check if target is in world
                    player.place(world, target, player.get_holding())  # call player attack method
                    minimap.refresh([target], world)  # refresh minimap on target
                    display_board(world, player, screen, cam, minimap)  # update display

            elif event.button is 4:
                if shift_pressed:
                    # Zoom In
                    block_size += 1
                    zoom_change = True
                else:
                    if player.inventory_open:
                        player.inventory_index = (player.inventory_index - 1) % len(player.inventory)
                        display_board(world, player, screen, cam, minimap)  # update display
            elif event.button is 5:
                if shift_pressed:
                    # Zoom Out
                    if block_size >= min_block_size:
                        block_size -= 1
                        zoom_change = True
                else:
                    if player.inventory_open:
                        player.inventory_index = (player.inventory_index + 1) % len(player.inventory)
                        display_board(world, player, screen, cam, minimap)  # update display

    # move camera
    if cam.yvel is not 0 or cam.xvel is not 0:
        cam.move()

        # update minimap
        # print cam.get_perimeter()
        minimap.update(cam.get_perimeter(), world)

        display_board(world, player, screen, cam, minimap)  # remove once god-mode is disabled

    # update world vars and update camera upon zoom
    if zoom_change:
        # grid dimensions of screen
        old_grid_width = grid_width
        old_grid_height = grid_height
        grid_width = int(12 * (128 / block_size))
        grid_height = int(9 * (128 / block_size))

        # change cam size and position, staying within world borders
        cam.width, cam.height = grid_width, grid_height
        # focus = (cam.x + old_grid_width // 2, cam.y + old_grid_height // 2)
        # TODO: keep player in same relative location on *screen*
        focus = (player.x, player.y)
        cam.x, cam.y = min(map_size - cam.width - 1, max(1, focus[0] - grid_width / 2)), min(map_size - cam.height - 1,
                                                                                             max(1, focus[
                                                                                                 1] - grid_height / 2))
        # cam.x, cam.y = min(map_size - cam.width - 1, max(1, cam.x + old_grid_width / 2)), min(map_size - cam.height - 1, max(1, cam.y + old_grid_height / 2))

        minimap.update(cam.get_area(), world)

    # move player
    if player.yvel is not 0 or player.xvel is not 0 or zoom_change:
        zoom_change = False
        player.move(world)
        player.update_orientation()

        cam.track(player)
        minimap.update(cam.get_perimeter(), world)
        # minimap.update(cam.get_area(), world)

        display_board(world, player, screen, cam, minimap)


        # facing = player.get_facing()
        # print world[facing[1]][facing[0]]
