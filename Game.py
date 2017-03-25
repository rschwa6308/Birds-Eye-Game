import pygame as pg

from Player import Player
from Game_Variables import *
from Reference import *
from Terrain_Gen import *
from Items import items








class Camera():

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.xvel = 0
        self.yvel = 0


    def move(self):
        newx = self.x + self.xvel * 0.1
        if 0 <= newx <= world_width-0.0001 and 0 <= newx+grid_width <= world_width-0.0001:
            self.x = newx
            
        newy = self.y + self.yvel * 0.1
        if 0 <= newy <= world_height-0.0001 and 0 <= newy+grid_height <= world_height-0.0001:
            self.y = newy
    
    
    def track(self, player, edge_buffer):

        left_dist = player.x + player.xvel*0.1 - cam.x
        right_dist = (cam.x+cam.width) - (player.x+player.xvel*0.1+player.width)
        top_dist = player.y + player.yvel*0.1 - cam.y
        bottom_dist = (cam.y+cam.height) - (player.y+player.yvel*0.1+player.height)

        if left_dist < edge_buffer:
            if not cam.x < 0.2:
                self.xvel = player.xvel
        elif right_dist < edge_buffer:
            #print cam.x+cam.width
            if not (cam.x+cam.width) > (world_width-0.2):
                self.xvel = player.xvel

        if top_dist < edge_buffer:
            if not cam.y < 0.2:
                self.yvel = player.yvel
        elif bottom_dist < edge_buffer:
            if not (cam.y+cam.height) > (world_height-0.2):
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

        perimeter.extend([(x + int(self.x), int(self.y)) for x in range(self.width)])

        for y in range(1, self.height-1):
            perimeter.append((int(self.x), y + int(self.y)))
            perimeter.append((int(self.x) + self.width-1, y + int(self.y)))

        perimeter.extend([(x + int(self.x), int(self.y) + self.height-1) for x in range(self.width)])

        return perimeter







          
class Minimap():
    
    scale = 200/map_size + 1

    open = True
    
    def __init__(self):
        self.image = pg.Surface((map_size*self.scale, map_size*self.scale))
        self.image.set_alpha(64)        #quarter transparent
        self.blocks_seen = []

    def update(self, new_blocks, board):
        for new in new_blocks:
            if new not in self.blocks_seen:
                for y in range(self.scale):
                    for x in range(self.scale):
                        #print new
                        draw_color = items[board[new[1]][new[0]]]["color"]
                        self.image.set_at((new[0]*self.scale + x, new[1]*self.scale + y), draw_color)

                self.blocks_seen.append(new)

    def refresh(self, new_blocks, board):
        #print new_blocks
        for block in new_blocks:
            if block in self.blocks_seen:
                self.blocks_seen.remove(block)
        self.update(new_blocks, board)

    def get_image(self, cam):
        img = self.image.copy()

        #draw cam rect
        pg.draw.rect(img, yellow, pg.Rect(cam.x*self.scale, cam.y*self.scale, cam.width*self.scale, cam.height*self.scale), 1)

        #draw player point
        #pg.draw.rect(img, yellow, pg.Rect(int(player.x)*self.scale, int(player.y)*self.scale, self.scale, self.scale))     #currently disabled - looks like garbage

        return img
    



def display_inventory(player):
    overlay_height = len(player.inventory) * 30 + 75
    overlay = pg.Surface((200, overlay_height), pg.SRCALPHA)
    overlay.fill((0,0,0, 64))                                #quarter transparent black
    #pg.draw.rect(overlay, black, overlay.get_rect(), 5)

    title_image = inventory_font.render(" Inventory ", True, black)
    #print title_image.get_height()
    title_image.set_alpha(255)
    title_x = overlay.get_width()/2 - title_image.get_width()/2
    overlay.blit(title_image, (title_x, 20))
    pg.draw.line(overlay, black, (title_x, 25 + title_image.get_height()), (title_x + title_image.get_width(), 25 + title_image.get_height()), 3)

    row = 0
    for i in range(len(player.inventory)):
        item_id, quantity = player.inventory[i]
        if quantity is not 0:
            #print item_id
            item_name = items[item_id]["name"]
            text = item_name + ": " + str(quantity)
            if i is player.inventory_index:
                text += "   *"
            #print text
            text_image = inventory_font.render(text, True, black)
            text_image.set_alpha(255)
            #print text_image.get_size()
            overlay.blit(text_image, (20, row*30 + 75))
            row += 1

    screen.blit(overlay, (screen_width - overlay.get_width() - 10, 10))

    pg.display.update()





