from splinter.browser import Browser
from lettuce import before, after, world

@before.all
def initial_setup(server):    
    world.browser = Browser('webdriver.firefox')

@after.all
def teardown_browser(total):
    world.browser.quit()
