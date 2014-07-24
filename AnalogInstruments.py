"""
Analog Instruments version 1.1
By NieXS

I'd like to thank Nyowa225 for making his glorious RevHunter app, which allowed
me to learn how to write this.  This app uses the shared memory library that is
bundled in his app.

Feel free  to  modify and redistribute  this app  in whichever ways you like as
long as you don't make money off it. Suggestions, (constructive) criticism, and
of course bug reports are always welcome.
"""

import sys
sys.path.insert(0,'apps/python/AnalogInstruments/dll')
import ac
import acsys
import math
import os
from sm_nfo.sim_info import SimInfo
from telemetry_client import InternalTelemetryClient
sim_info = SimInfo()
import configparser

# Change settings in the ini file!

# State stuff
have_setup = 0
shift_light_drawn = False
sl_timer = 0
tyre_optimal_temp = range(85,101)
max_boost = 0.1
max_fuel = 1
fuel_icon_warning_path = "apps/python/AnalogInstruments/images/fuel icon warning.png"
dt_ratio = 1
draw_boost_gauge = True
		
telemetry_client = InternalTelemetryClient()

def parse_color(a):
	if len(a) != 9:
		return [1.0,1.0,1.0,1.0]
	else:
		return [int(a[1:3],16)/255,int(a[3:5],16)/255,int(a[5:7],16)/255,int(a[7:9],16)/255]

def acMain(ac_version):
	global imperial, debug_mode, window_x_pos, window_y_pos, tyre_mon_xpos, tyre_mon_ypos
	global gear_color, gear_background, speed_color, speed_background, throttle_gauge_color, brake_gauge_color, clutch_gauge_color, boost_bar_color, fuel_bar_color
	global draw_digital_speedo, draw_shift_light, draw_gear_indicator, draw_speedometer, draw_tachometer, draw_odometer, draw_g_meter, draw_boost_gauge
	global draw_fuel_gauge, draw_throttle_gauge, draw_brake_gauge, draw_clutch_gauge, draw_tyre_monitor, draw_background
	global tach_needle_end, speedo_needle_end, tach_radius, speedo_radius, rpm_pivot_y, speed_pivot_y, rpm_pivot_x, speed_pivot_x, speedo_tl_x, speedo_tl_y
	global speedo_total_width, speedo_total_height
	global tach_redline_color, tach_bigline_color, tach_smallline_color, tach_needle_color1
	global speedo_bigline_color, speedo_smallline_color, speedo_needle_color1
	global throttle_gauge_inner_radius, throttle_gauge_outer_radius, throttle_gauge_min_y, throttle_gauge_max_y
	global brake_gauge_inner_radius, brake_gauge_outer_radius, brake_gauge_min_y, brake_gauge_max_y
	global clutch_gauge_inner_radius, clutch_gauge_outer_radius, clutch_gauge_min_y, clutch_gauge_max_y
	global throttle_gauge_root_x, throttle_gauge_root_y
	global brake_gauge_root_x, brake_gauge_root_y
	global clutch_gauge_root_x, clutch_gauge_root_y
	global throttle_gauge_right, brake_gauge_right, clutch_gauge_right
	global boost_radius, fuel_radius, boost_pivot_y, fuel_pivot_y, boost_pivot_x, fuel_pivot_x, boost_needle_end, fuel_needle_end, boost_needle_color, fuel_needle_color
	global odometer_fg, odometer_bg, g_meter_range, g_meter_x_anchor, g_meter_y_anchor, g_meter_opacity, window_width, window_height, background_image_path, background_image_path_noboost
	global tyre_monitor_opacity, g_meter_opacity
	global window, debug_label, indicated_max_rpm
	global flt_label1, frt_label1, rlt_label1, rrt_label1
	global flt_label2, frt_label2, rlt_label2, rrt_label2
	global fuel_warning_label
	global config
	global telemetry_client
	global draw_abs_status, draw_tcs_status, abs_label, abs_off_label, tcs_label, tcs_off_label
	global gear_x, gear_y, shift_light_x, shift_light_y, shift_light_radius, gear_width, gear_height
	global tach_min_angle, tach_max_angle, speedo_min_angle, speedo_max_angle
	global shift_light_on_color, shift_light_off_color
	global rpms_file
	config_file = configparser.ConfigParser()
	config_file.read('apps/python/AnalogInstruments/settings.ini')
	config = config_file[config_file['settings']['theme']]
	rpms_file = configparser.ConfigParser()
	rpms_file.read('apps/python/AnalogInstruments/rpms.ini')

	# SETTINGS #

	# Change this to 'True' to have speed measured in MPH
	imperial = config.getboolean('imperial')
	# Debug mode (basically just some numbers)
	debug_mode = config.getboolean('debug_mode')
	# Main window positions, change those if you're not using a single monitor 1080p setup
	window_x_pos  = int(config['window_x_pos'])# (Your horz. res-1320)/2
	window_y_pos  = int(config['window_y_pos']) # Your vert. res - 250
	# These are relative to the window's position
	tyre_mon_xpos = int(config['tyre_mon_x_pos'])# 20 px from the left on single mon 1080p
	tyre_mon_ypos = int(config['tyre_mon_y_pos'])# 920 px from the top
	# Color settings
	gear_color           = parse_color(config['gear_color'])
	gear_background      = parse_color(config['gear_background'])
	speed_color          = parse_color(config['digi_speedo_color'])
	speed_background     = parse_color(config['digi_speedo_background'])
	throttle_gauge_color = parse_color(config['throttle_gauge_color'])
	brake_gauge_color    = parse_color(config['brake_gauge_color'])
	clutch_gauge_color   = parse_color(config['clutch_gauge_color'])
	boost_bar_color      = parse_color(config['boost_bar_color']) 
	fuel_bar_color       = parse_color(config['fuel_bar_color'])
	shift_light_on_color = parse_color(config['shift_light_on_color'])
	shift_light_off_color = parse_color(config['shift_light_off_color'])
	# Some more settings, hopefully pretty self-explanatory
	draw_digital_speedo = config.getboolean('draw_digital_speedo')
	draw_shift_light    = config.getboolean('draw_shift_light')
	draw_gear_indicator = config.getboolean('draw_gear_indicator')
	draw_speedometer    = config.getboolean('draw_speedometer')
	draw_tachometer     = config.getboolean('draw_tachometer')
	draw_odometer       = config.getboolean('draw_odometer')
	draw_g_meter        = config.getboolean('draw_g_meter')
	draw_boost_gauge    = config.getboolean('draw_boost_gauge')
	draw_fuel_gauge     = config.getboolean('draw_fuel_gauge')
	draw_throttle_gauge = config.getboolean('draw_throttle_gauge')
	draw_brake_gauge    = config.getboolean('draw_brake_gauge')
	draw_clutch_gauge   = config.getboolean('draw_clutch_gauge')
	draw_tyre_monitor   = config.getboolean('draw_tyre_monitor')
	draw_background     = config.getboolean('draw_background')
	draw_abs_status     = config.getboolean('draw_abs_status')
	draw_tcs_status     = config.getboolean('draw_tcs_status')

	# Dimensions of things, mess with those at your own risk
	tach_needle_end     = int(config['tach_needle_end'])
	speedo_needle_end   = int(config['speedo_needle_end'])
	tach_radius         = int(config['tach_radius'])
	speedo_radius       = int(config['speedo_radius'])
	rpm_pivot_y         = int(config['tach_y_anchor'])
	speed_pivot_y       = int(config['speedo_y_anchor'])
	rpm_pivot_x         = int(config['tach_x_anchor'])
	speed_pivot_x       = int(config['speedo_x_anchor'])
	speedo_tl_x         = int(config['digi_speedo_x'])
	speedo_tl_y         = int(config['digi_speedo_y'])
	speedo_total_width  = int(config['digi_speedo_width'])
	speedo_total_height = int(config['digi_speedo_height'])
	tach_min_angle      = int(config['tach_min_angle'])
	tach_max_angle      = int(config['tach_max_angle'])
	speedo_min_angle    = int(config['speedo_min_angle'])
	speedo_max_angle    = int(config['speedo_max_angle'])

	tach_redline_color = parse_color(config['tach_redline_color'])
	tach_bigline_color = parse_color(config['tach_bigline_color'])
	tach_smallline_color = parse_color(config['tach_smallline_color'])
	tach_needle_color1 = parse_color(config['tach_needle_color1'])

	speedo_bigline_color = parse_color(config['speedo_bigline_color'])
	speedo_smallline_color = parse_color(config['speedo_smallline_color'])
	speedo_needle_color1 = parse_color(config['speedo_needle_color1'])

	# G-Meter: 500-820
	# Brake/Throttle Max Y: 70 Min: 160
	throttle_gauge_inner_radius = int(config['throttle_gauge_inner_radius'])
	throttle_gauge_outer_radius = int(config['throttle_gauge_outer_radius'])
	throttle_gauge_min_y        = int(config['throttle_gauge_min_y'])
	throttle_gauge_max_y        = int(config['throttle_gauge_max_y'])
	throttle_gauge_root_x       = int(config['throttle_gauge_root_x'])
	throttle_gauge_root_y       = int(config['throttle_gauge_root_y'])
	throttle_gauge_right        = config.getboolean('throttle_gauge_right')
	
	brake_gauge_inner_radius = int(config['brake_gauge_inner_radius'])
	brake_gauge_outer_radius = int(config['brake_gauge_outer_radius'])
	brake_gauge_min_y        = int(config['brake_gauge_min_y'])
	brake_gauge_max_y        = int(config['brake_gauge_max_y'])
	brake_gauge_root_x       = int(config['brake_gauge_root_x'])
	brake_gauge_root_y       = int(config['brake_gauge_root_y'])
	brake_gauge_right        = config.getboolean('brake_gauge_right')
	
	clutch_gauge_inner_radius = int(config['clutch_gauge_inner_radius'])
	clutch_gauge_outer_radius = int(config['clutch_gauge_outer_radius'])
	clutch_gauge_min_y        = int(config['clutch_gauge_min_y'])
	clutch_gauge_max_y        = int(config['clutch_gauge_max_y'])
	clutch_gauge_root_x       = int(config['clutch_gauge_root_x'])
	clutch_gauge_root_y       = int(config['clutch_gauge_root_y'])
	clutch_gauge_right        = config.getboolean('clutch_gauge_right')


	boost_radius     = int(config['boost_radius'])
	fuel_radius      = int(config['fuel_radius'])
	boost_pivot_y    = int(config['boost_y_anchor'])
	fuel_pivot_y     = int(config['fuel_y_anchor'])
	boost_pivot_x    = int(config['boost_x_anchor'])
	fuel_pivot_x     = int(config['fuel_x_anchor'])
	boost_needle_end = int(config['boost_needle_end'])
	fuel_needle_end  = int(config['fuel_needle_end'])
	boost_needle_color = parse_color(config['boost_needle_color'])
	fuel_needle_color = parse_color(config['fuel_needle_color'])


	odometer_fg = parse_color(config['odometer_foreground'])
	odometer_bg = parse_color(config['odometer_background'])

	tyre_monitor_opacity = float(config['tyre_monitor_opacity'])

	g_meter_range = int(config['g_meter_range'])
	g_meter_x_anchor = int(config['g_meter_x_anchor'])
	g_meter_y_anchor = int(config['g_meter_y_anchor'])
	g_meter_opacity = float(config['g_meter_opacity'])
	
	gear_x = int(config['gear_x'])
	gear_y = int(config['gear_y'])
	gear_width = int(config['gear_width'])
	gear_height = int(config['gear_height'])
	shift_light_x = int(config['shift_light_x'])
	shift_light_y = int(config['shift_light_y'])
	shift_light_radius = int(config['shift_light_radius'])

	# Kind of configurable but you'll have change most of the dimensions above so not recommended
	window_width  = int(config['window_width'])
	window_height = int(config['window_height'])
	background_image_path = config['background_path']
	background_image_path_noboost = config['background_noboost_path']
	abs_img = config['abs_img']
	abs_off_img = config['abs_off_img']
	tcs_img = config['tcs_img']
	tcs_off_img = config['tcs_off_img']
	window = ac.newApp("AnalogInstruments")
	ac.setTitle(window," ")
	ac.setBackgroundOpacity(window,0)
	ac.drawBorder(window,0)
	ac.setIconPosition(window,0,-10000)
	if draw_background:
		ac.drawBackground(window,1)
		ac.setBackgroundTexture(window,background_image_path)
	ac.setSize(window,window_width,window_height)
	ac.setPosition(window,window_x_pos,window_y_pos)
	debug_label = ac.addLabel(window,"")
	ac.setPosition(debug_label,20,window_height/10*9)
	ac.addRenderCallback(window,onWindowRender)
	# Setting up the tyre monitor labels (this can be done here because it doesn't depend on any car info)
	if draw_tyre_monitor:
		flt_label1 = ac.addLabel(window," ")
		ac.setPosition(flt_label1,tyre_mon_xpos+37,tyre_mon_ypos+5)
		flt_label2 = ac.addLabel(window," ")
		ac.setPosition(flt_label2,tyre_mon_xpos+37,tyre_mon_ypos+37)
		frt_label1 = ac.addLabel(window," ")
		ac.setPosition(frt_label1,tyre_mon_xpos+117,tyre_mon_ypos+5)
		frt_label2 = ac.addLabel(window," ")
		ac.setPosition(frt_label2,tyre_mon_xpos+117,tyre_mon_ypos+37)
		rlt_label1 = ac.addLabel(window," ")
		ac.setPosition(rlt_label1,tyre_mon_xpos+37,tyre_mon_ypos+101)
		rlt_label2 = ac.addLabel(window," ")
		ac.setPosition(rlt_label2,tyre_mon_xpos+37,tyre_mon_ypos+133)
		rrt_label1 = ac.addLabel(window," ")
		ac.setPosition(rrt_label1,tyre_mon_xpos+117,tyre_mon_ypos+101)
		rrt_label2 = ac.addLabel(window," ")
		ac.setPosition(rrt_label2,tyre_mon_xpos+117,tyre_mon_ypos+133)
	if draw_fuel_gauge:
		fuel_warning_label = ac.addLabel(window,"")
		ac.setSize(fuel_warning_label,12,14)
		ac.setPosition(fuel_warning_label,fuel_pivot_x - 6,fuel_pivot_y - 30)
		ac.setBackgroundTexture(fuel_warning_label,fuel_icon_warning_path)
	if draw_abs_status:
		abs_label = ac.addLabel(window,"")
		ac.setSize(abs_label,window_width,window_height)
		ac.setPosition(abs_label,0,0)
		ac.setBackgroundTexture(abs_label,abs_img)
		abs_off_label = ac.addLabel(window,"")
		ac.setSize(abs_off_label,window_width,window_height)
		ac.setPosition(abs_off_label,0,0)
		ac.setBackgroundTexture(abs_off_label,abs_off_img)
	if draw_tcs_status:
		tcs_label = ac.addLabel(window,"")
		ac.setSize(tcs_label,window_width,window_height)
		ac.setPosition(tcs_label,0,0)
		ac.setBackgroundTexture(tcs_label,tcs_img)
		tcs_off_label = ac.addLabel(window,"")
		ac.setSize(tcs_off_label,window_width,window_height)
		ac.setPosition(tcs_off_label,0,0)
		ac.setBackgroundTexture(tcs_off_label,tcs_off_img)
	return "Analog Instruments"

