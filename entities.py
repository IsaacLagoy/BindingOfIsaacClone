# imports
import pygame
import sys

assets_folder_path = sys.path[0]+'/Assets/'
sounds_folder_path = sys.path[0]+'/Sounds/'

# class
class entity():
    
    def __init__(self, x, y, health, damage, movement, image):
        
        self.x = x # position
        self.y = y
        self.dx = 0 # momentum
        self.dy = 0
        self.health = health
        self.damage = damage
        self.movement = movement
        self.image = pygame.image.load(image)
        
    def take_damage(self, damage):
        
        self.health -= damage
    
    def is_dead(self):
        
        return self.health <= 0 # true = death
    
    def set_x(self, x):
        
        self.x = x
        
    def set_y(self, y):
        
        self.y = y
        
    def set_image(self, image):
        
        self.image = pygame.image.load(image).convert()
        
    def get_hitbox(self):
        
        return ((self.x - self.image.get_width(), self.y - self.image.get_height()*2), (self.x + self.image.get_width(), self.y)) # top left, bottom right
    
    def shoot(self, target_x, target_y, max_cooldown, sound_file, image_file):
        
        check = False
        if self.cooldown <= 0:
            
            check = True
            self.cooldown = max_cooldown
            
        self.cooldown -= 1
        if check:
            
            # plays audio
            play_sound(sounds_folder_path + sound_file)
            
            # self, health, x, y, damage, movement, image, target_x, target_y, range
            return basic_bullet(1, self.x, self.y, self.damage, self.movement * 3, assets_folder_path + image_file, target_x, target_y, 300)
        
    def summon(self, max_cooldown, summoned):
        
        check = False
        if self.cooldown <= 0:
            
            check = True
            self.cooldown = max_cooldown
            
        self.cooldown -= 1
        if check:
            return summoned
    
class player(entity):
    
    def __init__(self, x, y, health, damage, movement, fire_rate, resolution):
        
        super().__init__(x, y, health, damage, movement, assets_folder_path + 'elvis.png')
        
        self.frame = 0
        self.frames = {'a' : [assets_folder_path + f'elvis_a{i}.png' for i in range(8)], 
                       's' : [assets_folder_path + f'elvis_s{i}.png' for i in range(8)],
                       'd' : [assets_folder_path + f'elvis_d{i}.png' for i in range(8)],
                       'w' : [assets_folder_path + f'elvis_w{i}.png' for i in range(8)]}
        self.frame_delay = 0
        self.direction = 's'
        self.cooldown = 0
        self.fire_rate = fire_rate
        self.bullet_speed = int(resolution[0]/1024*15)
        self.range = int(resolution[0]/1024*250)
        self.invincibility = 0
        
    def move(self, w, a, s, d):
        
        # calculates change in distance
        dy = int(s-w)*self.movement + self.dy
        dx = int(d-a)*self.movement + self.dx
           
        # updates walking animation
        if self.frame_delay > 1: 
            self.frame = self.frame + 1 if self.frame < 7 else 0
            self.set_image(self.frames[self.direction][self.frame])
            self.frame_delay = 0
        else: self.frame_delay += 1
        
        # determines player diection
        if dx > 0: self.direction = 'd'
        elif dx < 0: self.direction = 'a'
        elif dy > 0: self.direction = 's'
        elif dy < 0: self.direction = 'w'
        
        # updates position
        self.y += dy
        self.x += dx
        
        # reduces momentum
        self.dx //= 2
        self.dy //= 2
        
    def can_fire(self):
        
        if self.cooldown <= 0: # if cooldown, reset and playsound
            self.cooldown = self.fire_rate
            play_sound(sounds_folder_path + 'gun_shot.mp3')
            return True
        return False

class enemy(entity): ################################################################################################
    
    def __init__(self, x, y, health, damage, movement, image):
        
        super().__init__(x, y, health, damage, movement, image)
        
    def move(self, target_x, target_y, room, resolution):
        
        dx = abs(target_x-self.x)
        dy = abs(target_y-self.y)
        if dx == 0: dx = 0.001
        
        tempx = ((dx/(dx+dy)*self.movement) if self.x < target_x else -1*(dx/(dx+dy)*self.movement)) + self.x + self.dx
        x_tile = coordinate_to_tile(tempx, self.y, room.floor_plan, resolution)
        if not room.floor_plan[x_tile[0]][x_tile[1]].solid: # checks is enemy is moving to valid target
            self.x = tempx
            
        tempy = ((dy/(dx+dy)*self.movement) if self.y < target_y else -1*(dy/(dx+dy)*self.movement)) + self.y + self.dy
        y_tile = coordinate_to_tile(self.x, tempy, room.floor_plan, resolution)
        if not room.floor_plan[y_tile[0]][y_tile[1]].solid:
            self.y = tempy
            
        # reduces momentum
        self.dx = self.dx // 2 if self.dx > 2 else 0
        self.dy = self.dy // 2 if self.dy > 2 else 0
        
    def take_damage(self, damage, direction):
        
        self.health -= damage
        
        if direction == 'w': self.dy -= 20
        elif direction == 's': self.dy += 20
        elif direction == 'a': self.dx -= 20
        elif direction == 'd': self.dx += 20
            
