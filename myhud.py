#!/usr/bin/env python
#
# by
# Pavan Pamidimarri

from __future__ import absolute_import, print_function, division

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject
import gps, os, time
from socket import error as SocketError
from datetime import datetime
from astral import Astral, Location

class Handler:
	def onDestroy(self, *args):
		Gtk.main_quit()

class HeadUpDisplay(Gtk.Window):
	def __init__(self, speed_unit=None):
		GObject.GObject.__init__(self)
		self.MPH_UNIT_LABEL = 'mph'
		self.KPH_UNIT_LABEL = 'kmh'
		self.KNOTS_UNIT_LABEL = 'knots'
		self.conversions = {
			self.MPH_UNIT_LABEL: gps.MPS_TO_MPH,
			self.KPH_UNIT_LABEL: gps.MPS_TO_KPH,
			self.KNOTS_UNIT_LABEL: gps.MPS_TO_KNOTS
		}
		self.speed_unit = speed_unit or self.MPH_UNIT_LABEL
		if self.speed_unit not in self.conversions:
			raise TypeError(
				'%s is not a valid speed unit'
				% (repr(speed_unit))
 			)
		self.last_speed = 0
		self.last_heading = 0
		self.last_mode = 0
		self.latitude = None
		self.longitude = None

		self.font_face = 'Gotham'
		self.now_fmt = '%-I:%M %p'
		self.date_fmt = '%a, %b %-d'
		self.heading_markup = "<span font='28' face='" + self.font_face + "' color='%s'>%s</span>"
		self.speed_markup = "<span font='140' face='" + self.font_face + "' color='%s' font_features='tnum=1,lnum=1'>%s</span>"
		self.unit_markup = "<span font='14' face='" + self.font_face + "' color='%s'><b>%s</b></span>"
		self.today_markup = "<span font='17.5' face='" + self.font_face + "' color='%s' font_features='tnum=1,lnum=1'>%s</span>"
		self.now_markup = "<span font='21' face='" + self.font_face + "' weight='bold' color='%s' font_features='tnum=1,lnum=1'>%s</span>"
		self.thick_blank_markup = "<span font='12' color='#000000'> </span>"
		self.thin_blank_markup = "<span font='2' color='#000000'> </span>"

		self.builder = Gtk.Builder()
		self.builder.add_from_file("/home/pi/gpshud/gpshud.glade")
		self.builder.connect_signals(Handler())
		self.builder.get_object("window1").override_background_color(
			Gtk.StateType.NORMAL, Gdk.RGBA(0,0,0,1))

		self.builder.get_object("TopBlank").set_markup(self.thin_blank_markup)
		self.builder.get_object("Blank1").set_markup(self.thin_blank_markup)
		self.builder.get_object("Blank2").set_markup(self.thick_blank_markup)
		self.builder.get_object("Blank3").set_markup(self.thick_blank_markup)
		self.builder.get_object("BottomBlank").set_markup(self.thin_blank_markup)
		self.update_data()

	def update_data(self):
		color = '#000000'
		unitcolor = '#000000'
		if self.last_mode == 0 or self.last_mode == 1:
			color = '#000000'
			unitcolor = '#000000'
		elif self.is_day():
			color = '#FFFFFF'
			unitcolor = '#888888'
		else:
			color = '#BBBBBB'
			unitcolor = '#666666'

		self.builder.get_object("Heading").set_markup(self.heading_markup % (
			color, self.get_direction_text(self.last_heading)))
		self.builder.get_object("Speed").set_markup(self.speed_markup % (
			color, self.get_speed_text(self.last_speed)))
		self.builder.get_object("Unit").set_markup(self.unit_markup % (
			unitcolor, self.speed_unit.upper()))
		now = datetime.now()
		self.builder.get_object("Date").set_markup(self.today_markup % (
			color, now.strftime(self.date_fmt)))
		self.builder.get_object("Time").set_markup(self.now_markup % (
			color, now.strftime(self.now_fmt)))
		return True

	def get_speed_text(self, speed):
		if self.last_mode == 0 or self.last_mode == 1:
			return "-"
		else:
			return '%.0f' % (speed * self.conversions.get(self.speed_unit))

	def get_direction_text(self, heading):
		direction = ''
		if self.last_mode == 0 or self.last_mode == 1:
			direction = '-'
		elif (heading >= 22.5) and (heading < 67.5):
			direction = 'NE'
		elif (heading >= 67.5) and (heading < 112.5):
			direction = 'E'
		elif (heading >= 112.5) and (heading < 157.5):
			direction = 'SE'
		elif (heading >= 157.5) and (heading < 202.5):
			direction = 'S'
		elif (heading >= 202.5) and (heading < 247.5):
			direction = 'SW'
		elif (heading >= 247.5) and (heading < 292.5):
			direction = 'W'
		elif (heading >= 292.5) and (heading < 337.5):
			direction = 'NW'
		else:
			direction = 'N'
		return direction

	def is_day(self):
		l = Location()
		l.latitude = self.latitude
		l.longitude = self.longitude
		current_time = datetime.now(l.tzinfo)
		if (l.sunset() > current_time) and (l.sunrise() < current_time):
			return True
		else:
			return False

