'''
Created on 2016/03/04

@author: hirano
'''
from .colors import black_color, white_color, dark_gray_color, \
    gray_color
from itertools import chain
import pygame

BACKGROUND_COLOR_KEY = 'background_color'
SELECT_BACKGROUND_COLOR_KEY = 'select_background_color'
BORDER_WIDTHS_KEY = 'border_widths'
BORDER_COLOR_KEY = 'border_color'
TEXT_COLOR_KEY = 'text_color'
SELECT_TEXT_COLOR_KEY = 'select_text_color'
PADDING_KEY = 'padding'
FONT_KEY = 'font'
TEXT_FONT_KEY = 'txtfont'

OBJECT_RECTANGLE_CLASS = 'ObjectRectangle'
LABEL_CLASS = 'Label'
BUTTON_CLASS = 'Button'
STRING_LIST_VIEW_CLASS = 'StringListView'
STRING_LIST_ITEM_CLASS = 'StringListItem'
PROCESS_SPINNER_CLASS = 'ProcessSpinner'
VIRTUAL_KEYBOARD_CLASS = 'VirtualKeyboard'


class Theme(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.styles = {}

    def set(self, class_name, key, value):
        self.styles.setdefault(class_name, {})
        self.styles[class_name][key] = value

    def get_dict(self, obj, base_name=OBJECT_RECTANGLE_CLASS):
        classes = []
        klass = obj.__class__
        while True:
            classes.append(klass)
            #             print klass.__name__
            if klass.__name__ == base_name:
                break
            klass = klass.__bases__[0]
        re_style = {}
        for klass in classes:
            class_name = klass.__name__
            try:
                style = self.styles[class_name]
            except KeyError:
                style = {}

            re_style = dict(chain(iter(style.items()), iter(re_style.items())))

        return re_style


default_theme = Theme()
current = None


def init_default_theme():
    default_theme.set(class_name=OBJECT_RECTANGLE_CLASS,
                      key=BACKGROUND_COLOR_KEY,
                      value=black_color)
    default_theme.set(class_name=OBJECT_RECTANGLE_CLASS,
                      key=SELECT_BACKGROUND_COLOR_KEY,
                      value=gray_color)
    default_theme.set(class_name=OBJECT_RECTANGLE_CLASS,
                      key=BORDER_WIDTHS_KEY,
                      value=None)
    default_theme.set(class_name=OBJECT_RECTANGLE_CLASS,
                      key=BORDER_COLOR_KEY,
                      value=None)

    default_theme.set(class_name=LABEL_CLASS,
                      key=TEXT_COLOR_KEY,
                      value=white_color)
    default_theme.set(class_name=LABEL_CLASS,
                      key=SELECT_TEXT_COLOR_KEY,
                      value=dark_gray_color)
    default_theme.set(class_name=LABEL_CLASS,
                      key=PADDING_KEY,
                      value=(6, 6))
    default_theme.set(class_name=LABEL_CLASS,
                      key=BORDER_WIDTHS_KEY,
                      value=None)
    default_theme.set(class_name=LABEL_CLASS,
                      key=FONT_KEY,
                      value=pygame.font.SysFont('Courier New', 22))

    default_theme.set(class_name=BUTTON_CLASS,
                      key=BACKGROUND_COLOR_KEY,
                      value=black_color)
    default_theme.set(class_name=BUTTON_CLASS,
                      key=SELECT_BACKGROUND_COLOR_KEY,
                      value=gray_color)
    default_theme.set(class_name=BUTTON_CLASS,
                      key=BORDER_WIDTHS_KEY,
                      value=1)
    default_theme.set(class_name=BUTTON_CLASS,
                      key=BORDER_COLOR_KEY,
                      value=white_color)
    default_theme.set(class_name=BUTTON_CLASS,
                      key=TEXT_COLOR_KEY,
                      value=white_color)
    default_theme.set(class_name=BUTTON_CLASS,
                      key=SELECT_TEXT_COLOR_KEY,
                      value=dark_gray_color)
    default_theme.set(class_name=BUTTON_CLASS,
                      key=FONT_KEY,
                      value=pygame.font.SysFont('Courier New', 20, bold=True))

    default_theme.set(class_name=STRING_LIST_VIEW_CLASS,
                      key=BACKGROUND_COLOR_KEY,
                      value=dark_gray_color)
    default_theme.set(class_name=STRING_LIST_VIEW_CLASS,
                      key=SELECT_BACKGROUND_COLOR_KEY,
                      value=dark_gray_color)
    default_theme.set(class_name=STRING_LIST_VIEW_CLASS,
                      key=BORDER_WIDTHS_KEY,
                      value=1)
    default_theme.set(class_name=STRING_LIST_VIEW_CLASS,
                      key=BORDER_COLOR_KEY,
                      value=white_color)

    default_theme.set(class_name=STRING_LIST_ITEM_CLASS,
                      key=FONT_KEY,
                      value=pygame.font.SysFont('Courier New', 20, bold=True))


def use_theme(theme):
    """Make the given theme current.
    There are two included themes: light_theme, dark_theme.
    """
    global current
    current = theme
#     import scene
#     if scene.current is not None:
#         scene.current.stylize()

def init():
    init_default_theme()
    use_theme(default_theme)
