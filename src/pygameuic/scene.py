import pygame
from pygame.constants import MOUSEBUTTONDOWN, MOUSEBUTTONUP
from pygame.locals import USEREVENT
from . import window  # @UnresolvedImport
from .process_spinner import ProcessSpinner  # @UnresolvedImport
from .virtualKeyboard import VirtualKeyboard  # @UnresolvedImport
from .colors import black_color  # @UnresolvedImport
from . import callback
import time
import os

stack = []
current = None

SCREEN_SAVER_ONE_MINUTE = 1 * 60

def push(scene):
    global current
    stack.append(scene)
    current = scene
    current.all_dirty_item()

def pop():
    global current

    if len(stack) > 0:
        stack.pop()

    if len(stack) > 0:
        current = stack[-1]
        

class Scene(object):
    def __init__(self):
        self.window_surface = None
        self.surface = pygame.Surface(window.rect.size, pygame.SRCALPHA, 32)
        self.children = []
        self.minutes = 0
        self.screen_saver = False
        self.screen_saver_time = SCREEN_SAVER_ONE_MINUTE * 5

    def loaded(self):
        self.minutes = 0
        self.screen_saver = False

    def closed(self):
        pass

    def run(self):
        events = pygame.event.get() 
        if events is not None:
            for e in events:
                if e.type == USEREVENT + 1:
                    if not self.screen_saver:
                        self.minutes += 1
                if e.type == MOUSEBUTTONDOWN:
                    if not self.screen_saver:
                        self._unselectall()
                        pos = pygame.mouse.get_pos()
                        self._selectatmouse(pos)
                        hit_object = self._hit_object(pos)
                        if hit_object is not None:
                            hit_object.mouse_down(pos)
                        self.event_mousedown(pos)
                if e.type == MOUSEBUTTONUP:
                    if not self.screen_saver:
                        self._unselectall()
                        pos = pygame.mouse.get_pos()
                        hit_object = self._hit_object(pos)
                        if hit_object is not None:
                            hit_object.mouse_up(pos)
                        self.event_mouseup(pos)
                    else:
                        self.minutes = 0
                        self.screen_saver = False
                        self.all_dirty_item()
                        os.system("/home/pi/backlight.sh on")
                if e.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
        if self.minutes >= self.screen_saver_time and not self.screen_saver:
            self.screen_saver = True
            self.window_surface.fill(black_color)
            pygame.display.update()
            os.system("/home/pi/backlight.sh off")
        
    def event_mousedown(self, pos):
        pass
    
    def event_mouseup(self, pos):
        pass
    
    def show_process_spinner(self, slot, title=''):
        ps = ProcessSpinner(self.window_surface)
        ps.run(slot, title)
        
    def show_virtual_keyboard(self, text=''):
        vk = VirtualKeyboard(self.window_surface)
        return vk.run(text)
    
    def show_process_message(self, title='', sleep_time=1):
        self.show_process_spinner(lambda: time.sleep(sleep_time), title)
        
    def add_child(self, item):
        assert item is not None
        self.rm_child(item)
        self.children.append(item)
        item.dirty = True
        
    def rm_child(self, child):
        for index, ch in enumerate(self.children):
            if ch == child:
#                 ch.orphaned()
                del self.children[index]
                self.all_dirty_item()
                break;
            
    def all_dirty_item(self):
        self.window_surface.fill(black_color)
        for child in self.children:
            child.dirty = True
        
    def _draw(self):
#         print 'draw'
        draw_flag = False
        for child in self.children:
            if child.draw_blit(self.surface):
                draw_flag = True
                
        return draw_flag
    
    def displayUpdate(self):
        flag = self._draw()
        if flag and not self.screen_saver:
            self.window_surface.blit(self.surface, (0, 0))
            pygame.display.update()
            print ('update')
        
    def _unselectall(self):
        for child in self.children:
            if child.selected:
                child.selected = False
                child.dirty = True
                
    def _selectatmouse(self, pos):
        for child in self.children:
            if child.rect.collidepoint(pos) and child.enabled:
                child.selected = True
                child.dirty = True
                
    def _hit_object(self, pos):
        for child in self.children:
            if child.rect.collidepoint(pos) and child.enabled:
                return child
        return None
