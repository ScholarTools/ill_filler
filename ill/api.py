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
from . import config #..config_interface.Config


class API(object):
    
    """
    Attributes
    ----------
    interface :
        This type isn't well defined. Need to implement superclass.
    
    
    """    
    
    def __init__(self):
        
        self.verbose = False
        self.university = config.university
        self.save_folder = config.save_folder
        
        if config.university == 'Duke':
            from .implementations.Duke import Duke_ILL
            self.interface = Duke_ILL()
            
            
    def download_papers(self,papers='all',save_folder=None):

        if save_folder is None:
            save_folder = self.save_folder

        self.interface.download_papers(papers,save_folder)        
        
    def request_document(self,pmid):
        
        doc = ILL_DOC.from_pmid(pmid)
        self.interface.request_paper(doc)
        
    def __repr__(self):
        return (u'' +
            '         verbose : %s\n' % self.verbose  +
            '      university : %s\n' % self.university +
            '   save_folder: %s\n' % self.save_folder + 
            '    -----------  : \n' +
            '          METHODS: \n' +
            ' request_document: Submits a request for a document\n' + 
            '  download_papers: Download papers to disk')


class ILL_DOC(object):

    """
    Attributes
    ----------
    journal : string
    volume : string
    year : string
    pages: string
    author_string :
        Currently this is presented as:
            - name_1 (1 author)
            - name_1 and name_2 (2 authors)
            - name_1 et al. (3 or more authors)
    title
    """
    
    @classmethod
    def from_pmid(cls,pmid):
        """
        
        """
        self =  object.__new__(cls)        
        
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
        
        return self
    
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