def acShutdown():
	telemetry_client.disconnect()

def drawOdometer():
	global posting
	root_x = speed_pivot_x - 48
	root_y = speed_pivot_y - 50
	fg = odometer_fg
	bg = odometer_bg
	distance = sim_info.graphics.distanceTraveled/1000
	if imperial:
		distance = distance / 1.632
	s = "%3.1f" % (sim_info.graphics.distanceTraveled/1000)
	# zero-padding
	while len(s) < 5:
		s = "0" + s
	i = 0
	for c in s:
		if c != '.':
			drawNineSegment(root_x+96-24*(4-i),root_y,24,36,c,fg,bg)
			i = i + 1
	# Decimal point
	ac.glColor4f(0.0,0.0,0.0,1.0)
	ac.glQuad(root_x+48+22,root_y+30,4,4)

def drawBoostGauge():
	global max_boost
	boost = ac.getCarState(0,acsys.CS.TurboBoost)
	if boost > max_boost:
		max_boost = boost
	rad = (boost/max_boost)*math.pi # 180 deg range so it's easy
	outer_radius = boost_radius
	inner_radius = outer_radius - 4
	for i in range(0,int((boost/max_boost)*100),1):
		# p3 p4 - rad2
		# p1 p2 - rad1
		rad1 = math.pi - math.pi*(i/100)
		rad2 = math.pi - math.pi*((i+1)/100)
		
		p1_x = math.cos(rad1)*outer_radius + boost_pivot_x
		p1_y = boost_pivot_y - math.sin(rad1)*outer_radius
		p2_x = math.cos(rad1)*inner_radius + boost_pivot_x
		p2_y = boost_pivot_y - math.sin(rad1)*inner_radius
		p3_x = math.cos(rad2)*outer_radius + boost_pivot_x
		p3_y = boost_pivot_y - math.sin(rad2)*outer_radius
		p4_x = math.cos(rad2)*inner_radius + boost_pivot_x
		p4_y = boost_pivot_y - math.sin(rad2)*inner_radius
		
		ac.glBegin(2)
		ac.glColor4f(boost_bar_color[0],boost_bar_color[1],boost_bar_color[2],boost_bar_color[3])
		ac.glVertex2f(p1_x,p1_y)
		ac.glVertex2f(p2_x,p2_y)
		ac.glVertex2f(p3_x,p3_y)
		ac.glEnd()
		ac.glBegin(2)
		ac.glColor4f(boost_bar_color[0],boost_bar_color[1],boost_bar_color[2],boost_bar_color[3])
		ac.glVertex2f(p3_x,p3_y)
		ac.glVertex2f(p4_x,p4_y)
		ac.glVertex2f(p2_x,p2_y)
		ac.glEnd()
	# Needle
	rad = math.pi - rad
	bigend_x    = math.cos(rad)*boost_radius + boost_pivot_x
	bigend_y    = boost_pivot_y - math.sin(rad)*boost_radius
	littleend_x = math.cos(rad+math.pi)*boost_needle_end + boost_pivot_x
	littleend_y = boost_pivot_y - math.sin(rad+math.pi)*boost_needle_end
	# p1 p2 = big end
	# p3 p4 = little end
	p1_x = math.cos(rad+math.pi/2) + bigend_x
	p1_y = bigend_y - math.sin(rad+math.pi/2)
	p2_x = math.cos(rad-math.pi/2) + bigend_x
	p2_y = bigend_y - math.sin(rad-math.pi/2)
	p3_x = math.cos(rad+math.pi/2) + littleend_x
	p3_y = littleend_y - math.sin(rad+math.pi/2)
	p4_x = math.cos(rad-math.pi/2) + littleend_x
	p4_y = littleend_y - math.sin(rad-math.pi/2)
	
	ac.glBegin(2)
	ac.glColor4f(boost_needle_color[0],boost_needle_color[1],boost_needle_color[2],boost_needle_color[3])
	ac.glVertex2f(p1_x,p1_y)
	ac.glVertex2f(p2_x,p2_y)
	ac.glVertex2f(p3_x,p3_y)
	ac.glEnd()
	ac.glBegin(2)
	ac.glColor4f(boost_needle_color[0],boost_needle_color[1],boost_needle_color[2],boost_needle_color[3])
	ac.glVertex2f(p2_x,p2_y)
	ac.glVertex2f(p3_x,p3_y)
	ac.glVertex2f(p4_x,p4_y)
	ac.glEnd()

