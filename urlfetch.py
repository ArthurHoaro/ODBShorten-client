#!/usr/bin/python
#
# Open Database of Shortened Links client 
# ODBShorten client
# ===================================================
# "Because the Internet is the new memory of Humanity,
# It can not be lost by stupidity."
# Learn more about ODBShorten project: http://wiki.hoa.ro/doku.php?id=projects:obdshorten
#
# ODBShorten client is used to populate ODBShorten 
# by crawling shortened links
#
# Author: Arthur Hoaro <arthur@hoa.ro> <website>
# Version: 0.1.0-dev
# Licence: GNU Lesser General Public License <http://www.gnu.org/licenses/lgpl-3.0.txt>
# Code: URL
# Documentation: http://wiki.hoa.ro/doku.php?id=projects:obdshorten:client
# 
# ODBShorten client and ODBShorten API are currently
# in development mode and should not be used in another way
#

import urllib2
import httplib
import sys
import getopt
import json
import iso8601
from datetime import datetime
import pytz
from errors import *
import base64
from pydoc import help


linkNb = 0
API_URL = "http://localhost:7501/"
ERROR_KEY = ''
MESSAGE_KEY = ''
ERRORS = dict()

class APICall(object):
    """Handle communication between client and ODBShorten"""

    def make(self, url):
        """Returns a dict from the JSON file returned by the given API 'url'"""
        return json.load(urllib2.urlopen(API_URL + url))

    def getShortenerByName(self, shortenerName):
        """Returns values to create a Shortener according to 'shortenerName' given"""
        return self.make('shortener/get?name='+shortenerName)

    def getShortenerById(self, idShortener):
        """Returns values to create a Shortener according to 'shortenerName' given"""
        return self.make('shortener/get?id='+idShortener)

    def addLink(self, link, useName=False):
        """Add a real link into the database through API with the given 'link' (Link type)
        Need link.shortener (with id or name), link.varPart and link.real set"""
        if useName is True or (link.shortener.id is None and link.shortener.name is not None):
            return self.make('link/add?shortener='+ str(link.shortener.name) +'&var_part='+ link.varPart +'&real='+ self.urlEncode(link.real) )
        else:
            return self.make('link/add?shortener='+ str(link.shortener.id) +'&var_part='+ link.varPart +'&real='+ self.urlEncode(link.real) )

    def updateLink(self, link):
        """Update a link into the database through API with the given 'link' (Link type)
        Need link.id and link.real set"""
        return self.make('link/update?id_link='+ str(link.id) +'&real='+  self.urlEncode(link.real))

    def getLastEdit(self, link):
        """Returns the id, the real link and date of last edit of the given 'link' (Link type) through API
        Need link.shortener and varPart set"""
        return self.make('link/get/byvar?shortener='+ str(link.shortener.id) +'&var_part='+ link.varPart)

    def urlEncode(self, url):
        """Return encoded link from the given 'url' in order to send it through HTTP API"""
        return urllib2.quote(url)

def loadErrors():
    try:
        data = json.load(urllib2.urlopen(API_URL + 'errors.json'))
        global ERROR_KEY, MESSAGE_KEY, ERRORS
        ERROR_KEY = data['ERROR_KEY']
        MESSAGE_KEY = data['MESSAGE_KEY']
        ERRORS = data['ERROR_CODES']
        return True
    except Exception, e:
        return False

class ShortenerFactory(object):
    """Create Shorteners from its name, using the API"""   

    def createShortener(self, shortener):
        """Return a Shortener object from the 'shortener' name given"""
        data = APICall().getShortenerByName(shortener)
        if ERROR_KEY in data:
            return False

        id = data['id_shortener']
        domain = data['domain']
        sdir = data['subdir']
        options = {}
        if 'varnum' in data:
            options['optNum'] = data['varnum']
        if 'varalpha' in data:
            options['optAlpha'] = data['varalpha']
        if 'varcase' in data:
            options['optCase'] = data['varcase']

        return Shortener(id, shortener, domain, sdir, **options)
    
