# -*- coding: utf-8 -*-
"""
"""

from robobrowser import RoboBrowser

#from ill import main

#main.fill_form('8912442')

ILL_URL = 'https://duke-illiad-oclc-org.proxy.lib.duke.edu/illiad/NDD/illiad.dll'

browser = RoboBrowser(history=True) 
    
browser.open(ILL_URL)
    
form = browser.get_form()

browser.submit_form(form)

#print(form.submit_info)

#browser.submit_form(form)

form = browser.get_form()

print(form)

import pdb
pdb.set_trace()
