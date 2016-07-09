# -*- coding: utf-8 -*-
"""
"""

#Stadard
import os

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
        pdf_links = browser.find_all('a',href=re.compile("Form=75"))
         
        #current_url = browser.url         
         
        for info_link, pdf_link in zip(links_to_filled_requests,pdf_links):
            browser.follow_link(info_link)
            doc = self._parse_transaction_information()
            browser.back()
            
            #TODO: Expose this as an option to the user ...
            file_name = 'test1.pdf'
            file_path = os.path.join(config.save_folder,file_name)
            
            browser.download(pdf_link,file_path)
            
            import pdb
            pdb.set_trace()
            #TODO: need to verify that download is a pdf            

        

    def _parse_transaction_information(self):
        
        browser = self.browser
        
        table_tag = browser.find('table')

        td_tags = table_tag.find_all('td')
        
        doc = TransactionDoc()  
        
        def verify_and_assign(doc,tags,tag_text,name):
            if tags[0].text == tag_text:
                value = tags[1].text
                if value == '\xa0':
                    value = ''
                setattr(doc,name,value)
            else:
                #TODO: Use different Exception
                raise Exception('Expected "%s" for header but observed "%s" instead',tag_text,tags[0].text)

        verify_and_assign(doc,td_tags[0:2],'Journal Title','journal_title')
        verify_and_assign(doc,td_tags[2:4],'Volume','volume')
        verify_and_assign(doc,td_tags[4:6],'Issue','issue')
        verify_and_assign(doc,td_tags[6:8],'Month','month')
        verify_and_assign(doc,td_tags[8:10],'Year','year')        
        verify_and_assign(doc,td_tags[10:12],'Inclusive Pages','pages')
        verify_and_assign(doc,td_tags[12:14],'Article Author','authors')
        verify_and_assign(doc,td_tags[14:16],'Article Title','title')
        
        return doc
        

    def request_paper(self,doc,verbose=False):
        """
        Parameters
        ----------
        
        Returns
        -------
        transaction_id : string
        """
    
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
        
        #TODO: Raise specific exception
        if confirm is None:
            raise Exception("Unable to find confirmation for request, request may have failed")
        
        m = re.search('\d+',confirm.text)        
        transaction_id = m.group(0)

        return transaction_id        
  
  
class TransactionDoc(object):
    
    """
    Attributes
    ----------
    """

    def _null(self):
        self.journal_title = None
        self.volume = None
        self.issue = None
        self.month = None
        self.year = None
        self.pages = None
        self.authors = None
        self.title = None
    
    
    def __repr__(self):
        str = (u'' +
        'journal_title: %s\n' % self.journal_title + 
        '       volume: %s\n' % self.volume + 
        '        issue: %s\n' % self.issue + 
        '        month: %s\n' % self.month + 
        '         year: %s\n' % self.year + 
        '        pages: %s\n' % self.pages + 
        '      authors: %s\n' % self.authors + 
        '        title: %s\n' % self.title)