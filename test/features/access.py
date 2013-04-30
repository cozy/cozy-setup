# -*- coding: utf-8 -*-
import time

from salad.steps.everything import *
from lettuce import step

@step(u'And I wait for a second')
def and_i_wait_for_a_second(step):
    time.sleep(1)

