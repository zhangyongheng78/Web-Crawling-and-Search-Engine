ascii_letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'

import logging
from datamodel.search.YonghenzQirenfHuanjial_datamodel import YonghenzQirenfHuanjialLink, OneYonghenzQirenfHuanjialUnProcessedLink
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import Producer, GetterSetter, Getter
from lxml import html,etree
import re, os
from time import time
from uuid import uuid4

from urlparse import urlparse, parse_qs
from uuid import uuid4
import requests

logger = logging.getLogger(__name__)
LOG_HEADER = "[CRAWLER]"
detect_url = {}
detect_netloc = {}

deect_query = {}
@Producer(YonghenzQirenfHuanjialLink)
@GetterSetter(OneYonghenzQirenfHuanjialUnProcessedLink)
class CrawlerFrame(IApplication):
    app_id = "YonghenzQirenfHuanjial"

    def __init__(self, frame):
        self.app_id = "YonghenzQirenfHuanjial"
        self.frame = frame


    def initialize(self):
        self.count = 0
        links = self.frame.get_new(OneYonghenzQirenfHuanjialUnProcessedLink)
        if len(links) > 0:
            print "Resuming from the previous state."
            self.download_links(links)
        else:
            l = YonghenzQirenfHuanjialLink("http://www.ics.uci.edu/")
            print l.full_url
            self.frame.add(l)

    def update(self):
        unprocessed_links = self.frame.get_new(OneYonghenzQirenfHuanjialUnProcessedLink)
        if unprocessed_links:
            self.download_links(unprocessed_links)

    def download_links(self, unprocessed_links):
        for link in unprocessed_links:
            print "Got a link to download:", link.full_url
            downloaded = link.download()
            links = extract_next_links(downloaded)
            for l in links:
                if is_valid(l):
                    self.frame.add(YonghenzQirenfHuanjialLink(l))

    def shutdown(self):
        print (
            "Time time spent this session: ",
            time() - self.starttime, " seconds.")

def extract_next_links(rawDataObj):
    outputLinks = []
 
    if rawDataObj.is_redirected == 1:
        domain = rawDataObj.final_url
    else:
        domain = rawDataObj.url
    try:
        doc = html.fromstring(rawDataObj.content)
    except:
        return outputLinks
    doc.make_links_absolute(domain)
    dot = html.tostring(doc)
    all_urls = re.findall(r'href=[\'"]?([^\'" >]+)', dot)
    for i in all_urls:
        outputLinks.append(i)
    for i in detect_url:
        print "Subdomain: ",i,detect_url[i][0]
   
  
    '''
    rawDataObj is an object of type UrlResponse declared at L20-30
    datamodel/search/server_datamodel.py
    the return of this function should be a list of urls in their absolute form
    Validation of link via is_valid function is done later (see line 42).
    It is not required to remove duplicates that have already been downloaded. 
    The frontier takes care of that.
    
    Suggested library: lxml
    '''
    return outputLinks


def is_valid(url):
    '''
    Function returns True or False based on whether the url has to be
    downloaded or not.
    Robot rules and duplication rules are checked separately.
    This is a great place to filter out crawler traps.
    '''
    if type(url) == unicode:
        url = url.encode()
    try:
        response = requests.get(url)
    except:
        return False
    parsed = urlparse(url)
    path_list= []
    count = 0
    if parsed.netloc not in detect_url.keys(): #This is a new netloc
        detect_url[parsed.netloc] =[1,path_list]
        if parsed.path != "": #not sure if it's equal to "" when the path is empty
            tokenized_path = parsed.path[1:].split('/')
            tokenized_path.append(count)
            detect_url[parsed.netloc][1].append(tokenized_path)
            return True
            #Above, there is path in the url, but since the netloc is new initialized, so we append the
            #tokenized_path to the path_list, but no comparison, no exceed than 10, so return True
        else: #There is NO path of the url, therefore return True.
            return True
    else:#netloc is already in the detect_url
        detect_url[parsed.netloc][0] += 1 # netloc occurence number + 1
        # url's path may exist or not exist:
        if parsed.path != "":#target url has path
            tokenized_path = parsed.path[1:].split('/')
            tokenized_path.append(count)
            if(len(detect_url[parsed.netloc][1]) != 0): #Exists tokenized list
                for each_token_path in detect_url[parsed.netloc][1]:
                    if check_similarity(each_token_path,tokenized_path) == True: #They are very similar
                        each_token_path[-1] += 1
                        if each_token_path[-1] > 10: # if the similar path occurs more than 10:
                            return False
                        else:
                            return True #I am not sure if I want to return True here or not.
                detect_url[parsed.netloc][1].append(tokenized_path)
                return True
            else: #token path list is empty:
                detect_url[parsed.netloc][1].append(tokenized_path)
                return True
        else:#The url does not have path.
            return True
                               
    if parsed.scheme not in set(["http", "https"]):
        return False
    if "calendar.ics.uci.edu" in parsed.hostname:
        return False
    
    try:
        return ".ics.uci.edu" in parsed.hostname \
            and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4"\
            + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
            + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
            + "|thmx|mso|arff|rtf|jar|csv"\
            + "|rm|smil|wmv|swf|wma|zip|rar|gz|pdf)$", parsed.path.lower())


    
    except TypeError:
        print ("TypeError for ", parsed)
        return False

def check_similarity(l1, l2):
    count = 0
    base = 0
    for i in l1:
        if i in l2:
            count += 1
    if (l1 < l2):
        base = len(l1)
    else:
        base = len(l2)
    if count/base >= 0.95:
        return True
    return False