def drawFuelGauge():
	global max_fuel, fuel_warning_label
	fuel = sim_info.physics.fuel
	rad = (fuel/max_fuel)*math.pi # 180 deg range so it's easy
	outer_radius = fuel_radius 
	inner_radius = outer_radius - 4
	if fuel/max_fuel > 0.125:
		ac.setPosition(fuel_warning_label,-10000,0)
	else:
		ac.setPosition(fuel_warning_label,fuel_pivot_x - 6,fuel_pivot_y - 30)
	for i in range(0,int((fuel/max_fuel)*100),1):
		# p3 p4 - rad2
		# p1 p2 - rad1
		rad1 = math.pi - math.pi*(i/100)
		rad2 = math.pi - math.pi*((i+1)/100)
		
		p1_x = math.cos(rad1)*outer_radius + fuel_pivot_x
		p1_y = fuel_pivot_y - math.sin(rad1)*outer_radius
		p2_x = math.cos(rad1)*inner_radius + fuel_pivot_x
		p2_y = fuel_pivot_y - math.sin(rad1)*inner_radius
		p3_x = math.cos(rad2)*outer_radius + fuel_pivot_x
		p3_y = fuel_pivot_y - math.sin(rad2)*outer_radius
		p4_x = math.cos(rad2)*inner_radius + fuel_pivot_x
		p4_y = fuel_pivot_y - math.sin(rad2)*inner_radius
		
		ac.glBegin(2)
		ac.glColor4f(fuel_bar_color[0],fuel_bar_color[1],fuel_bar_color[2],fuel_bar_color[3])
		ac.glVertex2f(p1_x,p1_y)
		ac.glVertex2f(p2_x,p2_y)
		ac.glVertex2f(p3_x,p3_y)
		ac.glEnd()
		ac.glBegin(2)
		ac.glColor4f(fuel_bar_color[0],fuel_bar_color[1],fuel_bar_color[2],fuel_bar_color[3])
		ac.glVertex2f(p3_x,p3_y)
		ac.glVertex2f(p4_x,p4_y)
		ac.glVertex2f(p2_x,p2_y)
		ac.glEnd()
	# Needle
	rad = math.pi - rad
	bigend_x    = math.cos(rad)*fuel_radius + fuel_pivot_x
	bigend_y    = fuel_pivot_y - math.sin(rad)*fuel_radius
	littleend_x = math.cos(rad+math.pi)*fuel_needle_end + fuel_pivot_x
	littleend_y = fuel_pivot_y - math.sin(rad+math.pi)*fuel_needle_end
	# p1 p2 = big end
	# p3 p4 = little end
	p1_x = math.cos(rad+math.pi/2) + bigend_x
	p1_y = bigend_y - math.sin(rad+math.pi/2)
	p2_x = math.cos(rad-math.pi/2) + bigend_x
	p2_y = bigend_y - math.sin(rad-math.pi/2)
	p3_x = math.cos(rad+math.pi/2) + littleend_x
	p3_y = littleend_y - math.sin(rad+math.pi/2)
	p4_x = math.cos(rad-math.pi/2) + littleend_x
	p4_y = littleend_y - math.sin(rad-math.pi/2)
	
	ac.glBegin(2)
	ac.glColor4f(fuel_needle_color[0],fuel_needle_color[1],fuel_needle_color[2],fuel_needle_color[3])
	ac.glVertex2f(p1_x,p1_y)
	ac.glVertex2f(p2_x,p2_y)
	ac.glVertex2f(p3_x,p3_y)
	ac.glEnd()
	ac.glBegin(2)
	ac.glColor4f(fuel_needle_color[0],fuel_needle_color[1],fuel_needle_color[2],fuel_needle_color[3])
	ac.glVertex2f(p2_x,p2_y)
	ac.glVertex2f(p3_x,p3_y)
	ac.glVertex2f(p4_x,p4_y)
	ac.glEnd()

