"""
Created on 2016/03/03

@author: hirano
"""
import pygame

from . import callback  # @UnresolvedImport
from . import theme  # @UnresolvedImport
from . import kvc  # @UnresolvedImport


class ObjectRectangle(object):

    def __init__(self, rect):
        self.rect = rect
        self.background_color = None
        self.select_background_color = None
        self.border_widths = 1
        self.border_color = None
        self.stylise()
        self.selected = False
        self.enabled = True
        self.dirty = True
        self.surface = pygame.Surface((self.rect.w, self.rect.h)).convert()

        self.on_mouse_up = callback.Signal()
        self.on_mouse_down = callback.Signal()

    def mouse_up(self, point):
        self.on_mouse_up(self, point)

    def mouse_down(self, point):
        self.on_mouse_down(self, point)

    def stylise(self):
        style = theme.current.get_dict(self)
        for key, val in style.items():
            kvc.set_value_for_keypath(self, key, val)

    def _draw(self, screen):
        if not self.dirty: return False
        if self.selected:
            if self.select_background_color is not None:
                self.surface.fill(self.select_background_color)
        else:
            if self.background_color is not None:
                self.surface.fill(self.background_color)

        if self.border_color is not None and self.border_widths is not None:
            pygame.draw.rect(self.surface, self.border_color, (0, 0, self.rect.w, self.rect.h), self.border_widths)

        self.dirty = False
        return True

    def draw_blit(self, screen):
        if self._draw(screen):
            screen.blit(self.surface, (self.rect.x, self.rect.y))
            return True

        return False
