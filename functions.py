import json, pygame, math, random

from copy import deepcopy
tile_size = 20

def map_extreme_points(map_data):
    largest = [-99999999,-99999999]
    smallest = [9999999,99999999]
    for layer in list(map_data):
        for image_name in list(map_data[layer]):
            for pos in map_data[layer][image_name]:
                if pos[0] > largest[0]:
                    largest[0] = pos[0]
                if pos[1] > largest[1]:
                    largest[1] = pos[1]
                if pos[0] < smallest[0]:
                    smallest[0] = pos[0]
                if pos[1] < smallest[1]:
                    smallest[1] = pos[1]
    return smallest,largest

def load_map(path, map_data):
    #global map_data
    file = open(path,'r')
    data = file.read()
    file.close()
    loaded_map = json.loads(data)
    map_data = deepcopy(loaded_map)
    for layer in map_data:
        for image_type in map_data[layer]:
            map_data[layer][image_type] = [tuple(pos) for pos in map_data[layer][image_type]]
            map_data[layer][image_type] = set(map_data[layer][image_type])
    return map_data
            
def load_image(path,color_key=(0,0,0)):
    image = pygame.image.load(path).convert()
    image.set_colorkey(color_key)
    return image.copy()    
    
def load_group(path,name,no_of_images,mapper=None, images={}):
    color_key = (0, 0, 0)
    for i in range(no_of_images):
        image_id = name + '_' + str(i)
        image = pygame.image.load(path + '/' + image_id + '.png').convert()
        image.set_colorkey(color_key)
        images[image_id] = image
        if mapper != None:
            images[image_id] = switch_color(mapper, images[image_id])

def draw_center(image,surf,x,y,scroll=[0,0], flag=None):
    if flag:
        surf.blit(image,(x-scroll[0] - image.get_width()/2,y-scroll[1] - image.get_height()/2), special_flags=flag)
    else:
        surf.blit(image,(x-scroll[0] - image.get_width()/2,y-scroll[1] - image.get_height()/2))

def get_entity_locs(names):
    global entity_locs
    global map_data
    removed = []
    for layer in map_data:
        for image_name in map_data[layer]:
            if image_name in names:
                if len(map_data[layer][image_name]) == 1:
                    entity_locs[image_name] = list(map_data[layer][image_name])[0]
                else:
                    entity_locs[image_name] = list(map_data[layer][image_name])
                removed.append((image_name, layer))
    for name, layer in removed:
        del map_data[layer][name]
    return entity_locs

def switch_color(mapper, surf, colorkey=(0, 0, 0)):
    new_surf = pygame.Surface((surf.get_width(), surf.get_height()))
    new_surf.fill(colorkey)
    new_surf.set_colorkey(colorkey)
    for x in range(surf.get_width()):
        for y in range(surf.get_height()):
            color = surf.get_at((x, y))
            if color[:3] in mapper.keys():
                new_surf.set_at((x, y), mapper[tuple(color[:3])])
    return new_surf

def cap(value, minimum, maximum):
    if value < minimum:
        value = minimum
    if value > maximum:
        value = maximum

    return value

def point_collision(point, walls, dimensions):
    x = int(point[0]/dimensions[0])
    y = int(point[1]/dimensions[1])

    try:
        data = walls[str(x) + ':' + str(y)]
    except KeyError:
        return False
    return True

def onscreen(pos, scroll, surf):
    global tile_size
    if pos[0] > scroll[0] - tile_size and pos[0] < scroll[0] + surf.get_width() and pos[1] > scroll[1] - tile_size and pos[1] < scroll[1] + surf.get_height():
        return True
    return False
    
def tear_image(image, tear_size, pos):
    piece_data = []
    colorkey = (255, 255, 255)
    for x in range(int(image.get_width()/tear_size[0])):
        for y in range(int(image.get_height()/tear_size[1])):
            piece = pygame.Surface(tear_size)
            piece.set_colorkey(colorkey)
            for x1 in range(piece.get_width()):
                for y1 in range(piece.get_height()):
                    color = image.get_at((x * tear_size[0] + x1, y * tear_size[1] + y1))
                    piece.set_at((x1, y1), color[:3])
            piece_data.append([piece, (int(pos[0]) + x * tear_size[0], int(pos[1]) + y * tear_size[1])])
    return piece_data

def close_tiles(pos, tiles_dict, surf, scroll):
    global tile_size
    offsets = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neighbors = []
    x = int(pos[0]/tile_size)
    y = int(pos[1]/tile_size)

    for offset in offsets:
        tile_x = x + offset[0]
        tile_y = y + offset[1]
        neighbors.append([tile_x, tile_y])
    nearby_rects = []
    for neighbor in neighbors:
        try:
            tile_pos = tiles_dict[str(neighbor[0]) + ':' + str(neighbor[1])][0]
            rect = pygame.Rect(tile_pos[0] * tile_size, tile_pos[1] * tile_size, tile_size, tile_size)
            nearby_rects.append(rect)
        except KeyError:
            pass

    return nearby_rects

def get_new_orientation(current_orientation, x, y, velocity):

    if velocity:
        return math.atan2(y, x)
    else:
        return current_orientation

def map_to_range(pi, value):
    while value < pi:
        value += math.pi * 2
    while value > pi:
        value -= math.pi * 2

    return value

class Timer:
    def __init__(self, duration):
        self.duration = duration
        self.current = 0
        self.done = False
        self.triggered = False

    def count_down(self, dt):
        if self.current < self.duration:
            self.current += dt
            return False
        self.done = True
        return True

    def reset(self, duration=None):
        self.current = 0
        if duration != None:
            self.duration = duration
        self.done = False
        self.triggered = False

  

def angle_to(point1, point2):
    return math.atan2(point2[1]-point1[1],point2[0]-point1[0])

def normalize(vector):
    h = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
    try:
        return vector[0] / h, vector[1] / h
    except ZeroDivisionError:
        return [0, 0]

def distance(vector):
    return math.sqrt(vector[0] ** 2 + vector[1] ** 2)

def random_binomial():
    return random.random() - random.random()

def vector(a, b):
    return b[0] - a[0], b[1] - a[1]

def scalar_multiply(vector, scalar):
    return vector[0] * scalar, vector[1] * scalar

def point_in_circle(point, center, radius):
    return distance(vector(center, point)) < radius

def dot_product(vector1, vector2):
    return vector1[0] * vector2[0] + vector1[1] * vector2[1]

def angle_between(vector1, vector2):
    mag1 = distance(vector1)
    mag2 = distance(vector2)
    return math.acos(dot_product(vector1, vector2) / mag1 * mg2)