def drawTachometer(deltaT):
	rpm = ac.getCarState(0,acsys.CS.RPM)
	# degree range: 190..-10
	r = abs(tach_min_angle - tach_max_angle)
	rpm_deg = tach_max_angle - (rpm/indicated_max_rpm)*r
	rpm_rad = math.radians(rpm_deg)
	# Redline
	redline_start = (max_rpm - 500) - (max_rpm % 250)
	for i in range(0,indicated_max_rpm+1,250):
		if i >= redline_start and i+250 <= indicated_max_rpm:
			rad1 = math.radians(tach_max_angle - (i/indicated_max_rpm)*r)
			rad2 = math.radians(tach_max_angle - ((i+250)/indicated_max_rpm)*r)
			p1_x = math.cos(rad1)*tach_radius+rpm_pivot_x
			p1_y = -math.sin(rad1)*tach_radius+rpm_pivot_y
			p2_x = math.cos(rad1)*(tach_radius*9/10)+rpm_pivot_x
			p2_y = -math.sin(rad1)*(tach_radius*9/10)+rpm_pivot_y
			p3_x = math.cos(rad2)*tach_radius+rpm_pivot_x
			p3_y = -math.sin(rad2)*tach_radius+rpm_pivot_y
			p4_x = math.cos(rad2)*(tach_radius*9/10)+rpm_pivot_x
			p4_y = -math.sin(rad2)*(tach_radius*9/10)+rpm_pivot_y
			ac.glBegin(2)
			ac.glColor4f(tach_redline_color[0],tach_redline_color[1],tach_redline_color[2],tach_redline_color[3])
			ac.glVertex2f(p1_x,p1_y)
			ac.glVertex2f(p2_x,p2_y)
			ac.glVertex2f(p3_x,p3_y)
			ac.glEnd()
			ac.glBegin(2)
			ac.glColor4f(tach_redline_color[0],tach_redline_color[1],tach_redline_color[2],tach_redline_color[3])
			ac.glVertex2f(p2_x,p2_y)
			ac.glVertex2f(p3_x,p3_y)
			ac.glVertex2f(p4_x,p4_y)
			ac.glEnd()
		if i % 1000 == 0:
			rad  = math.radians(tach_max_angle - (i/indicated_max_rpm)*r)
			p1_x = math.cos(rad)*tach_radius+rpm_pivot_x
			p1_y = -math.sin(rad)*tach_radius+rpm_pivot_y
			p2_x = math.cos(rad)*(tach_radius*4/5)+rpm_pivot_x
			p2_y = -math.sin(rad)*(tach_radius*4/5)+rpm_pivot_y
			ac.glBegin(0)
			ac.glColor4f(tach_bigline_color[0],tach_bigline_color[1],tach_bigline_color[2],tach_bigline_color[3])
			ac.glVertex2f(p1_x,p1_y)
			ac.glVertex2f(p2_x,p2_y)
			ac.glEnd()
		elif i % 250 == 0 and i != 0:
			rad  = math.radians(tach_max_angle - (i/indicated_max_rpm)*r)
			p1_x = math.cos(rad)*tach_radius+rpm_pivot_x
			p1_y = -math.sin(rad)*tach_radius+rpm_pivot_y
			p2_x = math.cos(rad)*(tach_radius*9.25/10)+rpm_pivot_x
			p2_y = -math.sin(rad)*(tach_radius*9.25/10)+rpm_pivot_y
			ac.glBegin(0)
			ac.glColor4f(tach_smallline_color[0],tach_smallline_color[1],tach_smallline_color[2],tach_smallline_color[3])
			ac.glVertex2f(p1_x,p1_y)
			ac.glVertex2f(p2_x,p2_y)
			ac.glEnd()
	# Needle
	rpm_x       = math.cos(rpm_rad)*(tach_radius-3)+rpm_pivot_x
	rpm_y       = -math.sin(rpm_rad)*(tach_radius-3)+rpm_pivot_y
	rpm_end_x   = math.cos(rpm_rad+math.pi)*tach_needle_end+rpm_pivot_x
	rpm_end_y   = -math.sin(rpm_rad+math.pi)*tach_needle_end+rpm_pivot_y
	
	rpm_p1_x     = rpm_x + math.cos(rpm_rad-math.pi/2)*1.5
	rpm_p1_y     = rpm_y - math.sin(rpm_rad-math.pi/2)*1.5
	rpm_p2_x     = rpm_x + math.cos(rpm_rad+math.pi/2)*1.5
	rpm_p2_y     = rpm_y - math.sin(rpm_rad+math.pi/2)*1.5
	rpm_end_p1_x = rpm_end_x + math.cos(rpm_rad-math.pi/2)*3
	rpm_end_p1_y = rpm_end_y - math.sin(rpm_rad-math.pi/2)*3
	rpm_end_p2_x = rpm_end_x + math.cos(rpm_rad+math.pi/2)*3
	rpm_end_p2_y = rpm_end_y - math.sin(rpm_rad+math.pi/2)*3
	ac.glBegin(2)
	ac.glColor4f(tach_needle_color1[0],tach_needle_color1[1],tach_needle_color1[2],tach_needle_color1[3])
	ac.glVertex2f(rpm_p1_x,rpm_p1_y)
	ac.glVertex2f(rpm_p2_x,rpm_p2_y)
	ac.glVertex2f(rpm_end_p1_x,rpm_end_p1_y)
	ac.glEnd()
	ac.glBegin(2)
	ac.glColor4f(tach_needle_color1[0],tach_needle_color1[1],tach_needle_color1[2],tach_needle_color1[3])
	ac.glVertex2f(rpm_p1_x,rpm_p1_y)
	ac.glVertex2f(rpm_end_p2_x,rpm_end_p2_y)
	ac.glVertex2f(rpm_end_p1_x,rpm_end_p1_y)
	ac.glEnd()

def drawSpeedometer():
	speed = ac.getCarState(0,acsys.CS.DriveTrainSpeed)/dt_ratio #Drivetrain speed seems to be about 75-90% of the real speed wtf
	if imperial:
		speed = speed / 1.632
	# degree range: 190..-10
	r = abs(speedo_min_angle - speedo_max_angle)
	speed_deg = speedo_max_angle - (speed/indicated_max_speed)*r
	speed_rad = math.radians(speed_deg)
	for i in range(0,indicated_max_speed+1,5):
		if i % 20 == 0:
			rad  = math.radians(speedo_max_angle - (i/indicated_max_speed)*r)
			p1_x = math.cos(rad)*speedo_radius+speed_pivot_x
			p1_y = -math.sin(rad)*speedo_radius+speed_pivot_y
			p2_x = math.cos(rad)*(speedo_radius*4/5)+speed_pivot_x
			p2_y = -math.sin(rad)*(speedo_radius*4/5)+speed_pivot_y
			ac.glBegin(0)
			ac.glColor4f(speedo_bigline_color[0],speedo_bigline_color[1],speedo_bigline_color[2],speedo_bigline_color[3])
			ac.glVertex2f(p1_x,p1_y)
			ac.glVertex2f(p2_x,p2_y)
			ac.glEnd()
		elif i % 5 == 0 and i != 0:
			rad  = math.radians(speedo_max_angle - (i/indicated_max_speed)*r)
			p1_x = math.cos(rad)*speedo_radius+speed_pivot_x
			p1_y = -math.sin(rad)*speedo_radius+speed_pivot_y
			p2_x = math.cos(rad)*(speedo_radius*9.25/10)+speed_pivot_x
			p2_y = -math.sin(rad)*(speedo_radius*9.25/10)+speed_pivot_y
			ac.glBegin(0)
			ac.glColor4f(speedo_smallline_color[0],speedo_smallline_color[1],speedo_smallline_color[2],speedo_smallline_color[3])
			ac.glVertex2f(p1_x,p1_y)
			ac.glVertex2f(p2_x,p2_y)
			ac.glEnd()
	# Needle
	speed_x       = math.cos(speed_rad)*(speedo_radius-3)+speed_pivot_x
	speed_y       = -math.sin(speed_rad)*(speedo_radius-3)+speed_pivot_y
	speed_end_x   = math.cos(speed_rad+math.pi)*speedo_needle_end+speed_pivot_x
	speed_end_y   = -math.sin(speed_rad+math.pi)*speedo_needle_end+speed_pivot_y
	
	speed_p1_x     = speed_x + math.cos(speed_rad-math.pi/2)*1.5
	speed_p1_y     = speed_y - math.sin(speed_rad-math.pi/2)*1.5
	speed_p2_x     = speed_x + math.cos(speed_rad+math.pi/2)*1.5
	speed_p2_y     = speed_y - math.sin(speed_rad+math.pi/2)*1.5
	speed_end_p1_x = speed_end_x + math.cos(speed_rad+math.pi/2)*3
	speed_end_p1_y = speed_end_y - math.sin(speed_rad+math.pi/2)*3
	speed_end_p2_x = speed_end_x + math.cos(speed_rad-math.pi/2)*3
	speed_end_p2_y = speed_end_y - math.sin(speed_rad-math.pi/2)*3
	ac.glBegin(2)
	ac.glColor4f(speedo_needle_color1[0],speedo_needle_color1[1],speedo_needle_color1[2],speedo_needle_color1[3])
	ac.glVertex2f(speed_p1_x,speed_p1_y)
	ac.glVertex2f(speed_p2_x,speed_p2_y)
	ac.glVertex2f(speed_end_p1_x,speed_end_p1_y)
	ac.glEnd()
	ac.glBegin(2)
	ac.glColor4f(speedo_needle_color1[0],speedo_needle_color1[1],speedo_needle_color1[2],speedo_needle_color1[3])
	ac.glVertex2f(speed_p1_x,speed_p1_y)
	ac.glVertex2f(speed_end_p2_x,speed_end_p2_y)
	ac.glVertex2f(speed_end_p1_x,speed_end_p1_y)
	ac.glEnd()

