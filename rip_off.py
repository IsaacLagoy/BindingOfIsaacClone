""" to do """
# combine player and player bullets into temporary entity array

# pip and built-in imports
import pygame
import random
import sys
import time

# local imports
import rooms
import entities
import tiles

# global variables
ROOM_X, ROOM_Y = 15, 9

# definitions
def sort_enemies(lst):
        
    index = 0
    while index < len(lst):
        if index == 0:
            index = index + 1
        if lst[index].y >= lst[index - 1].y:
            index = index + 1
        else:
            lst[index], lst[index-1] = lst[index-1], lst[index]
            index = index - 1
                
    return lst
                
def generate_layout():
    
    size = random.randint(6, 6)*2-1
    layout = [[False for j in range(size)] for i in range(size)] # random odd number 7 to 11 (area)
    layout = generate_branch(size//2, size//2, layout, size)
    
    # loads rooms

    for x in range(len(layout)):
        for y in range(len(layout)):
            adjacents = get_adjacents(layout, x, y)
            
            if layout[x][y]: layout[x][y] = rooms.room(x, y, ROOM_X, ROOM_Y, adjacents, resolution) # creates room
    
    return layout
    
def generate_branch(x, y, layout, size):
    
    layout[x][y] = True # sets current room to an open room
    
    for i in range(-1, 2, 2):
        if not (x+i >= 0 and x+i < size): continue # continue to avoid IndexOutOfBounds Error  
        if not layout[x+i][y] and sum(bool(k) for k in get_adjacents(layout, x+i, y)) < 2 and random.uniform(0, 1) < .5:
            layout = generate_branch(x + i, y, layout, size) # checks for x rooms
        
    for j in range(-1, 2, 2):
        if not (y+j >= 0 and y+j < size): continue
        if not layout[x][y+j] and sum(bool(k) for k in get_adjacents(layout, x, y+j)) < 2 and random.uniform(0, 1) < .5:
            layout = generate_branch(x, y + j, layout, size) # checks for y rooms

    return layout

def get_adjacents(array, x, y):
        
    # sees if room has adjacent rooms
    adjacents = [False, False, False, False]
        
    if x - 1 >= 0:
        if array[x-1][y]: adjacents[0] = True
    if x + 1 < len(array):
        if array[x+1][y]: adjacents[2] = True
    if y - 1 >= 0:
        if array[x][y-1]: adjacents[1] = True
    if y + 1 < len(array):
        if array[x][y+1]: adjacents[3] = True
                
    return adjacents

def coordinate_to_tile(x, y):
    
    tile = [0, 0]
    
    tile[0] = int(x/resolution[0]*ROOM_X)
    tile[1] = int(y/resolution[1]*ROOM_Y)
    
    return tile

def check_tile_solid(coord): # coord is array of x and y
    
    x = coord[0]
    y = coord[1]
    return layout[player_x][player_y].floor_plan[x][y].solid

def scale_image(image):
    
    return pygame.transform.scale(image, (image.get_width()/16*resolution[0]/layout[player_x][player_y].room_width, image.get_height()/16*resolution[1]//layout[player_x][player_y].room_length))

def offset_location(x, y, image):
    
    return (x - image.get_width()/16*resolution[0]/layout[player_x][player_y].room_width//2, y - image.get_height()/16*resolution[1]/layout[player_x][player_y].room_length)

# top level variables
resolution = (1024, 512) # controls game size ****************************************************************************************
layout = generate_layout()
layout[len(layout)//2][len(layout)//2] = rooms.starter(len(layout)//2, len(layout)//2, ROOM_X, ROOM_Y, layout[len(layout)//2][len(layout)//2].adjacents, resolution)
player_bullets = []

# initialize pygame window
pygame.init()
clock = pygame.time.Clock()
surface = pygame.display.set_mode(resolution)
pygame.display.set_caption('test')
game_running = True
frames_per_second = 30

# sets up player variables
player_x, player_y = len(layout)//2, len(layout)//2
player = entities.player(resolution[0]//2, resolution[1]//2, 4, 1, resolution[0]//100, frames_per_second//2, resolution) 

# monster variables


######################################################################
#############            Game Running             ####################
######################################################################


while game_running:
    
    # allows program to quit 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
    
    """ USER INPUT """
    
    pressed = pygame.key.get_pressed()
    player.move( # player movement (direction control in move() func)
        pressed[pygame.K_w] and not check_tile_solid(coordinate_to_tile(player.x, player.y - player.movement)), 
        pressed[pygame.K_a] and not check_tile_solid(coordinate_to_tile(player.x - player.movement, player.y)), 
        pressed[pygame.K_s] and not check_tile_solid(coordinate_to_tile(player.x, player.y + player.movement)), 
        pressed[pygame.K_d] and not check_tile_solid(coordinate_to_tile(player.x + player.movement, player.y))
        )
    
    # overrides player facing direction for fire angle
    if pressed[pygame.K_RIGHT] : player.direction = 'd'
    elif pressed[pygame.K_LEFT] : player.direction = 'a'
    elif pressed[pygame.K_UP] : player.direction = 'w'
    elif pressed[pygame.K_DOWN] : player.direction = 's'
    if pressed[pygame.K_RIGHT] or pressed[pygame.K_LEFT] or pressed[pygame.K_UP] or pressed[pygame.K_DOWN]: 
        
        # fires bullets when cooldown is over
        if player.can_fire():
            player_bullets.append(entities.player_bullet(player.bullet_speed, player.damage, player.x, player.y-player.image.get_height()//2, player.direction, player.range))
    
    """ DOORS """
    
    # checks for doors
    coords = coordinate_to_tile(player.x, player.y)
    
    if type(layout[player_x][player_y].floor_plan[coords[0]][coords[1]]) == tiles.door:
        
        temp_x = layout[player_x][player_y].floor_plan[coords[0]][coords[1]].x_dest
        player_y = layout[player_x][player_y].floor_plan[coords[0]][coords[1]].y_dest # updates players location
        player_x = temp_x
        
        player.set_x(resolution[0]-player.x+10 if player.x > resolution[0]//2 else resolution[0]-player.x-10) # sets players position to opposite door with slight offset
        player.set_y(resolution[1]-player.y+10 if player.y > resolution[1]//2 else resolution[1]-player.y-10)
        
        # clears bullets from screen
        player_bullets = []
        
    """ GRAPHICS """
    
    # clears previous frame
    surface.fill('black')
    
    # builds room
    for x in range(layout[player_x][player_y].room_width):
        for y in range(layout[player_x][player_y].room_length):
                tile_image = pygame.transform.scale(layout[player_x][player_y].floor_plan[x][y].image, (resolution[0]//layout[player_x][player_y].room_width, resolution[1]//layout[player_x][player_y].room_length)) # scales room tiles to fit screen
                surface.blit(tile_image, (resolution[0]//layout[player_x][player_y].room_width*x, resolution[1]//layout[player_x][player_y].room_length*y)) # adds room tiles to screen
                
    """ ENTITY MOVEMENT """
    
    entities_list = layout[player_x][player_y].enemies[:] # creates list of all enities on screen
    entities_list.append(player)
    entities_list += player_bullets
    
    if len(entities_list) > 1 : entities_list = sort_enemies(entities_list) # sorts enemies based on perspective
    for entity in entities_list:
        
        surface.blit(scale_image(entity.image), offset_location(entity.x, entity.y, entity.image)) # adds entity to screen
        
        if type(entity) == entities.player:
            continue
        if type(entity) == entities.player_bullet:
            entity.move()
            if entity.distance > entity.range or entity.x >= resolution[0] or entity.y >= resolution[1]:
                player_bullets.remove(entity) # removes player bullets if they exceed range
        else:
            new_entity = entity.move(player.x, player.y, layout[player_x][player_y], resolution)
            if new_entity: # is true if bullet exists and is returned from the entuty.move() function (for non player bullet)
                layout[player_x][player_y].add_entity(new_entity)    
        
    """ VARIABLE UPDATES """
    
    # reduces bullet cooldown
    player.cooldown -= 1
    player.invincibility -= 1
    
    # checks for collisions
    for entity in layout[player_x][player_y].enemies:
        ecoord = entity.get_hitbox()
        
        # checks for bullet - entity collisions
        for player_bullet in player_bullets:
            bcoord = player_bullet.get_hitbox()
            
            if bcoord[1][0] > ecoord[0][0] and ecoord[1][0] > bcoord[0][0] and bcoord[1][1] > ecoord[0][1] and ecoord[1][1] > bcoord[0][1]:
                
                entity.take_damage(player_bullet.damage, player_bullet.direction) # deals damage and checks for death
                    
                player_bullets.remove(player_bullet)
                
        if entity.is_dead(): # removes entity if it is killed
            layout[player_x][player_y].enemies.remove(entity)
            
        # checks for enemy - player collisions
        pcoord = player.get_hitbox()
        
        if pcoord[1][0] > ecoord[0][0] and ecoord[1][0] > pcoord[0][0] and pcoord[1][1] > ecoord[0][1] and ecoord[1][1] > pcoord[0][1]:
                
            if player.invincibility <= 0: # checks for i-frames
                
                player.take_damage(entity.damage) # deals damage and checks for death2
                
                # plays oof
                entities.play_sound(entities.sounds_folder_path + 'oof.mp3')
                
                player.invincibility = frames_per_second//2 # activates invincibility period
                
                print('ouch')
            
            if player.is_dead(): # death sequence
                game_running = False # stops game when player dies
    
    """ RENDER """
    # checks sound loop
    entities.play_music()
    
    # renders screen
    pygame.display.flip()
    
    clock.tick(frames_per_second)

###########################################################################
################        end sequence                    ###################
###########################################################################

timestamp = time.time()
while timestamp > time.time() + 2:
    
    # draws death screen
    surface.fill('red')
    
    pygame.display.flip()