class blue_gnome(enemy):
    
    def __init__(self, x, y, health = 1, damage = 1, movement = 5):
        super().__init__(x, y, health, damage, movement, assets_folder_path + 'lil_gnome.png')
        
class red_gnome(enemy):
    
    def __init__(self, x, y, health = 1, damage = 1, movement = 5):
        super().__init__(x, y, health, damage, movement, assets_folder_path + 'red_gnome.png')
        
class biden(enemy):
    
    def __init__(self, x, y, health = 10, damage = 2, movement = 2):
        super().__init__(x, y, health, damage, movement, assets_folder_path + 'biden.png')
        
        self.cooldown = 0
        self.max_cooldown = 60
        
    def move(self, target_x, target_y, room, resolution):
        super().move(target_x, target_y, room, resolution)
        return self.shoot(target_x, target_y, self.max_cooldown, 'biden_blast.mp3', 'biden_blast.png')
        
class mao(enemy):
    
    def __init__(self, x, y, health = 10, damage = 2, movement = 2):
        super().__init__(x, y, health, damage, movement, assets_folder_path + 'mao.png')
        self.cooldown = 0
        self.max_cooldown = 120
        
    def move(self, target_x, target_y, room, resolution):
        super().move(target_x, target_y, room, resolution)
        return self.summon(self.max_cooldown, red_gnome(self.x, self.y, movement = self.movement * 2))
        
class left_right_enemy(enemy): ###################################################################################
    
    def __init__(self, x, y, health, damage, movement, image_a, image_d):
        super().__init__(x, y, health, damage, movement, image_a)
        self.image_a = image_a
        self.image_d = image_d
        
    def move(self, target_x, target_y, room, resolution):
        super().move(target_x, target_y, room, resolution)
        self.set_image(self.image_a if target_x < self.x else self.image_d)
        
class green_slime(left_right_enemy):
    
    def __init__(self, x, y, health = 2, damage = 1, movement = 4):
        super().__init__(x, y, health, damage, movement, assets_folder_path + 'slime_a.png', assets_folder_path + 'slime_d.png')
        
class red_slime(left_right_enemy):
    
    def __init__(self, x, y, health = 2, damage = 1, movement = 4):
        super().__init__(x, y, health, damage, movement, assets_folder_path + 'red_slime_a.png', assets_folder_path + 'red_slime_d.png')
        
class skull(left_right_enemy):
    
    def __init__(self, x, y, health = 3, damage = 1, movement = 3):
        super().__init__(x, y, health, damage, movement, assets_folder_path + 'skull_a.png', assets_folder_path + 'skull_d.png')
        
class blue_bus(left_right_enemy):
    
    def __init__(self, x, y, health = 2, damage = 1, movement = 6):
        super().__init__(x, y, health, damage, movement, assets_folder_path + 'blue_bus_a.png', assets_folder_path + 'blue_bus_d.png')
        
class snail(left_right_enemy):
    
    def __init__(self, x, y, health = 6, damage = 1, movement = 1):
        super().__init__(x, y, health, damage, movement, assets_folder_path + 'snail_a.png', assets_folder_path + 'snail_d.png')
        
class green_tank(left_right_enemy):
    
    def __init__(self, x, y, health = 7, damage = 1, movement = 4):
        super().__init__(x, y, health, damage, movement, assets_folder_path + 'green_tank_a.png', assets_folder_path + 'green_tank_d.png')
        self.cooldown = 0
        self.max_cooldown = 30
        
    def move(self, target_x, target_y, room, resolution):
        super().move(target_x, target_y, room, resolution)
        return self.shoot(target_x, target_y, self.max_cooldown, 'gun_shot.mp3', 'tiny_bullet.png')
        
