import pygame, sys
import time
import random
from pygame.locals import *
from game_entity import GameObject
from particle import Particle
from functions import *
from text import Font

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
clock = pygame.time.Clock()
SCREEN_SIZE = (1000, 700)
scale = 2
screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
display = pygame.Surface((int(SCREEN_SIZE[0]/scale), int(SCREEN_SIZE[1]/scale)))
display_overlay = pygame.Surface((display.get_width(), display.get_height()))
display_overlay_alpha = 255
positive_rotate = False
negative_rotate = False
accelerate = False
decelerate = False
initial_frame = time.time()
cld = open('current_level.txt', 'r')
level = int(cld.read())
cld.close()
game_fps = 60

map_data = load_map(f'levels/level_{level}.txt', {})

class Boat(GameObject):

    def __init__(self, x, y, width, height, angle=0):
        GameObject.__init__(self, x, y, width, height)
        self.angle = angle
        self.image = pygame.image.load('images/boat/player_boat.png')
        self.image.set_colorkey((0, 0, 0))
        self.boat_mask = pygame.mask.from_surface(self.image)
        self.rotation = 0
        self.decelerate_to_stop = False
        self.hit = False
        self.health = 7


class EnemyBoat(Boat):
    def __init__(self, x, y, width, height, angle=0):
        Boat.__init__(self, x, y, width, height, angle=0)
        self.steering_image = pygame.Surface((2,2))
        self.image = pygame.image.load('images/boat/boat.png')
        self.steering_image.fill((0, 244, 0))
        self.steering_mask = pygame.mask.from_surface(self.steering_image)

entity_locs = {}
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
entity_locs = get_entity_locs(['player_placer', 'enemy_placer'])

images = {}
color_key = (0, 0, 0)
load_group('images/particle', 'particle', 8, images=images, mapper={(58, 96, 74): (105, 159, 173), (79, 119, 84): (105, 159, 173)})
load_group('images/vfx/explosion', 'explosion', 9, images=images)
images['misile'] = load_image('images/boat/misile.png', (0, 0, 0))
images['enemy_bullet'] = load_image('images/boat/enemy_bullet.png', (0, 0, 0))
images['direction'] = load_image('images/boat/direction.png', (0, 0, 0))
images['island_0'] = load_image('images/boat/island_0.png', (0, 0, 0))
images['island_1'] = load_image('images/boat/island_1.png', (0, 0, 0))
images['island_2'] = load_image('images/boat/island_2.png', (0, 0, 0))
images['health_pickup'] = load_image('images/boat/health_pickup.png', (0, 0, 0))
images['font'] = load_image('images/font/font.png')
images['pause'] = load_image('images/boat/pause.png')

enemies = []
boat_pos = entity_locs['player_placer']
boat = Boat(*boat_pos, 28, 11, 0)
scroll = [0, 0]
boat_velocity = [0, 0]
acceleration = 0
particles = []
islands = []
explosions = []
waves = []
fish_circles = []
backward_deceleration = False
forward_deceleration = False
enemy_attack_timer = Timer(0.1)
boat_attack_timer = Timer(0)
transition_timer = Timer(0.3)
boat_attack = False
enemy_positions = {}
camera_origin = [boat.x, boat.y]
island_masks = {}
health_masks = {}
start = False
wall_hit = False
dead = False
won = False

# font
font = Font(images['font'])

for pos in entity_locs['enemy_placer']:
    enemy = EnemyBoat(*pos, 20, 10, 0)
    enemy.seen = False
    enemy.velocity = [0, 0]
    enemy.enemy_mask = pygame.mask.from_surface(enemy.image)
    enemies.append(enemy)


# map
tile_size = 20
walls = {}

for layer in map_data:
    for name in map_data[layer]:
        if name in ['island_0', 'island_1', 'island_2']:
            for pos in map_data[layer][name]:
                image = images[name].copy()
                island_masks[tuple(pos)] = pygame.mask.from_surface(image)
        if name == 'health_pickup':
            for pos in map_data[layer][name]:
                image = images[name]
                health_masks[tuple(pos)] = pygame.mask.from_surface(image)
