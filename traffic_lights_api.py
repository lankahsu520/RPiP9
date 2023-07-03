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

BCM_R=17#0
BCM_Y=27#2
BCM_G=22#3
lightR = {"name": "R", "bcmid": BCM_R, "control": rpip9gpio.CONTROL_NORMAL, "direction": GPIO.OUT, "val": GPIO.LOW, "delay": 3, "threading_pause": 1, "threading_handler": None, "threading_cond": None}
lightY = {"name": "Y", "bcmid": BCM_Y, "control": rpip9gpio.CONTROL_NORMAL, "direction": GPIO.OUT, "val": GPIO.LOW, "delay": 1}
lightG = {"name": "G", "bcmid": BCM_G, "control": rpip9gpio.CONTROL_NORMAL, "direction": GPIO.OUT, "val": GPIO.LOW, "delay": 5}

traffic_lights_gpio_all= {"R": lightR, "Y": lightY, "G": lightG }

class traffic_lights_ctx(rpip9gpio):

	def lightX_helper(self, gpioX, val):
		if (gpioX is not None):
			self.gpioSetHelper(gpioX, val)
			DBG_IF_LN(self, "(gpioX[{}/{}]: {})".format(gpioX["name"], gpioX["bcmid"], gpioX["val"]))

	def lightX_on(self, gpioX):
		if (gpioX is not None):
			self.lightX_helper(gpioX, 1)

	def lightX_off(self, gpioX):
		if (gpioX is not None):
			self.lightX_helper(gpioX, 0)

	def light_on(self, key):
		gpioX = self.gpioXlist.get(key)
		if (gpioX is not None):
			self.lightX_helper(gpioX, 1)

	def light_off(self, key):
		gpioX = self.gpioXlist.get(key)
		if (gpioX is not None):
			self.lightX_helper(gpioX, 0)

	def light_all_on(self):
		for key, gpioX in self.gpioXlist.items():
			self.lightX_helper(gpioX, 1)

	def light_all_off(self):
		for key, gpioX in self.gpioXlist.items():
			self.lightX_helper(gpioX, 0)

	def traffic_light_start(self, key):
		gpioX = self.gpioXlist.get(key)
		if (gpioX is not None):
			self.threadx_run_loop(gpioX)

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

	def threadx_tick(self, gpioX):
		self.lightX_on(self.gpioX_r)
		#sleep(self.gpioX_r["delay"])
		self.cond_wait(gpioX, self.gpioX_r["delay"])
		if ( self.is_quit == 1 ):
			return 1

		self.lightX_off(self.gpioX_r)
		self.lightX_on(self.gpioX_y)
		#sleep(self.gpioX_y["delay"])
		self.cond_wait(gpioX, self.gpioX_y["delay"])
		if ( self.is_quit == 1 ):
			return 1

		self.lightX_off(self.gpioX_y)
		self.lightX_on(self.gpioX_g)
		#sleep(self.gpioX_g["delay"])
		self.cond_wait(gpioX, self.gpioX_g["delay"])
		if ( self.is_quit == 1 ):
			return 1

		self.lightX_off(self.gpioX_g)
		self.lightX_on(self.gpioX_y)
		#sleep(self.gpioX_y["delay"])
		self.cond_wait(gpioX, self.gpioX_y["delay"])

		self.lightX_off(self.gpioX_y)
		if ( self.is_quit == 1 ):
			return 1

	def threadx_handler(self, gpioX):
		DBG_WN_LN(self, "looping ... (gpioX[{}/{}]: {})".format(gpioX["name"], gpioX["bcmid"], gpioX["val"]))
		if (gpioX is not None):
			while (self.is_quit == 0):
				if ("threading_pause" in gpioX) and (gpioX["threading_pause"] == 1):
					self.cond_sleep(gpioX)
				else:
					self.threadx_tick(gpioX)
				#sleep(self.hold_sec)
		DBG_WN_LN(self, "{} (gpioX[{}/{}]: {})".format(DBG_TXT_BYE_BYE, gpioX["name"], gpioX["bcmid"], gpioX["val"]))

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
		DBG_WN_LN(self, "press q to quit the loop (enter: start, space: pause, a: all on, r: Red on, y: Yellow on, g: Green on) ...")
		k='\x00'
		while ( self.is_quit == 0 ):
			k = self.inkey()
			self.threadx_pause_all()
			self.light_all_off()
			#DBG_WN_LN(self, ">>>>>>>> {}".format(k))
			if k=='\x71': # q
				break;
			elif k=='\x61': # a
				self.light_all_on()
			elif k=='\x72': # r
				self.light_on("R")
			elif k=='\x79': # y
				self.light_on("Y")
			elif k=='\x67': # g
				self.light_on("G")
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

	def ctx_init(self, gpioXlist):
		self.gpioXlist = gpioXlist
		self.gpioX_r = self.gpioXlist.get("R")
		self.gpioX_y = self.gpioXlist.get("Y")
		self.gpioX_g = self.gpioXlist.get("G")

		self.hold_sec = 0.01

		for key, gpioX in self.gpioXlist.items():
			#DBG_WR_LN(self, "(key: {})".format(key) )
			if ("threading_handler" in gpioX) and (gpioX["threading_handler"] is None):
				gpioX["threading_cond"] = threading.Condition()
				gpioX["threading_handler"] = threading.Thread(target=self.threadx_handler, args = (gpioX, ))
				gpioX["threading_handler"].start()

		sleep(0.5)

	def __init__(self, gpioXlist=traffic_lights_gpio_all, **kwargs):
		if ( isPYTHON(PYTHON_V3) ):
			super().__init__(**kwargs)
		else:
			super(traffic_lights_ctx, self).__init__(**kwargs)

		DBG_TR_LN(self, "{}".format(DBG_TXT_ENTER))
		self._kwargs = kwargs
		self.ctx_init(gpioXlist)

	def parse_args(self, args):
		self._args = args
		self.keyboard = args["keyboard"]
		DBG_TR_LN("(keyboard: {})".format( self.keyboard ));

	def start(self, args={"keyboard": 0}):
		self.linkGPIO()
		self.parse_args(args)

		for key, gpioX in self.gpioXlist.items():
			if  (gpioX["direction"] ==  GPIO.IN) and ("edge" in gpioX) and (gpioX["edge"] == rpip9gpio.EDGE_EVENT):
				DBG_IF_LN("call add_event_detect .. (gpioX[{}/{}]: {}).".format(gpioX["name"], gpioX["bcmid"], gpioX["val"]))
				GPIO.add_event_detect(gpioX["bcmid"], GPIO.BOTH, callback=self.edge_detect_cb)

		if (self.keyboard==1):
			self.keyboard_recv()
