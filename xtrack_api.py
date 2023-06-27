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

BCM_L2TRACK=24#5
BCM_L1TRACK=23#3
BCM_M0TRACK=18#1
BCM_R1TRACK=15#16
BCM_R2TRACK=14#15

l2track = {"name": "l2", "bcmid": BCM_L2TRACK, "control": rpip9gpio.CONTROL_NORMAL, "direction": GPIO.IN, "val": GPIO.LOW, "edge": rpip9gpio.EDGE_DEFAULT, "threading_pause": 1, "threading_handler": None, "threading_cond": None}
l1track = {"name": "l1", "bcmid": BCM_L1TRACK, "control": rpip9gpio.CONTROL_NORMAL, "direction": GPIO.IN, "val": GPIO.LOW, "edge": rpip9gpio.EDGE_DEFAULT, "threading_pause": 1, "threading_handler": None, "threading_cond": None}
m0track = {"name": "m0", "bcmid": BCM_M0TRACK, "control": rpip9gpio.CONTROL_NORMAL, "direction": GPIO.IN, "val": GPIO.LOW, "edge": rpip9gpio.EDGE_DEFAULT, "threading_pause": 1, "threading_handler": None, "threading_cond": None}
r1track = {"name": "r1", "bcmid": BCM_R1TRACK, "control": rpip9gpio.CONTROL_NORMAL, "direction": GPIO.IN, "val": GPIO.LOW, "edge": rpip9gpio.EDGE_DEFAULT, "threading_pause": 1, "threading_handler": None, "threading_cond": None}
r2track = {"name": "r2", "bcmid": BCM_R2TRACK, "control": rpip9gpio.CONTROL_NORMAL, "direction": GPIO.IN, "val": GPIO.LOW, "edge": rpip9gpio.EDGE_DEFAULT, "threading_pause": 1, "threading_handler": None, "threading_cond": None}

tracks_gpio_all = {"l2": l2track, "l1": l1track, "m0": m0track, "r1": r1track, "r2": r2track }
tracks_gpio_18 = {"m0": m0track}

class xtrack_ctx(rpip9gpio):

	def xtrack_start(self, key):
		gpioX = self.gpioXlist.get(key)
		if (gpioX is not None):
			self.threadx_run_loop(gpioX)

	def edge_busy(self, gpioX):
		if (gpioX is not None):
			val_org = gpioX["val"]
			gpioX["val"] = self.gpioGetVal(gpioX)
			if ( val_org != gpioX["val"] ):
				DBG_IF_LN(self, "({}: {}, bcmid: {})".format(gpioX["name"], gpioX["val"], gpioX["bcmid"]))
			else:
				pass
			sleep(self.hold_sec)

	def edge_wait(self, gpioX):
		#self.linkGPIO()
		#DBG_IF_LN(self, "start {}".format(gpioX["bcmid"]))
		if (gpioX is not None):
			count_down = self.edge_timeout

			channel = None
			if (gpioX["val"] == 0):
				channel = GPIO.wait_for_edge(gpioX["bcmid"], GPIO.RISING, timeout=count_down)
			else:
				channel = GPIO.wait_for_edge(gpioX["bcmid"], GPIO.FALLING, timeout=count_down)

			if (channel is not None):
				gpioX["val"] = self.gpioGetVal(gpioX)
				DBG_IF_LN(self, "(gpioX[{}/{}]: {})".format(gpioX["name"], gpioX["bcmid"], gpioX["val"]))

	def edge_detect_cb(self, bcmid):
		val = self.gpioGetValWithID(bcmid)
		for key, gpioX in self.gpioXlist.items():
			if (gpioX["bcmid"] == bcmid ):
				gpioX["val"] = val
				DBG_IF_LN(self, "(gpioX[{}/{}]: {})".format(gpioX["name"], gpioX["bcmid"], gpioX["val"]))

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
		if ("edge" in gpioX) and ( gpioX["edge"] == rpip9gpio.EDGE_BUSY):
			self.edge_busy(gpioX)
		elif ("edge" in gpioX) and ( gpioX["edge"] == rpip9gpio.EDGE_WAIT):
			self.edge_wait(gpioX)
		elif ("edge" in gpioX) and ( gpioX["edge"] == rpip9gpio.EDGE_EVENT):
			self.cond_sleep(gpioX)

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

	def ctx_init(self, tracks_gpio):
		self.gpioXlist = tracks_gpio

		self.edge_timeout = 1000

		self.hold_sec = 0.01

		for key, gpioX in self.gpioXlist.items():
			#DBG_WR_LN(self, "(key: {})".format(key) )
			if ("threading_handler" in gpioX) and (gpioX["threading_handler"] is None):
				gpioX["threading_cond"] = threading.Condition()
				gpioX["threading_handler"] = threading.Thread(target=self.threadx_handler, args = (gpioX, ))
				gpioX["threading_handler"].start()

		sleep(0.5)

	def __init__(self, tracks_gpio=tracks_gpio_all, **kwargs):
		if ( isPYTHON(PYTHON_V3) ):
			super().__init__(**kwargs)
		else:
			super(xtrack_ctx, self).__init__(**kwargs)

		DBG_TR_LN(self, "{}".format(DBG_TXT_ENTER))
		self._kwargs = kwargs
		self.ctx_init(tracks_gpio)

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

#xtrack_mgr = xtrack_ctx()
##xtrack_mgr.keyboard_recv()
#xtrack_mgr.xtrack_start("l1track")
#while True:
#	pass
