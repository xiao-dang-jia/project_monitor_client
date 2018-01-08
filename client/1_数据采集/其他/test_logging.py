#!/usr/bin/python
# -*- coding: UTF-8 -*-

import logging

logging.basicConfig(filename='test.log', mode='w',level=logging.WARNING,format='%(asctime)s %(message)s')
look = 'Look'
leap = 'Leap'
logging.warning('%s before you %s', look, leap)
logging.debug('This message should go to the log file')
logging.info('So should this')
logging.warning('And this, too')

logger = logging.getLogger(__name__)