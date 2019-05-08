#!/usr/bin/env python3
#
# (c) 2019 Yoichi Tanibayashi
#
import PiServo

import pigpio
import time

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
logger.propagate = False
def get_logger(name, debug):
    l = logger.getChild(name)
    if debug:
        l.setLevel(DEBUG)
    else:
        l.setLevel(INFO)
    return l


#####
PULSE_HOME = [1470, 1430, 1490, 1490]

#####
class OttoPi:
    def __init__(self, pi, pin1, pin2, pin3, pin4, debug=False):
        self.debug = debug
        self.logger = get_logger(__class__.__name__, debug)
        self.logger.debug('pin: %s', [pin1, pin2, pin3, pin4])

        self.pi  = pi
        self.pin = [pin1, pin2, pin3, pin4]

        self.servo = PiServo.PiServo(self.pi, self.pin, PULSE_HOME,
                                     debug=self.debug)

        self.home()
        self.off()


    def off(self):
        self.servo.off()

    def move(self, p_lst=[], interval_msec=0, v=None, q=False):
        self.logger.debug('p_lst=%s, interval_msec=%d, v=%s, q=%s',
                          p_lst, interval_msec, v, q)

        self.servo.move(p_lst, interval_msec, v, q)


    def move1(self, p1, p2, p3, p4, v=None, q=False):
        self.logger.debug('(p1, p2, p3, p4)=%s, v=%s, q=%s',
                          (p1, p2, p3, p4), v, q)

        self.servo.move1([p1, p2, p3, p4], v, q)


    def home(self, v=None, q=False):
        self.logger.debug('v=%s, q=%s', v, q)
        self.move1(0, 0, 0, 0, v=v, q=q)

    def change_rl(self, rl=''):
        self.logger.debug('rl=%s', rl)

        if rl=='':
            return ''

        if rl[0] == 'right'[0]:
            return 'left'
        if rl[0] == 'left'[0]:
            return 'right'
        return ''


    def turn_right(self, n=1, v=None, q=False):
        self.logger.debug('n=%d, v=%s, q=%s', n, str(v), q)

        for i in range(n):
            self.turn1('r', v=v, q=q)

    def turn_left(self, n=1, v=None, q=False):
        self.logger.debug('n=%d, v=%s, q=%s', n, str(v), q)

        for i in range(n):
            self.turn1('l', v=v, q=q)

    def turn1(self, rl='r', v=None, q=False):
        self.logger.debug('rl=%s, v=%s, q=%s', rl, str(v), q)

        p1 = (700, 300)
        p2 = 300
        p3 = 200

        self.home()
        time.sleep(0.5)
        
        if rl[0] == 'left'[0]:
            self.move([[p1[0], 0, p2, p1[1]],
                       [0, -p2, p2, 0],
                       [-p1[1], 0, 0, -p1[0]],
                       [0,0,0,0]],
                      interval_msec=100, v=v, q=q)

        if rl[0] == 'right'[0]:
            self.move([[-p1[1], -p2, 0, -p1[0]],
                       [0, -p2, p2, 0],
                       [p1[0], 0, 0, p1[1]],
                       [0, 0, 0, 0]],
                      interval_msec=100, v=v, q=q)


        time.sleep(0.1)
            

    def forward(self, n=1, rl='r', v=None, q=False):
        self.logger.debug('n=%d, rl=%s, v=%s, q=%s',
                          n, rl, str(v), q)

        self.walk(n, 'f', rl, v=v, q=q)
        
    def backward(self, n=1, rl='r', v=None, q=False):
        self.logger.debug('n=%d, rl=%s, v=%s, q=%s',
                          n, rl, str(v), q)

        self.walk(n, 'b', rl, v=v, q=q)
        
    def walk(self, n=1, mv='f', rl='r', v=None, q=False):
        self.logger.debug('n=%d, mv=%s rl=%s, v=%s, q=%s',
                          n, mv, rl, str(v), q)

        self.home()
        time.sleep(0.5)

        for i in range(n):
            self.walk1(mv, rl, v=v, q=q)
            rl = self.change_rl(rl)

        self.walk1('e', rl, v=v, q=q)

    def walk1(self, mv='f', rl='r', v=None, q=False):
        self.logger.debug('mv=%s, rl=%s, v=%s, q=%s',
                          mv, rl, str(v), q)

        if rl == '':
            return

        p1 = (700, 330)
        p2 = (400)

        if rl[0] == 'right'[0]:
            self.move1(p1[0],0,0,p1[1], v=v, q=q)
        if rl[0] == 'left'[0]:
            self.move1(-p1[1], 0, 0, -p1[0], v=v, q=q)

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


    def finish(self):
        self.logger.debug('')

        self.servo.home()
        time.sleep(1)
        self.servo.off()
        
#####
class Sample:
    def __init__(self, pin1, pin2, pin3, pin4, debug=False):
        self.debug = debug
        self.logger = get_logger(__class__.__name__, debug)

        self.pin = [pin1, pin2, pin3, pin4]

        self.pi = pigpio.pi()
        self.ottopi = OttoPi(self.pi, self.pin, debug=debug)

#####
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('pin1', type=int, default=4)
@click.argument('pin2', type=int, default=17)
@click.argument('pin3', type=int, default=27)
@click.argument('pin4', type=int, default=22)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(pin1, pin2, pin3, pin4, debug):
    logger = get_logger('', debug)
    logger.debug('pins: %d, %d, %d, %d', pin1, pin2, pin3, pin4)

    obj = Sample(pin1, pin2, pin3, pin4, debug=debug)
    try:
        obj.main()
    finally:
        print('finally')
        obj.finish()

if __name__ == '__main__':
    main()
