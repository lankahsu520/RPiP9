# -*- coding: utf-8 -*-
"""
 ***************************************************************************
 * Copyright (C) 2023, Lanka Hsu, <lankahsu@gmail.com>, et al.
 *
 * This software is licensed as described in the file COPYING, which
 * you should have received as part of this distribution.
 *
 * You may opt to use, copy, modify, merge, publish, distribute and/or sell
 * copies of the Software, and permit persons to whom the Software is
 * furnished to do so, under the terms of the COPYING file.
 *
 * This software is distributed on an "AS IS" basis, WITHOUT WARRANTY OF ANY
 * KIND, either express or implied.
 *
 ***************************************************************************
"""

from rpip9gpio import *
#from threadx_api import *
import threading
from _thread import start_new_thread

BCM_TRIGGER=5#29
BCM_ECHO=6#31

trigger = {"name": "trigger", "bcmid": BCM_TRIGGER, "control": rpip9gpio.CONTROL_NORMAL, "direction": GPIO.OUT, "val": GPIO.LOW, "reply": "echo", "ultrasonic_cond": None, "pause": 1}
echo = {"name": "echo", "bcmid": BCM_ECHO, "control": rpip9gpio.CONTROL_NORMAL, "direction": GPIO.IN, "val": GPIO.LOW, "distance": 0, "distance_last": [], "duration": 0, "s_time": 0, "e_time": 0, "add_event": 0}

ultrasonic_gpio = {"trigger": trigger, "echo": echo}

# 0: loop, 1: wait_for_edge, 2: event_detect
ULTRASONIC_EDGE_LOOP=0
ULTRASONIC_EDGE_WAIT=1
ULTRASONIC_EDGE_EVENT=2
ULTRASONIC_EDGE_DEFAULT=ULTRASONIC_EDGE_EVENT

