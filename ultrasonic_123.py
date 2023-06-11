#!/usr/bin/env python3
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

from ultrasonic_api import *

#usonic_mgr = ultrasonic_ctx(edge_mode=ULTRASONIC_EDGE_LOOP)
#usonic_mgr = ultrasonic_ctx(edge_mode=ULTRASONIC_EDGE_WAIT)
#usonic_mgr = ultrasonic_ctx(edge_mode=ULTRASONIC_EDGE_EVENT)
usonic_mgr = ultrasonic_ctx(edge_mode=ULTRASONIC_EDGE_DEFAULT)
usonic_mgr.startx("trigger")
usonic_mgr.keyboard_recv()
