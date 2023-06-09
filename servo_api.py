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

BCM_TILT=12#32
BCM_PAN=13#33

sw_tilt_330 = {"name": "tilt", "bcmid": BCM_TILT, "control": rpip9gpio.CONTROL_SW, "direction": GPIO.OUT, "val": 50, "def": 50, "freq": 330, "pwm": None, "max": 100, "min": 0, "step": 1, "threading_pause": 1, "threading_handler": None, "threading_cond": None, "divisor": 1}
sw_pan_330 = {"name": "pan", "bcmid": BCM_PAN, "control": rpip9gpio.CONTROL_SW, "direction": GPIO.OUT, "val": 50, "def": 50, "freq": 330, "pwm": None, "max": 100, "min": 0, "step": 1, "threading_pause": 1, "threading_handler": None, "threading_cond": None, "divisor": 1}

servo_sw_tilt_330 = {"tilt": sw_tilt_330}
servo_sw_tilt_pan_330 = {"tilt": sw_tilt_330, "pan": sw_pan_330}

sw_tilt_50 = {"name": "tilt", "bcmid": BCM_TILT, "control": rpip9gpio.CONTROL_SW, "direction": GPIO.OUT, "val": 750, "def": 750, "freq": 50, "pwm": None, "max": 1250, "min": 250, "step": 10, "threading_pause": 1, "threading_handler": None, "threading_cond": None, "divisor": 100}
sw_pan_50 = {"name": "pan", "bcmid": BCM_PAN, "control": rpip9gpio.CONTROL_SW, "direction": GPIO.OUT, "val": 750, "def": 750, "freq": 50, "pwm": None, "max": 1250, "min": 250, "step": 10, "threading_pause": 1, "threading_handler": None, "threading_cond": None, "divisor": 100}

servo_sw_tilt_50 = {"tilt": sw_tilt_50}
servo_sw_tilt_pan_50 = {"tilt": sw_tilt_50, "pan": sw_pan_50}

hw_tilt = {"name": "tilt", "bcmid": BCM_TILT, "control": rpip9gpio.CONTROL_HW, "direction": GPIO.OUT, "val": 72500, "def": 72500, "freq": 50, "pwm": None, "max": 120000, "min": 25000, "step": 950, "threading_pause": 1, "threading_handler": None, "threading_cond": None, "divisor": 1}
hw_pan = {"name": "pan", "bcmid": BCM_PAN, "control": rpip9gpio.CONTROL_HW, "direction": GPIO.OUT, "val": 72500, "def": 72500, "freq": 50, "pwm": None, "max": 120000, "min": 25000, "step": 950, "threading_pause": 1, "threading_handler": None, "threading_cond": None, "divisor": 1}

servo_hw_tilt_and_pan = {"tilt": hw_tilt, "pan": hw_pan}
servo_hw_tilt = {"tilt": hw_tilt}

