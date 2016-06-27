# -*- coding: utf-8 -*-
"""
"""

#Standard Library
from xml.etree import ElementTree
import time

#Third Party
import requests
from robobrowser import RoboBrowser

#Local
from . import config


def fill_form(pmid=None):
    """
    """
    d = PubmedDoc(pmid)
    
    #TODO: switch on university
    
    handle_Duke(d)

class PubmedDoc(object):
    
    def __init__(self,pmid):
        
        #View response in browser using:
        #http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=<PMID>&retmode=xml        
        
        FETCH_URL = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
    
        #Sadly JSON is not available
        params = {'db':'pubmed','id':pmid,'retmode':'xml'}
    
        response = requests.get(FETCH_URL,params=params)

        tree = ElementTree.fromstring(response.content)        
        
        print('initializing tree')
        #We go down a few levels here ...
        #/PubmedArticleSet/PubmedArticle/MedlineCitation/Article
        article = tree.find('.//Article')
        
        self.journal = _get_element_text(article,'.//Title')
        self.volume = _get_element_text(article,'.//Volume')
        self.year = _get_element_text(article,'.//Year')
        
        #What other pagination is possible?
        self.pages = _get_element_text(article,'.//MedlinePgn')
        
        authors = article.findall('.//Author')
        first_author = PubmedAuthor(authors[0])
        if len(authors) == 1:
            self.author_string = first_author.last_name
        elif len(authors) == 2:
            second_author =  PubmedAuthor(authors[1])    
            self.author_string = '%s and %s'%(first_author.last_name,second_author.last_name)
        else:
            self.author_string = '%s et al.'%first_author.last_name
            
        self.title = _get_element_text(article,'.//ArticleTitle')
        print('finishing tree')
    
    def __repr__(self):
        return ('' + 
            '      journal: %s\n' % self.journal +
            '       volume: %s\n' % self.volume +
            '         year: %s\n' % self.year +
            '        pages: %s\n' % self.pages + 
            'author_string: %s\n' % self.author_string + 
            '        title: %s\n' % self.title)

#This might eventually move if we ever got more implementations

class PubmedAuthor(object):
    
    def __init__(self,author_xml):
        self.fore_name = _get_element_text(author_xml,'.//ForeName')
        self.last_name = _get_element_text(author_xml,'.//LastName')

def _get_element_text(parent,search_text):
    
    temp = parent.find(search_text)
    if temp is None:
        return ''
    else:
        return temp.text
        
def handle_Duke(doc):
    #TODO: Move to some spreadsheet
    ILL_URL = 'https://duke-illiad-oclc-org.proxy.lib.duke.edu/illiad/NDD/illiad.dll'
    
    #Step 1 ids
    S1_USER_NAME_ID = "j_username"
    S1_PASSWORD_ID  = "j_password"
    S1_SUBMIT_ID = "Submit"
    
    
    browser = RoboBrowser(history=True) 
    
    browser.open(ILL_URL)
    
    form = browser.get_form()
    
    import pdb
    pdb.set_trace()
    
    
    #1) When logging in, get the forwarding page
    #--------------------------------------------------------------------------
    browser = RoboBrowser(history=True) 
    browser.open(ILL_URL)
    form = browser.get_form()

    #TODO: Add on check value="here"

    browser.submit_form(form)    
    
    #2) Login now
    form = browser.get_form()
    form['j_username'].value = config.user_name
    form['j_password'].value = config.password
    browser.submit_form(form)
    
    #3) Navitage to the request an article bit
    
    import pdb
    pdb.set_trace()
    
    #article_link = browser.select
    #browser.follow_link
    
    
    '''
    try:
        print('Looking for forwarding page')
        # <input type="submit" value="here">
        form_submit = driver.find_element_by_xpath("//input[@value='here'][@type='submit']")
    except serrors.NoSuchElementException:
        pass
    else:
        print('Clicking to go to next page')
        #TODO: We probably need a try/except on this as well
        form_submit.click()
    '''
    
    time.sleep(5)
                      
    #1) Do we need to login?
    try:
        print('finding username')
        username = driver.find_element_by_id(S1_USER_NAME_ID)
        password = driver.find_element_by_id(S1_PASSWORD_ID)
    except serrors.NoSuchElementException:
        #Then we are already logged in
        print('Already logged in')
        pass
    else:
        print('Logging in')
        #TODO: login
        username.send_keys(config.user_name)
        password.send_keys(config.password)
        
        submit_button = driver.find_element_by_id(S1_SUBMIT_ID)
        submit_button.click()
        
    
    #2) Go to request an article
    #--------------------------------------------------------------------------
    try:
        article_link = driver.find_element_by_link_text('Article')
    except serrors.NoSuchElementException:
        #This is an error, at this point we should be able to request an article
        raise Exception('Unable to find the "request an article" option')
    else:
        article_link.click()

    #3) Populate the form
    #--------------------------------------------------------------------------
    driver.find_element_by_id('PhotoJournalTitle').send_keys(doc.journal)
    driver.find_element_by_id('PhotoJournalVolume').send_keys(doc.volume)             
    driver.find_element_by_id('PhotoJournalYear').send_keys(doc.year) 
    driver.find_element_by_id('PhotoJournalInclusivePages').send_keys(doc.pages)
    driver.find_element_by_id('PhotoArticleAuthor').send_keys(doc.author_string)
    driver.find_element_by_id('PhotoArticleTitle').send_keys(doc.title)
    
    #We'll let the user click ...    
        