def drawTyreMonitor():
	global flt_label1, frt_label1, rlt_label1, rrt_label1 # Temp
	global flt_label2, frt_label2, rlt_label2, rrt_label2 # Pressure
	fl_t, fr_t, rl_t, rr_t = ac.getCarState(0,acsys.CS.CurrentTyresCoreTemp)
	temps = [fl_t, fr_t, rl_t, rr_t]
	fl_p, fr_p, rl_p, rr_p = ac.getCarState(0,acsys.CS.DynamicPressure)
	wheelslip = ac.getCarState(0,acsys.CS.TyreSlip)
	wear      = sim_info.physics.tyreWear
	dirt      = sim_info.physics.tyreDirtyLevel
	ac.setText(flt_label1,"%dC"%fl_t)
	ac.setText(frt_label1,"%dC"%fr_t)
	ac.setText(rlt_label1,"%dC"%rl_t)
	ac.setText(rrt_label1,"%dC"%rr_t)
	# Outside of tyre = white if normal, yellow if losing grip, red if lost grip
	for i in range(0,4):
		outside_color = [1.0,1.0,1.0,tyre_monitor_opacity]
		if wheelslip[i] >= 35000:
			outside_color = [1.0,0.0,0.0,tyre_monitor_opacity]
		elif wheelslip[i] >= 25000:
			percent = (int(wheelslip[i])-25000)/10000
			outside_color = [1.0,(165 - 165*percent)/255,0.0,tyre_monitor_opacity] # Orange
		elif wheelslip[i] >= 10000:
			percent = (int(wheelslip[i])-10000)/15000
			outside_color = [1.0,(255 - 90*percent)/255,0.0,tyre_monitor_opacity]
		elif wheelslip[i] > 7000:
			# 100% = [1.0,1.0,0.0,1.0]
			#   0% = [1.0,1.0,1.0,1.0]
			percent = (int(wheelslip[i])-7000)/3000
			outside_color = [1.0,1.0,1-percent,tyre_monitor_opacity]
		root_x = tyre_mon_xpos
		root_y = tyre_mon_ypos
		if i == 1 or i == 3:
			root_x = root_x + 80
		if i == 2 or i == 3:
			root_y = root_y + 96
		ac.glColor4f(outside_color[0],outside_color[1],outside_color[2],outside_color[3])
		ac.glQuad(root_x,root_y,36,4)
		ac.glQuad(root_x,root_y+4,4,56)
		ac.glQuad(root_x+32,root_y+4,4,56)
		ac.glQuad(root_x,root_y+60,36,4)
		# 28x56
		# Dirty level
		ac.glColor4f(150/255,75/255,0.0,tyre_monitor_opacity)
		ac.glQuad(root_x+4,root_y+60,28,-(56*dirt[i]/5))
		# Inside of tyre = blue if v. cold, light blue if cold, white if normal, yellow if hot, red if v. hot
		inside_color = [1.0,1.0,1.0,tyre_monitor_opacity]
		if temps[i] < (tyre_optimal_temp[0]-25):
			inside_color = [0.0,100.0/255,1.0,tyre_monitor_opacity]
		elif temps[i] < (tyre_optimal_temp[0]-10):
			percent = (-int(temps[i])+tyre_optimal_temp[0])/25
			inside_color = [0.0,(255 - 155*percent)/255,1.0,tyre_monitor_opacity]
		elif temps[i] < tyre_optimal_temp[0]:
			percent = (tyre_optimal_temp[0]-int(temps[i]))/10
			inside_color = [1-percent,1.0,1.0,tyre_monitor_opacity]
		elif int(temps[i]) in tyre_optimal_temp:
			inside_color = [1.0,1.0,1.0,tyre_monitor_opacity]
		elif temps[i] < (tyre_optimal_temp[-1]+15):
			percent = (int(temps[i])-tyre_optimal_temp[-1])/15
			inside_color = [1.0,1.0,1-percent,tyre_monitor_opacity]
		elif temps[i] <= (tyre_optimal_temp[-1]+25):
			percent = (int(temps[i])-tyre_optimal_temp[-1]-15)/10
			inside_color = [1.0,1-percent,0.0,tyre_monitor_opacity]
		else: # DANGER
			inside_color = [1.0,0.0,0.0,tyre_monitor_opacity]
		# no. of bars inside tyre = wear level
		bars = int(wear[i]/10)
		if bars > 9:
			bars = 9
		for j in range(0,bars):
			ac.glColor4f(inside_color[0],inside_color[1],inside_color[2],inside_color[3])
			ac.glQuad(root_x + 6,root_y + 54 - 6*j,24,4)
	ac.setText(flt_label2,"%d psi"%fl_p)
	ac.setText(frt_label2,"%d psi"%fr_p)
	ac.setText(rlt_label2,"%d psi"%rl_p)
	ac.setText(rrt_label2,"%d psi"%rr_p)
	

def drawBrakeGauge():
	global posting, post_time_elapsed, post_total_time
	inner_min_rad = math.asin((brake_gauge_root_y-brake_gauge_min_y)/brake_gauge_inner_radius)
	inner_max_rad = math.asin((brake_gauge_root_y-brake_gauge_max_y)/brake_gauge_inner_radius)
	outer_min_rad = math.asin((brake_gauge_root_y-brake_gauge_min_y)/brake_gauge_outer_radius)
	outer_max_rad = math.asin((brake_gauge_root_y-brake_gauge_max_y)/brake_gauge_outer_radius)
	for i in range(0,int((ac.getCarState(0,acsys.CS.Brake))*100),1):
		# p1 = inner, p2 = outer
		# p3 = inner, p4 = outer
		rad1 = (inner_max_rad-inner_min_rad)/100*i     + inner_min_rad + (math.pi if brake_gauge_right else 0)
		rad2 = (outer_max_rad-outer_min_rad)/100*i     + outer_min_rad + (math.pi if brake_gauge_right else 0)
		rad3 = (inner_max_rad-inner_min_rad)/100*(i+1) + inner_min_rad + (math.pi if brake_gauge_right else 0)
		rad4 = (outer_max_rad-outer_min_rad)/100*(i+1) + outer_min_rad + (math.pi if brake_gauge_right else 0)
		
		p1_x = math.cos(rad1)*brake_gauge_inner_radius + brake_gauge_root_x
		p1_y = brake_gauge_root_y - math.sin(rad1)*brake_gauge_inner_radius
		p2_x = math.cos(rad2)*brake_gauge_outer_radius + brake_gauge_root_x
		p2_y = brake_gauge_root_y - math.sin(rad2)*brake_gauge_outer_radius
		p3_x = math.cos(rad3)*brake_gauge_inner_radius + brake_gauge_root_x
		p3_y = brake_gauge_root_y - math.sin(rad3)*brake_gauge_inner_radius
		p4_x = math.cos(rad4)*brake_gauge_outer_radius + brake_gauge_root_x
		p4_y = brake_gauge_root_y - math.sin(rad4)*brake_gauge_outer_radius
		
		ac.glBegin(2)
		ac.glColor4f(brake_gauge_color[0],brake_gauge_color[1],brake_gauge_color[2],brake_gauge_color[3])
		ac.glVertex2f(p1_x,p1_y)
		ac.glVertex2f(p2_x,p2_y)
		ac.glVertex2f(p3_x,p3_y)
		ac.glEnd()
		ac.glBegin(2)
		ac.glColor4f(brake_gauge_color[0],brake_gauge_color[1],brake_gauge_color[2],brake_gauge_color[3])
		ac.glVertex2f(p3_x,p3_y)
		ac.glVertex2f(p4_x,p4_y)
		ac.glVertex2f(p2_x,p2_y)
		ac.glEnd()

