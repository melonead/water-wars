import pygame, sys, json
from pygame.locals import *
from text import Font
from copy import deepcopy

pygame.init()
clock = pygame.time.Clock()
SCREEN_SIZE = (1000, 700)
scale = 2
screen = pygame.display.set_mode(SCREEN_SIZE,0,32)
display = pygame.Surface((SCREEN_SIZE[0]//scale,SCREEN_SIZE[1]//scale))
image_browser = pygame.Surface((SCREEN_SIZE[0],SCREEN_SIZE[1]))
map_info_size = (SCREEN_SIZE[0]//2,50)
map_info = pygame.Surface(map_info_size)
export_surf = pygame.Surface((100,8))

color_key = (0,0,0)
images = {}
def export(path):
    global export_map
    file = open(path,'w')
    file.seek(0)
    file.write(json.dumps(export_map))
    file.close()

def load_map(path):
    global map_data
    file = open(path,'r')
    data = file.read()
    file.close()
    loaded_map = json.loads(data)
    map_data = deepcopy(loaded_map)
    for layer in map_data:
        for image_type in map_data[layer]:
            map_data[layer][image_type] = [tuple(pos) for pos in map_data[layer][image_type]]
            map_data[layer][image_type] = set(map_data[layer][image_type])
            
def load_image(path,color_key=(0,0,0)):
    image = pygame.image.load(path).convert()
    image.set_colorkey(color_key)
    return image.copy()

def load_group(path,name,no_of_images):
    global images
    global color_key
    for i in range(no_of_images):
        image_id = name + '_' + str(i)
        image = pygame.image.load(path + '/' + image_id + '.png').convert()
        image.set_colorkey(color_key)
        images[image_id] = image

def draw_center(image,surf,x,y,scroll=[0,0]):
    surf.blit(image,(x-scroll[0] - image.get_width()/2,y-scroll[1] - image.get_height()/2))

def auto_fill(map_data, mouse_pos):
    # auto fill
    # fill in an enclosed area of tiles
    # find the boundaries of the enclosed area
        # top left = min(mouse_pos[0] - tile_pos[0]) no tile to the left, min(mouse_pos[1] - tile_pos[1]) no tile above
        # bottom right = max(mouse_pos
    # for all the tiles in the enclosed are if no tile to its left add it to the map data
    # if there is a tile:
        # check the location of the tile
            # if it is located within the enclosed area continue adding tile
            # otherwise it is located on the boundaries, in which case go to the next row
    pass

images['island_1'] = load_image('images/boat/island_1.png', (0, 0, 0))
images['health_pickup'] = load_image('images/boat/health_pickup.png', (0, 0, 0))
images['font'] = load_image('images/font/font.png')
images['island_0'] = load_image('images/boat/island_0.png')
images['island_2'] = load_image('images/boat/island_2.png', (0, 0, 0))
images['enemy_placer'] = load_image('images/boat/enemy_placer.png')
images['player_placer'] = load_image('images/boat/player_placer.png')


# Font
ft = Font(images['font'])

right = False
left = False
up = False
down = False
click = False
erase = False
browsing_images = False
scroll = [0,0]
image_browser_scroll = 0
tile_size = 20
image_keys = {}
grid_sizes = {'tile': tile_size, 'precise': 1}
modes = ['tile','precise']
mode_switcher = 0
current_layer = 0
current_image = None
current_image_name = None
layers = 0
map_data = {}
export_map = {}
level = 5
map_data_file = f'levels/level_{level}.txt'

while True:
    display.fill((0,0,0))
    map_info.fill((40,40,40))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_a:
                left = True
            if event.key == K_d:
                right = True
            if event.key == K_w:
                up = True
            if event.key == K_s:
                down = True
            if event.key == K_UP:
                mode_switcher = (mode_switcher + 1) % len(modes)
            if event.key == K_l:
                current_layer = (current_layer + 1) % layers
            if event.key == K_n:
                layers += 1
                map_data[str(layers-1)] = {}
            if event.key == K_i:
                if browsing_images == False:
                    browsing_images = True
                else:
                    browsing_images = False
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                click = True
            if event.button == 3:
                erase = True
            if event.button == 4:
                pass
            if event.button == 5:
                pass
        if event.type == MOUSEBUTTONUP:
            if event.button == 1:
                click = False
            if event.button == 3:
                erase = False
        if event.type == KEYUP:
            if event.key == K_a:
                left = False
            if event.key == K_d:
                right = False
            if event.key == K_w:
                up = False
            if event.key == K_s:
                down = False
    if right and (not browsing_images):
        scroll[0] += 6
    if left and (not browsing_images):
        scroll[0] -= 6
    if up and (not browsing_images):
        scroll[1] -= 6
    if down and (not browsing_images):
        scroll[1] += 6

    used_scroll = [0,0]
    used_scroll[0] = int(scroll[0] / tile_size) * tile_size
    used_scroll[1] = int(scroll[1] / tile_size) * tile_size
      
    mx,my = pygame.mouse.get_pos()
    mx = int(mx/scale)
    my = int(my/scale)
    mode = modes[mode_switcher]
    mx = int(mx/grid_sizes[mode])
    my = int(my/grid_sizes[mode])
    mouse_rect = pygame.Rect(mx * grid_sizes[mode], my * grid_sizes[mode], 5, 5)
    pygame.draw.rect(display, (255,0,0),mouse_rect)
    
    # GUI image browsing
    if browsing_images:
        y = 10
        x = 0
        largest_width = 0
        largest_height = 0
        for image,name in zip(images.values(),images.keys()):
            image_browser.blit(image,(x,y))
            image_rect = pygame.Rect(x,y,image.get_width(),image.get_height())
            pygame.draw.rect(image_browser,(255,0,0),image_rect,1)
            mouse_x,mouse_y = pygame.mouse.get_pos()
            mouse_y -= image_browser_scroll
            mouse_rect = pygame.Rect(mouse_x,mouse_y, 5, 5)
            if click and mouse_rect.colliderect(image_rect):
                current_image = image.copy()
                current_image_name = name
                click = False
                browsing_images = False
            y += image.get_height() + 10


        if up:
            image_browser_scroll -= 50
            up = False
        if down:
            image_browser_scroll += 50
            down = False


        screen.blit(image_browser,(0,image_browser_scroll))
    
    # EDITING map
    if click and map_data and (not browsing_images):

        tx = mx + int((used_scroll[0]/tile_size))
        ty = my + int((used_scroll[1]/tile_size))
        if current_image_name not in list(map_data[str(current_layer)]):
            map_data[str(current_layer)][current_image_name] = set()
        if current_image != None:
            if modes[mode_switcher] == 'tile':
                map_data[str(current_layer)][current_image_name].add((tx,ty))
            else:
                if current_image_name[:4] != 'tile':
                    map_data[str(current_layer)][current_image_name].add((mx + used_scroll[0], my + used_scroll[1]))
                    image_keys[(mx + used_scroll[0], my + used_scroll[1])] = pygame.Rect(mx + used_scroll[0], my + used_scroll[1], *current_image.get_size())

        if map_data[str(current_layer)]:
            for image_name in list(map_data[str(current_layer)]):
                if image_name != current_image_name:
                    if (tx,ty) in map_data[str(current_layer)][image_name]:
                        map_data[str(current_layer)][image_name].remove((tx,ty))
             
    if erase and (not browsing_images):
        tx = mx + int((used_scroll[0]/tile_size))
        ty = my + int((used_scroll[1]/tile_size))
        a,b = pygame.mouse.get_pos()
        if map_data[str(current_layer)]:
            to_remove = []
            for image_name in list(map_data[str(current_layer)]):
                if modes[mode_switcher] == 'tile':
                    if (tx,ty) in map_data[str(current_layer)][image_name]:
                        map_data[str(current_layer)][image_name].remove((tx,ty))
                else:
                    for key, rect in zip(image_keys.keys(), image_keys.values()):
                        if pygame.Rect(a//scale,b//scale,5,5).colliderect(rect):
                            try:
                                map_data[str(current_layer)][image_name].remove(key)
                                to_remove.append(key)
                            except KeyError:
                                pass
                    for k in to_remove:
                        try:
                            del image_keys[k]
                        except KeyError:
                            pass
                            
    # RENDERING map
    if map_data:
        for i in range(layers):
            for image_name in map_data[str(i)]:
                if image_name != None:
                    if image_name[:4] == 'tile':
                        for pos in map_data[str(i)][image_name]:
                            display.blit(images[image_name].copy(), (pos[0] * tile_size - used_scroll[0], pos[1] * tile_size - used_scroll[1]))
                    else:
                        for pos in map_data[str(i)][image_name]:
                            display.blit(images[image_name].copy(),(pos[0] - used_scroll[0], pos[1] - used_scroll[1]))
    # GUI map info
    ft.write('current layer: ' + str(current_layer), map_info, 5, 5)
    ft.write('total layers: ' + str(layers), map_info, 5, 20)
    ft.write('export or import', export_surf, 0, 0)
    ft.write('mode: ' + str(modes[mode_switcher]), map_info, 5, 35)
    map_info.blit(export_surf, (120, 5))
    a,b = pygame.mouse.get_pos()
    # EXPORTING map data or LOADING map from a file if map data is empty
    if pygame.Rect(a//scale,b//scale,5,5).colliderect(pygame.Rect(120,5,*export_surf.get_size())):
        if click:
            if map_data:
                export_map = deepcopy(map_data)
                for layer in export_map:
                    for image in export_map[layer]:
                        export_map[layer][image] = list(export_map[layer][image])
                export(map_data_file)
            if not map_data:
                load_map(map_data_file)
                layers = len(map_data)
            click = False
                        
    if current_image != None:
        if modes[mode_switcher] == 'tile':
            display.blit(current_image,(mx * tile_size, my * tile_size))
        else:
            display.blit(current_image,(mx, my))

    if not browsing_images:
        screen.blit(pygame.transform.scale(display,SCREEN_SIZE),(0,0))
    m_surf = pygame.transform.scale(map_info, (map_info_size[0] * 2, map_info_size[1] * 2))
    m_surf.set_alpha(100)
    screen.blit(m_surf, (0,0))
    pygame.display.update()
    clock.tick(50)
