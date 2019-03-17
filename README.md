# GPS-based HUD for Tesla Model 3

## Introduction

This project creates a Head-Up Display in a car using data from a GPS receiver. It displays the current heading and speed and time based on GPS data. It is intended for use in cars that do not have an OBD2 port, like the Tesla Model 3.

Features:
* Shows blank screen when there is no GPS fix, so no incorrect information is displayed
* Adjusts time from the GPS signal, so does not need a real-time clock on the Pi
* Displays current heading, speed, speed unit, time and date

## Hardware
* [Raspberry Pi 3B+](https://smile.amazon.com/gp/product/B07BDR5PDW/)
* Sunlight-readable display, e.g. [Newhaven Display NHD-7.0-HDMI-N-RSXN-CTU](http://www.newhavendisplay.com/nhd70hdminrsxnctu-p-9552.html)
* [Adafruit Ultimate GPS HAT](https://smile.amazon.com/gp/product/B00S7FAJC4/)
* [External GPS antenna](https://smile.amazon.com/Waterproof-Active-Antenna-28dB-Gain/dp/B00LXRQY9A/)
* [SMA to uFL adapter cable](https://smile.amazon.com/SMA-u-FL-IPEX-Adapter-Cable/dp/B0769KKPYN/)
* [Beamsplitter mirror of the right dimensions to suit your setup](https://telepromptermirror.com/glass-teleprompter-mirror/)
* [3D printed mounts](https://www.thingiverse.com/thing:3496105) to place your monitor and mirror in the right place for driver's line-of-sight in the car
* HDMI cable long enough to go from the place you store the Pi to the monitor
* Compatible car power cable for the monitor you choose (I used [this one](https://smile.amazon.com/gp/product/B07BSFSW8N/))
* 5V, 2A car power cable for the Pi

## Software
* [Raspbian Stretch Lite](https://downloads.raspberrypi.org/raspbian_lite_latest)
* Code used from [this project](https://github.com/rnorris/gpsd/blob/master/xgpsspeed)
* [unclutter](https://wiki.archlinux.org/index.php/unclutter)
* [gpsd](http://www.catb.org/gpsd/)
* Python packages: [astral](https://pypi.org/project/astral/), [GTK+ 3.0](https://python-gtk-3-tutorial.readthedocs.io/en/latest/), [pycairo](https://pycairo.readthedocs.io/en/latest/), [gps](https://pypi.org/project/gps/)

## Instructions

TODO

## [Pictures](https://imgur.com/a/LB97YwX)

**Car parked in daylight, driver's view**
![https://i.imgur.com/RM7JgaY.jpg](Parked in daylight)

**Side view of 3D-printed mounts on the Tesla Model 3**
![https://i.imgur.com/68HfFuC.jpg?1](Side view)