class servo_ctx(rpip9gpio):

	def servo_angle_helper(self, key, angle):
		gpioX = self.gpioXlist.get(key)
		if (gpioX is not None):
			if ( angle > gpioX["max"] ):
				angle = gpioX["max"]
				DBG_WN_LN(self, "(gpioX[{}/{}]: {} > max: {})".format( gpioX["name"], gpioX["bcmid"], angle, gpioX["max"]) )
			if ( angle < gpioX["min"]  ):
				angle = gpioX["min"]
				DBG_WN_LN(self, "(gpioX[{}/{}]: {} < min: {})".format( gpioX["name"], gpioX["bcmid"], angle, gpioX["min"]) )
			gpioX["val"] = angle

			DBG_IF_LN(self, "(gpioX[{}/{}]: {} <= {} <= {})".format( gpioX["name"], gpioX["bcmid"], gpioX["min"], gpioX["val"], gpioX["max"] ) )
			self.pwmAngle(key, gpioX["val"] )

	def servo_angle_def(self, key):
		gpioX = self.gpioXlist.get(key)
		if (gpioX is not None):
			self.threadx_pause(gpioX)
			DBG_IF_LN(self, "(gpioX[{}/{}]: {}, def: {}, step: {})".format(gpioX["name"], gpioX["bcmid"], gpioX["val"], gpioX["def"], gpioX["step"] ))
			self.servo_angle_helper(key, gpioX["def"] )

	def servo_angle_inc(self, key):
		gpioX = self.gpioXlist.get(key)
		if (gpioX is not None):
			self.threadx_pause(gpioX)
			#DBG_DB_LN(self, "(gpioX[{}/{}]: {}, step: {})".format(gpioX["name"], gpioX["bcmid"], gpioX["val"], gpioX["step"] ))
			self.servo_angle_helper(key, gpioX["val"] + gpioX["step"] )

	def servo_angle_dec(self, key):
		gpioX = self.gpioXlist.get(key)
		if (gpioX is not None):
			self.threadx_pause(gpioX)
			self.servo_angle_helper(key, gpioX["val"] - gpioX["step"] )

	def servo_move(self, gpioX):
		if (gpioX is not None):
			angle_old = gpioX["val"]
			key = gpioX["name"]
			for i in range (angle_old, gpioX["max"]+1, gpioX["step"]):
				if ( self.is_quit == 0 ) and ( gpioX["threading_pause"] == 0 ):
					self.servo_angle_helper(key, i)
					sleep(self.hold_sec)
			for i in range (gpioX["max"], gpioX["min"]+1, -gpioX["step"]):
				if ( self.is_quit == 0 ) and ( gpioX["threading_pause"]  == 0 ):
					self.servo_angle_helper(key, i)
					sleep(self.hold_sec)
			for i in range (gpioX["min"], angle_old+1, gpioX["step"]):
				if ( self.is_quit == 0 ) and ( gpioX["threading_pause"]  == 0 ):
					self.servo_angle_helper(key, i)
					sleep(self.hold_sec)

	def servo_start(self, key):
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
		self.servo_move(gpioX)

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
		DBG_WN_LN(self, "press q to quit the loop (a: all, z: tilt, x: pan, ←: left, ↑: up, →: right, ↓: down, enter: default) ...")
		k='\x00'
		while ( self.is_quit == 0 ):
			k = self.inkey()
			self.threadx_pause_all()
			if k=='\x71': # q
				break;
			elif k=='\x41': # up
				self.servo_angle_inc("tilt")
			elif k=='\x42': # down
				self.servo_angle_dec("tilt")
			elif k=='\x43': # right
				self.servo_angle_inc("pan")
			elif k=='\x44': # left
				self.servo_angle_dec("pan")
			elif k=='\x0d': # enter
				self.servo_angle_def("tilt")
				self.servo_angle_def("pan")
			elif k=='\x61': # a
				self.threadx_run_all()
			elif k=='\x7a': # z
				self.servo_start("tilt")
			elif k=='\x78': # x
				self.servo_start("pan")
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
					if ( gpioX["control"] == self.CONTROL_SW):
						gpioX["pwm"].stop()
					elif ( gpioX["control"] == self.CONTROL_HW ):
						gpioX["pwm"].set_mode(gpioX["bcmid"], pigpio.INPUT)

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

	def __init__(self, gpioXlist=servo_hw_tilt_and_pan, **kwargs):
		if ( isPYTHON(PYTHON_V3) ):
			super().__init__(**kwargs)
		else:
			super(servo_ctx, self).__init__(**kwargs)

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
			if  ("direction" in gpioX) and (gpioX["direction"] ==  GPIO.IN) and ("edge" in gpioX) and (gpioX["edge"] == rpip9gpio.EDGE_EVENT):
				DBG_IF_LN("call add_event_detect .. (gpioX[{}/{}]: {}).".format(gpioX["name"], gpioX["bcmid"], gpioX["val"]))
				GPIO.add_event_detect(gpioX["bcmid"], GPIO.BOTH, callback=self.edge_detect_cb)

		if (self.keyboard==1):
			self.keyboard_recv()
