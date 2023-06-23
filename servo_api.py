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

BCM_TILT=12#32
BCM_PAN=13#33

sw_tilt_330 = {"name": "tilt", "bcmid": BCM_TILT, "control": rpip9gpio.CONTROL_SW, "direction": GPIO.OUT, "val": 50, "def": 50, "freq": 330, "pwm": None, "max": 100, "min": 0, "step": 1, "cruise": 0, "threading": None, "cruise_cond": None, "divisor": 1}
sw_pan_330 = {"name": "pan", "bcmid": BCM_PAN, "control": rpip9gpio.CONTROL_SW, "direction": GPIO.OUT, "val": 50, "def": 50, "freq": 330, "pwm": None, "max": 100, "min": 0, "step": 1, "cruise": 0, "threading": None, "cruise_cond": None, "divisor": 1}

servo_sw_tilt_330 = {"tilt": sw_tilt_330}
servo_sw_tilt_pan_330 = {"tilt": sw_tilt_330, "pan": sw_pan_330}

sw_tilt_50 = {"name": "tilt", "bcmid": BCM_TILT, "control": rpip9gpio.CONTROL_SW, "direction": GPIO.OUT, "val": 750, "def": 750, "freq": 50, "pwm": None, "max": 1250, "min": 250, "step": 10, "cruise": 0, "threading": None, "cruise_cond": None, "divisor": 100}
sw_pan_50 = {"name": "pan", "bcmid": BCM_PAN, "control": rpip9gpio.CONTROL_SW, "direction": GPIO.OUT, "val": 750, "def": 750, "freq": 50, "pwm": None, "max": 1250, "min": 250, "step": 10, "cruise": 0, "threading": None, "cruise_cond": None, "divisor": 100}

servo_sw_tilt_50 = {"tilt": sw_tilt_50}
servo_sw_tilt_pan_50 = {"tilt": sw_tilt_50, "pan": sw_pan_50}

hw_tilt = {"name": "tilt", "bcmid": BCM_TILT, "control": rpip9gpio.CONTROL_HW, "direction": GPIO.OUT, "val": 72500, "def": 72500, "freq": 50, "pwm": None, "max": 120000, "min": 25000, "step": 950, "cruise": 0, "threading": None, "cruise_cond": None, "divisor": 1}
hw_pan = {"name": "pan", "bcmid": BCM_PAN, "control": rpip9gpio.CONTROL_HW, "direction": GPIO.OUT, "val": 72500, "def": 72500, "freq": 50, "pwm": None, "max": 120000, "min": 25000, "step": 950, "cruise": 0, "threading": None, "cruise_cond": None, "divisor": 1}

servo_hw_tilt_and_pan = {"tilt": hw_tilt, "pan": hw_pan}
servo_hw_tilt = {"tilt": hw_tilt}