class symmetric_frame_enemy(enemy): #############################################################################
    
    def __init__(self, x, y, health, damage, movement, images):
        super().__init__(x, y, health, damage, movement, images[0])
        self.images = images
        self.frame = 0
        self.frame_delay = 0
    
    def move(self, target_x, target_y, room, resolution):
        super().move(target_x, target_y, room, resolution)
        
        if self.frame_delay > 1: 
            self.frame = self.frame + 1 if self.frame < len(self.images) - 1 else 0
            self.set_image(self.images[self.frame])
            self.frame_delay = 0
        else: self.frame_delay += 1
        
class crab(symmetric_frame_enemy):
    
    def __init__(self, x, y, health = 4, damage = 2, movement = 3):
        super().__init__(x, y, health, damage, movement, [
            assets_folder_path + 'crab_0.png', 
            assets_folder_path + 'crab_1.png'
            ])
        
class asymmetric_frame_enemy(enemy): #############################################################################
    
    def __init__(self, x, y, health, damage, movement, images_a, images_d):
        super().__init__(x, y, health, damage, movement, images_a[0])
        self.images_a = images_a
        self.images_d = images_d
        self.frame = 0
        self.frame_delay = 0
    
    def move(self, target_x, target_y, room, resolution):
        super().move(target_x, target_y, room, resolution)
        
        if self.frame_delay > 1: 
            self.frame = self.frame + 1 if self.frame < len(self.images_a) - 1 else 0
            self.set_image(self.images_a[self.frame] if target_x < self.x else self.images_d[self.frame])
            self.frame_delay = 0
        else: self.frame_delay += 1
        
class ball_man(asymmetric_frame_enemy):
    
    def __init__(self, x, y, health = 4, damage = 2, movement = 4):
        
        temp_images = [assets_folder_path + f'ball_man_d{i}.png' for i in range(8)]
        
        super().__init__(x, y, health, damage, movement, temp_images[::-1], temp_images)

class player_bullet():
    
    def __init__(self, speed, damage, x, y, direction, range):
        
        self.speed = speed
        self.damage = damage
        self.x = x
        self.y = y
        self.image = pygame.image.load(assets_folder_path + 'elvis_bullet.png')
        self.direction = direction
        self.range = range
        self.distance = 0
        
    def move(self):
        
        if self.direction == 'w': self.y -= self.speed
        elif self.direction == 's': self.y += self.speed 
        elif self.direction == 'a': self.x -= self.speed 
        elif self.direction == 'd': self.x += self.speed 
        
        self.distance += self.speed
        
    def get_hitbox(self):
        
        return ((self.x - self.image.get_width()*2, self.y - self.image.get_height()*3), (self.x + self.image.get_width()*2, self.y))
        
def coordinate_to_tile(x, y, floor_plan, resolution):
    
    tile = [0, 0]
    
    tile[0] = int(x/resolution[0]*len(floor_plan))
    tile[1] = int(y/resolution[1]*len(floor_plan[0]))
    
    return tile

class basic_bullet(enemy):
    
    def __init__(self, health, x, y, damage, movement, image, target_x, target_y, range):
        
        self.movement = movement
        self.damage = damage
        self.x = x
        self.y = y
        self.image = pygame.image.load(image)
        self.target_x = target_x
        self.target_y = target_y
        self.range = range
        self.distance = 0
        self.health = health
        
    # player.x, player.y, layout[player_x][player_y], resolution from rip off
    
    def take_damage(self, damage, direction): # direction does nothing but for player parry
        
        self.health -= damage
        
    def is_dead(self):
        
        return not (self.health > 0 and self.distance < self.range) # true = death
    
    def move(self, x, y, room, resolution):
        
        dx = abs(self.target_x-self.x)
        dy = abs(self.target_y-self.y)
        if dx == 0: dx = 0.001
        
        new_dx = ((dx/(dx+dy)*self.movement) if self.x < self.target_x else -1*(dx/(dx+dy)*self.movement))
        new_dy = ((dy/(dx+dy)*self.movement) if self.y < self.target_y else -1*(dy/(dx+dy)*self.movement))
        
        self.x += new_dx # adjusts position  
        self.y += new_dy
            
        self.distance += self.movement
        
        self.target_x += new_dx # moves destination based on movement
        self.target_y += new_dy
        
# definitions
def play_sound(file):
    
    for i in range(1, num_channels):
        
        if not pygame.mixer.Channel(i).get_busy():
            pygame.mixer.Channel(i).play(pygame.mixer.Sound(file))
            break
    else:
        print('out of channels')
        
def play_music(): # music thread
        
    if not pygame.mixer.Channel(0).get_busy():
        pygame.mixer.Channel(0).play(pygame.mixer.Sound(sounds_folder_path + 'home_depo.mp3'))
        
# for playing sounds
num_channels = 10
pygame.mixer.init()
pygame.mixer.set_num_channels(num_channels)
