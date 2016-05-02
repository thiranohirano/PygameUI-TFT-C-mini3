# coding=utf-8

import pygame
from . import object_rectangle
from . import callback
from . import imageview

class ImageButton(object_rectangle.ObjectRectangle):

    def __init__(self, rect, img):
        if rect is None:
            rect = pygame.Rect((0, 0), img.get_size())
        elif rect.w == 0 and rect.h == 0:
            rect.size = img.get_size()

        object_rectangle.ObjectRectangle.__init__(self, rect)

        self.on_clicked = callback.Signal()

        self.image_view = imageview.ImageView(pygame.Rect(0, 0, rect.w, rect.h), img)
        self.image_surface = pygame.Surface((self.rect.w, self.rect.h)).convert()
        self.select_over_surface = pygame.Surface((self.rect.w, self.rect.h)).convert()
        self.select_over_surface.fill(self.select_background_color)
        self.select_over_surface.set_alpha(100)

    def mouse_up(self, point):
        self.on_clicked(self)

    def _draw(self, screen):
        if not object_rectangle.ObjectRectangle._draw(self, screen):
            return False

        self.image_surface.fill(self.background_color)
        self.image_view.dirty = True
        self.image_view.draw_blit(self.image_surface)
        self.surface.blit(self.image_surface, (0, 0))
        if self.selected:
            self.surface.blit(self.select_over_surface, (0, 0))
        return True