class ultrasonic_ctx(rpip9gpio):
	def distance(self, gpioX):
		if (gpioX is not None):
			if (gpioX["e_time"]>0) and (gpioX["s_time"]>0):
				gpioX["duration"] = gpioX["e_time"] - gpioX["s_time"]
				if (self.average > 0):
					gpioX["distance_last"].append(gpioX["duration"]  * 340 *100 /2) #17150
					if ( len(gpioX["distance_last"]) > self.average ):
						gpioX["distance_last"].pop(0)
					gpioX["distance"] = averageX(gpioX["distance_last"])
				else:
					gpioX["distance"] = gpioX["duration"] * 17150

	def watch(self, gpioX):
		if (gpioX["e_time"]>0) and (gpioX["s_time"]>0):
			DBG_IF_LN(self, "(distance: {} cm)".format( gpioX["distance"] ))
		#print("(distance: {} cm)".format( gpioX["distance"] ) )

	def start_shout(self, gpioX):
		#self.linkGPIO()
		#DBG_IF_LN(self, "start")
		if (gpioX is not None):
			self.gpioSetLow(gpioX)
			sleep(self.hold_sec)
			self.gpioSetHigh(gpioX)
			sleep(self.shout_sec)
			self.gpioSetLow(gpioX)

	def echo_value_tick(self, gpioX, val):
		#self.linkGPIO()
		#DBG_TR_LN(self, start")
		if (gpioX is not None):
			count_down = self.echo_timeout
			while (self.gpioGetVal(gpioX) != val ) and (count_down > 0) and (self.is_quit == 0):
				count_down -= 1
				if (val == True):
					gpioX["s_time"] = time.time()
				else:
					gpioX["e_time"] = time.time()

	def echo_wait_edge(self, gpioX, val):
		#self.linkGPIO()
		#DBG_IF_LN(self, "start {}".format(gpioX["bcmid"]))
		if (gpioX is not None):
			count_down = self.edge_timeout
			if (val == True):
				channel = GPIO.wait_for_edge(gpioX["bcmid"], GPIO.RISING, timeout=count_down)
				if (channel is not None):
					gpioX["s_time"] = time.time()
			else:
				channel = GPIO.wait_for_edge(gpioX["bcmid"], GPIO.FALLING, timeout=count_down)
				if (channel is not None):
					gpioX["e_time"] = time.time()

	def echo_edge_detect_cb(self, bcmid):
		val = self.gpioGetValWithID(bcmid)
		#DBG_IF_LN(self, "(bcmid: {}, val: {})".format(bcmid, val))
		for key, gpioX in self.gpioXlist.items():
			if (gpioX["bcmid"] == bcmid ):
				if ( val ):
					gpioX["s_time"] = time.time()
				else:
					gpioX["e_time"] = time.time()
					self.wakeup(self.gpioX_trigger)

	def threadx_handler(self):
		gpioX_echo = self.gpioX_echo
		gpioX_trigger = self.gpioX_trigger
		if (gpioX_echo is not None):

			self.linkGPIO()
			DBG_IF_LN(self, "looping ... (use_edge: {}, {}: {}, {}: {})".format(self.use_edge, gpioX_trigger["name"], gpioX_trigger["bcmid"], gpioX_echo["name"], gpioX_echo["bcmid"]))
			if ( self.use_edge == ULTRASONIC_EDGE_EVENT):
				if (gpioX_echo["add_event"] == 0):
					gpioX_echo["add_event"] = 1
					DBG_IF_LN("call add_event_detect ...")
					GPIO.add_event_detect(gpioX_echo["bcmid"], GPIO.BOTH, callback=self.echo_edge_detect_cb)

			while (self.is_quit == 0):
				if (gpioX_trigger["pause"] == 1):
					self.gosleep(gpioX_trigger)
				else:
					gpioX_echo["s_time"] = 0
					gpioX_echo["e_time"] = 0
					self.start_shout(gpioX_trigger)

					if ( self.use_edge == ULTRASONIC_EDGE_LOOP):
						self.echo_value_tick(gpioX_echo, True)
						self.echo_value_tick(gpioX_echo, False)
					elif ( self.use_edge == ULTRASONIC_EDGE_WAIT):
						self.echo_wait_edge(gpioX_echo, True)
						self.echo_wait_edge(gpioX_echo, False)
					elif ( self.use_edge == ULTRASONIC_EDGE_EVENT):
						self.gosleep(gpioX_trigger)
					self.distance(gpioX_echo)
					self.watch(gpioX_echo)
				sleep(self.hold_sec)

	def wakeup(self, gpioX):
		gpioX["ultrasonic_cond"].acquire()
		#DBG_IF_LN(self, "notify ...")
		gpioX["ultrasonic_cond"].notify()
		gpioX["ultrasonic_cond"].release()

	def gosleep(self, gpioX):
		gpioX["ultrasonic_cond"].acquire()
		#DBG_IF_LN(self, "wait ...")
		gpioX["ultrasonic_cond"].wait()
		gpioX["ultrasonic_cond"].release()
		#DBG_IF_LN(self, "exit")

	def startx(self, key):
		gpioX = self.gpioXlist.get(key)
		if ( gpioX is not None ):
			DBG_WN_LN(self, "(pause: {}, use_edge: {})".format( gpioX["pause"], self.use_edge ))
			gpioX["pause"] = 0

			self.wakeup(gpioX)

	def pausex(self, key):
		gpioX = self.gpioXlist.get(key)
		if ( gpioX is not None ):
			DBG_WN_LN(self, "(pause: {}, use_edge: {})".format( gpioX["pause"], self.use_edge ))
			gpioX["pause"] = 1

	def switch(self, key):
		# 1: pause, 0: running
		gpioX = self.gpioXlist.get(key)
		if ( gpioX is not None ):
			if ( gpioX["pause"] == 1):
				self.startx(key)
			else:
				self.pausex(key)
			return gpioX["pause"]
		else:
			return 1

	def keyboard_recv(self):
		DBG_WN_LN(self, "press q to quit the loop (enter:start, space:pause) ...")
		k='\x00'
		while ( self.is_quit == 0 ):
			k = self.inkey()
			if k=='\x71': # q
				break;
			elif k=='\x0d': # enter
				self.startx("trigger")
			elif k=='\x20': # space
				self.pausex("trigger")
			elif k=='\x03':
				break;

	def release(self):
		self.is_quit = 1
		for key, gpioX in self.gpioXlist.items():
			if (gpioX["direction"] == GPIO.OUT ):
				self.wakeup(gpioX)

		if ( self.gpioXlnk == 1 ):
			for key, gpioX in self.gpioXlist.items():
				if (gpioX["direction"] == GPIO.IN ):
					GPIO.remove_event_detect(gpioX["bcmid"])
			GPIO.cleanup()

	def ctx_init(self, edge_mode):
		self.shout_sec = 0.00002
		self.echo_timeout = 5000
		self.edge_timeout = 1000
		self.average = 0
		self.use_edge = edge_mode

		self.gpioXlist = ultrasonic_gpio
		self.gpioX_trigger = self.gpioXlist.get("trigger")
		self.gpioX_echo = self.gpioXlist.get("echo")

		self.hold_sec = 0.01

		for key, gpioX in self.gpioXlist.items():
			#DBG_WR_LN(self, "(key: {})".format(key) )
			if (gpioX["direction"] == GPIO.OUT ):
				gpioX["ultrasonic_cond"] = threading.Condition()
				start_new_thread(self.threadx_handler, ())

		sleep(0.5)

	def __init__(self, edge_mode=ULTRASONIC_EDGE_DEFAULT, **kwargs):
		if ( isPYTHON(PYTHON_V3) ):
			super().__init__(**kwargs)
		else:
			super(ultrasonic_ctx, self).__init__(**kwargs)

		DBG_TR_LN(self, "{}".format(DBG_TXT_ENTER))
		self._kwargs = kwargs
		self.ctx_init(edge_mode)

#usonic_mgr = ultrasonic_ctx(edge_mode=ULTRASONIC_EDGE_DEFAULT)
#usonic_mgr.startx("trigger")
#usonic_mgr.keyboard_recv()
