# -*- coding: utf-8 -*-
"""
"""

#Third-Party
from robobrowser import RoboBrowser

import re

#Local imports
from .. import config

class Duke_ILL(object):

    """
    Improvements
    ------------
    * Allow saving session and reloading
    * Extract and return transaction #
    * Allow addition of notes (other fields?)
    
    """

    ILL_URL = 'https://duke-illiad-oclc-org.proxy.lib.duke.edu/illiad/NDD/illiad.dll'
    LOGIN_URL = 'https://login.proxy.lib.duke.edu/login?url=https://duke.illiad.oclc.org/illiad/NDD/illiad.dll'
    
    def __init__(self):
        # TODO: support reloading session 
        self.browser = RoboBrowser(history=True)
        self.browser.open(self.ILL_URL)
    
    def _nav_to(self,location):
        pass
    
    def _login_if_necessary(self):
        if self.browser.url == self.LOGIN_URL:
            self._login()
    
    def _login(self):
        
        browser = self.browser        

        if browser.url != self.LOGIN_URL:
            raise Exception('Unable to login unless at the login page')
        
        #1) Handle forwarding page
        #-------------------------        
        form = browser.get_form()
        #TODO: Verify presence of:
        #<input value="here" type="submit">
        browser.submit_form(form)    
        
        #2) Login now
        #-------------------------
        form = browser.get_form()
        form['j_username'].value = config.user_name
        form['j_password'].value = config.password
        browser.submit_form(form)
        
        
        #3) Apparently we need to manually continue via presssing continue
        #-----------------------------------------------------------------
        form = browser.get_form()
        browser.submit_form(form)   

    def download_papers(self,papers,save_folder):
        """
        
        papers = 'all'
        """
        browser = self.browser
        
        self._login_if_necessary()
        
        #https://duke-illiad-oclc-org.proxy.lib.duke.edu/illiad/NDD/illiad.dll?Action=10&Form=64
        
        #<a href="illiad.dll?Action=10&amp;Form=64">Electronically Received Articles</a>
        browser.open(self.ILL_URL + '?Action=10&Form=64')        
        
        #Need to be able to:
        #1) follow transaction - find href that contains Form=72
        #2) Download pdf        
        
        #<a href="illiad.dll?Action=10&amp;Form=72&amp;Value=1074064">1074064</a>
        #<a href="illiad.dll?Action=10&amp;Form=75&amp;Value=1074064"><span class="urlPDF">View</span></a>
        
        #NOTE: When downloading a pdf, you can download too much too quickly, and
        #have to wait for 15 minutes ...    
       
        links_to_filled_requests = browser.find_all('a',href=re.compile("Form=72"))
         
        #Now, let's follow these links, get the info, and then download the papers         
         
        import pdb
        pdb.set_trace()
        

    def request_paper(self,doc):
        #
        #   
    
        browser = self.browser
        
        self._login_if_necessary()
    
        # Navitage to the request an article bit
        #---------------------------------------
        temp = browser.find_element_by_link_text('Article')
        browser.follow_link(temp)        
        #<a href="illiad.dll?Action=10&amp;Form=22">Article</a>     
        
        
        # Fill out the form
        #------------------
        form = browser.get_form(None,{'name':'ArticleRequest'})
        form['PhotoJournalTitle'].value = doc.journal
        form['PhotoJournalVolume'].value = doc.volume
        form['PhotoJournalYear'].value= doc.year
        form['PhotoJournalInclusivePages'].value = doc.pages
        form['PhotoArticleAuthor'].value = doc.author_string
        form['PhotoArticleTitle'].value = doc.title   
        
        #There are multiple submit values, let's make sure we select
        #the right one
        form.select_submit_via_value_attribute('Submit Request')
                
        browser.submit_form(form)        

        #<div id="status"><span class="statusInformation">Article Request Received. Transaction Number 1073756</span>
        confirm = browser.find('span',{'class':'statusInformation'})
        
        import pdb
        pdb.set_trace()
        
        pass
    
 
    
    #4) 

    

  
    
    
    
    
    #	
  
    #Others:
    #Notes
    #
  
    
    #TODO: validate confirm
    #Could extract transaction number - would facilitate allowing a download
    #and naming file according to document info
    #e.g. <span class="statusInformation">Article Request Received. Transaction Number 1073767</span>
  
    