class servo_ctx(rpip9gpio):
	def servo_angle_helper(self, key, angle):
		gpioX = self.gpioXlist.get(key)
		if (gpioX is not None):
			if ( angle > gpioX["max"] ):
				angle = gpioX["max"]
				DBG_WN_LN(self, "(key: {}, angle: {} > max_angle: {} )".format(key, angle, gpioX["max"]) )
			if ( angle < gpioX["min"]  ):
				angle = gpioX["min"]
				DBG_WN_LN(self, "(key: {}, angle: {} < min_angle: {} )".format(key, angle, gpioX["min"]) )
			gpioX["val"] = angle

			DBG_IF_LN(self, "(key: {}, min_angle: {}, val: {}, max_angle: {})".format( key, gpioX["min"], gpioX["val"], gpioX["max"] ) )
			self.pwmAngle(key, gpioX["val"] )

	def servo_angle_def(self, key):
		gpioX = self.gpioXlist.get(key)
		if (gpioX is not None):
			self.servo_stop(key)
			DBG_IF_LN(self, "(val: {}, def: {}, step: {})".format(gpioX["val"], gpioX["def"], gpioX["step"] ))
			self.servo_angle_helper(key, gpioX["def"] )

	def servo_angle_inc(self, key):
		gpioX = self.gpioXlist.get(key)
		if (gpioX is not None):
			self.servo_stop(key)
			#DBG_DB_LN(self, "(val: {}, step: {})".format(gpioX["val"], gpioX["step"] ))
			self.servo_angle_helper(key, gpioX["val"] + gpioX["step"] )

	def servo_angle_dec(self, key):
		gpioX = self.gpioXlist.get(key)
		if (gpioX is not None):
			self.servo_stop(key)
			self.servo_angle_helper(key, gpioX["val"] - gpioX["step"] )

	def servo_move(self, gpioX):
		if (gpioX is not None):
			angle_old = gpioX["val"]
			key = gpioX["name"]
			for i in range (angle_old, gpioX["max"]+1, gpioX["step"]):
				if ( self.is_quit == 0 ) and ( gpioX["cruise"] == 1 ):
					self.servo_angle_helper(key, i)
					sleep(self.hold_sec)
			for i in range (gpioX["max"], gpioX["min"]+1, -gpioX["step"]):
				if ( self.is_quit == 0 ) and ( gpioX["cruise"]  == 1 ):
					self.servo_angle_helper(key, i)
					sleep(self.hold_sec)
			for i in range (gpioX["min"], angle_old+1, gpioX["step"]):
				if ( self.is_quit == 0 ) and ( gpioX["cruise"]  == 1 ):
					self.servo_angle_helper(key, i)
					sleep(self.hold_sec)

	def servo_stop(self, key):
		gpioX = self.gpioXlist.get(key)
		if (gpioX is not None):
			gpioX["cruise"] = 0

	def servo_stop_all(self):
		for key, gpioX in self.gpioXlist.items():
			gpioX["cruise"] = 0

	def servo_start(self, key):
		gpioX = self.gpioXlist.get(key)
		if (gpioX is not None):
			if ( gpioX["cruise"] == 0):
				gpioX["cruise"] = 1
				self.wakeup(gpioX)
			else:
				gpioX["cruise"] = 0

	def threadx_handler(self, gpioX):
		DBG_WN_LN(self, "looping (name: {}) ...".format(gpioX["name"]))
		while (self.is_quit == 0):
			if (gpioX["cruise"] == 0):
				self.servo_sleep(gpioX)
			else:
				self.servo_move(gpioX)
			#sleep(self.hold_sec)
		DBG_WN_LN(self, "{} (name: {}) ".format(DBG_TXT_BYE_BYE, gpioX["name"]))

	def wakeup(self, gpioX):
		gpioX["cruise_cond"].acquire()
		#DBG_IF_LN(self, "notify ...")
		gpioX["cruise_cond"].notify()
		gpioX["cruise_cond"].release()

	def servo_sleep(self, gpioX):
		gpioX["cruise_cond"].acquire()
		#DBG_IF_LN(self, "wait ...")
		gpioX["cruise_cond"].wait()
		gpioX["cruise_cond"].release()
		#DBG_IF_LN(self, "exit")

	def start(self, args={"keyboard": 0}):
		self.linkGPIO()
		self.parse_args(args)
		if (self.keyboard==1):
			self.keyboard_recv()

	def keyboard_recv(self):
		DBG_WN_LN(self, "press q to quit the loop (a: all, z:tilt, x:pan, ←:left, ↑:up, →:right, ↓:down, enter: default) ...")
		k='\x00'
		while ( self.is_quit == 0 ):
			k = self.inkey()
			self.servo_stop_all()
			if k=='\x41': # up
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
				self.servo_start("tilt")
				self.servo_start("pan")
			elif k=='\x7a': # z
				self.servo_start("tilt")
			elif k=='\x78': # x
				self.servo_start("pan")
			elif k=='\x71': # q
				break;
			elif k=='\x03':
				break;

	def release(self):
		DBG_IF_LN("(is_quit: {}, gpioXlnk: {})".format(self.is_quit, self.gpioXlnk ))
		if ( self.is_quit == 0 ):
			self.is_quit = 1
			for key, gpioX in self.gpioXlist.items():
				if (gpioX["direction"] == GPIO.OUT ):
					self.wakeup(gpioX)

			if ( self.gpioXlnk == 1 ):
				for key, gpioX in self.gpioXlist.items():
					if ( gpioX["control"] == self.CONTROL_SW):
						gpioX["pwm"].stop()
					elif ( gpioX["control"] == self.CONTROL_HW ):
						gpioX["pwm"].set_mode(gpioX["bcmid"], pigpio.INPUT)
					gpioX["threading"].join()
				DBG_WN_LN("call GPIO.cleanup ...")
				GPIO.cleanup()


	def ctx_init(self, servo_gpio):
		self.gpioXlist = servo_gpio

		self.hold_sec = 1

		for key, gpioX in self.gpioXlist.items():
			#DBG_WR_LN(self, "(key: {})".format(key) )
			if (gpioX["direction"] == GPIO.OUT ):
				gpioX["cruise_cond"] = threading.Condition()
				gpioX["threading"] = threading.Thread(target=self.threadx_handler, args = (gpioX, ))
				gpioX["threading"].start()

		sleep(0.5)

	def __init__(self, servo_gpio=servo_hw_tilt_and_pan, **kwargs):
		if ( isPYTHON(PYTHON_V3) ):
			super().__init__(**kwargs)
		else:
			super(servo_ctx, self).__init__(**kwargs)

		DBG_TR_LN(self, "{}".format(DBG_TXT_ENTER))
		self._kwargs = kwargs
		self.ctx_init(servo_gpio)

	def parse_args(self, args):
		self._args = args
		self.keyboard = args["keyboard"]
		DBG_TR_LN("(keyboard: {})".format( self.keyboard ));

