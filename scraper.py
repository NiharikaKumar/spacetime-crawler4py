from configparser import ConfigParser
from utils.config import Config
import re
import urllib.robotparser
from urllib.parse import urldefrag, urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
from stopwords import STOPWORDS



# deliverable 1
# stores all the unique links the scraper has come across
unique_links = {}

# deliverable 2
# stores the link of the page with the most words and records its count
largest_page = ""
largest_page_url = 0

# deliverable 3
# stores all the tokens and their frequencies; global url word frequency counter
all_tokens = {}

# deliverable 4
# stores the number of the subdomains under the ics domain
ics_subdomains = 0


ignore_tags = ['header', 'footer', 'aside']
seedurls = []
get_seedurls()


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]



def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    
    
    # If the response status is outside the valid 200 range, return empty list
    # do not scrape that url
    if resp.status < 200 or resp.status >= 300:
        return list()

    # If the content of the response is None, return empty list
    if resp is None or resp.raw_response is None or resp.raw_response.content is None:
        return list()
    
    links = []

    # create beautifulsoup object using 'lxml' (faster)
    soup = BeautifulSoup(resp.raw_response.content, 'lxml')

    # tokenize the contents of the page
    tokens = tokenize(soup.get_text())

    with open('results.txt', 'w+') as results:
        for token in all_tokens:
            results.write(f"{token}: {all_tokens[token]}\n")

    parsed = urlparse(url)

    # get the robot.txt of the mentioned url
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url('https://' + parsed.netloc + '/robots.txt')
    rp.read()

    # remove certain tags (Avoid data noise)
    for tag in ignore_tags:
        for element in soup.find_all(tag):
            element.decompose()

    count += 1
    print("\t number:", count)

    # find all href (links) from <a> tag and loop through them
    for link in soup.find_all('a', href=True):
        # get full url
        full_url = get_full_url(url, link)

        # if the link has not been scraped before, 
        # and if the robot.txt allows it
        # add to unique_links and add to return set (Avoid duplicates)
        if full_url not in unique_links and full_url != url and rp.can_fetch('*', full_url):
            unique_links[full_url] = 0
            links.add(full_url)


    return list()



def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        # if parsed not in seedurls: return False (Avoid other urls)
        if parsed.netloc not in seedurls:
            return False
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise



def get_seedurls():
    # Get seedurl and add them to unique_links
    cparser = ConfigParser()
    cparser.read('config.ini')
    config = Config(cparser)


    for url in config.seed_urls:
        unique_links[url] = 0
        seedurls.append(urlparse(url).netloc)

        

def tokenize(content_string: str) -> list[str]:
    """
    Gets a string which contains all the text on a URL, and breaks it into
    tokens by splitting on anything that is not a alphanumeric character
    """

    words = []
    word = ""

    for char in content_string:
        # if the character is alphanum, attach it to the current word
        if is_alphanum(char):
            word += char
        
        # if the character is not alphanum, split the word there
        # add to the global token count
        # a word needs to have atleast 3 letters to be considered a word
        else:
            if len(word) > 2:
                word = word.lower()
                words.append(word)
                add_to_all_tokens(word)

                word = ""
    
    return words



def is_alphanum(character: str) -> bool:
    """
    returns true/false depending on whether a character is an alphanumeric 
    character, i.e. is between A-Z or a-z or 0-9
    """

    if 48 <= ord(character) <= 57:
        return True
    elif 65 <= ord(character) <= 90:
        return True
    elif 97 <= ord(character) <= 122:
        return True
    else:
        return False
    


def add_to_all_tokens(word: str) -> None:
    """
    Adds the token to the global count dictionary based on if it is a
    stopword. If the word exists already, it increments count for that word
    """

    if word not in STOPWORDS:
        if word not in all_tokens:
            all_tokens[word] = 1
        else:
            all_tokens[word] += 1
    


def get_full_url(url, link):
    # get the full urls
    # remove fragmentation
    full_url = urljoin(url, link['href'])
    full_url, _ = urldefrag(full_url)
    
    # Remove '/' at the end of url
    # if full_url[-1] == '/':
    #     full_url = full_url[:-1]
    # return full_url
    parsed_url = urlparse(full_url)
    clean_url = urlunparse(parsed_url._replace(query=""))
    if clean_url[-1] == '/':
        clean_url = clean_url[:-1]
    return clean_url