def drawThrottleGauge():
	global posting, post_time_elapsed, post_total_time
	inner_min_rad = math.asin((throttle_gauge_root_y-throttle_gauge_min_y)/throttle_gauge_inner_radius)
	inner_max_rad = math.asin((throttle_gauge_root_y-throttle_gauge_max_y+1)/throttle_gauge_inner_radius)
	outer_min_rad = math.asin((throttle_gauge_root_y-throttle_gauge_min_y)/throttle_gauge_outer_radius)
	outer_max_rad = math.asin((throttle_gauge_root_y-throttle_gauge_max_y+1)/throttle_gauge_outer_radius)
	for i in range(0,int((ac.getCarState(0,acsys.CS.Gas))*100),1):
		# p1 = inner, p2 = outer
		# p3 = inner, p4 = outer
		rad1 = (inner_max_rad-inner_min_rad)/100*(100-i)     - inner_max_rad + (math.pi if throttle_gauge_right else 0)
		rad2 = (outer_max_rad-outer_min_rad)/100*(100-i)     - outer_max_rad + (math.pi if throttle_gauge_right else 0)
		rad3 = (inner_max_rad-inner_min_rad)/100*(100 - i+1) - inner_max_rad + (math.pi if throttle_gauge_right else 0)
		rad4 = (outer_max_rad-outer_min_rad)/100*(100 - i+1) - outer_max_rad + (math.pi if throttle_gauge_right else 0)
		
		p1_x = math.cos(rad1)*throttle_gauge_inner_radius + throttle_gauge_root_x
		p1_y = throttle_gauge_root_y - math.sin(rad1)*throttle_gauge_inner_radius
		p2_x = math.cos(rad2)*throttle_gauge_outer_radius + throttle_gauge_root_x
		p2_y = throttle_gauge_root_y - math.sin(rad2)*throttle_gauge_outer_radius
		p3_x = math.cos(rad3)*throttle_gauge_inner_radius + throttle_gauge_root_x
		p3_y = throttle_gauge_root_y - math.sin(rad3)*throttle_gauge_inner_radius
		p4_x = math.cos(rad4)*throttle_gauge_outer_radius + throttle_gauge_root_x
		p4_y = throttle_gauge_root_y - math.sin(rad4)*throttle_gauge_outer_radius
		
		ac.glBegin(2)
		ac.glColor4f(throttle_gauge_color[0],throttle_gauge_color[1],throttle_gauge_color[2],throttle_gauge_color[3])
		ac.glVertex2f(p1_x,p1_y)
		ac.glVertex2f(p2_x,p2_y)
		ac.glVertex2f(p3_x,p3_y)
		ac.glEnd()
		ac.glBegin(2)
		ac.glColor4f(throttle_gauge_color[0],throttle_gauge_color[1],throttle_gauge_color[2],throttle_gauge_color[3])
		ac.glVertex2f(p3_x,p3_y)
		ac.glVertex2f(p4_x,p4_y)
		ac.glVertex2f(p2_x,p2_y)
		ac.glEnd()

def drawClutchGauge():
	global posting, post_time_elapsed, post_total_time
	inner_min_rad = math.asin((clutch_gauge_root_y-clutch_gauge_min_y)/clutch_gauge_inner_radius)
	inner_max_rad = math.asin((clutch_gauge_root_y-clutch_gauge_max_y+1)/clutch_gauge_inner_radius)
	outer_min_rad = math.asin((clutch_gauge_root_y-clutch_gauge_min_y)/clutch_gauge_outer_radius)
	outer_max_rad = math.asin((clutch_gauge_root_y-clutch_gauge_max_y+1)/clutch_gauge_outer_radius)
	for i in range(0,int((1-ac.getCarState(0,acsys.CS.Clutch))*100),1):
		# p1 = inner, p2 = outer
		# p3 = inner, p4 = outer
		rad1 = (inner_max_rad-inner_min_rad)/100*(100-i)     - inner_max_rad + (math.pi if clutch_gauge_right else 0)
		rad2 = (outer_max_rad-outer_min_rad)/100*(100-i)     - outer_max_rad + (math.pi if clutch_gauge_right else 0)
		rad3 = (inner_max_rad-inner_min_rad)/100*(100 - i+1) - inner_max_rad + (math.pi if clutch_gauge_right else 0)
		rad4 = (outer_max_rad-outer_min_rad)/100*(100 - i+1) - outer_max_rad + (math.pi if clutch_gauge_right else 0)
		
		p1_x = math.cos(rad1)*clutch_gauge_inner_radius + clutch_gauge_root_x
		p1_y = clutch_gauge_root_y - math.sin(rad1)*clutch_gauge_inner_radius
		p2_x = math.cos(rad2)*clutch_gauge_outer_radius + clutch_gauge_root_x
		p2_y = clutch_gauge_root_y - math.sin(rad2)*clutch_gauge_outer_radius
		p3_x = math.cos(rad3)*clutch_gauge_inner_radius + clutch_gauge_root_x
		p3_y = clutch_gauge_root_y - math.sin(rad3)*clutch_gauge_inner_radius
		p4_x = math.cos(rad4)*clutch_gauge_outer_radius + clutch_gauge_root_x
		p4_y = clutch_gauge_root_y - math.sin(rad4)*clutch_gauge_outer_radius
		
		ac.glBegin(2)
		ac.glColor4f(clutch_gauge_color[0],clutch_gauge_color[1],clutch_gauge_color[2],clutch_gauge_color[3])
		ac.glVertex2f(p1_x,p1_y)
		ac.glVertex2f(p2_x,p2_y)
		ac.glVertex2f(p3_x,p3_y)
		ac.glEnd()
		ac.glBegin(2)
		ac.glColor4f(clutch_gauge_color[0],clutch_gauge_color[1],clutch_gauge_color[2],clutch_gauge_color[3])
		ac.glVertex2f(p3_x,p3_y)
		ac.glVertex2f(p4_x,p4_y)
		ac.glVertex2f(p2_x,p2_y)
		ac.glEnd()

def drawGMeter():
	global posting, post_time_elapsed, post_total_time
	# Colors
	c1 = [0.0,200/255,1.0,g_meter_opacity] # Middle one
	c2 = [0.0,150/255,1.0,g_meter_opacity] # Inner
	c3 = [0.0,125/255,1.0,g_meter_opacity] # Middle inner
	c4 = [0.0,100/255,1.0,g_meter_opacity] # Outer
	g = ac.getCarState(0,acsys.CS.AccG)[0]
	# Neg range: 660..511
	# Pos range: 660..809
	l_x = r_x = 0
	pixels = int(abs(g)*(g_meter_range/2.52))
	if abs(g) >= 2.52:
		pixels = g_meter_range # ALL OF THEM
	if g < 0:
		r_x = g_meter_x_anchor
		l_x = r_x - pixels
	else:
		l_x = g_meter_x_anchor
		r_x = l_x + pixels
	t_y = g_meter_y_anchor
	for i in range(0,11,1):
		c = []
		offset = 0
		if i == 0 or i == 1 or i == 9 or i == 10:
			c = c4
			offset = 4
		elif i == 2 or i == 8:
			c = c3
			offset = 2
		elif i == 3 or i == 7:
			c = c3
			offset = 1
		elif i == 4 or i == 6:
			c = c2
			offset = 1
		else:
			c = c1
		if g > 0 and r_x - offset <= l_x:
			continue
		elif g < 0 and l_x + offset >= r_x:
			continue
		l_offset = r_offset = 0
		if g > 0:
			r_offset = - offset
		if g < 0:
			l_offset = offset
		ac.glBegin(0)
		ac.glColor4f(c[0],c[1],c[2],c[3])
		ac.glVertex2f(l_x+l_offset,t_y+i)
		ac.glVertex2f(r_x+r_offset,t_y+i)
		ac.glEnd()
		

