# -*- coding: utf-8 -*-
"""
"""

import requests
from xml.etree import ElementTree

from selenium import webdriver

driver = webdriver.Firefox()

def fill_form(pmid=None):
    """
    """
    d = PubmedDoc(pmid)

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
        import pdb
        pdb.set_trace()
    
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
        
def handle_Duke(driver,doc):
    #TODO: Move to some spreadsheet
    ILL_URL = 'https://duke-illiad-oclc-org.proxy.lib.duke.edu/illiad/NDD/illiad.dll'
    
    #1) Do we need to login?
  
    username = selenium.find_element_by_id("username")
    password = selenium.find_element_by_id("password")

    username.send_keys("YourUsername")
    password.send_keys("Pa55worD")

    selenium.find_element_by_name("submit").click()
  
    #2) Navigate to requesting a journal article (for now)
    
    #3) Populate the form
    
        
        