import pygame, math, random
from functions import *

def get_collisions(rect,platforms):
    data = []
    for platform in platforms:
        if rect.colliderect(platform):
            data.append(platform)
    return data



class Particle:
    def __init__(self, pos, size, color, velocity, kind, life, speed=1, bounce=random.randint(6, 8)/10, interactive=False):
        self.pos = pos
        self.size = size
        self.velocity = velocity
        self.color = color
        self.bounce = bounce
        self.type = kind
        self.life = life
        self.speed = speed
        self.interactive = interactive
        self.rect = pygame.Rect(*pos, size, size)
      
    def update(self, walls):
        collisions_sides = {'right': False, 'left': False, 'top': False, 'bottom': False}
        self.pos[0] += self.velocity[0] * self.speed
        if self.interactive:
            if self.velocity[0] > 0:
                if point_collision([self.pos[0] + self.size, self.pos[1]], walls, [20, 20]):
                    collisions_sides['right'] = True
                    self.velocity[0] *= -self.bounce
                    while point_collision([self.pos[0] + self.size, self.pos[1]], walls, [20, 20]):
                        self.pos[0] += self.velocity[0]
            if self.velocity[0] < 0:
                if point_collision(self.pos.copy(), walls, [20, 20]):
                    collisions_sides['left'] = True
                    self.velocity[0] *= -self.bounce
                    while point_collision(self.pos.copy(), walls, [20, 20]):
                        self.pos[0] += self.velocity[0]

        self.pos[1] += self.velocity[1] * self.speed
        if self.interactive:
            if self.velocity[1] > 0:
                if point_collision([self.pos[0], self.pos[1] + self.size], walls, [20, 20]):
                    collisions_sides['bottom'] = True
                    self.velocity[1] *= -self.bounce
                    while point_collision([self.pos[0], self.pos[1] + self.size], walls, [20, 20]):
                        self.pos[1] += self.velocity[1]
            if self.velocity[1] < 0:
                if point_collision(self.pos.copy(), walls, [20, 20]):
                    collisions_sides['top'] = True
                    self.velocity[1] *= -self.bounce
                    while point_collision(self.pos.copy(), walls, [20, 20]):
                        self.pos[1] += self.velocity[1]
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]

        return collisions_sides
        
    
    def draw_circle(self, surf, scroll):
        pygame.draw.circle(surf, self.color, [(self.pos[0] + int(self.size/2)) - scroll[0], (self.pos[1] + int(self.size/2)) - scroll[1]], int(self.size/2))

    def draw_rect(self, surf, scroll):
        pygame.draw.rect(surf, self.color, pygame.Rect(self.rect.x - scroll[0], self.rect.y - scroll[1], self.size, self.size))
        