#display_board takes the board+player to print, the screen to be printed on, and a bounding camera object and updates the screen
def display_board(board, player, screen, cam, minimap):
    screen.fill(blue)
    #draw world
    for y in range(0, cam.height+1):
        for x in range(0, cam.width+1):
            gridx = x+int(cam.x)						#calculate board coordinates
            gridy = y+int(cam.y)
            drawx = (x - (cam.x - int(cam.x))) * block_size			#calculate screen coordinates
            drawy = (y - (cam.y - int(cam.y))) * block_size
            cell = board[gridy][gridx]

            draw_color = items[cell]["color"]                            #select color for water, land, and trees
                

            pg.draw.rect(screen, draw_color, pg.Rect(drawx, drawy, block_size, block_size))

    #draw player
    drawx = (player.x - cam.x) * block_size
    drawy = (player.y - cam.y) * block_size
    screen.blit(player.get_image(), (drawx, drawy))
    

    #draw minimap
    if minimap.open:
        screen.blit(minimap.get_image(cam), (10, 10))


    #draw inventory if open
    if player.inventory_open:
        display_inventory(player)


    #flip display
    pg.display.update()




    
#grid dimensions of screen
grid_width = 12 * (128/block_size)
grid_height = 9 * (128/block_size)

#pixel dimensions of screen
screen_width = grid_width * block_size
screen_height = grid_height * block_size

#grid demensions of world
world_width = len(world[0])
world_height = len(world)
  
#initialize display
screen = pg.display.set_mode((grid_width*block_size, grid_height*block_size))			#8 cells by 6 cells (block_sizepx)

#pick island center within camera range to spawn on
spawn = choice([l for l in land if (grid_width/2 < l[0] < world_width-grid_width/2) and (grid_height/2 < l[1] < world_height-grid_height/2)])

#initialize player
player = Player(spawn[0], spawn[1])


#(floating_grid_value, floating_grid_value, int_grid_value, int_grid_value)
cam = Camera(player.x-grid_width/2, player.y-grid_height/2, grid_width, grid_height)

#initialize minimap
minimap = Minimap()
minimap.update(cam.get_area(), world)


#initialize screen
display_board(world, player, screen, cam, minimap)




clock = pg.time.Clock()

done = False
while not done:
    clock.tick(60)
    
    #user input
    for event in pg.event.get():
      
        if event.type == pg.QUIT:
            pg.quit()
            done = True
            break
            
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_i:
                cam.yvel = -player.speed
            elif event.key == pg.K_k:
                cam.yvel = player.speed
            elif event.key == pg.K_j:
                cam.xvel = -player.speed
            elif event.key == pg.K_l:
                cam.xvel = player.speed
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
                display_board(world, player, screen, cam, minimap)          #update display
            elif event.key == pg.K_m:
                minimap.open = not minimap.open
                display_board(world, player, screen, cam, minimap)  # update display

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

        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button is 1:
                target = player.get_facing()                                        #get coords of target
                if 0 <= target[0] < world_width and 0 <= target[1] < world_height:  #check if target is in world
                    player.attack(world, target)                                        #call player attack method
                    minimap.refresh([target], world)                                    #refresh minimap on target
                    display_board(world, player, screen, cam, minimap)                  #update display
            elif event.button is 3:
                target = player.get_facing()                                        #get coords of target
                if 0 <= target[0] < world_width and 0 <= target[1] < world_height:  # check if target is in world
                    player.place(world, target, player.get_holding())                   #call player attack method
                    minimap.refresh([target], world)                                    #refresh minimap on target
                    display_board(world, player, screen, cam, minimap)                  #update display

            elif event.button is 4:
                if player.inventory_open:
                    player.inventory_index = (player.inventory_index - 1) % (len(player.inventory) - 1)
                    display_board(world, player, screen, cam, minimap)      # update display
            elif event.button is 5:
                if player.inventory_open:
                    player.inventory_index = (player.inventory_index + 1) % (len(player.inventory) - 1)
                    display_board(world, player, screen, cam, minimap)      #update display


      

    #move camera
    if cam.yvel is not 0 or cam.xvel is not 0:
        cam.move()

        #update minimap
        #print cam.get_perimeter()
        minimap.update(cam.get_perimeter(), world)
    
        display_board(world, player, screen, cam, minimap)          #remove once god-mode is disabled
    
      
    #move player
    if player.yvel is not 0 or player.xvel is not 0:
        player.move(world)
        player.update_orientation()
        
        cam.track(player, 3)
        minimap.update(cam.get_perimeter(), world)
        
        display_board(world, player, screen, cam, minimap)


    #facing = player.get_facing()
    #print world[facing[1]][facing[0]]
    
            


























