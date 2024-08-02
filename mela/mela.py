import gc
import os
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
 
    if self.settings.wifi['connect_on_boot']:
      self.wlan_connect()
      
#********************************************************************      
  def wlan_disconnect(self):
    import network
    
    sta_if=network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.disconnect()
    sta_if.active(False)

#********************************************************************      
  def wlan_connect(self):
    import network
    import utime as time
    
    sta_if=network.WLAN(network.STA_IF)
    sta_if.active(True)
    if sta_if.isconnected():
      print('WLAN already connected. Board IP: %s' % sta_if.ifconfig()[0])
      return True  
    try:
      wlan_found=False
      print("Scanning WLANs")
      wlans=self.info.wlan_scan(False)
      for ssid, bssid, channel, rssi, authmode, hidden in sorted(wlans, key=lambda x: x[3], reverse=True):        
        ssid = ssid.decode('utf-8')
        if ssid==self.settings.wifi['ssid']:
          print("WLAN ssid: %s found at chan: %d rssi: %d bssid: %s" % (ssid, channel, rssi, bssid.hex('-')))
          wlan_found=True
      if not wlan_found:
        print("WLAN %s not found!" % self.settings.wifi['ssid'])
        return False
      print('Trying to connect...')
      start = time.ticks_ms()
      sta_if.connect(self.settings.wifi['ssid'],self.settings.wifi['key'])
      for _ in range(10000):
        if sta_if.isconnected():
          print('\nConnected! Time:  %d ms. Board IP: %s' % (time.ticks_diff(time.ticks_ms(), start), sta_if.ifconfig()[0]))
          self.wifi=sta_if
          return True
        else:
          print('.', end='')
          time.sleep_ms(100)
      print('\nConnection timeout!')
      sta_if.disconnect()
      sta_if.active(False)
      return False
    except OSError as e:
      print("\nWLAN connection problem. ", str(e)) 
      return False 
    

#--------------------------------------------------------------------
#
#    Settings save/load class for our board
#
#--------------------------------------------------------------------
class Mela_settings:
  def __init__(self):
    self.data=self.load_settings()
    
#********************************************************************
  @property
  def wifi(self):
    return self.data['settings']['wifi']

#********************************************************************
  def load_settings(self):
    import ujson as json
    
    try:
      with open('settings.json','r') as settings_file:
        return json.load(settings_file)
    except:
      print("Settings file read problem. Returning default configuration.")
      return {'settings': {'wifi': {'connect_on_boot': False, 'networks': [{'ssid': 'LAN', 'key': '12345'}]}}} 

#********************************************************************
  def save_settings(self):
    import ujson as json
    
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
    
#********************************************************************
  def df(self):
    s = os.statvfs('//')
    T=(s[1]*s[2])/1048576
    F=(s[0]*s[3])/1048576
    P = '{0:.2f}%'.format(F/T*100)
    return ('VFS: Total:{0} Mb Free:{1} Mb ({2})'.format(T,F,P))

#********************************************************************
  def free(self):
    gc.collect()
    F = gc.mem_free()
    A = gc.mem_alloc()
    T = F+A
    P = '{0:.2f}%'.format(F/T*100)
    return ('RAM: Total:{0} bytes Free:{1} bytes ({2})'.format(T,F,P))

#********************************************************************
  def wlan_scan(self, prn=True):
    import network
    try:
      sta_if=network.WLAN(network.STA_IF)
      sta_if.active(True)
      print("WLAN interface activated. Starting scan...")      
      wlans=sta_if.scan()
      if prn:
        AUTHMODE = {0: "open", 1: "WEP", 2: "WPA-PSK", 3: "WPA2-PSK", 4: "WPA/WPA2-PSK"}
        count=0
        for ssid, bssid, channel, rssi, authmode, hidden in sorted(wlans, key=lambda x: x[3], reverse=True):
          count=count+1
          ssid = ssid.decode('utf-8')      
          print("%d ssid: %s chan: %d rssi: %d authmode: %s bssid: %s" % (count, ssid, channel, rssi, AUTHMODE.get(authmode, '?'), bssid.hex('-')))
      else:
        return wlans
    except OSError as e:
      print("WLAN connection problem. ", str(e))

#********************************************************************        
  def wlan_status(self):
      import network
      try:
        sta_if=network.WLAN(network.STA_IF)
        sta_if.active(True)
        STATUS={1000: "STAT_IDLE", 1001: " STAT_CONNECTING", 202: "STAT_WRONG_PASSWORD", 201: "STAT_NO_AP_FOUND", 1010: "STAT_GOT_IP", 203: "STAT_ASSOC_FAIL", 200: "STAT_BEACON_TIMEOUT", 204: "STAT_HANDSHAKE_TIMEOUT"}
        PM_MODES={0: 'PM_NONE', 1: 'PM_PERFORMANCE', 2: 'PM_POWERSAVE'}
        print("Current WLAN status: %s, power mode: %s, TX power: %s, MAC %s, ssid: %s, ch: %s" % (STATUS.get(sta_if.status(), '?'), PM_MODES.get(sta_if.config('pm'), '?'),sta_if.config('txpower'),sta_if.config('mac').hex('-'),sta_if.config('ssid'),sta_if.config('channel')))
      except OSError as e:
        print("WLAN connection problem. ", str(e))
    