def drawNineSegment(x,y,x_size,y_size,digit,colors,background):
	# Background
	ac.glBegin(2)
	ac.glColor4f(background[0],background[1],background[2],background[3])
	ac.glVertex2f(x,y)
	ac.glVertex2f(x+x_size,y)
	ac.glVertex2f(x+x_size,y+y_size)
	ac.glEnd()
	ac.glBegin(2)
	ac.glColor4f(background[0],background[1],background[2],background[3])
	ac.glVertex2f(x,y)
	ac.glVertex2f(x,y+y_size)
	ac.glVertex2f(x+x_size,y+y_size)
	ac.glEnd()
	# 2px padding
	root_x = x + 2
	root_y = y + 2
	max_x  = x + x_size - 2
	max_y  = y + y_size - 2
	# Definitions (DIFFERENT FOR SEGMENTS 8 AND 9)
	segment_width  = (max_y - root_y)/9
	segment_height = (max_x - root_x)/6
	
	i = 1
	segment_dict = {
		'1' : [ False, True, True, False, False, False, False, False, False],
		'2' : [ True, True, False, True, True, False, True, False, False],
		'3' : [ True, True, True, True, False, False, True, False, False],
		'4' : [ False, True, True, False, False, True, True, False, False],
		'5' : [ True, False, True, True, False, True, True, False, False],
		'6' : [ True, False, True, True, True, True, True, False, False],
		'7' : [ True, True, True, False, False, True, False, False, False],
		'8' : [ True, True, True, True, True, True, True, False, False],
		'9' : [ True, True, True, True, False, True, True, False, False],
		'0' : [ True, True, True, True, True, True, False, False, False],
		'N' : [ False, True, True, False, True, True, False, True, True],
		'R' : [ True, True, False, False, True, True, True, False, True],
		''  : [ False, False, False, False, False, False, False, False, False]}
	segments = segment_dict.get(digit,[True, True, True, True, True, True, True, True, True])
	for segment in segments:
		if segment:
			if i == 1 or i == 4 or i == 7: # horizontal segments
				l_x = segment_height + 1
				t_y = 0
				if i == 1:
					t_y = 1
				elif i == 7:
					t_y = segment_width*4 + 1
				elif i == 4:
					t_y = segment_width*8 + 1
				r_x = l_x + segment_height*4 - 2
				b_y = t_y + segment_width - 2
				# left/right triangle vertexes
				lt_x = l_x - segment_height/2 + 1
				tr_y = t_y + segment_width/2  - 1
				rt_x = r_x + segment_height/2 - 1
				# Adding the base coords
				l_x  = l_x + root_x
				r_x  = r_x + root_x
				t_y  = t_y + root_y
				b_y  = b_y + root_y
				lt_x = lt_x + root_x
				rt_x = rt_x + root_x
				tr_y = tr_y + root_y
				# Drawing the triangles
				# Left
				ac.glBegin(2)
				ac.glColor4f(colors[0],colors[1],colors[2],colors[3])
				ac.glVertex2f(lt_x,tr_y)
				ac.glVertex2f(l_x,t_y)
				ac.glVertex2f(l_x,b_y)
				ac.glEnd()
				# Right
				ac.glBegin(2)
				ac.glColor4f(colors[0],colors[1],colors[2],colors[3])
				ac.glVertex2f(rt_x,tr_y)
				ac.glVertex2f(r_x,t_y)
				ac.glVertex2f(r_x,b_y)
				ac.glEnd()
				# Middle top lt lb rt
				ac.glBegin(2)
				ac.glColor4f(colors[0],colors[1],colors[2],colors[3])
				ac.glVertex2f(l_x,t_y)
				ac.glVertex2f(l_x,b_y)
				ac.glVertex2f(r_x,t_y)
				ac.glEnd()
				# Middle bottom lb rt rb
				ac.glBegin(2)
				ac.glColor4f(colors[0],colors[1],colors[2],colors[3])
				ac.glVertex2f(l_x,b_y)
				ac.glVertex2f(r_x,t_y)
				ac.glVertex2f(r_x,b_y)
				ac.glEnd()
			elif i == 2 or i == 3 or i == 5 or i == 6:
				# (2 and 3) and (5 and 6) have same X coords
				# (2 and 6) and (3 and 5) have same Y coords
				l_x = r_x = t_y = b_y = tr_x = tt_y = bt_y = 0
				# X coords
				if i == 2 or i == 3:
					l_x  = segment_height*5 + 1
					r_x  = l_x + segment_height - 2
					tr_x = segment_height*5 + (segment_height - 2)/2 + 1
				elif i == 5 or i == 6:
					l_x  = 1
					r_x  = l_x + segment_height - 2
					tr_x = (segment_height - 2)/2 + 1
				# Y coords
				if i == 2 or i == 6:
					t_y  = segment_width + 1
					b_y  = segment_width*4 - 1
					tt_y = t_y - (segment_width - 2)/2 + 1
					bt_y = b_y + (segment_width - 2)/2 - 1
				elif i == 3 or i == 5:
					t_y  = segment_width*5 + 1
					b_y  = segment_width*8 - 1
					tt_y = t_y - (segment_width - 2)/2 + 1
					bt_y = b_y + (segment_width - 2)/2 - 1
				# Adding the base coords
				l_x  = l_x  + root_x
				r_x  = r_x  + root_x
				t_y  = t_y  + root_y
				b_y  = b_y  + root_y
				tr_x = tr_x + root_x
				tt_y = tt_y + root_y
				bt_y = bt_y + root_y
				# Drawing the triangles
				# Top
				ac.glBegin(2)
				ac.glColor4f(colors[0],colors[1],colors[2],colors[3])
				ac.glVertex2f(tr_x,tt_y)
				ac.glVertex2f(l_x,t_y)
				ac.glVertex2f(r_x,t_y)
				ac.glEnd()
				# Bottom
				ac.glBegin(2)
				ac.glColor4f(colors[0],colors[1],colors[2],colors[3])
				ac.glVertex2f(tr_x,bt_y)
				ac.glVertex2f(l_x,b_y)
				ac.glVertex2f(r_x,b_y)
				ac.glEnd()
				# Middle top lt lb rt
				ac.glBegin(2)
				ac.glColor4f(colors[0],colors[1],colors[2],colors[3])
				ac.glVertex2f(l_x,t_y)
				ac.glVertex2f(l_x,b_y)
				ac.glVertex2f(r_x,t_y)
				ac.glEnd()
				# Middle bottom lb rt rb
				ac.glBegin(2)
				ac.glColor4f(colors[0],colors[1],colors[2],colors[3])
				ac.glVertex2f(l_x,b_y)
				ac.glVertex2f(r_x,t_y)
				ac.glVertex2f(r_x,b_y)
				ac.glEnd()
			elif i == 8: # Top diagonal
				t1_x  = segment_height + segment_width/4
				t2_x  = segment_height
				t1_y = segment_width
				t2_y = t1_y + segment_width/4
				b1_x = segment_height*3
				b2_x = b1_x - segment_width/2
				b_y  = segment_width*4
				# Adding the base
				t1_x = t1_x + root_x
				t2_x = t2_x + root_x
				t1_y = t1_y + root_y
				t2_y = t2_y + root_y
				b1_x = b1_x + root_x
				b2_x = b2_x + root_x
				b_y  = b_y  + root_y
				ac.glBegin(2)
				ac.glColor4f(colors[0],colors[1],colors[2],colors[3])
				ac.glVertex2f(t1_x,t1_y)
				ac.glVertex2f(t2_x,t2_y)
				ac.glVertex2f(b1_x,b_y)
				ac.glEnd()
				ac.glBegin(2)
				ac.glColor4f(colors[0],colors[1],colors[2],colors[3])
				ac.glVertex2f(t2_x,t2_y)
				ac.glVertex2f(b1_x,b_y)
				ac.glVertex2f(b2_x,b_y)
				ac.glEnd()
			elif i == 9: # Bottom diagonal
				t_x  = segment_height*5
				t1_y = segment_width*8 - segment_width/2
				t2_y = t1_y + segment_width/2
				b1_x = segment_height*3 + segment_width/2
				b2_x = b1_x - segment_width/2
				b_y  = segment_width*5
				# Adding the base
				t_x  = t_x  + root_x
				t1_y = t1_y + root_y
				t2_y = t2_y + root_y
				b1_x = b1_x + root_x
				b2_x = b2_x + root_x
				b_y  = b_y  + root_y
				ac.glBegin(2)
				ac.glColor4f(colors[0],colors[1],colors[2],colors[3])
				ac.glVertex2f(t_x,t1_y)
				ac.glVertex2f(t_x,t2_y)
				ac.glVertex2f(b1_x,b_y)
				ac.glEnd()
				ac.glBegin(2)
				ac.glColor4f(colors[0],colors[1],colors[2],colors[3])
				ac.glVertex2f(t_x,t2_y)
				ac.glVertex2f(b1_x,b_y)
				ac.glVertex2f(b2_x,b_y)
				ac.glEnd()
		i = i + 1

