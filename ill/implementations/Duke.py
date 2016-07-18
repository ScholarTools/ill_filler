# -*- coding: utf-8 -*-
"""
"""

#Stadard
import os
from datetime import datetime
import string

#Third-Party
#This is actually the ScholarTools version of RoboBrowser
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
        self.log = DukeILLLog()
    
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
            transaction_id = info_link.text
            browser.follow_link(info_link)
            doc = self._parse_transaction_information()
            browser.back()
            
            #TODO: Create utils for shortening strings and removing bad chars
            #and placing underscores
            
            author_string = re.sub(r'\W+','',string.capwords(doc.authors))
            title_string = re.sub(r'\W+','',string.capwords(doc.title))
            if len(title_string) > 60:
                title_string = title_string[:60]
            file_name = '%s_%s_%s.pdf' % (doc.year,author_string,title_string)           
            
            #TODO: Expose this as an option to the user ...
            file_path = os.path.join(config.save_folder,file_name)
            
            browser.download(pdf_link,file_path)
            
            #TODO: need to verify that download is a pdf            
            self.log.log_download(transaction_id,file_name)    
        

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

        self.log.log_request(transaction_id,doc)

        return transaction_id        

class DukeILLLog(object):

    """
    Things to track:
    1) Requested documents and their transaction #s
    2) Downloaded files
    
    Table
    1) request date
    2) transaction #
    3) download date
    4) file name    
    5) pmid
    
    """

    def __init__(self):
        self.log_path = os.path.join(config.save_folder,'ill_log.txt')
        
        if os.path.isfile(self.log_path):
            #TODO: try [LogEntry.from_saved_string(line) for line in file]
            with open (self.log_path,'r') as file:
                temp = file.read().split('\n')
                
            data = [LogEntry.from_saved_string(x) for x in temp]
        else:
            data = []
            
        self.data = data    

    def log_download(self,transaction_number,file_name):
        
        doc = [x for x in self.data if x.transaction_number == transaction_number]
        
        if len(doc):
            matched_doc = doc[0]
            matched_doc.download_date = self.get_current_timestring()
            matched_doc.file_name = file_name
        else:
            new_log_entry = LogEntry(
                transaction_number=transaction_number,
                file_name=file_name,
                download_date=self.get_current_timestring())
            self.data.append(new_log_entry)
        
        self.save_to_disk()

    def log_request(self,transaction_number,ILL_doc):        
        new_log_entry = LogEntry(
            transaction_number=transaction_number,
            request_date=self.get_current_timestring(),
            pmid=ILL_doc.pmid)

        self.data.append(new_log_entry)                

        self.save_to_disk()

    def save_to_disk(self):
        data_for_disk = '\n'.join([x.get_save_string() for x in self.data])

        with open(self.log_path,'w') as file:
            file.write(data_for_disk)

    def get_current_timestring(self):
        temp_dt = datetime.now()
        return temp_dt.isoformat()


class LogEntry(object):

    def __init__(self,pmid='',request_date='',transaction_number='',file_name='',download_date=''):
        self.download_date = download_date
        self.file_name = file_name
        self.pmid = pmid
        self.request_date = request_date
        self.transaction_number = transaction_number
        
    @classmethod
    def from_saved_string(cls,string):
        self = cls()
        temp = string.split('\t')
        self.download_date = temp[0]
        self.file_name = temp[1]
        self.pmid = temp[2]
        self.request_date = temp[3]
        self.transaction_number = temp[4]
        
        return self
        
    
    def get_save_string(self):
        temp = [self.download_date,self.file_name,self.pmid,self.request_date,self.transaction_number]
        return '\t'.join(temp)
    
  
  
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
        return (u'' +
        'journal_title: %s\n' % self.journal_title + 
        '       volume: %s\n' % self.volume + 
        '        issue: %s\n' % self.issue + 
        '        month: %s\n' % self.month + 
        '         year: %s\n' % self.year + 
        '        pages: %s\n' % self.pages + 
        '      authors: %s\n' % self.authors + 
        '        title: %s\n' % self.title)