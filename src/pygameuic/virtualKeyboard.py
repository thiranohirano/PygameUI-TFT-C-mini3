"""

    (C) Copyright 2007 Anthony Maro
    (C) Copyright 2014 William B Phelps

   Version 2.1 - March 2014 - for PiTFT 320x240 touchscreen
   Version 2.2 - March 2014 - generalized for "any" touchscreen

   Now has 2 line input area (code specific for 2 lines)
       
   This program is free software; you can redistribute it and/or
   modify it under the terms of the GNU General Public License as
   published by the Free Software Foundation; either version 2 of the
   License, or (at your option) any later version.

   This program is distributed in the hope that it will be useful, but
   WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
   General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
   02111-1307, USA.

   Usage:
   
   from virtualKeyboard import VirtualKeyboard
   
   vkeybd = VirtualKeyboard(screen)
   userinput = vkeybd.run(default_text)
   
   screen is a full screen pygame screen.  The VirtualKeyboard will shade out the current screen and overlay
   a transparent keyboard.  default_text gets fed to the initial text import - used for editing text fields
   If the user clicks the escape hardware button, the default_text is returned
   
"""

#from string import maketrans

import pygame, time
from pygame.constants import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION
from pygame.rect import Rect
from . import object_rectangle

Uppercase = str.maketrans("abcdefghijklmnopqrstuvwxyz`1234567890-=[]\;\',./",
  'ABCDEFGHIJKLMNOPQRSTUVWXYZ~!@#$%^&*()_+{}|:"<>?')

# _keyWidth = 27 # default key width including borders
# _keyHeight = 29 # default key height 

# ----------------------------------------------------------------------------

class VirtualKeyboard(object_rectangle.ObjectRectangle):
    ''' Implement a basic full screen virtual keyboard for touchscreens '''

    def __init__(self, screen):

        self.screen = screen
        self.rect = self.screen.get_rect()
        self.w = self.rect.width
        self.h = self.rect.height

        # make a copy of the screen
        self.screenCopy = screen.copy()

        # create a background surface
        self.background = pygame.Surface(self.rect.size)
        self.background.fill((0, 0, 0))  # fill with black
        self.background.set_alpha(191)  # 50% transparent
        # blit background to screen
        self.screen.blit(self.background, (0, 0))

        self.keyW = int(self.w / 12 + 0.5) - 2  # key width with border
        self.keyH = int(self.h / 8 + 0.5)  # key height

        self.x = (self.w - (self.keyW + 2) * 12) / 2  # centered
        self.y = 5  # stay away from the edges (better touch)
#        print 'keys x {} w {} keyW {} keyH {}'.format(self.x, self.w, self.keyW, self.keyH)

        pygame.font.init()  # Just in case 
        self.font = pygame.font.SysFont('Courier New', int(self.keyW / 2), bold=True)  # keyboard font
        fsize = int(self.rect.height / 12 + 0.5)  # font size proportional to screen height
        self.txtfont = pygame.font.SysFont('Courier New', fsize, bold=True)

        object_rectangle.ObjectRectangle.__init__(self, self.rect)
        # set dimensions for text input box
#        self.textW = self.w-(self.keyW+2) # leave room for escape key (?)
        self.textW = (self.keyW + 2) * 11 + 2  # leave room for escape key 
        self.textH = self.keyH * 2 - 6

        self.caps = False
        self.keys = []
#        self.textbox = pygame.Surface((self.rect.width,self.keyH*2))
        self.addkeys()  # add all the keys
        self.paintkeys()  # paint all the keys

        pygame.display.update()


    def run(self, text=''):

        self.text = text
        # create an input text box
        # create a text input box with room for 2 lines of text. leave room for the escape key
        self.input = TextInput(self.screen, self.text, self.x, self.y, self.textW, self.textH, self.txtfont)

        counter = 0
        time.sleep(0.3)
        pygame.event.clear()
        
        clock = pygame.time.Clock()
        # main event loop (hog all processes since we're on top, but someone might want
        # to rewrite this to be more event based...
        while True:
            clock.tick(20)
            events = pygame.event.get() 
            if events != None:
                for e in events:
