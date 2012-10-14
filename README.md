Nest Away
=====

A Python script to set a Nest Thermostat away automatically based on Google Latitude location.  One or more latitude devices can be tracked.

## Install

Create a settings file at /etc/nest-away/settings.config and setup a cron job to run the nest_away.py script at a frequent interval (5min - 10min).

## Other

You will need to integrate your google latitude account with [Google Latitude Bridge] in order to get location updates.  You can also get optional [Pushover] notifications when a switch between away and home occurs.

Libraries Used:

* [pynest][pynest]
* [geopy][geopy]
* [simplejson][simplejson]
* [pushover][pushover]

[pynest]: https://github.com/RandyLevensalor/pynest
[geopy]: http://code.google.com/p/geopy
[simplejson]: http://code.google.com/p/simplejson
[pushover]: https://github.com/pix0r/pushover
[Google Latitude Bridge]: https://latitudebridge.appspot.com
[Pushover]: https://pushover.net/
