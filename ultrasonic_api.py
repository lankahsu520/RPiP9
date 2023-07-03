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
#from _thread import start_new_thread

BCM_TRIGGER=5#29
BCM_ECHO=6#31

trigger = {"name": "trigger", "bcmid": BCM_TRIGGER, "control": rpip9gpio.CONTROL_NORMAL, "direction": GPIO.OUT, "val": GPIO.LOW, "threading_pause": 1, "threading_handler": None, "threading_cond": None, "threading_pause": 1}
echo = {"name": "echo", "bcmid": BCM_ECHO, "control": rpip9gpio.CONTROL_NORMAL, "direction": GPIO.IN, "val": GPIO.LOW, "edge": rpip9gpio.EDGE_DEFAULT, "distance": 0, "distance_last": [], "duration": 0, "s_time": 0, "e_time": 0}

ultrasonic_gpio = {"trigger": trigger, "echo": echo}

class ultrasonic_ctx(rpip9gpio):

	def watch(self, gpioX):
		if (gpioX["e_time"]>0) and (gpioX["s_time"]>0):
			DBG_IF_LN(self, "(distance: {} cm)".format( gpioX["distance"] ))
		#print("(distance: {} cm)".format( gpioX["distance"] ) )

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

	def start_shout(self, gpioX_trigger):
		#self.linkGPIO()
		if (gpioX_trigger is not None):
			DBG_TR_LN(self, "shout !!! {}".format(gpioX_trigger))
			self.gpioSetLow(gpioX_trigger)
			sleep(self.hold_sec)
			self.gpioSetHigh(gpioX_trigger)
			sleep(self.shout_sec)
			self.gpioSetLow(gpioX_trigger)

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

	def edge_wait(self, gpioX, val):
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

	def edge_detect_cb(self, bcmid):
		val = self.gpioGetValWithID(bcmid)
		#DBG_IF_LN(self, "(bcmid: {}, val: {})".format(bcmid, val))
		for key, gpioX in self.gpioXlist.items():
			if (gpioX["bcmid"] == bcmid ):
				if ( val ):
					gpioX["s_time"] = time.time()
				else:
					gpioX["e_time"] = time.time()
					self.cond_wakeup(self.gpioX_trigger)

	def threadx_pause(self, gpioX):
		#gpioX = self.gpioXlist.get(key)
		if (gpioX is not None) and ("threading_pause" in gpioX):
			gpioX["threading_pause"] = 1

	def threadx_pause_all(self):
		for key, gpioX in self.gpioXlist.items():
			if ("threading_handler" in gpioX) and (gpioX["threading_handler"] is not None):
				self.threadx_pause(gpioX)

	def threadx_run_loop(self, gpioX):
		#gpioX = self.gpioXlist.get(key)
		if (gpioX is not None) and ("threading_pause" in gpioX):
			gpioX["threading_pause"] = 0
			DBG_WN_LN(self, "run in loop ... (gpioX[{}/{}]: {})".format( gpioX["name"], gpioX["bcmid"], gpioX["val"]) )
			self.cond_wakeup(gpioX)

	def threadx_run_all(self):
		for key, gpioX in self.gpioXlist.items():
			if ("threading_handler" in gpioX) and (gpioX["threading_handler"] is not None):
				self.threadx_run_loop(gpioX)

	def threadx_tick(self, gpioX_trigger, gpioX_echo):
		gpioX_echo["s_time"] = 0
		gpioX_echo["e_time"] = 0
		self.start_shout(gpioX_trigger)

		if ("edge" in gpioX_echo) and ( gpioX_echo["edge"] == rpip9gpio.EDGE_BUSY):
			self.echo_value_tick(gpioX_echo, True)
			self.echo_value_tick(gpioX_echo, False)
		elif ("edge" in gpioX_echo) and ( gpioX_echo["edge"] == rpip9gpio.EDGE_WAIT):
			self.edge_wait(gpioX_echo, True)
			self.edge_wait(gpioX_echo, False)
		elif ("edge" in gpioX_echo) and ( gpioX_echo["edge"] == rpip9gpio.EDGE_EVENT):
			self.cond_sleep(gpioX_trigger)
		self.distance(gpioX_echo)
		self.watch(gpioX_echo)

	def threadx_handler(self, gpioX_trigger, gpioX_echo):
		DBG_WN_LN(self, "looping ... ({}: {}, bcmid:{}, {}: {}, bcmid:{}, edge: {})".format(gpioX_trigger["name"], gpioX_trigger["val"], gpioX_trigger["bcmid"], gpioX_echo["name"], gpioX_echo["val"], gpioX_echo["bcmid"], self.stredge(gpioX_echo["edge"])))
		if (gpioX_trigger is not None) and (gpioX_echo is not None):
			while (self.is_quit == 0):
				if ("threading_pause" in gpioX_trigger) and (gpioX_trigger["threading_pause"] == 1):
					self.cond_sleep(gpioX_trigger)
				else:
					self.threadx_tick(gpioX_trigger, gpioX_echo)
				#sleep(self.hold_sec)
		DBG_WN_LN(self, "{} ({}: {}, bcmid:{}, {}: {}, bcmid:{})".format(DBG_TXT_BYE_BYE, gpioX_trigger["name"], gpioX_trigger["bcmid"], gpioX_trigger["val"], gpioX_echo["name"], gpioX_echo["val"], gpioX_echo["bcmid"]))

	def cond_wakeup(self, gpioX):
		if ("threading_cond" in gpioX) and (gpioX["threading_cond"] is not None):
			gpioX["threading_cond"].acquire()
			#DBG_IF_LN(self, "notify ...")
			gpioX["threading_cond"].notify()
			gpioX["threading_cond"].release()

	def cond_wait(self, gpioX, timeout):
		if ("threading_cond" in gpioX) and (gpioX["threading_cond"] is not None):
			gpioX["threading_cond"].acquire()
			DBG_WN_LN(self, "wait ... (gpioX[{}/{}]: {})".format(gpioX["name"], gpioX["bcmid"], gpioX["val"]))
			gpioX["threading_cond"].wait(timeout)
			gpioX["threading_cond"].release()
			#DBG_IF_LN(self, "exit")

	def cond_sleep(self, gpioX):
		if ("threading_cond" in gpioX) and (gpioX["threading_cond"] is not None):
			gpioX["threading_cond"].acquire()
			DBG_WN_LN(self, "wait ... (gpioX[{}/{}]: {})".format(gpioX["name"], gpioX["bcmid"], gpioX["val"]))
			gpioX["threading_cond"].wait()
			gpioX["threading_cond"].release()
			#DBG_IF_LN(self, "exit")

	def keyboard_recv(self):
		DBG_WN_LN(self, "press q to quit the loop (enter: start, space: pause) ...")
		k='\x00'
		while ( self.is_quit == 0 ):
			k = self.inkey()
			self.threadx_pause_all()
			if k=='\x71': # q
				break;
			elif k=='\x0d': # enter
				self.threadx_run_all()
			elif k=='\x20': # space
				self.threadx_pause_all()
			elif k=='\x03':
				break;

	def release(self):
		DBG_IF_LN("(is_quit: {}, gpioXlnk: {})".format(self.is_quit, self.gpioXlnk ))
		if ( self.is_quit == 0 ):
			self.is_quit = 1
			for key, gpioX in self.gpioXlist.items():
				if ("threading_handler" in gpioX) and (gpioX["threading_handler"] is not None):
					self.cond_wakeup(gpioX)
					gpioX["threading_handler"].join()

			if ( self.gpioXlnk == 1 ):
				for key, gpioX in self.gpioXlist.items():
					if ("edge" in gpioX) and (gpioX["edge"] == rpip9gpio.EDGE_EVENT):
						GPIO.remove_event_detect(gpioX["bcmid"])

				DBG_WN_LN("call GPIO.cleanup ...")
				GPIO.cleanup()

	def ctx_init(self, gpioXlist, edge_mode):
		self.gpioXlist = gpioXlist
		self.gpioX_trigger = self.gpioXlist.get("trigger")
		self.gpioX_echo = self.gpioXlist.get("echo")

		self.shout_sec = 0.00002
		self.echo_timeout = 5000
		self.edge_timeout = 1000
		self.average = 0
		self.gpioX_echo["edge"] = edge_mode

		self.hold_sec = 0.01

		for key, gpioX in self.gpioXlist.items():
			#DBG_WR_LN(self, "(key: {})".format(key) )
			if ("threading_handler" in gpioX) and (gpioX["threading_handler"] is None):
				gpioX["threading_cond"] = threading.Condition()
				gpioX["threading_handler"] = threading.Thread(target=self.threadx_handler, args = (gpioX, self.gpioX_echo))
				gpioX["threading_handler"].start()

		sleep(0.5)

	def __init__(self, gpioXlist=ultrasonic_gpio, edge_mode=rpip9gpio.EDGE_DEFAULT, **kwargs):
		if ( isPYTHON(PYTHON_V3) ):
			super().__init__(**kwargs)
		else:
			super(ultrasonic_ctx, self).__init__(**kwargs)

		DBG_TR_LN(self, "{}".format(DBG_TXT_ENTER))
		self._kwargs = kwargs
		self.ctx_init(gpioXlist, edge_mode)

	def parse_args(self, args):
		self._args = args
		self.keyboard = args["keyboard"]
		DBG_TR_LN("(keyboard: {})".format( self.keyboard ));

	def start(self, args={"keyboard": 0}):
		self.linkGPIO()
		self.parse_args(args)

		for key, gpioX in self.gpioXlist.items():
			if ("edge" in gpioX) and (gpioX["edge"] == rpip9gpio.EDGE_EVENT):
				DBG_IF_LN("call add_event_detect .. (gpioX[{}/{}]: {}).".format(gpioX["name"], gpioX["bcmid"], gpioX["val"]))
				GPIO.add_event_detect(gpioX["bcmid"], GPIO.BOTH, callback=self.edge_detect_cb)

		if (self.keyboard==1):
			self.keyboard_recv()

#usonic_mgr = ultrasonic_ctx(edge_mode=ULTRASONIC_EDGE_DEFAULT)
#usonic_mgr.startx("trigger")
#usonic_mgr.keyboard_recv()
