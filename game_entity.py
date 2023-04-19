import pygame,math

def get_collisions(rect,platforms):
    data = []
    for platform in platforms:
        if rect.colliderect(platform):
            data.append(platform)
    return data

ids = 0         

class Physics:

    def __init__(self,x,y,width,height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x,y,width,height)

    def move(self,velocity,platforms):
        collisions_data = {'left': False, 'right': False, 'top': False, 'bottom': False}
        self.rect.x += velocity[0]
        obstacles = get_collisions(self.rect,platforms)
        self.x = int(self.rect.x)

        for obstacle in obstacles:
            if velocity[0] > 0:
                self.rect.right = obstacle.left
                collisions_data['right'] = True
            if velocity[0] < 0:
                self.rect.left = obstacle.right
                collisions_data['left'] = True

        self.rect.y += velocity[1]
        obstacles = get_collisions(self.rect,platforms)
        self.y = int(self.rect.y)

        for obstacle in obstacles:
            if velocity[1] > 0:
                self.rect.bottom = obstacle.top
                collisions_data['bottom'] = True
            if velocity[1] < 0:
                self.rect.top = obstacle.bottom
                collisions_data['top'] = True

        return collisions_data
    
class GameObject:

    def __init__(self,x,y,width,height,animation_data=None,animated=False,default_animation=None,offset=[0, 0]): # animated = boolean to show if the entity is animated or not
        global ids
        ids += 1
        self.id = ids
        self.frame_no = 0
        self.animated = animated
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.physics = Physics(self.x,self.y,width,height)
        self.animator = Animator(self.id)
        self.current_animation = default_animation
        self.flip = [False,False]
        if animation_data != None:
            self.animator.load_animation(animation_data)
        self.rotation = 0
        self.offset = offset


        #self.physics.rect = pygame.Rect(self.physics.x + self.offset[0], self.physics.y + self.offset[1], self.width - self.offset[0], self.height - self.offset[1])

    def update(self,velocity,platforms, offset=[0,0], rect_size=None):
        if rect_size != None:
            self.physics.rect.size = rect_size
        collisions_data = self.physics.move(velocity,platforms)
        self.set_pos(self.physics.rect.x + offset[0], self.physics.rect.y + offset[1])
        if self.animated:
            self.frame_no = (self.frame_no + 1) % self.current_animation_frames_quantity()
            frame_index = self.get_frame()
            frame = self.current_animation_frames()[frame_index]
            return collisions_data,frame
        else:
            return collisions_data
   
    def rect_center(self):
        return self.physics.rect.center
    def get_frame(self):
        return self.frame_no

    def set_pos(self,x,y):
        self.x = x
        self.y = y
    def current_animation_frames_quantity(self):
        return len(self.get_frames()[self.current_animation])
    def current_animation_frames(self):
        return self.animator.frames[self.current_animation]

    def draw(self,surf,*scroll):
        pygame.draw.rect(surf,(255,0,0),pygame.Rect(self.physics.x - scroll[0], self.physics.y - scroll[1], *self.physics.rect.size))

    def display(self,image,surf,scroll_x,scroll_y):
        surf.blit(pygame.transform.flip(pygame.transform.rotate(image,self.rotation),self.flip[0],self.flip[1]),(self.x - self.offset[0] - scroll_x,self.y - self.offset[1] -scroll_y))

    def get_center(self):
        return self.x ,self.y

    def get_frames(self):
        return self.animator.get_frames()

    def change_animation(self,animation):
        if self.animated:
            self.frame_no = 0
            self.current_animation = animation
            self.current_animation_frames_quantity()
            self.current_animation_frames()
            
    
class Animator:

    def __init__(self,entity_id):
        self.frames = {}
        self.entity_id = entity_id
        
    def load_animation(self,animation_data): # [['run',(2,3,4,6)]]
        for data in animation_data:
            self.frames[data[0]] = []
            for i,frame_count in enumerate(data[1]):
                for j in range(frame_count):
                    frame_name = data[0] + '_' + str(i)
                    self.frames[data[0]].append(frame_name)
        
        return self.frames
    def get_frames(self):
        return self.frames
    
    def set_animation(self):
        pass
    def change_animation(self):
        pass
    def play(self,animation,duration):
        pass
        



animation_manager = {} # information on animation of every entity



















        
