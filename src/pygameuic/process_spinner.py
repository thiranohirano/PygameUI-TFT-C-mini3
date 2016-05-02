'''
Created on 2016/03/02

@author: hirano
'''
import threading

import pygame
from .colors import white_color

from pygame.constants import RLEACCEL, SRCALPHA
from . import resource  # @UnresolvedImport
from . import object_rectangle

class ProcessSpinner(object_rectangle.ObjectRectangle):
    '''
    classdocs
    '''
    def __init__(self, screen):
        self.size = 100
        self.current_frame = 0
        self.frame_count = 32
        self.spinnering_flag = True
        self.screen = screen
        self.rect = self.screen.get_rect()
        self.w = self.rect.width
        self.h = self.rect.height

        self.keyW = int(self.w / 12 + 0.5) - 2
        self.font = pygame.font.SysFont('Courier New', int(self.keyW / 2), bold=True)

        object_rectangle.ObjectRectangle.__init__(self, self.rect)
        # make a copy of the screen
        self.screenCopy = screen.copy()
        # create a background surface
        self.background = pygame.Surface(self.rect.size)
        self.background.fill((0, 0, 0))  # fill with black
        self.background.set_alpha(191)  # 50% transparent
        # blit background to screen
        self.screen.blit(self.background, (0, 0))
        
        self.image = resource.get_image("spinner_all")

    def run(self, slot, title=''):
        self.title = title
        t = threading.Thread(target=self._spinnering)
        t.start()
        slot()
        self.spinnering_flag = False
        t.join()
        self._clear()
        
    def _spinnering(self):
        self._draw_title(self.screen)
        clock = pygame.time.Clock()
        while self.spinnering_flag:
            clock.tick(15)
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self._draw(self.screen, self.background)
            
    def _draw_title(self, screen):
        pygame.font.init()  # Just in case 
        titlefont = self.font
        text = titlefont.render(self.title, 1, white_color)
        textpos = text.get_rect()
        blockoffx = (self.w / 2)
        blockoffy = (self.h / 2)
        offsetx = blockoffx - (textpos.width / 2)
        offsety = blockoffy - textpos.height - self.size / 2 - 20
        screen.blit(text, (offsetx, offsety))
        pygame.display.update()
            
    def _draw(self, screen, background):
        center_x = self.size / 2
        center_y = self.size / 2
        frame_pattern = int(self.current_frame / 8)
        layer = pygame.Surface((self.size, self.size), SRCALPHA, 32)
        
        layer.blit(self.image, (0, 0), ((self.current_frame % 8) * self.size, 0, self.size, self.size))
        layer2 = pygame.Surface((self.size, self.size), SRCALPHA, 32)
        # layer2.fill(black_color)
        
        layer2.set_alpha(192)
        color_key = layer2.get_at((0, 0))
        layer2.set_colorkey(color_key, RLEACCEL)
        screen_center_x = (self.w - self.size) / 2
        screen_center_y = (self.h - self.size) / 2
        screen.blit(self.screenCopy, (screen_center_x, screen_center_y), (screen_center_x, screen_center_y, self.size, self.size))
        screen.blit(background, (screen_center_x, screen_center_y), (screen_center_x, screen_center_y, self.size, self.size))
        frame_x = 0
        frame_y = 0
        if (frame_pattern // 2) == 0:
            frame_x = center_x
        if (frame_pattern % 3) != 0:
            frame_y = center_y
         
        screen.blit(layer, (screen_center_x + frame_x, screen_center_y + frame_y), (frame_x, frame_y, self.size / 2, self.size / 2))

        pygame.display.update((screen_center_x, screen_center_y, self.size, self.size))
        
    def _clear(self):    
        ''' Put the screen back to before we started '''
        self.screen.blit(self.screenCopy, (0, 0))
        pygame.display.update()
        pygame.event.clear()
