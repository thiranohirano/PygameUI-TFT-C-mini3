'''
Created on 2016/03/07

@author: hirano
'''
from . import label  # @UnresolvedImport
from . import callback  # @UnresolvedImport

class Button(label.Label):
    '''
    classdocs
    '''
    def __init__(self, rect, text):
        '''
        Constructor
        '''
        label.Label.__init__(self, rect, text)
        self.enabled = True
        self.on_clicked = callback.Signal()
        
    def mouse_up(self, point):
        self.on_clicked(self)
