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

app_list = []
is_quit = 0
app_apps = {
	"dbg_more": DBG_LVL_INFO
	,"keyboard": 1
}

def app_start():
	global app_apps

	#DBG_ER_LN("(dbg_more: {})".format( app_apps["dbg_more"] ))

	#usonic_mgr = ultrasonic_ctx(edge_mode=ULTRASONIC_EDGE_LOOP, dbg_more=app_apps["dbg_more"])
	#usonic_mgr = ultrasonic_ctx(edge_mode=ULTRASONIC_EDGE_WAIT, dbg_more=app_apps["dbg_more"])
	#usonic_mgr = ultrasonic_ctx(edge_mode=ULTRASONIC_EDGE_EVENT, dbg_more=app_apps["dbg_more"])
	usonic_mgr = ultrasonic_ctx(edge_mode=ULTRASONIC_EDGE_DEFAULT, dbg_more=app_apps["dbg_more"])
	app_watch(usonic_mgr)
	usonic_mgr.start( app_apps )

def app_watch(app_ctx):
	global app_list

	app_list.append( app_ctx )

def app_release():
	global app_list

	DBG_DB_LN("{}".format(DBG_TXT_ENTER))

	for x in app_list:
		try:
			objname = DBG_NAME(x)
			if not x.release is None:
				DBG_DB_LN("call {}.release ...".format( objname ) )
				x.release() # No handlers could be found for logger "google.api_core.bidi"
		except Exception:
			pass
	DBG_DB_LN("{}".format(DBG_TXT_DONE))

def app_stop():
	global is_quit

	if ( is_quit == 0 ):
		is_quit = 1

def app_exit():
	app_stop()
	app_release()
	DBG_DB_LN("{}".format(DBG_TXT_DONE))

def show_usage(argv):
	print("Usage: {} <options...>".format(argv[0]) )
	print("  -h, --help")
	print("  -k, --key")
	print("(sudo systemctl status pigpiod)")
	print("(sudo service pigpiod start)\n")
	app_exit()
	sys.exit(0)

def parse_arg(argv):
	global app_apps

	try:
		opts,args = getopt.getopt(argv[1:], "hd:k", ["help", "debug", "key"]);
	except getopt.GetoptError:
		show_usage(argv)

	#print (opts)
	#print (args)

	if (len(opts) > 0):
		for opt, arg in opts:
			if opt in ("-h", "--help"):
				show_usage(argv)
			elif opt in ("-d", "--debug"):
				app_apps["dbg_more"] = dbg_debug_helper( int(arg) )
			elif opt in ("-k", "--key"):
				app_apps["keyboard"] = 1
			else:
				print ("(opt: {})".format(opt))
	else:
		show_usage(argv)

def signal_handler(sig, frame):
	if sig in (signal.SIGINT, signal.SIGTERM):
		app_exit()
		return
	sys.exit(0)

def main(argv):
	global app_apps

	signal.signal(signal.SIGINT, signal_handler)
	signal.signal(signal.SIGTERM, signal_handler)

	parse_arg(argv)

	app_start()

	app_exit()
	DBG_WN_LN("{} (is_quit: {})".format(DBG_TXT_BYE_BYE, is_quit))

if __name__ == "__main__":
	main(sys.argv[0:])