# touch screen does not have these events...
#                    if (e.type == KEYDOWN):
#                        if e.key == K_ESCAPE:
#                            self.clear()
#                            return self.text # Return what we started with
#                        if e.key == K_RETURN:
#                            self.clear()
#                            return self.input.text # Return what the user entered
#                        if e.key == K_LEFT:
#                            self.input.deccursor()
#                            pygame.display.flip()
#                        if e.key == K_RIGHT:
#                            self.input.inccursor()
#                            pygame.display.flip()
                    if (e.type == MOUSEBUTTONDOWN):
                        self.selectatmouse()   
                    if (e.type == MOUSEBUTTONUP):
                        if self.clickatmouse():
                            # user clicked enter or escape if returns True
                            self.clear()
                            return self.input.text  # Return what the user entered
                    if (e.type == MOUSEMOTION):
                        if e.buttons[0] == 1:
                            # user click-dragged to a different key?
                            self.selectatmouse()

            counter += 1
            if counter > 5:                
                self.input.flashcursor()
                counter = 0
# #            gtk.main_iteration(block=False)

    def unselectall(self, force=False):
        ''' Force all the keys to be unselected
            Marks any that change as dirty to redraw '''
        for key in self.keys:
            if key.selected:
                key.selected = False
                key.dirty = True

    def clickatmouse(self):
        ''' Check to see if the user is pressing down on a key and draw it selected '''
        self.unselectall()
        for key in self.keys:
            keyrect = Rect(key.x, key.y, key.w, key.h)
            if keyrect.collidepoint(pygame.mouse.get_pos()):
                key.dirty = True
                if key.bskey:
                    # Backspace
                    self.input.backspace()
                    self.paintkeys() 
                    return False
                if key.fskey:
                    self.input.inccursor()
                    self.paintkeys() 
                    return False
                if key.spacekey:                    
                    self.input.addcharatcursor(' ')
                    self.paintkeys() 
                    return False
                if key.shiftkey:
                    self.togglecaps()
                    self.paintkeys() 
                    return False
                if key.escape:
                    self.input.text = ''  # clear input
                    return True
                if key.enter:
                    return True
                if self.caps:
                    keycap = key.caption.translate(Uppercase)
                else:
                    keycap = key.caption
                self.input.addcharatcursor(keycap)
                self.paintkeys()
                return False

        self.paintkeys() 
        return False

    def togglecaps(self):
        ''' Toggle uppercase / lowercase '''
        if self.caps: 
            self.caps = False
        else:
            self.caps = True
        for key in self.keys:
            key.dirty = True        

    def selectatmouse(self):
        # User has touched the screen - is it inside the textbox, or inside a key rect?
        self.unselectall()
        pos = pygame.mouse.get_pos()
#        print 'touch {}'.format(pos)
        if self.input.rect.collidepoint(pos):