class Shortener(object):
    """Shortener object
    Attributes:
    - id [int]
    - domain [str]
    - directory [str] (e.g. 'http://short.en/link/afgkd', '/link/' is subdir)
    - options [booleans]:
        * optApha: allow alphabetic characters
        * optCase: alphabetic characters are case sensitive
        * optNum : allow numeric characters"""
    
    def __init__(self, id, name, domain, sdir, **options):
        """"Create a shortener"""
        # self._domain = domain
        # self._dir = sdir
        self.id = id
        self.name = name
        self.domain = domain
        self.dir = sdir
        self._optNum = True
        self._optAlpha = True
        self._optCase = True
        for key, value in options.items():
            try:
                attr = getattr(self, "_set_"+str(key))
                attr(value)
            except:
                print 'ERROR'
        self.updateCharset()
        
    def updateCharset(self):
        """Updating allowed characters depending on options"""
        self._charset = ''
        if self.optAlpha:
            self._charset += self.char_range('a', 'z')
        if self.optCase:
            self._charset += self.char_range('A', 'Z')
        if self.optNum:
            self._charset += self.char_range('0', '9')
        
    def char_range(self, c1, c2):
        """Generates the characters from `c1` to `c2`, inclusive."""
        out = ''
        for c in xrange(ord(c1), ord(c2)+1):
            out += chr(c)
        return out
    
    def __str__(self):
        return 'Shortener (id '+ str(self.id) +') : '+ self.domain + self.dir +' -- Options : optNum = '+ str(self.optNum) +' - optAlpha = '+ str(self.optAlpha) +' - optCase = '+ str(self.optCase) +' ~ Charset => (' + self.charset + ')'
    
    def _get_optNum(self):
        return self._optNum
    def _set_optNum(self, opt):
        self._optNum = opt
        self.updateCharset()
    optNum = property(_get_optNum, _set_optNum)
    
    def _get_optAlpha(self):
        return self._optAlpha
    def _set_optAlpha(self, optAlpha):
        self._optAlpha = optAlpha
        self.updateCharset()
    optAlpha = property(_get_optAlpha, _set_optAlpha)
    
    def _get_optCase(self):
        return self._optCase
    def _set_optCase(self, opt):
        self._optCase = opt
        self.updateCharset()
    optCase = property(_get_optCase, _set_optCase)
    
    def _get_charset(self):
        return self._charset
    def _set_charset(self):
        self.updateCharset()
    charset = property(_get_charset, _set_charset)

    def set_options(self, **options):
        for key, value in options.items():
            try:
                attr = getattr(self, "_set_"+str(key))
                attr(value)
            except:
                print 'ERROR'
    
class Link(object):
    """Link object - association varPart <-> real link
    Attributes:
    - id shortener [int]
    - varPart [str]: string of shortener leading to a specific link
    - real [str]: the real link
    - dateAdd (optional) [datetime]
    - dateEdit(optional) [datetime]"""        
    
    def __init__(self, shortener, varPart, real=None, dateAdd=None, dateEdit=None):
        self._id = None
        self.shortener = shortener
        self.varPart = varPart
        self.real = real
        self.dateAdd = dateAdd
        self.dateEdit = dateEdit

    def _get_id(self):
        return self._id
    def _set_id(self, id):
        self._id = id
    id = property(_get_id, _set_id)

    def __str__(self):
        return 'Link: shortener = '+ str(self.shortener.id) + ' - varPart = '+ self.varPart

    def strUrl(self):
        return self.shortener.domain + self.shortener.dir + self.varPart



class Crawler(object):
    """Object used to crawl link's varPart
    Attributes
    - shortener [Shortener]"""

    def __init__(self, shortener):
        self.shortener = shortener

    def next(self, string):
        """ Get next sequence of characters.
     
        Treats characters as numbers (0-255). Function tries to increment
        character at the first position. If it fails, new character is
        added to the back of the list.
     
        It's basically a number with base = 256.
     
        :param string: A list of characters (can be empty).
        :type string: list
        :return: Next list of characters in the sequence
        :rettype: list

        FROM https://gist.github.com/astro-/1121315
        """
        if len(string) <= 0:
            string.append(self.indexToCharacter(0))
        else:
            string[0] = self.indexToCharacter((self.characterToIndex(string[0]) + 1) % len(self.charset))
            if self.characterToIndex(string[0]) is 0:
                return list(string[0]) + self.next(string[1:])
        return string

    def characterToIndex(self, char):
        return self.charset.index(char)
 
    def indexToCharacter(self, index):
        if self.charset <= index:
            raise ValueError("Index out of range.")
        else:
            return self.charset[index]

    def _get_charset(self):
        return self.shortener.charset
    charset = property(_get_charset)

class Logging(object):
    def write(self, msg):
        print '['+ str(datetime.now()) +'] ' + str(linkNb) + ' - '+ str(msg)


