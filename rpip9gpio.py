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

from pythonX9 import *

import RPi.GPIO as GPIO
import pigpio # PWM HW

#from gpiozero import *

TONES = { "DO": 262, "DO#": 277, "RE": 294, "RE#": 311, "MI": 330, "FA": 349, "FA#": 370, "SO": 392, "SO#": 415, "LA": 440, "LA#": 466, "SI": 494, "DO2": 523 }

class rpip9gpio(pythonX9):
	GPIO_MODE=GPIO.BCM
	CONTROL_NORMAL=0
	CONTROL_SW=1
	CONTROL_HW=2

	# 0: busy loop, 1: wait_for_edge, 2: event_detect
	EDGE_BUSY=0
	EDGE_WAIT=1 # GPIO.wait_for_edge
	EDGE_EVENT=2 # GPIO.add_event_detect
	EDGE_DEFAULT=EDGE_EVENT

	def setGPIO(self, key, bcmid):
		if ( self.gpioXlnk == 0 ):
			DBG_IF_LN(self, "(key: {}, bcmid: {})".format(key, bcmid) )
			gpioX = self.gpioXlist.get(key)
			if (gpioX is not None):
				gpioX["bcmid"] = bcmid

	def linkGPIO(self):
		if ( self.gpioXlnk == 0 ):
			self.gpioXlnk = 1
			DBG_IF_LN(self, "call GPIO.setmode ... (gpioXmode: {})".format(self.gpioXmode) )
			GPIO.setmode(self.gpioXmode)
			GPIO.setwarnings(False)

			for key, gpioX in self.gpioXlist.items():
				if ( gpioX["control"] == self.CONTROL_SW ):
					DBG_IF_LN(self, "CONTROL_SW (key: {}, bcmid: {}, direction: {})".format(key, gpioX["bcmid"], gpioX["direction"]) )
					if ( gpioX["direction"] == GPIO.OUT ):
						GPIO.setup( gpioX["bcmid"], gpioX["direction"], initial=GPIO.LOW )
					else:
						GPIO.setup( gpioX["bcmid"], gpioX["direction"])

					gpioX["pwm"] = GPIO.PWM(gpioX["bcmid"], gpioX["freq"])
					dutyCycle = gpioX["def"]/gpioX["divisor"]
					gpioX["pwm"].start( 0 )
					DBG_DB_LN(self, "pwmAngle (SW) (key: {}, def: {}, dutyCycle: {})".format(key, gpioX["def"], dutyCycle))
					gpioX["pwm"].ChangeDutyCycle(dutyCycle)
				elif ( gpioX["control"] == self.CONTROL_HW ):
					DBG_IF_LN(self, "CONTROL_HW (key: {}, bcmid: {}, direction: {})".format(key, gpioX["bcmid"], gpioX["direction"]) )
					gpioX["pwm"] = pigpio.pi()
					DBG_DB_LN(self, "pwmAngle (HW) (key: {}, def: {})".format(key, gpioX["def"]))
					gpioX["pwm"].hardware_PWM(gpioX["bcmid"], gpioX["freq"], gpioX["def"])
				else:
					DBG_IF_LN(self, "CONTROL_NORMAL ... (key: {}, bcmid: {}, direction: {})".format(key, gpioX["bcmid"], gpioX["direction"]) )
					if ( gpioX["direction"] == GPIO.OUT ):
						GPIO.setup( gpioX["bcmid"], gpioX["direction"], initial=GPIO.LOW )
					else:
						GPIO.setup( gpioX["bcmid"], gpioX["direction"])
						#GPIO.setup( gpioX["bcmid"], gpioX["direction"], pull_up_down=GPIO.PUD_UP)
						#GPIO.setup( gpioX["bcmid"], gpioX["direction"], pull_up_down=GPIO.PUD_DOWN)

	def pwmFreq(self, key, freq):
		self.linkGPIO()
		gpioX = self.gpioXlist.get(key)
		if (gpioX is not None):
			if ( gpioX["control"] == self.CONTROL_SW ):
					DBG_DB_LN(self, "(key: {}, freq: {})".format(key, freq))
					gpioX["pwm"].ChangeFrequency(freq)

	def pwmPower(self, key, power):
		self.linkGPIO()
		gpioX = self.gpioXlist.get(key)
		if (gpioX is not None):
			if ( gpioX["control"] == self.CONTROL_SW ):
					DBG_DB_LN(self, "pwmPower (SW) (key: {}, power: {})".format(key, power))
					gpioX["pwm"].ChangeDutyCycle(power)

	def pwmAngle(self, key, angle):
		self.linkGPIO()
		gpioX = self.gpioXlist.get(key)
		if (gpioX is not None):
			if ( gpioX["control"] == self.CONTROL_SW ):
				DBG_DB_LN(self, "pwmAngle (SW) (key: {}, angle: {})".format(key, angle))
				#dutyCycle = angle / 18. + 3.
				dutyCycle = angle/gpioX["divisor"]
				gpioX["pwm"].ChangeDutyCycle(dutyCycle)
			elif ( gpioX["control"] == self.CONTROL_HW ):
				dutyCycle = angle
				DBG_DB_LN(self, "pwmAngle (HW) (key: {}, angle: {}, dutyCycle: {})".format(key, angle, dutyCycle))
				gpioX["pwm"].hardware_PWM(gpioX["bcmid"], gpioX["freq"], dutyCycle)

	def gpioGetVal(self, gpioX):
		return GPIO.input(gpioX["bcmid"])

	def gpioGetValWithID(self, bcmid):
		return GPIO.input(bcmid)

	def gpioSetOutputHigh(self, gpioX, val):
		DBG_DB_LN(self, "(key: {}, bcmid: {}, val: {})".format(gpioX["name"], gpioX["bcmid"], val) )
		GPIO.output(gpioX["bcmid"], val)

	def gpioSetOutputLow(self, gpioX, val):
		DBG_DB_LN(self, "(key: {}, bcmid: {}, val: {})".format(gpioX["name"], gpioX["bcmid"], val) )
		GPIO.output(gpioX["bcmid"], val)

	def gpioSetHelper(self, gpioX, val):
		self.linkGPIO()
		if (gpioX is not None):
			gpioX["val"] = val
			if (val == GPIO.HIGH):
				self.gpioSetOutputHigh(gpioX, val)
			else:
				self.gpioSetOutputLow(gpioX, val)

	def gpioSetHigh(self, gpioX):
		self.gpioSetHelper(gpioX, GPIO.HIGH)

	def gpioSetHighWithKey(self, key):
		gpioX = self.gpioXlist.get(key)
		if (gpioX is not None):
			self.gpioSetHelper(gpioX, GPIO.HIGH)

	def gpioSetLow(self, gpioX):
		self.gpioSetHelper(gpioX, GPIO.LOW)

	def gpioSetLowWithKey(self, key):
		gpioX = self.gpioXlist.get(key)
		if (gpioX is not None):
			self.gpioSetHelper(gpioX, GPIO.LOW)

	def gpioToggle(self, key):
		gpioX = self.gpioXlist.get(key)
		if (gpioX is not None):
			if ( gpioX["val"] == GPIO.LOW ):
				gpioX["val"] = GPIO.HIGH
			else:
				gpioX["val"] = GPIO.LOW
			self.gpioSetHelper(gpioX, gpioX["val"])

	def release(self):
		if ( self.is_quit == 0 ):
			self.is_quit = 1
			if ( self.gpioXlnk == 1 ):
				DBG_IF_LN("call GPIO.cleanup ...")
				GPIO.cleanup()

	def rpip9gpio_init(self):
		self.gpioXmode = self.GPIO_MODE
		self.gpioXlnk = 0
		self.gpioXlist = {}

		self.melody = TONES

	def __init__(self, **kwargs):
		if ( isPYTHON(PYTHON_V3) ):
			super().__init__(**kwargs)
		else:
			super(rpip9gpio, self).__init__(**kwargs)

		self._kwargs = kwargs
		self.rpip9gpio_init()
