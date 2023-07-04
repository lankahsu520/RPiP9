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

import board
import adafruit_dht

DHT_BOARD4=board.D4
DHT_BOARD18=board.D18

dht11 = {"name": "dht11", "type": "dht11", "bcmid": DHT_BOARD4, "dhtX": None, "val": GPIO.LOW, "delay": 3, "threading_pause": 1, "threading_handler": None, "threading_cond": None}
dht22 = {"name": "dht22", "type": "dht22", "bcmid": DHT_BOARD18, "dhtX": None, "val": GPIO.LOW, "delay": 3, "threading_pause": 1, "threading_handler": None, "threading_cond": None}

dht_gpio_all = {"dht11": dht11}

class dhtx_ctx(rpip9gpio):

	def dhtx_temperature(self, gpioX):
		if (gpioX is not None) and (gpioX["dhtX"] is not None):
			gpioX["temperature_c"] = gpioX["dhtX"].temperature
			gpioX["temperature_f"] = gpioX["temperature_c"] * (9 / 5) + 32

	def dhtx_humidity(self, gpioX):
		if (gpioX is not None):
			gpioX["humidity"] = gpioX["dhtX"].humidity

	def dhtx_lookup(self, gpioX):
		if (gpioX is not None):
			try:
				self.dhtx_temperature(gpioX)
				self.dhtx_humidity(gpioX)
			except RuntimeError as error:
				DBG_ER_LN(self, "{}".format( error.args[0] ))

	def dhtx_start(self, key):
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
		if (gpioX is not None):
			self.dhtx_lookup(gpioX)
			DBG_IF_LN(self, "(gpioX[{}/{}], Temperature: {:.1f} F / {:.1f} C, Humidity: {}%)".format( gpioX["name"], gpioX["bcmid"], gpioX["temperature_c"], gpioX["temperature_f"], gpioX["humidity"]) )
			self.cond_wait(gpioX, gpioX["delay"])

	def threadx_handler(self, gpioX):
		DBG_WN_LN(self, "looping ... (gpioX[{}/{}]: {})".format(gpioX["name"], gpioX["bcmid"], gpioX["val"]))
		if (gpioX is not None):
			if ("type" in gpioX):
				if (gpioX["type"] == "dht22" ):
					gpioX["dhtX"] = adafruit_dht.DHT22( gpioX["bcmid"] )
				else:
					gpioX["dhtX"] = adafruit_dht.DHT11( gpioX["bcmid"] )
			gpioX["temperature_c"] = 0
			gpioX["temperature_f"] = gpioX["temperature_c"] * (9 / 5) + 32
			gpioX["humidity"] = 0
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
			DBG_DB_LN(self, "wait ... (gpioX[{}/{}]: {})".format(gpioX["name"], gpioX["bcmid"], gpioX["val"]))
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
					if ("dhtX" in gpioX) and (gpioX["dhtX"] is not None):
						gpioX["dhtX"].exit()

			if ( self.gpioXlnk == 1 ):
				for key, gpioX in self.gpioXlist.items():
					if ("edge" in gpioX) and (gpioX["edge"] == rpip9gpio.EDGE_EVENT):
						GPIO.remove_event_detect(gpioX["bcmid"])

				DBG_WN_LN("call GPIO.cleanup ...")
				GPIO.cleanup()

	def ctx_init(self, gpioXlist):
		self.gpioXlist = gpioXlist

		self.hold_sec = 0.01

		for key, gpioX in self.gpioXlist.items():
			#DBG_WR_LN(self, "(key: {})".format(key) )
			if ("threading_handler" in gpioX) and (gpioX["threading_handler"] is None):
				gpioX["threading_cond"] = threading.Condition()
				gpioX["threading_handler"] = threading.Thread(target=self.threadx_handler, args = (gpioX, ))
				gpioX["threading_handler"].start()

		sleep(0.5)

	def __init__(self, gpioXlist=dht_gpio_all, **kwargs):
		if ( isPYTHON(PYTHON_V3) ):
			super().__init__(**kwargs)
		else:
			super(dhtx_ctx, self).__init__(**kwargs)

		DBG_TR_LN(self, "{}".format(DBG_TXT_ENTER))
		self._kwargs = kwargs
		self.ctx_init(gpioXlist)

	def parse_args(self, args):
		self._args = args
		self.keyboard = args["keyboard"]
		DBG_TR_LN("(keyboard: {})".format( self.keyboard ));

	def start(self, args={"keyboard": 0}):
		#self.linkGPIO()
		self.parse_args(args)

		for key, gpioX in self.gpioXlist.items():
			if  ("direction" in gpioX) and (gpioX["direction"] ==  GPIO.IN) and ("edge" in gpioX) and (gpioX["edge"] == rpip9gpio.EDGE_EVENT):
				DBG_IF_LN("call add_event_detect .. (gpioX[{}/{}]: {}).".format(gpioX["name"], gpioX["bcmid"], gpioX["val"]))
				GPIO.add_event_detect(gpioX["bcmid"], GPIO.BOTH, callback=self.edge_detect_cb)

		if (self.keyboard==1):
			self.keyboard_recv()
