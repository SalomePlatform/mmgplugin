#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import sys
import subprocess as SP
import pprint as PP

try:
    from StringIO import StringIO  # python2
except ImportError:
    from io import StringIO  # python3


"""
simplississimus logger for milady
"""

# return-exit code for linux bash/python scripts
_OK = 0
_KO = 1

# ANSI foreground color codes
BLACK = 30
RED = 31
GREEN = 32
YELLOW = 33
BLUE = 34
MAGENTA = 35
CYAN = 36
WHITE = 37
RESET = 39
CSI = '\033['


def colorize(code):
  """
  for terminal ANSI color code
  example: colorize(RED)
  """
  return CSI + str(code) + 'm'


class Logger(object):
  """simplississimus logger with color"""

  def __init__(self):
    self._levels = {'test': -1, 'debug': 0, 'info': 1, 'warning': 2, 'error': 3, 'critical': 4}
    self.set_level('info')  # default
    self.set_color(True)
    self._isInTest = False
    # usually _isVerboseTest True ONLY in debugging test phase, NEVER in production
    # because logger.test(msg) pollute mandatory clear unittest log, one line per test.
    self._isVerboseTest = False
    self._testStream = None
    self._testBuffer = None

  def set_level(self, level):
    self._level = self._levels[level]

  def set_color(self, iscolor):
    self._color = iscolor

  def indent(self, msg, nb=12, car=" "):
    """indent nb car (spaces) multi lines message except first one"""
    s = msg.split("\n")
    res = ("\n" + car * nb).join(s)
    return res

  def _log(self, level, color, msg):
    if ( (self._isInTest) and (level != 'TEST') ):
      self._testStream.write("[%s] %s\n" % (level.ljust(9), self.indent(msg)))
    else:
      if self._color:
        print("%s[%s] %s%s" % (colorize(color), level.ljust(9), self.indent(msg), colorize(RESET)))
      else:
        print("[%s] %s" % (level.ljust(9), self.indent(msg)))

  def test(self, msg):
    """usually isVerboseTest True only if debugging test, NEVER in production"""
    if self._isVerboseTest: self._log('TEST', CYAN, msg)

  def debug(self, msg):
    if self._level <= 0: self._log('DEBUG', BLUE, msg)

  def info(self, msg):
    if self._level <= 1: self._log('INFO', GREEN, msg)

  def warning(self, msg):
    if self._level <= 2: self._log('WARNING', RED, msg)

  def error(self, msg):
    if self._level <= 3: self._log('ERROR', RED, msg)

  def critical(self, msg):
    if self._level <= 4: self._log('CRITICAL', YELLOW, msg)

  def getLevelName(self):
    return self._level

  def setVerboseTest(self, value=True):
    """to get test message in unittest log"""
    self._isVerboseTest = value

  def resetVerboseTest(self):
    self._isVerboseTest = False

  def setBeginTest(self):
    """begin of redirect logger messages to stringIO buffer to avoid message in unittest log"""
    self._isInTest = True
    self._testStream = StringIO()  # all log messages are buffered (except logger.test messages)

  def setEndTest(self):
    """end of redirect logger messages to stringIO buffer to avoid message in unittest log"""
    self._isInTest = False
    self._testStream = None

  def getTestBuffer(self):
    self._testBuffer = self._testStream.getvalue()
    self.test("getTestBuffer\n%s" % self._testBuffer)
    return self._testBuffer

# define local sssimple logger
_logger = Logger()

def getLogger():
  return _logger

def getLoggerLevelName():
  return _logger.getLevelName()

#################################################################
# main
#################################################################
if __name__ == '__main__':
  _logger.set_level('info')  # or 'debug' or ...
  _logger.info("Hello world from simple milady logger")
  _logger.warning("Good Bye world from simple milady logger, exit python")
  exit(_OK)
