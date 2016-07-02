# -*- coding: utf-8 -*-
"""
"""

#Standard Library Imports
import os
import importlib.machinery #Python 3.3+

try:
    from . import user_config as config
except ImportError:
    raise Exception('user_config.py not found')

if hasattr(config,'config_location'):
    #In this case the config is really only a pointer to another config  
    config_location = config.config_location
    
    if not os.path.exists(config_location):
        raise Exception('Specified configuration path does not exist')
    
    loader = importlib.machinery.SourceFileLoader('config', config_location)    
    config = loader.load_module()



class Config(object):
    
    def __init__(self):
        
        #This is where we specify our expectations about the interface
        self.university = config.university
        self.user_name = config.user_name
        self.password = config.password
        self.save_folder = config.save_folder
        
    def __repr__(self):
        return ('' + 
            ' university: %s\n' % self.university +
            '  user_name: %s\n' % self.user_name +
            '   password: %s\n' % self.password + 
            'save_folder: %s\n' % self.save_folder)    