def acUpdate(deltaT):
	global window_width, have_setup, indicated_max_rpm, max_rpm, indicated_max_speed
	global rpm_pivot_x, rpm_pivot_y, speed_pivot_x, speed_pivot_y, tach_radius, speedo_radius, max_fuel
	global fuel_warning_label, dt_ratio
	global draw_boost_gauge
	global rpms_file
	ac.setBackgroundOpacity(window,0)
	if have_setup:
		telemetry_client.tick()
	if debug_mode:
		ac.setText(debug_label,"%2.2f" % (ac.getCarState(0,acsys.CS.DriveTrainSpeed)/ac.getCarState(0,acsys.CS.SpeedKMH)))
	if have_setup == 0:
		max_rpm = sim_info.static.maxRpm
		ac.console("Maximum RPM for car %s: %d" %(ac.getCarName(0),max_rpm))
		if max_rpm < 500:
			if rpms_file.has_section(ac.getCarName(0)):
				max_rpm = int(rpms_file[ac.getCarName(0)]['max_rpm'])
			else:
				ac.console("Don't know max RPMs for this car, go play with it in practice mode first!")
				max_rpm = 20000
		else:
			if not rpms_file.has_section(ac.getCarName(0)):
				rpms_file.add_section(ac.getCarName(0))
			rpms_file[ac.getCarName(0)]['max_rpm'] = str(max_rpm)
			with open('apps/python/AnalogInstruments/rpms.ini','w') as file:
				rpms_file.write(file)
			ac.console("Learned max RPM for this car")
		telemetry_client.connect()
		carinfo_file = configparser.ConfigParser()
		carinfo_file.read("apps/python/AnalogInstruments/carinfo.ini")
		if carinfo_file.has_section(ac.getCarName(0)):
			dt_ratio = float(carinfo_file[ac.getCarName(0)]['ratio'])
			indicated_max_speed = int(carinfo_file[ac.getCarName(0)]['top_speed'])
			has_turbo = carinfo_file[ac.getCarName(0)].getboolean('has_turbo')
		else:
			ac.console("Car %s isn't in carinfo.ini!" % ac.getCarName(0))
			dt_ratio = 1
			indicated_max_speed = 320
			has_turbo = True
		if (not has_turbo or not draw_boost_gauge) and draw_background:
			ac.setBackgroundTexture(window,background_image_path_noboost)
			draw_boost_gauge = False
		# Max fuel
		max_fuel = sim_info.static.maxFuel
		car_model = sim_info.static.carModel
		compound  = str(sim_info.graphics._tyreCompound)
		# Optimal tyre temp range as taken from that forum post
		if "exos_125_s1" in car_model:
			if "SuperSoft" in compound:
				tyre_optimal_temp = range(85,111)
			elif "Soft" in compound:
				tyre_optimal_temp = range(105,126)
			elif "Medium" in compound:
				tyre_optimal_temp = range(90,116)
			elif "Hard" in compound:
				tyre_optimal_temp = range(110,136)
		elif "exos_125" in car_model:
			tyre_optimal_temp = range(90,121)
		elif "Semislick" in compound:
			tyre_optimal_temp = range(75,101)
		elif "Street" in compound:
			tyre_optimal_temp = range(75,86)
		elif "_gt2" in car_model:
			if "SuperSoft" in compound:
				tyre_optimal_temp = range(90,106)
			elif "Soft" in compound:
				tyre_optimal_temp = range(90,106)
			elif "Medium" in compound:
				tyre_optimal_temp = range(85,106)
			elif "Hard" in compound:
				tyre_optimal_temp = range(80,101)
			elif "SuperHard" in compound:
				tyre_optimal_temp = range(80,101)
		elif "70F1" in compound:
			tyre_optimal_temp = range(50,91)
		elif "Soft" in compound:
			tyre_optimal_temp = range(80,111)
		elif "Medium" in compound:
			tyre_optimal_temp = range(75,106)
		elif "Hard" in compound:
			tyre_optimal_temp = range(70,101)
		
		if draw_tachometer:
			# Tach setup
			indicated_max_rpm = max_rpm + 1000 - (max_rpm % 1000)
			# Tach labels
			for i in range(0,indicated_max_rpm+1,1000):
				r = abs(tach_min_angle - tach_max_angle)
				rad  = math.radians(tach_max_angle - (i/indicated_max_rpm)*r)
				label = ac.addLabel(window," ")
				ac.setText(label,"%d" % (i/1000))
				x_offset = 0
				y_offset = 0
				if rad < math.pi/2:
					x_offset = 15 - math.sin(rad)*15
					y_offset = math.cos(rad)*5
				ac.setPosition(label,math.cos(rad)*(tach_radius*4/5)+rpm_pivot_x-x_offset,rpm_pivot_y - math.sin(rad)*(tach_radius*4/5)-y_offset)
		if draw_speedometer:
			# Speedo setup
			if imperial:
				indicated_max_speed = int(indicated_max_speed/1.6) #TODO: round up to multiple of 20
			# Speedo labels
			for i in range(0,indicated_max_speed+1,20):
				r = abs(speedo_min_angle - speedo_max_angle)
				rad = math.radians(speedo_max_angle - (i/indicated_max_speed)*r)
				label = ac.addLabel(window," ")
				ac.setText(label,"%d" % i)
				x_offset = 0
				y_offset = 0
				if rad < math.pi/2:
					x_offset = 23 - math.sin(rad)*23
					y_offset = math.cos(rad)*5
				ac.setPosition(label,math.cos(rad)*speedo_radius*4/5+speed_pivot_x-x_offset,speed_pivot_y - math.sin(rad)*speedo_radius*4/5-y_offset)
		have_setup = 1

def onWindowRender(deltaT):
	global debug_label, indicated_max_rpm, max_rpm, indicated_max_speed, shift_light_drawn, sl_timer
	global tach_radius, rpm_pivot_x, rpm_pivot_y, speedo_radius, speed_pivot_x, speed_pivot_y
	global speedo_tl_x, speedo_tl_y, speedo_total_width, speedo_total_height, gear_color, gear_background, speedo_color, speedo_background
	global abs_label, abs_off_label, tcs_label, tcs_off_label
	global draw_abs_status, draw_tcs_status
	global telemetry_client
	if draw_abs_status:
		if telemetry_client.abs_enabled:
			ac.setPosition(abs_off_label,-10000,-10000)
		else:
			ac.setPosition(abs_off_label,0,0)
		if telemetry_client.abs_in_action:
			ac.setPosition(abs_label,0,0)
		else:
			ac.setPosition(abs_label,-10000,-10000)
	if draw_tcs_status:
		if telemetry_client.tc_enabled:
			ac.setPosition(tcs_off_label,-10000,-10000)
		else:
			ac.setPosition(tcs_off_label,0,0)
		if telemetry_client.tc_in_action:
			ac.setPosition(tcs_label,0,0)
		else:
			ac.setPosition(tcs_label,-10000,-10000)
	rpm = ac.getCarState(0,acsys.CS.RPM)
	# Distance covered
	if draw_odometer:
		drawOdometer()
	# Tach
	if draw_tachometer:
		drawTachometer(deltaT)
	# Speedo
	if draw_speedometer:
		drawSpeedometer()
	# Shift light
	if draw_shift_light:
		sl_center_x = shift_light_x
		sl_center_y = shift_light_y
		sl_radius   = shift_light_radius
		if sl_timer > 0.1:
			shift_light_drawn = not shift_light_drawn
			sl_timer = 0
		else:
			sl_timer = sl_timer + deltaT
		if max_rpm - rpm <= 500 and shift_light_drawn:
			color = shift_light_on_color
		else:
			color = shift_light_off_color
		for i in range(0,360,15):
			ac.glBegin(2)
			ac.glColor4f(color[0],color[1],color[2],color[3])
			ac.glVertex2f(sl_center_x + math.cos(math.radians(i))*sl_radius,sl_center_y + math.sin(math.radians(i))*sl_radius)
			ac.glVertex2f(sl_center_x + math.cos(math.radians(i+15))*sl_radius,sl_center_y + math.sin(math.radians(i+15))*sl_radius)
			ac.glVertex2f(sl_center_x,sl_center_y)
			ac.glEnd()
	# Gear
	if draw_gear_indicator:
		gear = ac.getCarState(0,acsys.CS.Gear)
		digit = ''
		if gear > 1:
			digit = "%d" % (gear - 1)
		elif gear == 1:
			digit = "N"
		elif gear == 0:
			digit = "R"
		drawNineSegment(gear_x,gear_y,gear_width,gear_height,digit,gear_color,gear_background)
	# Digital speedo
	if draw_digital_speedo:
		# First Digit
		hundred = ''
		speed = ac.getCarState(0,acsys.CS.SpeedKMH) # Actual speed instead of drivetrain speed
		if imperial:
			speed = ac.getCarState(0,acsys.CS.SpeedMPH)
		if speed >= 100:
			hundred = "%d" % ((speed - (speed % 100))/100)
		drawNineSegment(speedo_tl_x,speedo_tl_y,speedo_total_width/3,speedo_total_height,hundred,speed_color,speed_background)
		# Second Digit
		ten = ''
		if speed >= 10:
			ten = "%d" % (((speed % 100) - (speed % 10))/10)
		drawNineSegment(speedo_tl_x+speedo_total_width/3,speedo_tl_y,speedo_total_width/3,speedo_total_height,ten,speed_color,speed_background)
		# Third Digit
		dec = "%d" % (speed % 10)
		drawNineSegment(speedo_tl_x+2*(speedo_total_width/3),speedo_tl_y,speedo_total_width/3,speedo_total_height,dec,speed_color,speed_background)
	
	# Brake Gauge
	if draw_brake_gauge:
		drawBrakeGauge()
	# Throttle Gauge
	if draw_throttle_gauge:
		drawThrottleGauge()
	# Clutch Gauge
	if draw_clutch_gauge:
		drawClutchGauge()
	# G Meter
	if draw_g_meter:
		drawGMeter()
	# Tyre Monitor
	if draw_tyre_monitor:
		drawTyreMonitor()
	# BOOOOOST
	if draw_boost_gauge:
		drawBoostGauge()
	# Fuel
	if draw_fuel_gauge:
		drawFuelGauge()