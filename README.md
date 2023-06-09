# 1. Overview

RPiP9 把 Raspberry Pi 上常見的模組搜集而成。

當然你會覺得網路上有，為什麼還寫出這些範例？

網路上都是以課程為單位在教學，完全沒有思慮 busy loop、multi thread、資源交換，甚至是程式碼共用等問題。

不敢說自己寫的很完美，至少會用我在業界的態度來撰寫。

# 2. Depend on

- [netifaces 0.11.0](https://pypi.org/project/netifaces/)
- [RPi.GPIO 0.7.1](https://pypi.org/project/RPi.GPIO/)
- [pigpio 1.78](https://pypi.org/project/pigpio/)

```bash
sudo systemctl status pigpiod
sudo service pigpiod start
```

- [libgpiod 2.0.1](https://pypi.org/project/libgpiod/)

```bash
sudo apt-get install libgpiod2
```

- [adafruit-circuitpython-dht 4.0.2](https://pypi.org/project/adafruit-circuitpython-dht/), [Adafruit_CircuitPython_DHT](https://github.com/adafruit/Adafruit_CircuitPython_DHT)

# 3. Current Status


# 4. Build
```bash
Do nothing
```
# 5. Example or Usage

#### - dht11_123.py : [DHT11](https://datasheetspdf.com/pdf/792210/ABCPROYECTOS/DHT11/1), Temperature Sensor example

> 相關說明可見 [Adafruit_CircuitPython_DHT](https://github.com/adafruit/Adafruit_CircuitPython_DHT)

![dht1101](./images/dht1101.jpg)

```mermaid
flowchart LR
	subgraph DHT11
		VCC["VCC (3.3VDC A 5VDC) (pin 1)"]
		Data["Data"]
		None["None"]
		GND["GND"]
	end
	subgraph "Raspberry Pi"
		BCM4[BCM 4]
		5V_PI[5V]
		GND_PI[GND]
	end
	BCM4 <--> Data
	5V_PI <--> VCC
	GND_PI <--> GND
```

```bash
$ make dht11_123.py
----->> layer_python - /work/codebase/lankahsu520/RPiP9/python


----->> run dht11_123.py
[ -d "/work/codebase/lankahsu520/RPiP9/python" ] &&  PYTHONPATH=/work/codebase/lankahsu520/RPiP9/python ./dht11_123.py -d 3
[23306/1983243328] dhtx_api.py|threadx_handler:0086 - looping ... (gpioX[dht11/4]: 0)
[23306/1983243328] dhtx_api.py|cond_sleep:0122 - wait ... (gpioX[dht11/4]: 0)
[23306/1995710528] dhtx_api.py|keyboard_recv:0128 - press q to quit the loop (enter: start, space: pause) ...
[23306/1995710528] dhtx_api.py|threadx_run_loop:0071 - run in loop ... (gpioX[dht11/4]: 0)
[23306/1983243328] dhtx_api.py|threadx_tick:0082 - (gpioX[dht11/4], Temperature: 24.0 F / 75.2 C, Humidity: 34%)
[23306/1983243328] dhtx_api.py|dhtx_lookup:0050 - A full buffer was not returned. Try again.
[23306/1983243328] dhtx_api.py|threadx_tick:0082 - (gpioX[dht11/4], Temperature: 24.0 F / 75.2 C, Humidity: 34%)
[23306/1983243328] dhtx_api.py|dhtx_lookup:0050 - A full buffer was not returned. Try again.
[23306/1983243328] dhtx_api.py|threadx_tick:0082 - (gpioX[dht11/4], Temperature: 24.0 F / 75.2 C, Humidity: 34%)
[23306/1983243328] dhtx_api.py|threadx_tick:0082 - (gpioX[dht11/4], Temperature: 24.0 F / 75.2 C, Humidity: 36%)
[23306/1995710528] dhtx_api.py|release:0143 - (is_quit: 0, gpioXlnk: 0)
[23306/1983243328] dhtx_api.py|threadx_handler:0102 - Bye-Bye !!! (gpioX[dht11/4]: 0)
[23306/1995710528] dht11_123.py|main:0119 - Bye-Bye !!! (is_quit: 1)

```

#### - servo_tilt_123.py : [SG90](https://datasheetspdf.com/pdf/791970/TowerPro/SG90/1) (180 degree Rotation), Micro Servo example

> a frequency of 50Hz. That frequency was selected because the servo motor expect a pulse every 20ms (period), that means 50 pulses per second or Hertz.
>
> 範例中，使用者可以使用 GPIO.PWM (rpip9gpio.CONTROL_SW) 或是使用 hardware_PWM (rpip9gpio.CONTROL_HW)  進行操作。操作中可以發現，使用軟體(GPIO.PWM)模擬時，抖動的情形會很明顯。

![servoSG9001](./images/servoSG9001.jpg)
![servoSG9001](./images/servoSG9002.jpg)

```mermaid
flowchart LR
	subgraph servo
		PWM["PWM (Orange)"]
		VCC["VCC (Red)"]
		GND["GND (Brown)"]
	end
	subgraph "Raspberry Pi"
		BCM12[BCM 12]
		5V_PI[5V]
		GND_PI[GND]
	end
	BCM12 <--> PWM
	5V_PI <--> VCC
	GND_PI <--> GND
```

| api         | Codes                                                        | freq | min                       | max                        | step |
| ----------- | ------------------------------------------------------------ | ---- | ------------------------- | -------------------------- | ---- |
| GPIO.PWM    | gpioX["pwm"] = GPIO.PWM(gpioX["bcmid"], gpioX["freq"])<br>gpioX["pwm"].start(0)<br>gpioX["pwm"].ChangeDutyCycle(dutyCycle) | 330  | 0                         | 100                        | 1    |
| GPIO.PWM    |                                                              | 50   | 2.5<br>(50/20)            | 12.5<br>(250/20)           | 0.05 |
| pigpio.pi() | gpioX["pwm"] = pigpio.pi()<br>gpioX["pwm"].hardware_PWM(gpioX["bcmid"], gpioX["freq"], dutyCycle) |      | 25000<br>(1000000*0.5/20) | 120000<br>(1000000*2.4/20) | 950  |
|             |                                                              |      |                           |                            |      |

```bash
$ make servo_tilt_123.py
----->> layer_python - /work/codebase/lankahsu520/RPiP9/python


----->> run servo_tilt_123.py
PYTHONPATH=/work/codebase/lankahsu520/RPiP9/python ./servo_tilt_123.py -d 3
[26939/0000] servo_api.py|threadx_handler:0114 - looping tilt...
[26939/-001] rpip9gpio.py|linkGPIO:0045 - call GPIO.setmode ... (gpioXmode: 11)
[26939/-001] rpip9gpio.py|linkGPIO:0063 - CONTROL_HW (key: tilt, bcmid: 12, direction: 0)
[26939/-001] rpip9gpio.py|linkGPIO:0065 - pwmAngle (HW) (key: tilt, def: 72500)
[26939/-001] servo_api.py|keyboard_recv:0142 - press q to quit the loop (z:tilt, x:pan, ←:left, ↑:up, →:right, ↓:down, enter: default) ...
[26939/-001] servo_api.py|servo_angle_def:0062 - (val: 72500, def: 72500, step: 950)
[26939/-001] servo_api.py|servo_angle_helper:0055 - (key: tilt, min_angle: 25000, val: 72500, max_angle: 120000)
[26939/-001] rpip9gpio.py|pwmAngle:0102 - pwmAngle (HW) (key: tilt, angle: 72500, dutyCycle: 72500)
[26939/-001] servo_api.py|servo_angle_helper:0055 - (key: tilt, min_angle: 25000, val: 73450, max_angle: 120000)
[26939/-001] rpip9gpio.py|pwmAngle:0102 - pwmAngle (HW) (key: tilt, angle: 73450, dutyCycle: 73450)
[26939/-001] servo_api.py|servo_angle_helper:0055 - (key: tilt, min_angle: 25000, val: 74400, max_angle: 120000)
[26939/-001] rpip9gpio.py|pwmAngle:0102 - pwmAngle (HW) (key: tilt, angle: 74400, dutyCycle: 74400)
[26939/-001] servo_api.py|servo_angle_helper:0055 - (key: tilt, min_angle: 25000, val: 75350, max_angle: 120000)
[26939/-001] rpip9gpio.py|pwmAngle:0102 - pwmAngle (HW) (key: tilt, angle: 75350, dutyCycle: 75350)
[26939/-001] servo_api.py|release:0168 - (is_quit: 0, gpioXlnk: 1)
[26939/-001] servo_api.py|release:0181 - call GPIO.cleanup ...
[26939/-001] servo_tilt_123.py|main:0123 - Bye-Bye !!! (is_quit: 1)

```

#### - servo_tilt_pan_123.py : [SG90 ](https://datasheetspdf.com/pdf/791970/TowerPro/SG90/1)(180 degree Rotation)*2, Micro Servo example

![servoSG9003](./images/servoSG9003.jpg)

```mermaid
flowchart LR
	subgraph "servo (tilt)"
		PWM_tilt["PWM (Orange)"]
		VCC_tilt["VCC (Red)"]
		GND_tilt["GND (Brown)"]
	end
	subgraph "servo (pan)"
		PWM_pan["PWM (Orange)"]
		VCC_pan["VCC (Red)"]
		GND_pan["GND (Brown)"]
	end
	subgraph "Raspberry Pi"
		BCM12[BCM 12]
		BCM13[BCM 13]
		5V_PI[5V]
		GND_PI[GND]
	end
	BCM12 <--> PWM_tilt
	BCM13 <--> PWM_pan
	5V_PI <--> VCC_tilt
	GND_PI <--> GND_tilt
```
> This is just an illustration to avoid overly complex graphics. Please correctly connect VCC and GND.

```bash
$ make servo_tilt_pan_123.py
----->> layer_python - /work/codebase/lankahsu520/RPiP9/python


----->> run servo_tilt_pan_123.py
PYTHONPATH=/work/codebase/lankahsu520/RPiP9/python ./servo_tilt_pan_123.py -d 3
[9036/0000] servo_api.py|threadx_handler:0116 - looping (name: tilt) ...
[9036/0000] servo_api.py|threadx_handler:0116 - looping (name: pan) ...
[9036/-001] rpip9gpio.py|linkGPIO:0044 - call GPIO.setmode ... (gpioXmode: 11)
[9036/-001] rpip9gpio.py|linkGPIO:0050 - CONTROL_SW (key: tilt, bcmid: 12, direction: 0)
[9036/-001] rpip9gpio.py|linkGPIO:0050 - CONTROL_SW (key: pan, bcmid: 13, direction: 0)
[9036/-001] servo_api.py|keyboard_recv:0139 - press q to quit the loop (a: all, z:tilt, x:pan, ←:left, ↑:up, →:right, ↓:down, enter: default) ...
[9036/-001] servo_api.py|servo_angle_helper:0057 - (key: tilt, val: 250 <= 760 <= 1250)
[9036/-001] servo_api.py|servo_angle_helper:0057 - (key: tilt, val: 250 <= 770 <= 1250)
[9036/-001] servo_api.py|servo_angle_helper:0057 - (key: pan, val: 250 <= 760 <= 1250)
[9036/-001] servo_api.py|servo_angle_helper:0057 - (key: pan, val: 250 <= 770 <= 1250)
[9036/-001] servo_api.py|servo_angle_helper:0057 - (key: pan, val: 250 <= 780 <= 1250)
[9036/-001] servo_api.py|release:0168 - (is_quit: 0, gpioXlnk: 1)
[9036/-001] servo_api.py|threadx_handler:0123 - Bye-Bye !!! (name: tilt)
[9036/-001] servo_api.py|threadx_handler:0123 - Bye-Bye !!! (name: pan)
[9036/-001] servo_api.py|release:0184 - call GPIO.cleanup ...
[9036/-001] servo_tilt_pan_123.py|main:0126 - Bye-Bye !!! (is_quit: 1)

```

#### - traffic_lights_123.py : Traffic Lights example

> 這是一個很簡單的 GPIO.OUT 操作。

![traffic_lights01](./images/traffic_lights01.jpg)
```mermaid
flowchart LR
	subgraph "traffic lights"
		GND_lights["GND"]
		R_lights["Red"]
		Y_lights["Yellow"]
		G_lights["Green"]
	end
	subgraph "Raspberry Pi"
		BCM17[BCM 17]
		BCM27[BCM 27]
		BCM22[BCM 22]
		GND_PI[GND]
	end
	BCM17 <--> R_lights
	BCM27 <--> Y_lights
	BCM22 <--> G_lights
	GND_PI <--> GND_lights
```

```bash
$ make traffic_lights_123.py
----->> layer_python - /work/codebase/lankahsu520/RPiP9/python


----->> run traffic_lights_123.py
[ -d "/work/codebase/lankahsu520/RPiP9/python" ] &&  PYTHONPATH=/work/codebase/lankahsu520/RPiP9/python ./traffic_lights_123.py -d 3
[22395/1984283712] traffic_lights_api.py|threadx_handler:0124 - looping ... (gpioX[R/17]: 0)
[22395/1984283712] traffic_lights_api.py|cond_sleep:0152 - wait ... (gpioX[R/17]: 0)
[22395/1995558976] rpip9gpio.py|linkGPIO:0087 - call GPIO.setmode ... (gpioXmode: GPIO.BCM)
[22395/1995558976] rpip9gpio.py|linkGPIO:0092 - CONTROL_NORMAL (gpioX[R/17]: 0, direction: GPIO.OUT)
[22395/1995558976] rpip9gpio.py|linkGPIO:0092 - CONTROL_NORMAL (gpioX[Y/27]: 0, direction: GPIO.OUT)
[22395/1995558976] rpip9gpio.py|linkGPIO:0092 - CONTROL_NORMAL (gpioX[G/22]: 0, direction: GPIO.OUT)
[22395/1995558976] traffic_lights_api.py|keyboard_recv:0158 - press q to quit the loop (enter: start, space: pause, a: all on, r: Red on, y: Yellow on, g: Green on) ...
[22395/1995558976] traffic_lights_api.py|lightX_helper:0038 - (gpioX[R/17]: 0)
[22395/1995558976] traffic_lights_api.py|lightX_helper:0038 - (gpioX[Y/27]: 0)
[22395/1995558976] traffic_lights_api.py|lightX_helper:0038 - (gpioX[G/22]: 0)
[22395/1995558976] traffic_lights_api.py|threadx_run_loop:0085 - run in loop ... (gpioX[R/17]: 0)
[22395/1984283712] traffic_lights_api.py|lightX_helper:0038 - (gpioX[R/17]: 1)
[22395/1984283712] traffic_lights_api.py|cond_wait:0144 - wait ... (gpioX[R/17]: 1)
[22395/1984283712] traffic_lights_api.py|lightX_helper:0038 - (gpioX[R/17]: 0)
[22395/1984283712] traffic_lights_api.py|lightX_helper:0038 - (gpioX[Y/27]: 1)
[22395/1984283712] traffic_lights_api.py|cond_wait:0144 - wait ... (gpioX[R/17]: 0)
[22395/1984283712] traffic_lights_api.py|lightX_helper:0038 - (gpioX[Y/27]: 0)
[22395/1984283712] traffic_lights_api.py|lightX_helper:0038 - (gpioX[G/22]: 1)
[22395/1984283712] traffic_lights_api.py|cond_wait:0144 - wait ... (gpioX[R/17]: 0)
[22395/1984283712] traffic_lights_api.py|lightX_helper:0038 - (gpioX[G/22]: 0)
[22395/1984283712] traffic_lights_api.py|lightX_helper:0038 - (gpioX[Y/27]: 1)
[22395/1984283712] traffic_lights_api.py|cond_wait:0144 - wait ... (gpioX[R/17]: 0)
[22395/1984283712] traffic_lights_api.py|lightX_helper:0038 - (gpioX[Y/27]: 0)
[22395/1984283712] traffic_lights_api.py|lightX_helper:0038 - (gpioX[R/17]: 1)
[22395/1984283712] traffic_lights_api.py|cond_wait:0144 - wait ... (gpioX[R/17]: 1)
[22395/1995558976] traffic_lights_api.py|lightX_helper:0038 - (gpioX[R/17]: 0)
[22395/1995558976] traffic_lights_api.py|lightX_helper:0038 - (gpioX[Y/27]: 0)
[22395/1995558976] traffic_lights_api.py|lightX_helper:0038 - (gpioX[G/22]: 0)
[22395/1995558976] traffic_lights_api.py|release:0183 - (is_quit: 0, gpioXlnk: 1)
[22395/1984283712] traffic_lights_api.py|threadx_handler:0132 - Bye-Bye !!! (gpioX[R/17]: 0)
[22395/1995558976] traffic_lights_api.py|release:0196 - call GPIO.cleanup ...
[22395/1995558976] traffic_lights_123.py|main:0119 - Bye-Bye !!! (is_quit: 1)

```

#### - xtrack_18_123.py : Tracker Sensor (TCRT5000), Tracker Sensor example

> 這是一個很簡單的 GPIO.IN 操作。
>
> 請使用者自行調整 "edge"，在遍尋網路上的示範裏少有的。
>

```python
	# 0: busy loop, 1: wait_for_edge, 2: event_detect
	EDGE_BUSY=0
	EDGE_WAIT=1 # GPIO.wait_for_edge
	EDGE_EVENT=2 # GPIO.add_event_detect
	EDGE_DEFAULT=EDGE_EVENT
```

![tracker001](./images/tracker001.jpg)
```mermaid
flowchart LR
	subgraph "tracker"
		OUT["OUT"]
		VCC["VCC"]
		GND["GND"]
	end
	subgraph "Raspberry Pi"
		BCM18[BCM 18]
		5V_PI[5V]
		GND_PI[GND]
	end
	BCM18 <--> OUT
	5V_PI <--> VCC
	GND_PI <--> GND

```

```bash
$ make xtrack_18_123.py
----->> layer_python - /work/codebase/lankahsu520/RPiP9/python


----->> run xtrack_18_123.py
PYTHONPATH=/work/codebase/lankahsu520/RPiP9/python ./xtrack_18_123.py -d 3
[17053/1981854784] xtrack_api.py|threadx_handler:0110 - looping ... (m0: 0, bcmid:18)
[17053/1981854784] xtrack_api.py|cond_sleep:0130 - wait ... (m0: 0, bcmid: 18)
[17053/1996340032] rpip9gpio.py|linkGPIO:0050 - call GPIO.setmode ... (gpioXmode: 11)
[17053/1996340032] rpip9gpio.py|linkGPIO:0073 - CONTROL_NORMAL ... (key: m0, bcmid: 18, direction: 1)
[17053/1996340032] xtrack_api.py|start:0204 - call add_event_detect ...
[17053/1996340032] xtrack_api.py|keyboard_recv:0136 - press q to quit the loop (enter: start, space: pause) ...
[17053/1996340032] xtrack_api.py|threadx_run_loop:0093 - run in loop ... (m0: 0, bcmid: 18)
[17053/1981854784] xtrack_api.py|cond_sleep:0130 - wait ... (m0: 0, bcmid: 18)
[17053/1972368448] xtrack_api.py|edge_detect_cb:0077 - (m0: 1, bcmid: 18)
[17053/1972368448] xtrack_api.py|edge_detect_cb:0077 - (m0: 0, bcmid: 18)
[17053/1972368448] xtrack_api.py|edge_detect_cb:0077 - (m0: 1, bcmid: 18)
[17053/1972368448] xtrack_api.py|edge_detect_cb:0077 - (m0: 0, bcmid: 18)
[17053/1972368448] xtrack_api.py|edge_detect_cb:0077 - (m0: 1, bcmid: 18)
[17053/1972368448] xtrack_api.py|edge_detect_cb:0077 - (m0: 0, bcmid: 18)
[17053/1972368448] xtrack_api.py|edge_detect_cb:0077 - (m0: 1, bcmid: 18)
[17053/1972368448] xtrack_api.py|edge_detect_cb:0077 - (m0: 0, bcmid: 18)
[17053/1996340032] xtrack_api.py|release:0151 - (is_quit: 0, gpioXlnk: 1)
[17053/1981854784] xtrack_api.py|threadx_handler:0118 - Bye-Bye !!! (m0: 0, bcmid:18)
[17053/1996340032] xtrack_api.py|release:0164 - call GPIO.cleanup ...
[17053/1996340032] xtrack_18_123.py|main:0120 - Bye-Bye !!! (is_quit: 1)

```

#### - xtrack_all_456.py : Tracker Sensor (TCRT5000)*5, Tracker Sensor example
```mermaid
flowchart TD
	subgraph "r2"
		OUT_r2["OUT"]
		VCC_r2["VCC"]
		GND_r2["GND"]
	end
	subgraph "r1"
		OUT_r1["OUT"]
		VCC_r1["VCC"]
		GND_r1["GND"]
	end
	subgraph "m0"
		OUT_m0["OUT"]
		VCC_m0["VCC"]
		GND_m0["GND"]
	end
	subgraph "l1"
		OUT_l1["OUT"]
		VCC_l1["VCC"]
		GND_l1["GND"]
	end
	subgraph "l2"
		OUT_l2["OUT"]
		VCC_l2["VCC"]
		GND_l2["GND"]
	end
	subgraph "Raspberry Pi"
		BCM24[BCM 24]
    BCM23[BCM 23]
    BCM18[BCM 18]
		BCM15[BCM 15]
    BCM14[BCM 14]
		5V_PI[5V]
		GND_PI[GND]
	end
	BCM14 <--> OUT_r2

	BCM15 <--> OUT_r1

	BCM18 <--> OUT_m0
	5V_PI <--> VCC_m0
	GND_PI <--> GND_m0

	BCM23 <--> OUT_l1

	BCM24 <--> OUT_l2

```
> This is just an illustration to avoid overly complex graphics. Please correctly connect VCC and GND.

```bash
$ make xtrack_all_456.py
----->> layer_python - /work/codebase/lankahsu520/RPiP9/python


----->> run xtrack_all_456.py
PYTHONPATH=/work/codebase/lankahsu520/RPiP9/python ./xtrack_all_456.py -d 3
[25239/1982067776] xtrack_api.py|threadx_handler:0110 - looping ... (l2: 0, bcmid:24)
[25239/1982067776] xtrack_api.py|cond_sleep:0130 - wait ... (l2: 0, bcmid: 24)mid:23)

[25239/1972368448] xtrack_api.py|cond_sleep:0130 - wait ... (l1: 0, bcmid: 23)
[25239/1951396928] xtrack_api.py|threadx_handler:0110 - looping ... (r1: 0, bcmid:15)
[25239/1951396928] xtrack_api.py|cond_sleep:0130 - wait ... (r1: 0, bcmid: 15)
[25239/1961882688] xtrack_api.py|threadx_handler:0110 - looping ... (m0: 0, bcmid:18)
[25239/1961882688] xtrack_api.py|cond_sleep:0130 - wait ... (m0: 0, bcmid: 18)
[25239/1940911168] xtrack_api.py|threadx_handler:0110 - looping ... (r2: 0, bcmid:14)
[25239/1940911168] xtrack_api.py|cond_sleep:0130 - wait ... (r2: 0, bcmid: 14)
[25239/1996454720] rpip9gpio.py|linkGPIO:0050 - call GPIO.setmode ... (gpioXmode: 11)
[25239/1996454720] rpip9gpio.py|linkGPIO:0073 - CONTROL_NORMAL ... (key: l2, bcmid: 24, direction: 1)
[25239/1996454720] rpip9gpio.py|linkGPIO:0073 - CONTROL_NORMAL ... (key: l1, bcmid: 23, direction: 1)
[25239/1996454720] rpip9gpio.py|linkGPIO:0073 - CONTROL_NORMAL ... (key: m0, bcmid: 18, direction: 1)
[25239/1996454720] rpip9gpio.py|linkGPIO:0073 - CONTROL_NORMAL ... (key: r1, bcmid: 15, direction: 1)
[25239/1996454720] rpip9gpio.py|linkGPIO:0073 - CONTROL_NORMAL ... (key: r2, bcmid: 14, direction: 1)
[25239/1996454720] xtrack_api.py|start:0204 - call add_event_detect ...
[25239/1996454720] xtrack_api.py|start:0204 - call add_event_detect ...
[25239/1996454720] xtrack_api.py|start:0204 - call add_event_detect ...
[25239/1996454720] xtrack_api.py|start:0204 - call add_event_detect ...
[25239/1996454720] xtrack_api.py|start:0204 - call add_event_detect ...
[25239/1996454720] xtrack_api.py|keyboard_recv:0136 - press q to quit the loop (enter: start, space: pause) ...
[25239/1996454720] xtrack_api.py|threadx_run_loop:0093 - run in loop ... (l2: 0, bcmid: 24)
[25239/1996454720] xtrack_api.py|threadx_run_loop:0093 - run in loop ... (l1: 0, bcmid: 23)
[25239/1996454720] xtrack_api.py|threadx_run_loop:0093 - run in loop ... (m0: 0, bcmid: 18)
[25239/1996454720] xtrack_api.py|threadx_run_loop:0093 - run in loop ... (r1: 0, bcmid: 15)
[25239/1982067776] xtrack_api.py|cond_sleep:0130 - wait ... (l2: 0, bcmid: 24)
[25239/1972368448] xtrack_api.py|cond_sleep:0130 - wait ... (l1: 0, bcmid: 23)
[25239/1996454720] xtrack_api.py|threadx_run_loop:0093 - run in loop ... (r2: 0, bcmid: 14)
[25239/1961882688] xtrack_api.py|cond_sleep:0130 - wait ... (m0: 0, bcmid: 18)
[25239/1951396928] xtrack_api.py|cond_sleep:0130 - wait ... (r1: 0, bcmid: 15)
[25239/1940911168] xtrack_api.py|cond_sleep:0130 - wait ... (r2: 0, bcmid: 14)
[25239/1930425408] xtrack_api.py|edge_detect_cb:0077 - (m0: 1, bcmid: 18)
[25239/1930425408] xtrack_api.py|edge_detect_cb:0077 - (m0: 0, bcmid: 18)
[25239/1930425408] xtrack_api.py|edge_detect_cb:0077 - (m0: 1, bcmid: 18)
[25239/1930425408] xtrack_api.py|edge_detect_cb:0077 - (m0: 0, bcmid: 18)
[25239/1930425408] xtrack_api.py|edge_detect_cb:0077 - (m0: 1, bcmid: 18)
[25239/1930425408] xtrack_api.py|edge_detect_cb:0077 - (m0: 0, bcmid: 18)
[25239/1996454720] xtrack_api.py|release:0151 - (is_quit: 0, gpioXlnk: 1)
[25239/1982067776] xtrack_api.py|threadx_handler:0118 - Bye-Bye !!! (l2: 0, bcmid:24)
[25239/1972368448] xtrack_api.py|threadx_handler:0118 - Bye-Bye !!! (l1: 0, bcmid:23)
[25239/1961882688] xtrack_api.py|threadx_handler:0118 - Bye-Bye !!! (m0: 0, bcmid:18)
[25239/1951396928] xtrack_api.py|threadx_handler:0118 - Bye-Bye !!! (r1: 0, bcmid:15)
[25239/1940911168] xtrack_api.py|threadx_handler:0118 - Bye-Bye !!! (r2: 0, bcmid:14)
[25239/1996454720] xtrack_api.py|release:0164 - call GPIO.cleanup ...
[25239/1996454720] xtrack_all_456.py|main:0120 - Bye-Bye !!! (is_quit: 1)

```

#### - ultrasonic_123.py : [HC-SR04](https://datasheetspdf.com/pdf/1380138/ETC1/HC-SR04/1), Ultrasonic Sensor example

> 包含了 GPIO.IN 和 GPIO.OUT 操作。
>
> 請使用者自行調整 "edge"，在遍尋網路上的示範裏少有的。

![ultrasonic01](./images/ultrasonic01.jpg)

```mermaid
flowchart LR
	subgraph ultrasonic
		VCC[VCC]
		Trigger[Trigger]
		Echo[Echo]
		GND[GND]
	end
	subgraph "Raspberry Pi"
		BCM5[BCM 5]
		BCM6[BCM 6]
		5V_PI[5V]
		GND_PI[GND]
	end
	BCM5 <--> Trigger
	BCM6 <--> Echo
	5V_PI <--> VCC
	GND_PI <--> GND
```

```bash
 $ make ultrasonic_123.py
----->> layer_python - /work/codebase/lankahsu520/RPiP9/python


----->> run ultrasonic_123.py
PYTHONPATH=/work/codebase/lankahsu520/RPiP9/python ./ultrasonic_123.py -d 3
[7089/0000] rpip9gpio.py|linkGPIO:0043 - call GPIO.setmode ... (gpioXmode: 11)
[7089/-001] rpip9gpio.py|linkGPIO:0061 - call GPIO.setup - CONTROL_NORMAL ... (key: trigger, bcmid: 5, direction: 0)
[7089/-001] rpip9gpio.py|linkGPIO:0061 - call GPIO.setup - CONTROL_NORMAL ... (key: echo, bcmid: 6, direction: 1)
[7089/-001] ultrasonic_api.py|threadx_handler:0109 - looping ... (use_edge: 2, trigger: 5, echo: 6)
[7089/-001] ultrasonic_api.py|threadx_handler:0113 - call add_event_detect ...
[7089/-001] ultrasonic_api.py|startx:0152 - (pause: 1, use_edge: 2)
[7089/-001] ultrasonic_api.py|keyboard_recv:0176 - press q to quit the loop (enter:start, space:pause) ...
[7089/-001] ultrasonic_api.py|watch:0053 - (distance: 7.2577595710754395 cm)
[7089/-001] ultrasonic_api.py|watch:0053 - (distance: 9.073221683502197 cm)
[7089/-001] ultrasonic_api.py|watch:0053 - (distance: 10.303974151611328 cm)
[7089/-001] ultrasonic_api.py|watch:0053 - (distance: 9.392154216766357 cm)
[7089/-001] ultrasonic_api.py|watch:0053 - (distance: 9.159088134765625 cm)
[7089/-001] ultrasonic_api.py|watch:0053 - (distance: 9.6701979637146 cm)
[7089/-001] ultrasonic_api.py|watch:0053 - (distance: 9.179532527923584 cm)
[7089/-001] ultrasonic_api.py|watch:0053 - (distance: 9.085488319396973 cm)
[7089/-001] ultrasonic_api.py|watch:0053 - (distance: 9.416687488555908 cm)
[7089/-001] ultrasonic_api.py|watch:0053 - (distance: 8.316779136657715 cm)
[7089/-001] ultrasonic_api.py|watch:0053 - (distance: 9.608864784240723 cm)
[7089/-001] ultrasonic_api.py|watch:0053 - (distance: 9.64975357055664 cm)
[7089/-001] ultrasonic_api.py|watch:0053 - (distance: 5.973851680755615 cm)

```
# 6. License

RPiP9 is under the New BSD License (BSD-3-Clause).


# 7. Documentation
Run an example and read it.

![RaspberryPi3B01](./images/RaspberryPi3B01.jpg)

![RaspberryPi3B02](./images/RaspberryPi3B02.jpg)

# Appendix

# I. Study

## I.1. [Servo Motor Control Using Raspberry Pi](https://www.donskytech.com/servo-motor-control-using-raspberry-pi/)

## I.2. [【树莓派/入门】使用MAX30102测量血氧浓度](https://blog.csdn.net/qq_33446100/article/details/128537113)

## I.3. [Raspberry Pi Pinout](https://pinout.xyz/)

![pinout.xyz](./images/pinout.xyz.png)

# II. Debug

## II.1. Can’t connect to pigpio at localhost(8888)

```bash
$ sudo vi /lib/systemd/system/pigpiod.service
ExecStart=/usr/bin/pigpiod -l -n 127.0.0.1

$ sudo netstat -tulpn | grep pigpiod
$ sudo service pigpiod start
$ sudo systemctl status pigpiod
$ sudo systemctl enable pigpiod
```

# III. Glossary