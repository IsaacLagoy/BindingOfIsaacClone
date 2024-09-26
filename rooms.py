#imports
import tiles
import random
import entities
import sys

assets_folder_path = sys.path[0]+'/Assets/'

#classes
class room():
    
    def __init__(self, x, y, room_width, room_length, adjacents, resolution):
        
        # generates floor plan for room
        self.resolution = resolution
        self.enemies = []
        self.floor_plan = []
        self.x = x
        self.y = y
        self.room_width = room_width # x 
        self.room_length = room_length # y
        self.adjacents = adjacents # w n e s doors
        
        # creates room
        self.build_room({'floor':90,'hole':95,'rock':100})
        self.generate_enemies()
    
    def generate_enemies(self):
        
        
        for i in range(random.randint(1, 3)):
            location = self.get_valid_spawn_coords()
            choices = [
                entities.blue_gnome(location[0], location[1], movement = self.movement_standard(5)),
                entities.green_slime(location[0], location[1], movement = self.movement_standard(4)),
                entities.skull(location[0], location[1], movement = self.movement_standard(3)),
                entities.biden(location[0], location[1], movement = self.movement_standard(2)),
                entities.mao(location[0], location[1], movement = self.movement_standard(2)),
                entities.blue_bus(location[0], location[1], movement = self.movement_standard(6)),
                entities.red_gnome(location[0], location[1], movement = self.movement_standard(5)),
                entities.red_slime(location[0], location[1], movement = self.movement_standard(4)),
                entities.crab(location[0], location[1], movement = self.movement_standard(3)),
                entities.snail(location[0], location[1], movement = self.movement_standard(1)),
                entities.ball_man(location[0], location[1], movement = self.movement_standard(5)),
                entities.green_tank(location[0], location[1], movement = self.movement_standard(4))
            ]
            self.enemies.append(random.choice(choices))
            
        
    def add_doors(self):
            
        # overrides walls with doors
        if self.adjacents[0]: self.floor_plan[self.room_width//2][0] = tiles.door(assets_folder_path + 'stone_door.png', self.x-1, self.y, 'w')
        if self.adjacents[2]: self.floor_plan[self.room_width//2][-1] = tiles.door(assets_folder_path + 'stone_door.png', self.x+1, self.y, 'e')
        if self.adjacents[1]: self.floor_plan[0][self.room_length//2] = tiles.door(assets_folder_path + 'stone_door.png', self.x, self.y-1, 'n')
        if self.adjacents[3]: self.floor_plan[-1][self.room_length//2] = tiles.door(assets_folder_path + 'stone_door.png', self.x, self.y+1, 's')
        
    def get_floor_tile(self, object_chance):
        
        pick = random.randint(0,99)
        if 0 <= pick and pick < object_chance['floor']: 
            return tiles.floor(assets_folder_path + 'stone_floor.png')
        elif object_chance['floor'] <= pick and pick < object_chance['hole']: 
            return tiles.hole(assets_folder_path + 'stone_hole.png')
        elif object_chance['hole'] <= pick and pick < object_chance['rock']: 
            return tiles.rock(assets_folder_path + 'stone_rock.png', 3)
        
    def build_room(self, object_chance):
        
        for x in range(self.room_width):
            row = []
            for y in range(self.room_length):
                
                # creates the outter walls
                if y == 0: row.append(tiles.wall(assets_folder_path + 'stone_wall.png', 'w'))
                elif y == self.room_length - 1: row.append(tiles.wall(assets_folder_path + 'stone_wall.png', 'e'))
                elif x == 0: row.append(tiles.wall(assets_folder_path + 'stone_wall.png', 'n'))
                elif x == self.room_width - 1: row.append(tiles.wall(assets_folder_path + 'stone_wall.png', 's'))
                else:
                    # checks if its placing things in floor position
                    if (x == 1 and y == self.room_length//2) or (x == self.room_width -2 and y == self.room_length//2) or (x == self.room_width//2 and y == 1) or (x == self.room_width//2 and y == self.room_length-2):
                        row.append(tiles.floor(assets_folder_path + 'stone_floor.png'))
                    else:
                        row.append(self.get_floor_tile(object_chance))
                    
            self.floor_plan.append(row)
                    
        self.add_doors()
        
    def sort_enemies(self):
        
        index = 0
        while index < len(self.enemies):
            if index == 0:
                index = index + 1
            if self.enemies[index].y >= self.enemies[index - 1].y:
                index = index + 1
            else:
                self.enemies[index], self.enemies[index-1] = self.enemies[index-1], self.enemies[index]
                index = index - 1
                
    def get_valid_spawn_coords(self):
        
        while True:
            x_max = self.resolution[0]//self.room_width*self.room_width
            y_max = self.resolution[1]//self.room_length*self.room_length # get valid coordinates within room
            
            test_x = random.randint(0, x_max)
            test_y = random.randint(0, y_max)
            
            test_tile = self.coordinate_to_tile(test_x, test_y)
            if not self.floor_plan[test_tile[0]][test_tile[1]].solid: return (test_x, test_y)
            
    def coordinate_to_tile(self, x, y):
    
        tile = [0, 0]
    
        tile[0] = int(x/self.resolution[0]*self.room_width)
        tile[1] = int(y/self.resolution[1]*self.room_length)
    
        return tile
        
    def movement_standard(self, movement):
        
        return int(self.resolution[0]/1024*movement)
    
    def add_entity(self, entity):
        
        self.enemies.append(entity)
        
class starter(room):
    
    def __init__(self, x, y, room_width, room_length, adjacents, resolution):
        
        self.x = x
        self.y = y
        self.room_width = room_width
        self.room_length = room_length
        self.adjacents = adjacents
        self.resolution = resolution
        self.enemies = []
        self.floor_plan = []
            
        # creates room
        
        self.build_room({'floor': 100, 'hole': 100, 'rock': 100})
        