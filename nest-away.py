#! /usr/bin/python

# nest_away.py -- a python script to set a Nest Thermostat away based on
# Google Latitude location.
#
# by Timothy Lusk, darkcube@gmail.com
#

import urllib2
import sys
import ConfigParser
import time

# use the built-in if it's available (python 2.6), if not use the included library
try:
   import json
except ImportError:
    from lib import simplejson as json

from lib.geopy import distance
from lib.geopy import units
from lib.nestpy.nest import Nest
from lib.pushover import pushover

class Latitude:
    def __init__(self, key):
        self._key = key
        self._latitude = 0
        self._longitude = 0
        self._accuracy = 0
    
    def load(self):
        retry = 0
        while True:
            try:
                result = urllib2.urlopen("https://latitudebridge.appspot.com/lookup?key=" + self._key).read()
                result = json.loads(result)['data']
                
                self._latitude = result['latitude']
                self._longitude = result['longitude']
                self._accuracy = result['accuracy']
                
                return 0
            except:
                if( retry < 5 ):
                    time.sleep( 1 )
                    retry += 1
                else:
                    return -1
    
    def coordinates(self):
        return (self._latitude, self._longitude)
        
    def accuracy(self):
        return self._accuracy

def is_home( home_latitude, home_longitude, latitude_keys):
    
    for key in latitude_keys:
        location = Latitude(key)
        if( location.load() < 0 ):
            print "Error loading latitude location"
            sys.exit(-1)
        
        dist = distance.distance((home_latitude, home_longitude), location.coordinates()).meters
        dist = max( dist - location.accuracy(), 0 )
        if( units.miles( meters = dist ) < 1 ):
            return True            
    
    return False

def set_home( nest_username, nest_password, home ):

    try:
        nest = Nest(nest_username, nest_password)
        nest.login()
        nest.get_status()
    except:
        print "Error logging into home.nest.com"
        sys.exit(-1)
    
    if( home ):
        nest.set_away("home")
    else:
        nest.set_away("away")

def send_notification( pushover_app_token, pushover_user_token, home ):
    pushover_args = {}
    pushover_args['token'] = pushover_app_token
    pushover_args['user'] = pushover_user_token
    if( home ):
        pushover_args['message'] = "Welcome Home!"
    else:
        pushover_args['message'] = "Your thermostat is away."
    
    try:
        pushover.pushover( **pushover_args )
    except:
        print "Error sending pushover notification"

def main():
    
    try:
        config = ConfigParser.ConfigParser()
        config.read('/etc/nest-away/settings.config')
    
        nest_username = config.get('Settings', 'nest_username')
        nest_password = config.get('Settings', 'nest_password')
        home_latitude = config.getfloat('Settings', 'home_latitude')
        home_longitude = config.getfloat('Settings', 'home_longitude')
        latitude_keys = json.loads(config.get('Settings', 'latitude_keys'))
        pushover_enabled = config.getboolean('Settings', 'pushover_enabled')
        pushover_app_token = config.get('Settings', 'pushover_app_token')
        pushover_user_token = config.get('Settings', 'pushover_user_token')
        
        try:
            previously_home = config.getboolean('Cache', 'previously_home')
        except:
            previously_home = False
    except:
        print "Error parsing configuration file"
        sys.exit(-1)
    
    home = is_home( home_latitude, home_longitude, latitude_keys )
    set_home( nest_username, nest_password, home )
    
    if( pushover_enabled and ( previously_home != home ) ):
        send_notification( pushover_app_token, pushover_user_token, home )
    
    try:
        config.set('Cache', 'previously_home', home)
        with open('/etc/nest-away/settings.config', 'wb') as configfile:
            config.write(configfile)
    except:
        print "Error updating configuration file"

if __name__=="__main__":
   main()