in_menu = True
first_menu = True
to_game = False
to_subsequent = False
to_help = False
first_time = True
pause = False
cont = False
click = False
quit_game = False
def menu():
    pygame.mixer.music.pause()
    global in_menu
    global first_menu
    global to_game
    global to_subsequent
    global to_help
    global first_time
    global pause
    global cont
    global click
    global start
    global quit_game
    global game_fps
    global level
    while in_menu:
        display.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    click = False
        mx, my = pygame.mouse.get_pos()
        mx = mx/scale
        my = my/scale
        mouse_rect = pygame.Rect(mx, my, 5, 5)
        start_dent = 0
        help_dent = 0
        quit_dent = 0
        cont_dent = 0
        if first_menu:
            buttons = [pygame.Rect(40, 40, 50, 10), pygame.Rect(40, 60, 50, 10), pygame.Rect(40, 80, 50, 10)]
            for i, button in enumerate(buttons):
                if mouse_rect.colliderect(button):
                    if i == 0:
                        start_dent = 10
                    if i == 1:
                        help_dent = 10
                    if i == 2:
                        quit_dent = 10
                    if click == True:
                        if i == 0:
                            to_game = True
                        if i == 1:
                            to_help = True
                        if i == 2:
                            pygame.quit()
                            sys.exit()
            font.write('start', display, 40 + start_dent, 40)
            font.write('help', display, 40 + help_dent, 60)
            font.write('quit', display, 40 + quit_dent, 80)
            
        if pause or level > 1:
            to_subsequent = True
        if to_subsequent and not to_help:
            first_menu = False
            buttons = [pygame.Rect(40, 40, 50, 10), pygame.Rect(40, 60, 50, 10), pygame.Rect(40, 80, 50, 10), pygame.Rect(40, 100, 50, 10)]
            for i, button in enumerate(buttons):
                if mouse_rect.colliderect(button):
                    if i == 0:
                        cont_dent = 10
                    if i == 1:
                        start_dent = 10
                    if i == 2:
                        help_dent = 10
                    if i == 3:
                        quit_dent = 10
                    if click == True:
                        if i == 0:
                            to_game = True
                            game_fps = 60
                        if i == 1:
                            start = True
                            to_game = True
                        if i == 2:
                            to_help = True
                        if i == 3:
                            pygame.quit()
                            sys.exit()
            font.write('continue', display, 40 + cont_dent, 40)
            font.write('start', display, 40 + start_dent, 60)
            font.write('help', display, 40 + help_dent, 80)
            font.write('quit', display, 40 + quit_dent, 100)
            
        if to_game:
            in_menu = False
            first_menu = False
        if to_help:
            font.write('x:    Rotate anticlockwise', display, 40, 40)
            font.write('c:    Rotate clockwise', display, 40, 54)
            font.write('j:    Accelerate forward', display, 40, 68)
            font.write('k:    Decelerate to stop', display, 40, 82)
            font.write('l:    Shoot', display, 40, 96)
            font.write('Avoid collisions with: the enemy boats, islands', display, 40, 110)
            font.write('Menu', display, 40,130)
            first_menu = False
            buttons = [pygame.Rect(40, 130, 50, 10)]
            for i, button in enumerate(buttons):
                if mouse_rect.colliderect(button):
                    if click == True:
                        if i == 0:
                            first_menu = True
                            to_help = False
                
        screen.blit(pygame.transform.scale(display, SCREEN_SIZE), (0, 0))
        pygame.display.update()
        clock.tick(60)

# sounds
sounds = {}
sounds['health_pickup'] = pygame.mixer.Sound('sounds/health_pickup.wav')
sounds['explosion'] = pygame.mixer.Sound('sounds/explosion.wav')
sounds['engine_buzz'] = pygame.mixer.Sound('sounds/engine_buzz.wav')
for i in range(4):
    sounds[f'enemy_attack_{i}'] = pygame.mixer.Sound(f'sounds/enemy_attack_{i}.wav')
    sounds[f'enemy_attack_{i}'].set_volume(0.6)
