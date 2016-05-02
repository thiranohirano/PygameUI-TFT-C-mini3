import pygame
import os
from pygame.locals import *
from .object_rectangle import *
from .label import *
from .button import *
from .stringlistview import *
from .imageview import *
from .imagebutton import *
from .callback import *
from .virtualKeyboard import *
from .process_spinner import *
from .scene import Scene  # @UnresolvedImport
from . import scene  # @UnresolvedImport
from . import window  # @UnresolvedImport
from . import theme  # @Reimport @UnresolvedImport
from . import colors

Rect = pygame.Rect
window_surface = None
ui_quit = False

class SceneManager(object):
    def __init__(self):
        self.scenes = []

    def append_scene(self, scene):
        scene.window_surface = window_surface
        self.scenes.append(scene)
        
    def use_scene(self, index):
        if scene.current is not None:
            scene.current.closed()
        scene.pop()
        scene.push(self.scenes[index])
        scene.current.loaded()
        scene.current.__class__.__class__.__name__
        
scene_manager = SceneManager()

def init(name=' ', window_size=(480, 320), mouse=True, fullscreen=False):
    pygame.init()
    pygame.font.init()
    global window_surface
    if fullscreen:
        window_surface = pygame.display.set_mode(window_size, FULLSCREEN)
    else:
        window_surface = pygame.display.set_mode(window_size)
    pygame.display.set_caption(name)
    window.rect = pygame.Rect((0, 0), window_size)
    theme.init()
    pygame.mouse.set_visible(mouse)
    os.system("/home/pi/backlight.sh setup")
    
def quit():
    global ui_quit
    ui_quit = True

def append_scene(_scene):
    global scene_manager
    scene_manager.append_scene(_scene)
    
def use_scene(_index):
    global scene_manager
    scene_manager.use_scene(_index)


def col_rect(col, row, col_span, row_span, margin=5):
#     padding = 5
#     one_col = (window.rect.w - margin * 2)  // 12
#     one_row = (window.rect.h - margin * 2) // 8
#     return pygame.Rect(col * one_col + padding + margin, row * one_row + padding + margin, col_span * one_col - padding * 2, row_span * one_row - padding * 2)
    return window.col_rect(col, row, col_span, row_span, margin)


def col_rect_mini(col, row, col_span, row_span, margin=5, padding=5):
    return window.col_rect_mini(col, row, col_span, row_span, margin, padding)
    
def run():
    assert len(scene.stack) > 0
    clock = pygame.time.Clock()
    pygame.time.set_timer(USEREVENT + 1, 1000)
    while True:
        clock.tick(20)
        scene.current.run()
        scene.current.displayUpdate()
        if ui_quit:
            window_surface.fill(colors.black_color)
            pygame.display.update()
            scene.current.closed()
            pygame.quit()
            import sys
            sys.exit()
