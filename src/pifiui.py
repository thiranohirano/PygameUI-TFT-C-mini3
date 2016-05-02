'''
Created on 2016/03/07

@author: hirano
'''
import pygame
import pygameuic as ui
import pifi
import myfunctions

class PifiUI(ui.Scene):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        ui.Scene.__init__(self)
        # self.main_frame = ui.ObjectRectangle(ui.window.rect)
        # self.main_frame.enabled = False
        # self.main_frame.border_color = mycolors.belize_hole
        # self.main_frame.border_widths = 9
        # self.add_child(self.main_frame)
        
        btn = ui.Button(ui.col_rect_mini(7, 0, 1, 1), 'X')
        btn.on_clicked.connect(self.back)
        self.add_child(btn)
        
        scan_btn = ui.Button(ui.col_rect_mini(1, 5, 6, 1), 'Scan')
        scan_btn.on_clicked.connect(self.scan)
        self.add_child(scan_btn)
        
        scan_label = ui.Label(ui.col_rect_mini(1, 0, 6, 1), 'Select WiFi network...')
        self.add_child(scan_label)
        
        self.ap_listview = ui.StringListView(ui.col_rect_mini(0, 1, 8, 4), [], row_num=4)
        # self.ap_listview.items_font = pygame.font.SysFont('Courier New', 20, bold=True)
        self.ap_listview.on_selected.connect(self.ap_selected)
        self.add_child(self.ap_listview)
        
        self.pifi = pifi.PiFi()
        
    def back(self, btn):
        ui.use_scene(0)
        
    def scan(self, btn):
        self.show_process_spinner(self.scan_process, "Scanning for WiFi networks...")
        
    def scan_process(self):
        self.pifi.getWifiAPs()
        aps_list = []
        for ap in self.pifi.aps:
            strength = "H"
            if ap.signal < -80:
                strength = "L"
            elif ap.signal < -60:
                strength = "M"
            aps_list.append(strength+" SSID:" + ap.ssid)
        self.ap_listview.string_items = aps_list
        
    def ap_selected(self, slv, item, index):
        print(str(index))
        self.pifi.setAPFromIndex(index)
        if self.pifi.selected_ap_encrypted:
            input_pwd = self.show_virtual_keyboard()
            if input_pwd != '':
                self.pifi.selected_ap_password = input_pwd
            else: return
            
        self.show_process_spinner(self.generate_process, "Generating Config File...")
        ip_address = myfunctions.get_ip_address('wlan0')
        if ip_address is not None:
            self.show_process_message("Success! IP: %s" % ip_address, 2)
        else:
            self.show_process_message("Failed! Check WiFi password", 2)

    def generate_process(self):
        self.pifi.generateEtcInterfaces()
        self.pifi.generateWPASupplicant()
        self.pifi.reconnect()