sounds['engine_buzz'].set_volume(0.1)
engine_buzz_timer = Timer(3.5)
explosion_sound_timer = Timer(0.3)
pygame.mixer.music.load('sounds/music/music_0.wav')
pygame.mixer.music.play(-1)
# -----------------------------------------------------
menu()          
smallest, largest = map_extreme_points(map_data)
display.set_alpha(170)

while not quit_game:

    scroll[0] += (camera_origin[0] + math.cos(math.radians(boat.rotation)) * 90 - scroll[0] - display.get_width()/2)/15
    scroll[1] += (camera_origin[1] + math.sin(math.radians(boat.rotation)) * 90 - scroll[1] - display.get_height()/2)/15
    dt = time.time() - initial_frame
    initial_frame = time.time()
    display.fill((58, 112, 142))
    
    scroll[0] = cap(scroll[0], smallest[0] - 100, largest[0] - display.get_width() + 300)
    scroll[1] = cap(scroll[1], smallest[1] - 100, largest[1] - display.get_height() + 300)
    mx, my = pygame.mouse.get_pos()
    mx = mx/scale
    my = my/scale
    mouse_rect = pygame.Rect(mx, my, 5, 5)
    
    for wave in fish_circles:
        pygame.draw.circle(display, (237, 230, 203), (wave[2][0] - scroll[0], wave[2][1] - scroll[1]), wave[0], int(wave[1]))
        wave[1] -= 0.5
        wave[0] += 1
        if int(wave[1]) <= 0:
            fish_circles.remove(wave)
    
    # map render
    for layer in map_data:
        for name in map_data[layer]:
            for pos in map_data[layer][name]:
                if name in ['island_0', 'island_1', 'island_2']:
                    display.blit(images[name], (pos[0] - scroll[0], pos[1] - scroll[1]))
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                click = True
        if event.type == MOUSEBUTTONUP:
            if event.button == 1:
                click = False
                
        if event.type == KEYDOWN:
            if event.key == K_c:
                positive_rotate = True
            if event.key == K_x:
                negative_rotate = True
            if event.key == K_j:
                accelerate = True
            if event.key == K_k:
                decelerate = True
            if event.key == K_l:
                boat_attack = True
                            
        if event.type == KEYUP:
            if event.key == K_c:
                positive_rotate = False
            if event.key == K_x:
                negative_rotate = False
            if event.key == K_j:
                accelerate = False
            if event.key == K_k:
                decelerate = False
            if event.key == K_l:
                boat_attack = False
    bt_im = pygame.transform.rotate(boat.image, -boat.rotation)
    boat.boat_mask = pygame.mask.from_surface(bt_im)
    collisions_data = boat.update(boat_velocity, [], offset=[bt_im.get_width()/2, bt_im.get_height()/2], rect_size=(bt_im.get_width(), bt_im.get_height()))
    #boat.draw(display, *scroll) 
    t = dt * 60
    if positive_rotate:
        if not boat.decelerate_to_stop:
            boat.rotation += 3
    if negative_rotate:
        if not boat.decelerate_to_stop:
            boat.rotation -= 3
    if accelerate:
        if not boat.decelerate_to_stop:
            acceleration += 0.05
    if decelerate:
        if not boat.decelerate_to_stop:
            if acceleration > 0:
                acceleration -= 0.05
            else:
                accleration = 0
            
    if acceleration != 0:
        sounds['engine_buzz'].set_volume(acceleration/10)
        if engine_buzz_timer.current == 0:
            sounds['engine_buzz'].play()
        engine_buzz_timer.count_down(dt)
        if engine_buzz_timer.done:
            engine_buzz_timer.reset()
        
        for i in range(5):
            angle = math.radians(boat.rotation + 180) + math.radians(random.randrange(-10, 10))
            pos = boat.x + -math.cos(math.radians(boat.rotation)) * 12, boat.y + -math.sin(math.radians(boat.rotation)) * 12
            if onscreen(pos, scroll, display):
                part = Particle(list(pos), 2, (0, 255, 0), [math.cos(angle) *  acceleration / random.randint(1, 5) , math.sin(angle) * acceleration / random.randint(1, 5)], 'water bubbles', 10)
                part.index = random.randint(0, 5)
                particles.append(part)
    else:
        sounds['engine_buzz'].stop()
        engine_buzz_timer.reset()

    
    if boat_attack:
        speed = 10
        angle = math.radians(boat.rotation + 180)
        if boat_attack_timer.done:
            part = Particle([boat.x, boat.y], 5, (0, 0, 255), [math.cos(angle) * speed, math.sin(angle) * speed], 'boat bullet', 10)
            part.angle = angle
            part.hit = False
            particles.append(part)
            boat_attack_timer.reset(0.5)
    boat_attack_timer.count_down(dt)
    pygame.draw.circle(display, (255, 0, 0), [boat.get_center()[0] - scroll[0], boat.get_center()[1] - scroll[1]], 70, 1)
    
    enemy_positions = {}

    camera_origin = [boat.x, boat.y]
    closest_boat_distance = 9999999
    closest_boat_location = [9999, 9999]
    for enemy in enemies:
        enemy_surf = pygame.transform.rotate(enemy.image, -math.degrees(enemy.rotation))
        enemy.steering_mask = pygame.mask.from_surface(enemy.steering_image)
        enemy.boat_mask = pygame.mask.from_surface(enemy_surf)
        #draw_center(enemy.boat_mask.to_surface(), display, enemy.x, enemy.y, scroll)
        d = distance(vector([enemy.x, enemy.y], [boat.x, boat.y]))
        if d < closest_boat_distance:
            closest_boat_distance = d
            closest_boat_location = [enemy.x, enemy.y]
        if enemy.hit:
            enemies.remove(enemy)
        if onscreen([enemy.x, enemy.y], scroll, display):
            enemy.seen = True
        if enemy.seen:
            angle = math.radians(random.randrange(0, 360, 20))
            angle = angle_to([enemy.x, enemy.y], [boat.x, boat.y])
            enemy.rotation = angle
            if distance(vector([enemy.x, enemy.y], [boat.x, boat.y])) > 150:
                enemy.velocity = [math.cos(angle) * 4, math.sin(angle) * 4]
            else:
                enemy.velocity = [0, 0]
            for neighbor in enemies:
                if neighbor is not enemy:
                    if distance(vector([enemy.x, enemy.y], [neighbor.x, neighbor.y])) < 50:
                        direction = [0, 0]
                        direction[0] = enemy.x - neighbor.x
                        direction[1] = enemy.y - neighbor.y
                        direction = normalize(direction)
                        enemy.velocity = [direction[0] * 4, direction[1] * 4]

        for i in range(0, 360, 90):
            steering_ray = [math.cos(enemy.rotation + math.radians(i)) * 30, math.sin(enemy.rotation + math.radians(i)) * 30]
            #pygame.draw.line(display, (255, 0, 0), (enemy.x - scroll[0], enemy.y - scroll[1]), (enemy.x + steering_ray[0] - scroll[0], enemy.y + steering_ray[1] - scroll[1]))
            a = enemy.x + steering_ray[0]
            b = enemy.y + steering_ray[1]
            #pygame.draw.line(display, (0, 255, 0), (a - scroll[0], b - scroll[1]), (a + math.cos(math.radians(i + 90) + enemy.rotation) * 100 - scroll[0], b + math.sin(math.radians(i + 90) + enemy.rotation) * 100 - scroll[1]))
            target = [a + math.cos(math.radians(i + 90) + enemy.rotation) * 100, b + math.sin(math.radians(i + 90) + enemy.rotation) * 100]
            for mask_key in island_masks.keys():
                offset = [mask_key[0] - (enemy.x + steering_ray[0]), mask_key[1] - (enemy.y + steering_ray[1])]
                overlap_area = enemy.steering_mask.overlap_area(island_masks[mask_key], offset)
                if overlap_area:
                    direction = [0, 0]
                    direction[0] = enemy.x - target[0]
                    direction[1] = enemy.y - target[1]
                    direction = normalize(direction)
                    enemy.velocity = [direction[0] * 4, direction[1] * 4]
        
        if enemy.velocity[0] != 0 or enemy.velocity[1] != 0:
            for i in range(5):
                angle = enemy.rotation + math.radians(180) + math.radians(random.randrange(-10, 10))
                pos = enemy.x + -math.cos(enemy.rotation) * 12, enemy.y + -math.sin(enemy.rotation) * 12
                part = Particle(list(pos), 2, (0, 255, 0), [math.cos(angle) *  random.randint(1, 5) , math.sin(angle) * random.randint(1, 5)], 'water bubbles', 10)
                part.index = random.randint(0, 5)
                particles.append(part)
    
        mask_overlap = boat.boat_mask.overlap_mask(enemy.boat_mask, (boat.x - enemy.x, boat.y - enemy.y))
        collision_center = mask_overlap.centroid()
        
        if sum(collision_center) != 0:
            explosions.append([0, [enemy.x, enemy.y]])
            enemies.remove(enemy)
            boat.health = 0
        enemy.update(enemy.velocity, [])
        enemy_surf.set_colorkey((0, 0, 0))
        draw_center(enemy_surf, display, enemy.x, enemy.y, scroll)


    if enemy_attack_timer.done:
        if enemies:
            if any([onscreen([enemy.x, enemy.y], scroll, display) for enemy in enemies]):
                data = [[onscreen([enemy.x, enemy.y], scroll, display), [enemy.x, enemy.y]] for enemy in enemies]
                sounds[f'enemy_attack_{random.randint(0, 3)}'].play()
                for datum in data:
                    if datum[0]:
                        for i in range(0, 360, 30):
                            angular_variation = math.radians(random.randrange(-10, 10))
                            speed = 6
                            angle = math.radians(i)
                            particles.append(Particle(datum[1].copy(), 5, (255, 0, 0), [math.cos(angle) * speed, math.sin(angle) * speed], 'enemy bullet', 10))
        enemy_attack_timer.reset(1)
    enemy_attack_timer.count_down(dt) 

    for particle in particles:
        if particle.type == 'boat bullet':
            particle.update({})
            particle.draw_rect(display, scroll)
            misile_surf = pygame.transform.rotate(images['misile'], -math.degrees(particle.angle))
            draw_center(misile_surf, display, *particle.pos, scroll)
            particle_mask = pygame.mask.from_surface(misile_surf)
            pygame.draw.circle(display, (255, 255, 0), (particle.pos[0] - scroll[0], particle.pos[1] - scroll[1]),2)
            for i in range(10):
                angle = particle.angle + math.radians(random.randrange(-10, 10))
                part = Particle([particle.pos.copy()[0] + -math.cos(particle.angle) * 20, particle.pos.copy()[1] + -math.sin(particle.angle) * 20], 7, (0, 255, 0), [math.cos(angle), math.sin(angle)], 'bullet spark', 10, speed = random.randint(1, 5))
                part.index = random.randint(0, 3)
                particles.append(part)
            if distance(vector(particle.pos, [boat.x, boat.y])) < 700 and not particle.hit:
                camera_origin = list(particle.pos)
            for enemy in enemies:
                if particle_mask.overlap(enemy.boat_mask, (enemy.x - particle.pos[0], enemy.y - particle.pos[1])):
                    enemies.remove(enemy)
                    particle.hit = True
                    surf = pygame.transform.rotate(enemy.image, -math.degrees(enemy.rotation))
                    sounds['explosion'].play()
                    enemy_boat_pieces = tear_image(surf, [random.randint(6,7), random.randint(6,7)], [enemy.x, enemy.y])
                    for piece in enemy_boat_pieces:
                        angle = math.radians(random.randint(0, 360))
                        part = Particle(list(piece[1]), piece[0].get_width(), (0, 0, 0), [math.cos(angle) * random.randint(1, 3), math.sin(angle) * random.randint(1, 3)], 'boat piece', 10)
                        part.image = piece[0]
                        part.image.set_colorkey((0, 0, 0))
                        particles.append(part)
                    for i in range(20):
                        angle = math.radians(random.randrange(0, 360))
                        index = random.randint(0, 3)
                        speed = 6 - index/2
                        part = Particle([enemy.x, enemy.y], 3, (255, 0, 0), [math.cos(angle) * speed, math.sin(angle) * speed], 'explosion particle', 10)
                        part.index = index
                        particles.append(part)
                    waves.append([40, 20, [enemy.x, enemy.y]])
                    explosions.append([0, [enemy.x, enemy.y]])
            for mask_key in island_masks.keys():
                if particle_mask.overlap(island_masks[mask_key], (mask_key[0] - (particle.pos[0] - misile_surf.get_width()/2), mask_key[1] - (particle.pos[1] - misile_surf.get_height()/2))):
                    particle.hit = True
                                            
            if particle.hit == True or not onscreen(particle.pos, scroll, display):
                particles.remove(particle)
        if particle.type == 'explosion particle':
            particle.update({})
            image = images[f'particle_{int(particle.index)}']
            image = switch_color({(105, 159, 173): (21, 16, 21)}, image, colorkey=(0, 0, 0))
            draw_center(image, display, *particle.pos, scroll)
            particle.index += 0.5
            if particle.index >= 7:
                particles.remove(particle)
        if particle.type == 'bullet spark':
            particle.update({})
            image = images[f'particle_{int(particle.index)}']
            image = switch_color({(105, 159, 173): (232, 178, 111)}, image, colorkey=(0, 0, 0))
            draw_center(image, display, *particle.pos, scroll)
            particle.index += 0.5
            if particle.index >= 7:
                particles.remove(particle)
   
                
        if particle.type == 'water bubbles':
            collisions = particle.update(walls)
            image = images[f'particle_{int(particle.index)}']
            draw_center(image, display, *particle.pos, scroll)
            if int(particle.index) != 8:
                particle.index += 0.2
            if int(particle.index) >= 8:
                particles.remove(particle)
            #pygame.draw.circle(display, (0, 255, 0), (particle.pos[0] - scroll[0], particle.pos[1] - scroll[1]), int(particle.life * 0.4))
        if particle.type == 'enemy bullet':
            particle.update({})
            draw_center(images['enemy_bullet'], display, *particle.pos, scroll)
            if point_in_circle(particle.pos, [boat.x, boat.y], 20):
                if boat.health > 0:
                    boat.health -= 0.5
                particles.remove(particle)
            particle.life -= 0.1
            if particle.life <= 0:
                try:
                    particles.remove(particle)
                except ValueError:
                    pass

        if particle.type == 'boat piece':
            particle.update({})
            draw_center(particle.image, display, *particle.pos, scroll)
            particle.life -= 0.2 
            if particle.life <= 0:
                particles.remove(particle)

    for explosion in explosions:
        draw_center(images[f'explosion_{int(explosion[0])}'], display, *explosion[1], scroll)
        explosion[0] += 0.3
        if explosion[0] >= 9:
            explosions.remove(explosion)
    for wave in waves:
        pygame.draw.circle(display, (237, 230, 203), (wave[2][0] - scroll[0], wave[2][1] - scroll[1]), wave[0], wave[1])
        wave[1] -= 1
        wave[0] += 2
        if wave[1] <= 0:
            waves.remove(wave)
    if random.randint(0, 20) == 0:
        fish_circles.append([1, 4, [random.randrange(int(scroll[0]), int(scroll[0] + display.get_width())), random.randrange(int(scroll[1]), int(scroll[1] + display.get_height()))]])
    if boat.health <= 0:
        dead = True
        transition_timer.count_down(dt)
    if dead:
        surf = pygame.transform.rotate(boat.image, -boat.rotation)
        boat_pieces = tear_image(surf, [random.randint(6,7), random.randint(6,7)], [boat.x, boat.y])
        for piece in boat_pieces:
            angle = math.radians(random.randint(0, 360))
            part = Particle(list(piece[1]), piece[0].get_width(), (0, 0, 0), [math.cos(angle) * random.randint(1, 5), math.sin(angle) * random.randint(1, 5)], 'boat piece', 10)
            part.image = piece[0]
            part.image.set_colorkey((0, 0, 0))
            particles.append(part)
        dead = False
                
    #print(boat.decelerate_to_stop)
    boat_velocity[0] = math.ceil(math.cos(math.radians(boat.rotation)) * acceleration)
    boat_velocity[1] = math.ceil(math.sin(math.radians(boat.rotation)) * acceleration)
    boat_surf = pygame.transform.rotate(boat.image, -boat.rotation)
    boat_surf.set_colorkey((0, 0, 0))
    draw_center(boat_surf, display, boat.x, boat.y, scroll)
    if acceleration > 0:
        direction = 1
    else:
        direction = -1
    motion_ray = [boat.x + math.cos(math.radians(boat.rotation)) * 10 * direction, boat.y + math.sin(math.radians(boat.rotation)) * 10 * direction]
    pygame.draw.circle(display, (255, 0, 0), (motion_ray[0] - scroll[0], motion_ray[1] - scroll[1]), 2)
    #if not onscreen([boat.x + math.cos(math.radians(boat.rotation)) * 50 * direction, boat.y + math.sin(math.radians(boat.rotation)) * 50 * direction], scroll, display):
     #   acceleration = 0    
    
    mx, my = pygame.mouse.get_pos()
    mx = mx/scale
    my = my/scale

    bt_im = pygame.transform.rotate(boat.image, -boat.rotation)
    #draw_center(boat.boat_mask.to_surface(), display, boat.x, boat.y, scroll)
    direction = angle_to(closest_boat_location, [boat.x + 20, boat.y])
    draw_center(pygame.transform.rotate(images['direction'], -math.degrees(direction)), display, boat.x + 20, boat.y, scroll)

    for mask_key in island_masks.keys():
        offset = [mask_key[0] - (boat.x - bt_im.get_width()/2), mask_key[1] - (boat.y - bt_im.get_height()/2)]
        #display.blit(island_masks[mask_key].to_surface(), (mask_key[0] - scroll[0], mask_key[1] - scroll[1]))
        overlap_area = boat.boat_mask.overlap_area(island_masks[mask_key], offset)
        if overlap_area:
            if explosion_sound_timer.current == 0:
                sounds['explosion'].play()
            explosion_sound_timer.count_down(dt)
            if explosion_sound_timer.done:
                explosion_sound_timer.reset()
            dead = True
            acceleration = 0

    to_remove = []
    for mask_key in health_masks.keys():
        offset = [mask_key[0] - (boat.x - bt_im.get_width()/2), mask_key[1] - (boat.y - bt_im.get_height()/2)]
        overlap_area = boat.boat_mask.overlap_area(health_masks[mask_key], offset)
        surf = health_masks[mask_key].to_surface()
        surf.set_colorkey((0, 0, 0))
        draw_center(surf, display, *mask_key, scroll)
        if overlap_area:
            if boat.health < 7:
                boat.health += 1
                to_remove.append(mask_key)
                sounds['health_pickup'].play()
                if boat.health > 7:
                    boat.health = 7
            break
    for mask_key in to_remove:
        del health_masks[mask_key]
    if int(boat.health) <= 0:
        dead = True
    if len(enemies) == 0 and not dead:
        won = True
    if dead or won or start:
        transition_timer.count_down(dt)
        pygame.mixer.music.stop()
        
    if (won == True or dead == True or start == True) and transition_timer.done:
        # reset the level
        transition_timer.reset()
        if won == True:
            level += 1
            if level > 5:
                break
            cld = open('current_level.txt', 'w')
            cld.seek(0)
            cld.write(str(level))
            cld.close()
        pygame.mixer.music.play(-1)
        positive_rotate = False
        negative_rotate = False
        start = False
        accelerate = False
        decelerate = False
        initial_frame = time.time()
        display_overlay_alpha = 255
        map_data = load_map(f'levels/level_{level}.txt', {})
        entity_locs = get_entity_locs(['player_placer', 'enemy_placer'])
        enemies = []
        boat_pos = entity_locs['player_placer']
        boat = Boat(*boat_pos, 28, 11, 0)
        scroll = [0, 0]
        boat_velocity = [0, 0]
        acceleration = 0
        particles = []
        islands = []
        backward_deceleration = False
        forward_deceleration = False
        enemy_attack_timer = Timer(0.1)
        boat_attack_timer = Timer(0)
        boat_attack = False
        enemy_positions = {}
        camera_origin = [boat.x, boat.y]
        island_masks = {}
        health_masks = {}
        wall_hit = False
        dead = False
        won = False
        for pos in entity_locs['enemy_placer']:
            enemy = EnemyBoat(*pos, 20, 10, 0)
            enemy.seen = False
            enemy.velocity = [0, 0]
            enemy.enemy_mask = pygame.mask.from_surface(enemy.image)
            enemies.append(enemy)

        tile_size = 20
        walls = {}

        for layer in map_data:
            for name in map_data[layer]:
                if name in ['island_0', 'island_1', 'island_2']:
                    for pos in map_data[layer][name]:
                        image = images[name].copy()
                        island_masks[tuple(pos)] = pygame.mask.from_surface(image)
                if name == 'health_pickup':
                    for pos in map_data[layer][name]:
                        image = images[name]
                        health_masks[tuple(pos)] = pygame.mask.from_surface(image)
        smallest, largest = map_extreme_points(map_data)
    # gui
    pause_rect = pygame.Rect(400, 5, images['pause'].get_width() * 2, images['pause'].get_height() * 2)
    display.blit(pygame.transform.scale(images['pause'], (images['pause'].get_width() * 2, images['pause'].get_height() * 2)), (400, 5))
    if mouse_rect.colliderect(pause_rect):
        if click == True:
            to_game = False
            in_menu = True
            pause = True
            to_subsequent = True
            game_fps = 1
            pygame.mixer.fadeout(2500)
            pygame.mixer.music.pause()
            menu()
    if game_fps != 60:
        game_fps = 60

    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play(-1)

    for i in range(int(boat.health)):
        x = 5 + i * (images['health_pickup'].get_width() + 2)
        display.blit(images['health_pickup'], (x, 5))
        x += 2
    font.write(f'level: {level}', display, 150, 5)
    #font.write(f'fps: {int(clock.get_fps())}', display, 250, 5)
    font.write(f'Enemy Boats: {len(enemies)}', display, 250, 5,  shadow=(1, 1, 1))
    display.blit(display_overlay, (0, 0))
    display_overlay.set_alpha(display_overlay_alpha)
    if display_overlay_alpha > 0:
        display_overlay_alpha -= 1
    screen.blit(pygame.transform.scale(display, SCREEN_SIZE), (0, 0))
    pygame.display.update()
    clock.tick(game_fps)

while True:

    display.fill((105, 159, 173))
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    font.write('You beat all the pirates and the waters are safer now.', display,  50, 120, color=(21, 16, 21), shadow=(232, 178, 111))
    screen.blit(pygame.transform.scale(display, SCREEN_SIZE), (0, 0))
    pygame.display.update()
    clock.tick(60)
