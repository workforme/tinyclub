# -*- encoding: utf-8 -*-
import sys, logging
from wsgilog import WsgiLog

logfile = "log/access.log" # 日志文件路径 #
logformat = "[%(asctime)s] %(filename)s:%(lineno)d(%(funcName)s): [%(levelname)s] %(message)s" # 日志格式 #
datefmt = "%Y-%m-%d %H:%M:%S" # 日志中显示的时间格式 #
loglevel = logging.DEBUG
interval = "d" # 每隔一天生成一个日志文件#
backups = 7 # 后台保留3个日志文件 #

class Log(WsgiLog):
    def __init__(self,application):
        WsgiLog.__init__(
            self,
            application,
            logformat = logformat,
            datefmt = datefmt,
            tofile = True,
            file = logfile,
            interval = interval,
            backups = backups
        )
'''
def addlogger(cls):
    class wrapper:
        def __init__(self,*args):
            self.wrapped=cls(*args)
            self.wrapped._logger=la
        def __getattr__(self,name):
            return getattr(self.wrapped,name)
    return wrapper

def logger(cls):
    class newcls:
        def __init__(self,arg):
            self.
'''