class Main(object):
	def __init__(self, host='localhost', port=gps.GPSD_PORT, device=None,
		debug=0, speed_unit=None):
		self.host = host
		self.port = port
		self.device = device
		self.debug = debug
		self.speed_unit = speed_unit
		self.date_set = False

		self.widget = HeadUpDisplay(speed_unit=self.speed_unit)
		self.window = self.widget.builder.get_object("window1")
		self.window.connect('delete_event', self.delete_event)
		self.window.connect('destroy', self.destroy)
		self.window.fullscreen()
		self.window.show_all()

	def watch(self, daemon, device):
		self.daemon = daemon
		self.device = device
		GObject.io_add_watch(daemon.sock, GObject.IO_IN, self.handle_response)
		GObject.io_add_watch(daemon.sock, GObject.IO_ERR, self.handle_hangup)
		GObject.io_add_watch(daemon.sock, GObject.IO_HUP, self.handle_hangup)
		return True

	def handle_response(self, source, condition):
		if self.daemon.read() == -1:
			self.handle_hangup(source, condition)
		if self.daemon.data['class'] == 'TPV':
			self.update_speed(self.daemon.data)
		return True

	def handle_hangup(self, _dummy, _unused):
		w = Gtk.MessageDialog(
			parent=self.window,
			type=Gtk.MessageType.ERROR,
			flags=Gtk.DialogFlags.DESTROY_WITH_PARENT,
			buttons=Gtk.ButtonsType.OK
		)
		w.connect("destroy", lambda unused: Gtk.main_quit())
		w.set_title('GPSD Error')
		w.set_markup("GPSD has stopped sending data.")
		w.run()
		Gtk.main_quit()
		return True

	def update_speed(self, data):
		self.widget.last_mode = data['mode']
		if  data['mode'] == 0 or data['mode'] == 1:
			self.renew_GPS()
		elif self.date_set == False:
			self.set_date()
		if hasattr(data, 'speed'):
			self.widget.last_speed = data.speed
		if hasattr(data, 'track'):
			self.widget.last_heading = data.track
		if hasattr(data, 'lat'):
			self.widget.latitude = data.lat
		if hasattr(data, 'lon'):
			self.widget.longitude = data.lon
		self.widget.update_data()

	def set_date(self):
		if self.daemon.utc != None and self.daemon.utc != '':
			gpsutc = self.daemon.utc[0:4] + self.daemon.utc[5:7] + self.daemon.utc[8:10] + ' ' + self.daemon.utc[11:19]
			ret_val = os.system('sudo date -u --set="%s"' % gpsutc)
			if ret_val == 0:
				self.date_set = True
			else:
				self.date_set = False
		else:
			self.date_set = False

	def renew_GPS(self):
		del self.daemon
		try:
			daemon = gps.gps(
				host=self.host,
				port=self.port,
				mode=gps.WATCH_ENABLE | gps.WATCH_JSON | gps.WATCH_SCALED,
				verbose=self.debug
			)
			self.watch(daemon, self.device)
		except SocketError:
			w = Gtk.MessageDialog(
				parent=self.window,
				type=Gtk.MessageType.ERROR,
				flags=Gtk.DialogFlags.DESTROY_WITH_PARENT,
				buttons=Gtk.ButtonsType.OK
			)
			w.set_title('Socket Error')
			w.set_markup(
				"Failed to connect to gpsd socket. Make sure that gpsd is running."
			)
			w.run()
			w.destroy()
		except KeyboardInterrupt:
			print("Keyboard interrupt")
			self.window.emit('delete_event', Gdk.Event(Gdk.NOTHING))
			w.run()
			w.destroy()

	def delete_event(self, _widget, _event, _data=None):
		return False

	def destroy(self, _unused, _empty=None):
		Gtk.main_quit()

	def run(self):
		try:
			daemon = gps.gps(
				host=self.host,
				port=self.port,
				mode=gps.WATCH_ENABLE | gps.WATCH_JSON | gps.WATCH_SCALED,
				verbose=self.debug
			)
			cover = Gtk.Window()
			cover.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(0,0,0,1))
			cover.fullscreen()
			cover.show()
			while True:
				data = daemon.next()
				if (data['class'] == 'TPV'):
					if data['mode'] == 0 or data['mode'] == 1:
						# wait a second...
						time.sleep(1)
					else:
						# signal acquired, good to go
						break
				else:
					# wait a second...
					time.sleep(1)
			cover.destroy()
			del cover
			self.watch(daemon, self.device)
			Gtk.main()
		except SocketError:
			w = Gtk.MessageDialog(
				parent=self.window,
				type=Gtk.MessageType.ERROR,
				flags=Gtk.DialogFlags.DESTROY_WITH_PARENT,
				buttons=Gtk.ButtonsType.OK
			)
			w.set_title('Socket Error')
			w.set_markup(
				"Failed to connect to gpsd socket. Make sure that gpsd is running."
			)
			w.run()
			w.destroy()
		except KeyboardInterrupt:
			print("Keyboard interrupt")
			self.window.emit('delete_event', Gdk.Event(Gdk.NOTHING))
			w.run()
			w.destroy()

if __name__ == '__main__':
	Main(
		host='localhost',
		port=gps.GPSD_PORT,
		device=None,
		speed_unit='mph',
		debug=0
	).run()
