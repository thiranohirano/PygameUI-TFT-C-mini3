'''
Created on 2016/03/04

@author: hirano
'''
import re
from . import object_rectangle  # @UnresolvedImport
import pygame
from .colors import white_color, dark_gray_color

CENTER = 0
LEFT = 1
RIGHT = 2
TOP = 3
BOTTOM = 4

WORD_WRAP = 0
CLIP = 1


class Label(object_rectangle.ObjectRectangle):
    def __init__(self, rect, text, halign=CENTER, valign=CENTER,
                 wrap=CLIP):
        self.font = pygame.font.SysFont('Courier New', 24)
        self.text_color = white_color
        self.select_text_color = dark_gray_color
        self.padding = (6, 6)
        object_rectangle.ObjectRectangle.__init__(self, rect)
        self.halign = halign
        self.valign = valign
        self._wrap_mode = wrap
        self._text = text
        self.enabled = False

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text  # unicode(text, "utf-8")
        self.dirty = True

    def render(self):
        """Force (re)draw the text to cached surfaces.
        """

        self._render(self._text)

    def _render(self, text):
        self.text_surfaces = []

        if text is None or len(text) == 0:
            self._text = None
            self.text_size = (0, 0)
            return

        text = text.replace("\r\n", "\n").replace("\r", "\n")

        if self._wrap_mode == CLIP:
            self._text = re.sub(r'[\n\t]{2,}', ' ', text)
            self.text_size = self._render_line(self._text)
        elif self._wrap_mode == WORD_WRAP:
            self._render_word_wrapped(text)

    def _render_line(self, line_text):
        line_text = line_text.strip()
        text_color = self.text_color
        if self.selected and self.select_text_color != None:
            text_color = self.select_text_color
        text_surface = self.font.render(line_text, True, text_color)
        self.text_surfaces.append(text_surface)

        return text_surface.get_size()

    def _render_word_wrapped(self, text):
        self._text = text
        self.text_size = [0, 0]

        line_width = 0
        max_line_width = self.frame.w - self.padding[0] * 2

        line_tokens = []
        tokens = re.split(r'(\s)', self._text)
        token_widths = {}

        for token in tokens:
            if len(token) == 0:
                continue

            token_width, _ = token_widths.setdefault(token,
                                                     self.font.size(token))

            if token == '\n' or token_width + line_width >= max_line_width:
                line_size = self._render_line(''.join(line_tokens))
                self.text_size[0] = max(self.text_size[0], line_size[0])
                self.text_size[1] += line_size[1]

                if token == '\n':
                    line_tokens, line_width = [], 0
                else:
                    line_tokens, line_width = [token], token_width
            else:
                line_width += token_width
                line_tokens.append(token)

        if len(line_tokens) > 0:
            line_size = self._render_line(''.join(line_tokens))
            self.text_size[0] = max(self.text_size[0], line_size[0])
            self.text_size[1] += line_size[1]

    def _determine_top(self):
        if self.valign == TOP:
            y = self.padding[1]
        elif self.valign == CENTER:
            y = self.rect.h // 2 - self.text_size[1] // 2
        elif self.valign == BOTTOM:
            y = self.rect.h - self.padding[1] - self.text_size[1]
        return y

    def _determine_left(self, text_surface):
        w = text_surface.get_size()[0]
        if self.halign == LEFT:
            x = self.padding[0]
        elif self.halign == CENTER:
            x = self.rect.w // 2 - w // 2
        elif self.halign == RIGHT:
            x = self.rect.w - 1 - self.padding[0] - w
        return x

    def _draw(self, screen):
        if not object_rectangle.ObjectRectangle._draw(self, screen) or not self._text:
            return False

        self.render()
        y = self._determine_top()
        for text_surface in self.text_surfaces:
            x = self._determine_left(text_surface)

            self.surface.blit(text_surface, (x, y))
            y += text_surface.get_size()[1]

        return True
