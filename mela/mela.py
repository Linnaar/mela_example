import gc
import os
import ujson as json
#======================================================================================================




#--------------------------------------------------------------------
#
#   Main class for our board
#
#--------------------------------------------------------------------
class Mela:
  def __init__(self):
    self.info=Mela_info()
    self.settings=Mela_settings()
    self.wifi=False
 
    try:
      if self.settings.wifi['connect_on_boot']:
        import network
        sta_if=network.WLAN(network.STA_IF)
        sta_if.active(True)
        #wlan_networks=sta_if.scan()
        #print(wlan_networks)
        sta_if.connect(self.settings.wifi['ssid'],self.settings.wifi['key'])
        self.wifi=sta_if
    except:
      print('WLAN connection problem')
      
  def wlan_connect(self):
    import network
    import utime as time
    sta_if=network.WLAN(network.STA_IF)
    sta_if.active(True)
    if sta_if.isconnected():
      print("WLAN already connected")
      return sta_if  
    try:
      print('Trying to connect to:', self.settings.wifi['ssid'])
      sta_if.connect(self.settings.wifi['ssid'],self.settings.wifi['key'])
      for _ in range(100):
        if sta_if.isconnected():
          print('\nConnected! Network information:', sta_if.ifconfig())
          return sta_if
        else:
          print('.', end='')
          time.sleep_ms(100)
        print('\nConnection failed!')
        sta_if.disconnect()
    except:
      print('WLAN connection problem')    
    

#--------------------------------------------------------------------
#
#    Settings save/load class for our board
#
#--------------------------------------------------------------------
class Mela_settings:
  def __init__(self):
    self.data=self.load_settings()

  @property
  def wifi(self):
    return self.data['settings']['wifi']

  def load_settings(self):
    try:
      with open('settings.json','r') as settings_file:
        return json.load(settings_file)
    except:
      print("Settings file read problem. Returning default configuration.")
      return {'settings': {'wifi': {'connect_on_boot': False, 'ssid': 'LAN', 'key': '12345'}}} 

  def save_settings(self):
    try:
      with open('settings.json','w') as settings_file:
        return json.dump(self.data,settings_file)
    except:
      print("Settings file write problem.")
      return False

#--------------------------------------------------------------------
#
#    Information class for our board
#
#--------------------------------------------------------------------
class Mela_info:
  def __init__(self):
    if not gc.isenabled(): gc.enable()
    gc.collect()

  def df(self):
    s = os.statvfs('//')
    T=(s[1]*s[2])/1048576
    F=(s[0]*s[3])/1048576
    P = '{0:.2f}%'.format(F/T*100)
    return ('VFS: Total:{0} Mb Free:{1} Mb ({2})'.format(T,F,P))

  def free(self):
    gc.collect()
    F = gc.mem_free()
    A = gc.mem_alloc()
    T = F+A
    P = '{0:.2f}%'.format(F/T*100)
    return ('RAM: Total:{0} bytes Free:{1} bytes ({2})'.format(T,F,P))

  def wlan_scan(self):
    import network
    try:
      sta_if=network.WLAN(network.STA_IF)
      sta_if.active(True)
      print("WLAN interface activated. Starting scan...")      
      wlans=sta_if.scan()
      AUTHMODE = {0: "open", 1: "WEP", 2: "WPA-PSK", 3: "WPA2-PSK", 4: "WPA/WPA2-PSK"}
      count=0
      for ssid, bssid, channel, rssi, authmode, hidden in sorted(wlans, key=lambda x: x[3], reverse=True):
        count=count+1
        ssid = ssid.decode('utf-8')      
        print("%d ssid: %s chan: %d rssi: %d authmode: %s bssid: %s" % (count, ssid, channel, rssi, AUTHMODE.get(authmode, '?'), bssid.hex('-')))
    except:
      print('WLAN connection problem')
        
  def wlan_status(self):
      import network
      try:
        sta_if=network.WLAN(network.STA_IF)
        sta_if.active(True)
        STATUS={1000: "STAT_IDLE", 1001: " STAT_CONNECTING", 202: "STAT_WRONG_PASSWORD", 201: "STAT_NO_AP_FOUND", 1010: "STAT_GOT_IP", 203: "STAT_ASSOC_FAIL", 200: "STAT_BEACON_TIMEOUT", 204: "STAT_HANDSHAKE_TIMEOUT"}
        print("Current WLAN status: %s" % STATUS.get(sta_if.status(), '?'))
      except:
        print('WLAN connection problem')
    