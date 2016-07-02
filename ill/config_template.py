# -*- coding: utf-8 -*-
"""
"""

import os

university = 'Duke'
user_name = 'bob_smith'
password = 'password'

name = os.environ['COMPUTERNAME']   
if name == 'TURTLE':
	save_folder = 'F:\Box Sync\Home Folder jah114\Sync\JimPapersResearch\docs'
elif name == 'PALADIN':
	save_folder = 'D:\Box Sync\Home Folder jah114\Sync\JimPapersResearch\docs'
else:
	raise Exception('unhandled computer id case')