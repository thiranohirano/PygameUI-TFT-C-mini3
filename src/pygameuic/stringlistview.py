'''
Created on 2016/03/10

@author: hirano
'''
import pygame
from . import object_rectangle  # @UnresolvedImport
from . import callback  # @UnresolvedImport
from . import label  # @UnresolvedImport
from pygame.rect import Rect
from pygameuic import window

class StringListView(object_rectangle.ObjectRectangle):
    '''
    classdocs
    '''
    def __init__(self, rect, items, row_num):
        '''
        Constructor
        '''
        object_rectangle.ObjectRectangle.__init__(self, rect)
        self.row_num = row_num
        self.items = []
        self._items_font = None
        self.string_items = items
        self.selected_index = None
        self.on_selected = callback.Signal()
        self.items_surface = pygame.Surface((self.rect.w - self.border_widths * 2, self.rect.h - self.border_widths * 2)).convert()
        
    @property
    def items_font(self):
        return self._items_font
        
    @items_font.setter
    def items_font(self, new_font):
        self._items_font = new_font
        self.string_items = self._string_items
    
    @property
    def string_items(self):
        return self._string_items
    
    @string_items.setter
    def string_items(self, new_items):
        del self.items[:]
            
        self._string_items = new_items
        x = 0
        y = 0
        w = self.rect.w
#         h = (window.rect.h - 10 - self.border_widths * 2) // 8 - 5
#         h = (self.rect.h - self.border_widths) / (self.rect.h // (10 + window.col_rect_mini(0, 0, 1, 1).h) + 1)
        h = (self.rect.h - self.border_widths) / self.row_num
        for item in self._string_items:
            string_list_item = StringListItem(Rect(x, y, w, h), item)
            if self._items_font is not None:
                string_list_item.font = self._items_font
            self.add_item(string_list_item)
            y += h
        self.dirty = True
        
    def add_item(self, item):
        assert item is not None
        self.rm_item(item)
        self.items.append(item)
        
    def rm_item(self, child):
        for index, ch in enumerate(self.items):
            if ch == child:
                del self.items[index]
                break;
            
    def all_dirty_item(self):
        for item in self.items:
            item.dirty = True
        
    def deselect(self):
        if self.selected_index is not None:
            self.items[self.selected_index].selected = False
        self.selected_index = None

    def select(self, index):
        self.deselect()
        self.selected_index = index

        if index is not None:
            item = self.items[self.selected_index]
            item.selected = True
            self.on_selected(self, item, index)
            
    def mouse_down(self, point):
        for index, item in enumerate(self.items):
            item_rect = Rect(self.rect.x, self.rect.y + item.rect.y, item.rect.w, item.rect.h)
            if item_rect.collidepoint(point):
                self.select(index)
                break
            
    def _draw(self, screen):
        if not object_rectangle.ObjectRectangle._draw(self, screen) :
            return False
        
        self.all_dirty_item()
        self.items_surface.fill(self.background_color)
        for item in self.items:
            item.draw_blit(self.items_surface)
            
        self.surface.blit(self.items_surface, (self.border_widths, self.border_widths))
        return True
    
class StringListItem(label.Label):
    
    def __init__(self, rect, text):
        label.Label.__init__(self, rect, text, halign=label.LEFT)