def main(argv=None):
    """Main
    Usage: urlfetch.py -s <shortener_name> [-f <str_size_mini>] [-t <str_size_maxi>] [-b <init_string>]
    Arguments: 
        * -s, --shortener
            Shortener name
        * -f, --from
            Mininal length of the variable string
        * -t, --to
            Maximal length of the variable string
        * -b, --base
            Initialize crawling from 'base' string"""

    if argv is None:
        argv = sys.argv
    usage = '[SYNTAX] Usage: '+ argv[0] +' -s <shortener_name> [-f <str_mini>] [-t <str_maxi>] [-b <init_string>]' 
    log = Logging()

    try:
        opts, args = getopt.getopt(argv[1:], "hs:f:t:b:", ["help=", "shortener=", "from=", "to=", "base="])
    except getopt.GetoptError:
        print usage
        sys.exit(2)

    if ('-s' or '--shortener') not in dict(opts):
        print usage 
        sys.exit()

    MINI = MAXI = varStr = None

    for opt, arg in opts:
        if opt in ("-s", "--shortener"):
            shortename = arg
        elif opt in ("-f", "--from"):
            MINI = arg
        elif opt in ('-t', '--to'):
            MAXI = arg
        elif opt in ('-b', '--base'):
            varStr = list(arg)
        else:
            print usage 
            sys.exit()

    log.write( '================ URLFetch program starting ================' )

    if MINI is None:
        MINI = 0
        log.write('Notice: No minimum value set. Using default '+ str(MINI))
    else:
        MINI = int(MINI)

    if MAXI is None:
        MAXI = 8
        log.write('Notice: No maximum value set. Using default '+ str(MAXI))
    else:
        MAXI = int(MAXI)

    if loadErrors() is False:
        log.write('ERROR: Unable to create ERROR codes from JSON')
        log.write('Exit program')
        sys.exit()

    sfactory = ShortenerFactory()
    s = sfactory.createShortener(shortename)
    print s
    # sys.exit()
    if s is False:
        log.write('ERROR: Shortener "' + shortename + '"" not found')
        log.write('Exit program')
        sys.exit()

    if varStr is None:
        varStr = list(s.charset[0])

    if len(varStr) < MINI:
        varStr = ''
        for i in range(MINI):
            varStr += s.charset[0]
        varStr = list(varStr)

    log.write( '| Starting information ')
    log.write( '| --------------------- ')
    log.write( '| - Shortener: '+ shortename )
    log.write( '| - From: '+ str(MINI) )
    log.write( '| - To: '+ str(MAXI) )
    log.write( '| - Domain: '+ str(s.domain) )
    log.write( '| - Subdir: '+ str(s.dir) )
    log.write( '| - Alpha: '+ str(s.optAlpha) )
    log.write( '| - Case: '+ str(s.optCase) )
    log.write( '| - Num: '+ str(s.optNum) )
    log.write( '| - Between: '+ str(MINI) +' and '+ str(MAXI) +'chars')
    log.write( '| - Base: '+ ''.join(varStr) )

    crawler = Crawler(s);
    global linkNb

    while len(varStr) <= MAXI:
        linkNb += 1
        log.write( 'Info: Trying to reach "'+ s.domain + s.dir + ''.join(varStr) +'"...' )
        ##################### 
        #   MAIN CODE
        #####################
        try:
            http = httplib.HTTPConnection(s.domain)
            http.request('GET', s.dir + ''.join(varStr))
            dHeaders = dict(http.getresponse().getheaders())
        except:
            log.write("| Unable to reach the domain. Maybe it doesn't exists ?")
        # Redirection found
        if 'location' in dHeaders and s.domain not in dHeaders['location']:
            real = dHeaders['location']
            link = Link(s, ''.join(varStr), real)
            log.write( '| Info: Result found !' )

            try:
                response = APICall().addLink(link)
                if 'id_link' in response:                    
                    link.id = response['id_link']

                if ERROR_KEY in response:              
                    if ERROR_KEY in response and int(response[ERROR_KEY]) == ERRORS['LINK_DUPLICATE']:
                        raise DuplicateLinkException(link)
                    elif MESSAGE_KEY in response:
                        raise WTFException(response[MESSAGE_KEY])
                    else:
                        raise WTFException()
                log.write( '| -> Added link ID '+ str(link.id) )

            # Link already exists
            except DuplicateLinkException, duplicate_e:
                log.write( '| -> '+ str(duplicate_e) )   
                now = datetime.now(pytz.utc)
                # Test if the link have been updated in more than a month (disabled in dev mode)
                if iso8601.parse_date(response['last_edit']) < now.replace(hour=now.hour+1):
                    # Test if real link have changed
                    if response['real'] != link.real:
                        log.write( '| -> Update needed on link ID '+ str(link.id) +'...' )
                        try:
                            update = APICall().updateLink(link)
                            if ERROR_KEY in update:
                                if int(update[ERROR_KEY]) == ERRORS['LINK_NOTHING_UPDATE']:           
                                    raise NothingUpdateException(link)
                                else:
                                    raise WTFException(update['message']) 
                        except UpdateLinkException, ule:
                            log.write('| '+ str(ule))
                        except WTFException, wtfe:
                            log.write( '| '+ str(wtfe))  
                            sys.exit()    
                        log.write( '| -> Link updated' )
                    else:
                        log.write('| -> Real link did not change') 
                else:
                    log.write('| -> Recent check: do not need update')                
            except WTFException, wtfe:
                log.write( '| '+ str(wtfe))  
                sys.exit()               
        else:
            log.write('| Info: Undefined')            
        varStr = crawler.next(varStr)
    print cpt
    
if __name__ == "__main__":
    main(sys.argv)