#            print 'input {}'.format(pos)
            self.input.setcursor(pos)
        else:
            for key in self.keys:
                keyrect = Rect(key.x, key.y, key.w, key.h)
                if keyrect.collidepoint(pos):
                    key.selected = True
                    key.dirty = True
                    self.paintkeys()
                    return

        self.paintkeys()        

    def addkeys(self):  # Add all the keys for the virtual keyboard 
        margin_x = 2
        margin_y = 2
        x = self.x
        y = self.y + self.textH + self.keyH / 4

        row = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=']
        for item in row:
            onekey = VKey(item, x, y, self.keyW, self.keyH, self.font)
            self.keys.append(onekey)
            x += self.keyW + margin_x

        y += self.keyH + margin_y  # overlap border
        x = self.x

        row = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']']
        for item in row:
            onekey = VKey(item, x, y, self.keyW, self.keyH, self.font)
            self.keys.append(onekey)
            x += self.keyW + margin_x

        y += self.keyH + margin_y
        x = self.x

        row = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`']
        for item in row:
            onekey = VKey(item, x, y, self.keyW, self.keyH, self.font)
            self.keys.append(onekey)
            x += self.keyW + margin_x

        x = self.x + self.keyW / 2 
        y += self.keyH + margin_y

        row = ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', '\\']
        for item in row:
            onekey = VKey(item, x, y, self.keyW, self.keyH, self.font)
            self.keys.append(onekey)
            x += self.keyW + margin_x

        x = self.x + 1
        y += self.keyH + self.keyH / 4

#        print 'addkeys keyW {} keyH {}'.format(self.keyW, self.keyH)

        onekey = VKey('Shift', x, y, int(self.keyW * 2.5), self.keyH, self.font)
        onekey.special = True
        onekey.shiftkey = True
        self.keys.append(onekey)
        x += onekey.w + self.keyW / 6

        onekey = VKey('Space', x, y, self.keyW * 5, self.keyH, self.font)
        onekey.special = True
        onekey.spacekey = True
        self.keys.append(onekey)
        x += onekey.w + self.keyW / 6

        onekey = VKey('Enter', x, y, int(self.keyW * 2.5), self.keyH, self.font)
        onekey.special = True
        onekey.enter = True
        self.keys.append(onekey)
        x += onekey.w + self.keyW / 3

        onekey = VKey('<-', x, y, int(self.keyW * 1.2 + 0.5), self.keyH, self.font)
        onekey.special = True
        onekey.bskey = True
        self.keys.append(onekey)
        x += onekey.w + self.keyW / 3

        xfont = self.font  # I like this X better
        onekey = VKey('X', self.x + self.textW + 1, self.y + 1, self.keyW - 3, self.keyH, xfont)  # exit key
        onekey.special = True
        onekey.escape = True
        self.keys.append(onekey)


    def paintkeys(self):
        ''' Draw the keyboard (but only if they're dirty.) '''
        for key in self.keys:
            key.draw(self.screen, self.background, self.caps)
        pygame.display.update()

    def clear(self):    
        ''' Put the screen back to before we started '''
        self.screen.blit(self.screenCopy, (0, 0))
        pygame.display.update()
        pygame.event.clear()
# ----------------------------------------------------------------------------

class TextInput():
    ''' Handles the text input box and manages the cursor '''
    def __init__(self, screen, text, x, y, w, h, txtfont):
        self.screen = screen
        self.text = text
        self.cursorpos = len(text)
        self.x = x
        self.y = y

        self.w = w
        self.h = h
        self.rect = Rect(x, y, w, h)
        self.layer = pygame.Surface((self.w, self.h))
        self.background = pygame.Surface((self.w, self.h))
        self.background.fill((0, 0, 0))  # fill with black

#        self.font = pygame.font.Font(None, fontsize) # use this if you want more text in the line
        rect = screen.get_rect()

        self.txtFont = txtfont
        # attempt to figure out how many chars will fit on a line
        # this does not work with proportional fonts
        tX = self.txtFont.render("XXXXXXXXXX", 1, (255, 255, 255))  # 10 chars
        rtX = tX.get_rect()  # how big is it?
        self.lineChars = int(self.w / (rtX.width / 10)) - 1  # chars per line (horizontal)
        self.lineH = rtX.height  # pixels per line (vertical)
#        print 'txtinp: width={} rtX={} font={} lineChars={} lineH={}'.format(self.w,rtX,fsize, self.lineChars,self.lineH)

        self.cursorlayer = pygame.Surface((2, self.lineH))  # thin vertical line
        self.cursorlayer.fill((255, 255, 255))  # white vertical line
        self.cursorvis = True

        self.cursorX = len(text) % self.lineChars
        self.cursorY = int(len(text) / self.lineChars)  # line 1

        self.draw()

    def draw(self):
        ''' Draw the text input box '''
#        self.layer.fill([255, 255, 255, 127]) # 140
        self.layer.fill((0, 0, 0))  # clear the layer
        pygame.draw.rect(self.layer, (255, 255, 255), (1, 1, self.w - 2, self.h - 2), 2)  # draw the box

# should be more general, but for now, just hack it for 2 lines
        txt1 = self.text[:self.lineChars]  # line 1
        txt2 = self.text[self.lineChars:]  # line 2
        t1 = self.txtFont.render(txt1, 1, (255, 255, 255))  # line 1
        self.layer.blit(t1, (4, 4))
        t2 = self.txtFont.render(txt2, 1, (255, 255, 255))  # line 1
        self.layer.blit(t2, (4, 4 + self.lineH))

        self.screen.blit(self.background, self.rect)
        self.screen.blit(self.layer, self.rect)
        self.drawcursor()

        pygame.display.update()

    def flashcursor(self):
        ''' Toggle visibility of the cursor '''
        if self.cursorvis:
            self.cursorvis = False
        else:
            self.cursorvis = True

        self.screen.blit(self.background, self.rect)
        self.screen.blit(self.layer, self.rect)

        if self.cursorvis:
            self.drawcursor()
        pygame.display.update()

    def addcharatcursor(self, letter):
        ''' Add a character whereever the cursor is currently located '''
        if self.cursorpos < len(self.text):
            # Inserting in the middle
            self.text = self.text[:self.cursorpos] + letter + self.text[self.cursorpos:]
            self.cursorpos += 1
            self.draw()
            return
        self.text += letter
        self.cursorpos += 1
        self.draw()

    def backspace(self):
        ''' Delete a character before the cursor position '''
        if self.cursorpos == 0: return
        self.text = self.text[:self.cursorpos - 1] + self.text[self.cursorpos:]
        self.cursorpos -= 1
        self.draw()
        return

    def deccursor(self):
        ''' Move the cursor one space left '''
        if self.cursorpos == 0: return
        self.cursorpos -= 1
        self.draw()

    def inccursor(self):
        ''' Move the cursor one space right (but not beyond the end of the text) '''
        if self.cursorpos == len(self.text): return
        self.cursorpos += 1
        self.draw()

    def drawcursor(self):
        ''' Draw the cursor '''
        line = int(self.cursorpos / self.lineChars)  # line number
        if line > 1: line = 1
        x = 4 + self.x
        y = 4 + self.y + line * self.lineH
        # Calc width of text to this point
        if self.cursorpos > 0:
            linetext = self.text[line * self.lineChars:self.cursorpos]
            rtext = self.txtFont.render(linetext, 1, (255, 255, 255))
            textpos = rtext.get_rect()
            x = x + textpos.width + 1
        self.screen.blit(self.cursorlayer, (x, y))

    def setcursor(self, pos):  # move cursor to char nearest position (x,y)
        line = int((pos[1] - self.y) / self.lineH)  # vertical
        if line > 1: line = 1  # only 2 lines
        x = pos[0] - self.x + line * self.w  # virtual x position
        p = 0
        l = len(self.text)
#        print 'setcursor {} x={},y={}'.format(pos,x,y)
#        print 'text {}'.format(self.text)
        while p < l:
            text = self.txtFont.render(self.text[:p + 1], 1, (255, 255, 255))  # how many pixels to next char?
            rtext = text.get_rect()
            textX = rtext.x + rtext.width
#            print 't = {}, tx = {}'.format(t,textX)
            if textX >= x: break  # we found it
            p += 1
        self.cursorpos = p
        self.draw()

# ----------------------------------------------------------------------------

class VKey(object):
    ''' A single key for the VirtualKeyboard '''
#    def __init__(self, caption, x, y, w=67, h=67):
    def __init__(self, caption, x, y, w, h, font):
        self.x = x
        self.y = y
        self.caption = caption
        self.w = w + 1  # overlap borders
        self.h = h + 1  # overlap borders
        self.special = False
        self.enter = False
        self.bskey = False
        self.fskey = False
        self.spacekey = False
        self.escape = False
        self.shiftkey = False
        self.font = font
        self.selected = False
        self.dirty = True
        self.keylayer = pygame.Surface((self.w, self.h)).convert()
        self.keylayer.fill((128, 128, 128))  # 0,0,0
# #        self.keylayer.set_alpha(160)
        # Pre draw the border and store in the key layer
        pygame.draw.rect(self.keylayer, (255, 255, 255), (0, 0, self.w, self.h), 4)

    def fill_gradient(self, surface, color, gradient, rect=None, vertical=True, forward=True):
        """fill a surface with a gradient pattern
        Parameters:
        color -> starting color
        gradient -> final color
        rect -> area to fill; default is surface's rect
        vertical -> True=vertical; False=horizontal
        forward -> True=forward; False=reverse
        
        Pygame recipe: http://www.pygame.org/wiki/GradientCode
        """
        if rect is None: rect = surface.get_rect()
        x1, x2 = rect.left, rect.right
        y1, y2 = rect.top, rect.bottom
        if vertical: h = y2 - y1
        else:        h = x2 - x1
        if forward: a, b = color, gradient
        else:       b, a = color, gradient
        rate = (
            float(b[0] - a[0]) / h,
            float(b[1] - a[1]) / h,
            float(b[2] - a[2]) / h
        )
        fn_line = pygame.draw.line
        if vertical:
            for line in range(y1, y2):
                color = (
                    min(max(a[0] + (rate[0] * (line - y1)), 0), 255),
                    min(max(a[1] + (rate[1] * (line - y1)), 0), 255),
                    min(max(a[2] + (rate[2] * (line - y1)), 0), 255)
                )
                fn_line(surface, color, (x1, line), (x2, line))
        else:
            for col in range(x1, x2):
                color = (
                    min(max(a[0] + (rate[0] * (col - x1)), 0), 255),
                    min(max(a[1] + (rate[1] * (col - x1)), 0), 255),
                    min(max(a[2] + (rate[2] * (col - x1)), 0), 255)
                )
                fn_line(surface, color, (col, y1), (col, y2))
                
    def draw(self, screen, background, shifted=False, forcedraw=False):
        '''  Draw one key if it needs redrawing '''
        if not forcedraw:
            if not self.dirty: return

        keyletter = self.caption
        if shifted:
            if self.shiftkey:
                self.selected = True  # highlight the Shift button
            if not self.special:
                keyletter = self.caption.translate(Uppercase)

        position = Rect(self.x, self.y, self.w, self.h)

        # put the background back on the screen so we can shade properly
        screen.blit(background, (self.x, self.y), position)

        # Put the shaded key background into key layer
        text_color = (255, 255, 255)
        if self.selected:
            color = (192, 192, 192)
            text_color = (50, 50, 50)
        else:
            color = (0, 0, 0)
        pygame.draw.rect(self.keylayer, color, (2, 2, self.w - 4, self.h - 4))
#             self.fill_gradient(self.keylayer, color, (127,127,127), Rect(1,1,self.w-4,self.h-2))
        # Copy key layer onto the screen using Alpha so you can see through it
        
        screen.blit(self.keylayer, (self.x, self.y))

        # Create a new temporary layer for the key contents
        # This might be sped up by pre-creating both selected and unselected layers when
        # the key is created, but the speed seems fine unless you're drawing every key at once
#         templayer = pygame.Surface((self.w,self.h))
#         templayer.set_colorkey((0,0,0))

        text = self.font.render(keyletter, 1, text_color)
        textpos = text.get_rect()
        blockoffx = (self.w / 2)
        blockoffy = (self.h / 2)
        offsetx = blockoffx - (textpos.width / 2)
        offsety = blockoffy - (textpos.height / 2)
#         templayer.blit(text,(offsetx, offsety))

#         screen.blit(templayer, (self.x,self.y))
        screen.blit(text, (self.x + offsetx, self.y + offsety))
        self.dirty = False

