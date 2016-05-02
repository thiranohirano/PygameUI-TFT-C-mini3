# coding=utf-8

import pygame
from . import object_rectangle
from . import resource

SCALE_TO_FILL = 0

class ImageView(object_rectangle.ObjectRectangle):
    def __init__(self, rect, img, content_mode=SCALE_TO_FILL):
        assert img is not None

        if rect is None:
            rect = pygame.Rect((0, 0), img.get_size())
        elif rect.w == 0 and rect.h == 0:
            rect.size = img.get_size()

        object_rectangle.ObjectRectangle.__init__(self, rect)

        self.enabled = False
        self.content_mode = content_mode
        self.image = img

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, new_image):
        self._image = new_image
        self.dirty = True

    def render(self):
        if self.content_mode == SCALE_TO_FILL:
            self._image = resource.scale_image(self._image, self.rect.size)
        else:
            assert False, "Unknown content_mode"

    def _draw(self, screen):
        if not object_rectangle.ObjectRectangle._draw(self, screen):
            return False

        self.render()
        self.surface.blit(self._image, (0, 0))

        return True
