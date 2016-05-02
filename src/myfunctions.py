# coding=utf-8

import socket
import struct

def get_ip_address(ifname):
    try:
        import fcntl
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_addr = socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])
        if ip_addr.startswith('169.254.'):
            raise Exception()
        else:
            return  ip_addr
    except Exception:
        return None