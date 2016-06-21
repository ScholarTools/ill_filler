# -*- coding: utf-8 -*-
"""
"""

from . import user_config as config

class Config(object):
    
    def __init__(self):
        
        #This is where we specify our expectations about the interface
        self.university = config.university
        self.user_name = config.user_name
        self.password = config.password
        
    def __repr__(self):
        return ('' + 
            'university: %s\n' % self.university +
            ' user_name: %s\n' % self.user_name +
            '  password: %s\n' % self.password)    