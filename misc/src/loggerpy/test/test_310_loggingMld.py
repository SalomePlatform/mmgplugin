#!/usr/bin/env python
# -*- coding: utf-8 -*-

# %% LICENSE_SALOME_CEA_BEGIN
# see MILADY/LICENCE file
# %% LICENSE_END


import unittest
import sys
import time
import signal
import os.path as PTH
import loggerpy.loggingMld as LOG
import unittestpy.unittestMilady as UTM



# classical unittest -> class TestCase(unittest.TestCase):
class TestCase(UTM.TestCaseMilady):

  def test_000(self):
    logger = LOG.getLogger()
    self.assertNotEqual(logger, None)
    # print dir(logger)
    self.assertTrue('Logger' in logger.__class__.__name__)

  def test_010(self):
    logger = LOG.getLogger()
    level = logger.getLevelName()
    self.assertEqual(LOG.getLoggerLevelName(), level)

  def test_020(self):
    logger = LOG.getLogger()
    msg = "hello from %s -> test_020" % PTH.basename(__file__)
    logger.warning(msg)
    logger.info(msg)
    self.assertIn(msg, logger.getTestBuffer())
    self.assertIn("WARNING", logger.getTestBuffer())
    self.assertIn("INFO", logger.getTestBuffer())


if __name__ == '__main__':
  unittest.main()
  pass
