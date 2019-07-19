#!/usr/bin/env python3
#
# (c) 2019 Yoichi Tanibayashi
#
'''
ロボット制御クライアント

OttoPiServerにコマンドを送信する

OttoPiClient -- ロボット制御クライアント
|
|(TCP/IP)
|
OttoPiServer -- ロボット制御サーバ (ネットワーク送受信スレッド)
 |
 +- OttoPiAuto -- ロボットの自動運転 (自動運転スレッド)
 |   |
 +---+- OttoPiCtrl -- コマンド制御 (動作実行スレッド)
         |
         + OttoPiMotion -- 動作定義
            |
            +- PiServo -- 複数サーボの同期制御
            +- OttoPiConfig -- 設定ファイルの読み込み・保存

'''
__author__ = 'Yoichi Tanibayashi'
__date__   = '2019'

import telnetlib
import time

#####
from MyLogger import MyLogger
my_logger = MyLogger(__file__)

#####
DEF_HOST = 'localhost'
DEF_PORT = 12345
    
#####
class OttoPiClient:
    def __init__(self, svr_host=DEF_HOST, svr_port=DEF_PORT, debug=False):
        self.debug = debug
        self.logger = my_logger.get_logger(__class__.__name__, debug)
        self.logger.debug('svr_host=%s, svr_port=%d', svr_host, svr_port)

        self.svr_host = svr_host
        self.svr_port = svr_port

        self.tn = self.open(self.svr_host, self.svr_port)

    def __del__(self):
        self.logger.debug('')
        self.close()

    def open(self, svr_host=DEF_HOST, svr_port=DEF_PORT):
        self.logger.debug('svr_host=%s, svr_port=%d', svr_host, svr_port)
        return telnetlib.Telnet(self.svr_host, self.svr_port)
        
    def close(self):
        self.logger.debug('')
        self.tn.close()

    def send_cmd(self, cmd):
        self.logger.debug('cmd=%s', cmd)

        in_data = self.tn.read_very_eager()
        if len(in_data) > 0:
            self.logger.debug('in_data:%a', in_data)

        if cmd[0] == ':':
            self.tn.write(cmd.encode('utf-8'))

            time.sleep(0.1)

            in_data = self.tn.read_very_eager()
            if len(in_data) > 0:
                self.logger.debug('in_data:%a', in_data)
            return
        
        for ch in cmd:
            self.logger.debug('ch=%a(0x%02x)', ch, ord(ch))

            self.tn.write(ch.encode('utf-8'))

            time.sleep(0.1)

            in_data = self.tn.read_very_eager()
            if len(in_data) > 0:
                self.logger.debug('in_data:%a', in_data)


##### Sample
class Sample:
    def __init__(self, svr_host, svr_port, command='', debug=False):
        self.debug = debug
        self.logger = my_logger.get_logger(__class__.__name__, debug)
        self.logger.debug('svr_host=%s, svr_port=%d', svr_host, svr_port)
        self.logger.debug('command=%s', command)

        self.cl = OttoPiClient(svr_host, svr_port, debug=self.debug)
        self.command = command

    def main(self):
        self.logger.debug('command:\'%s\'', self.command)
        
        if self.command != '':
            if self.command[0] == ':':
                self.cl.send_cmd(self.command)
                time.sleep(3)
            else:
                for ch in self.command:
                    self.logger.debug('ch=%a', ch)
                    self.cl.send_cmd(ch)
                    time.sleep(3)

            self.cl.send_cmd(':stop')

        else:
            self.cl.send_cmd(':happy')
            time.sleep(3)
            self.cl.send_cmd(':ojigi')
            time.sleep(3)
            self.cl.send_cmd(':stop')

    def end(self):
        self.logger.debug('')
        self.cl.close()

#####
import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('svr_host', type=str, default="localhost")
@click.argument('svr_port', type=int, default=DEF_PORT)
@click.option('--command', '-c', type=str, default='',
              help='control commands')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(svr_host, svr_port, command, debug):
    logger = my_logger.get_logger(__name__, debug)
    logger.info('svr_host=%s, svr_port=%d', svr_host, svr_port)
    
    obj = Sample(svr_host, svr_port, command, debug=debug)
    try:
        obj.main()
    finally:
        logger.info('finally')
        obj.end()

if __name__ == '__main__':
    main()
