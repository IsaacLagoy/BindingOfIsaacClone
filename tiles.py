# imports
import pygame

# classes
class tile():
    
    def __init__(self, image, solid):
        
        self.image = pygame.image.load(image)
        self.solid = solid
        
    def set_solid(self, solid):
        
        self.solid = solid
        
class rock(tile):
    
    def __init__(self, image, health):
        
        self.image = pygame.image.load(image)
        self.solid = True
        self.health = health
        
class wall(tile):
    
    def __init__(self, image, rotation):
        
        self.solid = True
        self.rotation = rotation
        self.image = pygame.image.load(image)
        self.image = pygame.transform.rotate(self.image, {'n':90, 'e':180, 's':270, 'w':0}[self.rotation])
            
class hole(tile):
    
    def __init__(self, image):
        
        self.image = pygame.image.load(image)
        self.solid = True
        
class floor(tile):
    
    def __init__(self, image):
        
        self.image = pygame.image.load(image)
        self.solid = False
        
class door(tile):
    
    def __init__(self, image, x_dest, y_dest, rotation):
        
        self.image = pygame.image.load(image)
        self.x_dest = x_dest
        self.y_dest = y_dest
        self.rotation = rotation
        self.solid = False
        self.image = pygame.transform.rotate(self.image, {'n':90, 'e':180, 's':270, 'w':0}[self.rotation])