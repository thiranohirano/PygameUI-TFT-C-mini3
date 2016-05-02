import sys
import os
import subprocess
import socket
import time
import pygame
import signal
from wifi import Cell, Scheme  # @UnresolvedImport

class PiFi:

  def __init__(self, interface='wlan0'):
    self.interface = interface
    self.aps = None

    # Templates for the interface files
    self.wpa_supplicant_path = '/etc/wpa_supplicant/wpa_supplicant.conf'
    self.wpa_supplicant_template = """
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
        ssid="%s"
        %s
}
"""
    self.etc_interfaces_path = '/etc/network/interfaces'
    self.etc_interfaces_template = """
auto lo

iface lo inet loopback
iface eth0 inet dhcp

allow-hotplug wlan0
iface wlan0 inet manual
wpa-roam %s
iface default inet dhcp
""" % self.wpa_supplicant_path

    # Vars for the selected AP, set by prompts
    self.selected_ap = None
    self.selected_ap_name = None
    self.selected_ap_password = None
    self.selected_ap_encrypted = None

    # IP address set by self.getIP()
    self.ip = None
  
  def getWifiAPs(self):
    print("Scanning for WiFi APs...\n")
    aps = Cell.all('wlan0')
    aps_by_signal_strength = sorted(aps, key=lambda ap: ap.signal, reverse=True)
    self.aps = aps_by_signal_strength

  def printAPs(self):
    print("Available networks:")
    index = 0
    for ap in self.aps:
      print("[%d] SSID:%s  Strength:%d  Protected:%s" % (index, ap.ssid, ap.signal, str(ap.encrypted)))
      index = index + 1
  
  def promptForSSID(self):
    ap_count = len(self.aps)
    while (True):
      prompt = "Select wifi AP (0-%d): " % (ap_count - 1)
      ap_index = input(prompt)
      if ap_index.isdigit():
        ap_index_int = int(ap_index)
        if (ap_index_int >= ap_count or ap_index_int < 0):
          pass
        else:  
          print("Selected wifi AP: " + self.aps[ap_index_int].ssid)
          break

      print("'%s' is not a valid selection. %s" % (ap_index, prompt)) 
      continue
    self.setAPFromIndex(ap_index_int)

  def setAPFromIndex(self, ap_index):
    self.selected_ap = self.aps[ap_index]
    self.selected_ap_ssid = self.selected_ap.ssid
    self.selected_ap_encrypted = self.selected_ap.encrypted

  def promptForPassword(self):
    if (self.selected_ap_encrypted):
      password = input("Enter password for '%s': " % self.selected_ap_ssid)
      self.selected_ap_password = password
    else:
      print("'%s' is not encrypted. No password necessary." % self.selected_ap_ssid)

  def generateWPASupplicant(self):
    print("Generating '%s'..." % self.wpa_supplicant_path)
    if (self.selected_ap_encrypted):
      encryption_string = 'psk="%s"' % self.selected_ap_password
    else:
      encryption_string = "key_mgmt=None"
    wpa_supplicant = self.wpa_supplicant_template % (self.selected_ap_ssid, encryption_string)

    file = open(self.wpa_supplicant_path, 'w')
    file.write(wpa_supplicant)
    file.close()

  def generateEtcInterfaces(self):
    print("Generating '%s'..." % self.etc_interfaces_path)
    file = open(self.etc_interfaces_path, 'w')
    file.write(self.etc_interfaces_template)
    file.close()

  def getIP(self):
    proc = subprocess.Popen(['hostname', '-I'], stdout=subprocess.PIPE)
    proc.wait()
    out = proc.stdout.readline()
    self.ip = out.strip()
    return self.ip

  def isConnected(self):
    self.getIP()
    #print 'Your IP address is: %s' % ip
    try:
      socket.inet_aton(self.ip)
      return True
    except socket.error:
      return False

  def reconnect(self):
    print('Re-connecting wifi...')
    proc = subprocess.Popen(['sudo', 'ifdown', self.interface], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()
    proc2 = subprocess.Popen(['sudo', 'ifup', self.interface], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc2.wait()
    time.sleep(3) #allow some time to get IP

  def run(self):
    self.getWifiAPs()
    while (True): 
      self.printAPs()
      print()
      self.promptForSSID()
      print()
      self.promptForPassword()
      self.generateEtcInterfaces()
      self.generateWPASupplicant()
      self.reconnect()
      if(self.isConnected()):
        break
      else:
        print()
        print("[ERROR] Failed to connect to '%s'!" % self.selected_ap_ssid)
        print("[ERROR] Please try again, and double-check your password.")
        print()

    print("SUCCESS! IP: %s" % self.ip)

