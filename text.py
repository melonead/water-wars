import pygame

class Font:

    def __init__(self,font):
        self.font = font
        self.height = 14
        self.char_size = {'a': 8, 'b': 6, 'c': 6, 'd': 8, 'e': 5, 'f': 6, 'g': 6, 'h': 7, 'i': 3, 'j': 5, 'k': 7, 'l': 3, 'm': 7, 'n': 7, 'o': 7, 'p': 6, 'q': 7, 'r': 5, 's': 7, 't': 5, 'u': 7, 'v': 7, 'w': 7, 'x': 7, 'y': 7, 'z': 7, 'A': 7, 'B': 7, 'C': 7, 'D': 8, 'E': 6, 'F': 6, 'G': 7, 'H': 8, 'I': 4, 'J': 7, 'K': 8, 'L': 6, 'M': 7, 'N': 7, 'O': 9, 'P': 7, 'Q': 10, 'R': 8, 'S': 7, 'T': 8, 'U': 8, 'V': 9, 'W': 9, 'X': 9, 'Y': 9, 'Z': 8, '1': 6, '2': 7, '3': 6, '4': 8, '5': 7, '6': 6, '7': 7, '8': 8, '9': 7, '0': 8, ':': 2, ';': 3, '.': 2, ',': 3, '?': 8, "'": 2, '[': 4, ']': 4, '+': 8, '-': 8, '=': 8}
        self.char_data = {}
        self.last_sentence = 0 # the y pos of the last sentence writen
        self.transparency = (0, 0, 0)
        
        x = 0
        for char in list(self.char_size.keys()):
            char_size = (self.char_size[char], self.height)
            char_surf = pygame.Surface(char_size)
            char_surf.set_colorkey(self.transparency)
            for yc in range(char_size[1]):
                for xc in range(char_size[0]):
                    c = self.font.get_at((x + xc, yc))
                    char_surf.set_at((xc, yc), c)
            self.char_data[char] = char_surf
            x += self.char_size[char] + 1

    def write(self,text,surf,x,y,line_length=float("inf"), color=None, shadow=None):
        start_x = x
        start_y = y
        for char in text:
            if char != ' ':
                char_surf = self.char_data[char]
                if color != None:
                    colored_char_surf = char_surf.copy()
                    for yc in range(self.height):
                        for xc in range(self.char_size[char]):
                            if char_surf.get_at((xc, yc)) != (0, 0, 0):
                                colored_char_surf.set_at((xc, yc), color)
                            
                    if shadow != None:
                        char_shadow = colored_char_surf.copy()
                        for yc in range(self.height):
                            for xc in range(self.char_size[char]):
                                if char_shadow.get_at((xc, yc)) == color:
                                    char_shadow.set_at((xc, yc), shadow)
                        surf.blit(char_shadow,(start_x + 1,start_y + 1))
                    surf.blit(colored_char_surf,(start_x,start_y))
                else:
                    if shadow != None:
                        char_shadow = char_surf.copy()
                        for yc in range(self.height):
                            for xc in range(self.char_size[char]):
                                if char_shadow.get_at((xc, yc)) == (255, 255, 255):
                                    char_shadow.set_at((xc, yc), shadow)
                        surf.blit(char_shadow,(start_x + 1,start_y + 1))
                    surf.blit(char_surf,(start_x,start_y))
                start_x += self.char_size[char] + 2
            else:
                start_x += 5
                if start_x >= line_length:
                    start_x = x
                    start_y += self.height + 3
