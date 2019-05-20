#!/usr/bin/env python3
#
# (c) 2019 Yoichi Tanibayashi
#
from PiServo import PiServo
from OttoPiConfig import OttoPiConfig

import pigpio
import time
import random

import click

from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO, WARN
logger = getLogger(__name__)
logger.setLevel(INFO)
console_handler = StreamHandler()
console_handler.setLevel(DEBUG)
handler_fmt = Formatter(
    '%(asctime)s %(levelname)s %(name)s.%(funcName)s> %(message)s',
    datefmt='%H:%M:%S')
console_handler.setFormatter(handler_fmt)
logger.addHandler(console_handler)
#logger.propagate = True
logger.propagate = False
def get_logger(name, debug):
    l = logger.getChild(name)
    if debug:
        l.setLevel(DEBUG)
    else:
        l.setLevel(INFO)
    return l


#####
DEF_PIN        = [17, 27, 22, 23]
DEF_PULSE_HOME = [1470, 1430, 1490, 1490]
DEF_PULSE_MIN  = [ 500,  500,  500,  500]
DEF_PULSE_MAX  = [2500, 2500, 2500, 2500]

N_CONTINUOUS = 99999

#####
class OttoPiMotion:
    def __init__(self, pi=None, pin=[],
                 pulse_home=[],
                 pulse_min=DEF_PULSE_MIN,
                 pulse_max=DEF_PULSE_MAX,
                 debug=False):
        self.debug = debug
        self.logger = get_logger(__class__.__name__, debug)
        self.logger.debug('pi  = %s', str(pi))
        self.logger.debug('pin = %s', pin)
        self.logger.debug('pulse_home = %s', pulse_home)
        self.logger.debug('pulse_min  = %s', pulse_min)
        self.logger.debug('pulse_max  = %s', pulse_max)

        if type(pi) == pigpio.pi:
            self.pi   = pi
            self.mypi = False
        else:
            self.pi   = pigpio.pi()
            self.mypi = True
        self.logger.debug('mypi = %s', self.mypi)
            
        self.cnf = OttoPiConfig()

        if pin != []:
            self.pin = pin
        else:
            self.pin = self.cnf.get_pin()
            self.logger.debug('pin = %s', self.pin)
            
        if pulse_home != []:
            self.pulse_home = pulse_home
        else:
            self.pulse_home = self.cnf.get_home()
            self.logger.debug('pulse_home = %s', self.pulse_home)
            
        self.pulse_min  = pulse_min
        self.pulse_max  = pulse_max

        self.stop_flag = False

        self.servo = None
        self.reset_servo()


    def __del__(self):
        self.logger.debug('')
        #self.end()


    def reset_servo(self):
        self.logger.debug('')
        del(self.servo)
        self.servo = PiServo(self.pi, self.pin,
                             self.pulse_home, self.pulse_min, self.pulse_max,
                             debug=self.debug & logger.propagate)
        self.servo.home()

    def end(self):
        self.logger.debug('')

        self.home()
        time.sleep(1)
        self.off()

        if self.mypi:
            self.pi.stop()
            self.mypi = False

    def off(self):
        self.logger.debug('')
        self.servo.off()

    def stop(self, n=1):
        self.logger.debug('n = %d', n)
        self.stop_flag = True

    def resume(self, n=1):
        self.logger.debug('n = %d', n)
        self.stop_flag = False

    def home(self, n=1, v=None, q=False):
        self.logger.debug('n=%d, v=%s, q=%s', n, v, q)
        self.move1(0, 0, 0, 0, v=v, q=q)

    def change_pos(self, i, d_pos, v=None, q=False):
        self.logger.debug('i=%d, d_pos=%d', i, d_pos)
        cur_pos = self.get_cur_position()
        cur_pos[i] += d_pos
        self.logger.info('cur_pos = %s', cur_pos)
        self.move1(cur_pos[0], cur_pos[1], cur_pos[2], cur_pos[3],
                   v=v, q=q)

    def move_up0(self, n=1, v=None, q=False):
        self.logger.debug('n=%d, v=%s, q=%s', n, str(v), q)
        self.change_pos(0, 5)

    def move_down0(self, n=1, v=None, q=False):
        self.logger.debug('n=%d, v=%s, q=%s', n, str(v), q)
        self.change_pos(0, -5)

    def move_up1(self, n=1, v=None, q=False):
        self.logger.debug('n=%d, v=%s, q=%s', n, str(v), q)
        self.change_pos(1, 5)

    def move_down1(self, n=1, v=None, q=False):
        self.logger.debug('n=%d, v=%s, q=%s', n, str(v), q)
        self.change_pos(1, -5)

    def move_up2(self, n=1, v=None, q=False):
        self.logger.debug('n=%d, v=%s, q=%s', n, str(v), q)
        self.change_pos(2, 5)

    def move_down2(self, n=1, v=None, q=False):
        self.logger.debug('n=%d, v=%s, q=%s', n, str(v), q)
        self.change_pos(2, -5)

    def move_up3(self, n=1, v=None, q=False):
        self.logger.debug('n=%d, v=%s, q=%s', n, str(v), q)
        self.change_pos(3, 5)

    def move_down3(self, n=1, v=None, q=False):
        self.logger.debug('n=%d, v=%s, q=%s', n, str(v), q)
        self.change_pos(3, -5)


    def adjust_home(self, i, v):
        self.logger.debug('i = %d, v = %d', i, v)
        self.pulse_home[i] += v
        self.logger.info('pulse_home = %s', self.pulse_home)
        cnf = OttoPiConfig(debug=self.debug)
        cnf.set_intlist('home', self.pulse_home)
        cnf.save()
        self.reset_servo()


    def home_up0(self, n=1):
        self.logger.debug('n = %d', n)
        self.adjust_home(0, 5)

    def home_down0(self, n=1):
        self.logger.debug('n = %d', n)
        self.adjust_home(0, -5)

    def home_up1(self, n=1):
        self.logger.debug('n = %d', n)
        self.adjust_home(1, 5)

    def home_down1(self, n=1):
        self.logger.debug('n = %d', n)
        self.adjust_home(1, -5)

    def home_up2(self, n=1):
        self.logger.debug('n = %d', n)
        self.adjust_home(2, 5)

    def home_down2(self, n=1):
        self.logger.debug('n = %d', n)
        self.adjust_home(2, -5)

    def home_up3(self, n=1):
        self.logger.debug('n = %d', n)
        self.adjust_home(3, 5)

    def home_down3(self, n=1):
        self.logger.debug('n = %d', n)
        self.adjust_home(3, -5)


    def get_cur_position(self):
        self.logger.debug('')
        cur_pulse = self.servo.get_cur_position()
        self.logger.debug('cur_pulse = %s', cur_pulse)
        cur_pos = [(cur_pulse[i] / 10) for i in range(len(cur_pulse))]
        self.logger.debug('cur_pos = %s', cur_pos)
        return cur_pos


    def move(self, p_list=[], interval_msec=0, v=None, q=False):
        self.logger.debug('p_list=%s, interval_msec=%d, v=%s, q=%s',
                          p_list, interval_msec, v, q)
        for p in p_list:
            self.move1(p[0], p[1], p[2], p[3], v, q)
            time.sleep(interval_msec/1000)


    def move1(self, p1, p2, p3, p4, v=None, q=False):
        self.logger.debug('(p1, p2, p3, p4)=%s, v=%s, q=%s',
                          (p1, p2, p3, p4), v, q)
        self.servo.move1([p1*10, p2*10, p3*10, p4*10], v, q)


    def change_rl(self, rl=''):
        self.logger.debug('rl=%s', rl)

        if rl[0] == 'right'[0]:
            return 'left'
        if rl[0] == 'left'[0]:
            return 'right'
        return ''


    def ojigi(self, n=1, interval_msec=1000, v=None, q=False):
        self.logger.debug('n=%d, interval_msec=%d, v=%s, q=%s',
                          n, interval_msec, str(v), q)

        if n == 0:
            n = N_CONTINUOUS
            self.logger.info('n=%d!', n)
            
        p1 = [10, 25, 15]
        p2 = 90

        self.home()
        time.sleep(0.3)

        for i in range(n):
            if self.stop_flag:
                break
            
            self.move([[-p1[0], -p2, 0, 0],
                       [-p1[0], -p2, p2, p1[0]]], v=v, q=q)
            self.move([[-p1[1], -p2, p2, p1[1]],
                       [-p1[2], -p2, p2, p1[1]]],
                      interval_msec=500, v=v, q=q)
            self.move([[-p1[0], -p2, 0, 0],
                       [0,0,0,0]],v=v,q=q)
            time.sleep(interval_msec/1000)
        
    def happy(self, n=1, interval_msec=0, v=None, q=False):
        self.logger.debug('n=%d, interval_msec=%d, v=%s, q=%s',
                          n, interval_msec, str(v), q)

        if n == 0:
            n = N_CONTINUOUS
            self.logger.info('n=%d!', n)
            
        p1 = 70
        p2 = 10

        self.home()
        time.sleep(0.3)

        for i in range(n):
            if self.stop_flag:
                break
            
            self.move([[p1,0,0,-p2],
                       [0,0,0,0],
                       [p2,0,0,-p1],
                       [0,0,0,0]],
                      v=v, q=q)
            time.sleep(interval_msec/1000)
                      

    def slide_right(self, n=1, interval_msec=0, v=None, q=False):
        self.logger.debug('n=%d, interval_msec=%d, v=%s, q=%s',
                          n, interval_msec, str(v), q)

        if n == 0:
            n = N_CONTINUOUS
            self.logger.info('n=%d!', n)

        for i in range(n):
            if self.stop_flag:
                break

            self.slide1('r', interval_msec=interval_msec, v=v, q=q)

    def slide_left(self, n=1, interval_msec=0, v=None, q=False):
        self.logger.debug('n=%d, interval_msec=%d, v=%s, q=%s',
                          n, interval_msec, str(v), q)

        if n == 0:
            n = N_CONTINUOUS
            self.logger.info('n=%d!', n)

        for i in range(n):
            if self.stop_flag:
                break

            self.slide1('l', interval_msec=interval_msec, v=v, q=q)

    def slide1(self, rl='r', interval_msec=0, v=None, q=False):
        self.logger.debug('rl=%s, interval_msec=%d, v=%s, q=%s',
                          rl, interval_msec, str(v), q)

        p1 = (80, 30)
        p2 = (-10, -60)

        self.home()
        time.sleep(interval_msec/1000)

        if rl[0] == 'left'[0]:
            self.move([(p1[0], 0, 0, p1[1]),
                       (p2[0], 0, 0, p2[1]),
                       (0,0,0,0)], interval_msec=interval_msec, v=v, q=q)

        if rl[0] == 'right'[0]:
            self.move([(-p1[1], 0, 0, -p1[0]),
                       (-p2[1], 0, 0, -p2[0]),
                       (0,0,0,0)], interval_msec=interval_msec, v=v, q=q)


    def turn_right(self, n=1, interval_msec=0, v=None, q=False):
        self.logger.debug('n=%d, interval_msec=%d, v=%s, q=%s',
                          n, interval_msec, str(v), q)

        if n == 0:
            n = N_CONTINUOUS
            self.logger.info('n=%d!', n)
            
        for i in range(n):
            if self.stop_flag:
                break
            
            self.turn1('r', interval_msec=interval_msec, v=v, q=q)

    def turn_left(self, n=1, interval_msec=0, v=None, q=False):
        self.logger.debug('n=%d, interval_msec=%d, v=%s, q=%s',
                          n, interval_msec, str(v), q)

        if n == 0:
            n = N_CONTINUOUS
            self.logger.info('n=%d!', n)
            
        for i in range(n):
            if self.stop_flag:
                break
            
            self.turn1('l', interval_msec=interval_msec, v=v, q=q)

    def turn1(self, rl='r', interval_msec=0, v=None, q=False):
        self.logger.debug('rl=%s, interval_msec=%d, v=%s, q=%s',
                          rl, interval_msec, str(v), q)

        p1 = (65, 35)
        p2 = 30

        self.home()
        time.sleep(interval_msec/1000)
        
        if rl[0] == 'left'[0]:
            self.move([[p1[0],   p2, p2,   p1[1]],
                       [0,      -p2, p2, p1[1]/2],
                       [0,      -p2, p2,       0],
                       [-p1[1],   0,  0,  -p1[0]],
                       [0,0,0,0]], interval_msec=interval_msec, v=v, q=q)

        if rl[0] == 'right'[0]:
            self.move([[-p1[1], -p2, -p2, -p1[0]],
                       [-p1[1]/2, -p2, p2, 0],
                       [0, -p2, p2, 0],
                       [p1[0], 0, 0, p1[1]],
                       [0,0,0,0]],
                      interval_msec=interval_msec, v=v, q=q)


    def forward(self, n=1, rl='', v=None, q=False):
        self.logger.debug('n=%d, rl=%s, v=%s, q=%s',
                          n, rl, str(v), q)

        self.walk(n, 'f', rl, v=v, q=q)
        
    def backward(self, n=1, rl='', v=None, q=False):
        self.logger.debug('n=%d, rl=%s, v=%s, q=%s',
                          n, rl, str(v), q)

        self.walk(n, 'b', rl, v=v, q=q)
        
    def walk(self, n=1, mv='f', rl='', v=None, q=False):
        self.logger.debug('n=%d, mv=%s rl=%s, v=%s, q=%s',
                          n, mv, rl, str(v), q)

        if n == 0:
            n = N_CONTINUOUS
            self.logger.info('n=%d!', n)
            
        if rl == '':
            rl = 'rl'[random.randint(0,1)]
            self.logger.debug('rl=%s', rl)

        self.home()
        time.sleep(0.5)

        for i in range(n):
            if self.stop_flag:
                break
            
            self.walk1(mv, rl, v=v, q=q)
            rl = self.change_rl(rl)

        self.walk1('end', rl, v=v, q=q)

    def walk1(self, mv='f', rl='r', v=None, q=False):
        self.logger.debug('mv=%s, rl=%s, v=%s, q=%s',
                          mv, rl, str(v), q)

        if rl == '':
            return

        p1 = (65, 35)
        p2 = (40)

        if rl[0] == 'right'[0]:
            if mv[0] == 'forward'[0]:
                self.move1( p1[0], p2/2,  0,  p1[1], v=v, q=q)
            if mv[0] == 'backward'[0]:
                self.move1( p1[0],  0,  0,  p1[1], v=v, q=q)
            if mv[0] == 'end'[0]:
                self.move1( p1[0], p2/2,  0,  p1[1], v=v, q=q)
                
        if rl[0] == 'left'[0]:
            if mv[0] == 'forward'[0]:
                self.move1(-p1[1], 0, -p2/2, -p1[0], v=v, q=q)
            if mv[0] == 'backward'[0]:
                self.move1(-p1[1], 0,   0, -p1[0], v=v, q=q)
            if mv[0] == 'end'[0]:
                self.move1(-p1[1], 0, -p2/2, -p1[0], v=v, q=q)

        time.sleep(.1)

        if mv[0] == 'end'[0]:
            self.home(v=v, q=q)
            return
        
        if rl[0] == 'right'[0]:
            if mv[0] == 'forward'[0]:
                self.move1(0, p2, p2, 0, v=v, q=q)
            if mv[0] == 'back'[0]:
                self.move1(0,-p2,-p2, 0, v=v, q=q)
            
        if rl[0] == 'left'[0]:
            if mv[0] == 'forowar'[0]:
                self.move1(0,-p2,-p2, 0, v=v, q=q)
            if mv[0] == 'back'[0]:
                self.move1(0, p2, p2, 0, v=v, q=q)

#####
