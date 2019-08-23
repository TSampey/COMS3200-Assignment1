###################################################################
#
#   COMS3200 - Assignment 1
#
#   Student Name: Thomas Sampey
#
###################################################################

import sys
import socket

from datetime import datetime
from urllib.parse import urlparse
from time import strptime
from dateutil import tz
from dateutil.parser import *

def main():
    """
    Main method
    Handles the initialisation of the program
    and when there is a redirect from the URL given
    """
    if len(sys.argv) > 1:
        print("URL Requested: "+sys.argv[1])
        url = sys.argv[1]

        #call function next part
        #open TCP connection
        statusCode= -1
        #initialUrl = sys.argv[1]
        prevUrl = ""
        i=0
        while statusCode == -1 or statusCode == 301 or statusCode == 302:
            if getProtocol(url) == "https" or getProtocol(prevUrl) == "https":
                print("https not supported")
                sys.exit()
            else:
                #print("HTTP")

                if prevUrl=="" and statusCode == -1:
                    
                    parsedUrl = parseURL(url)
                    #print(parsedUrl)
                    statusCode, prevUrl = processHTTP(parsedUrl)
                    #print("stat: "+ str(statusCode))
                    #print("Prev: "+prevUrl)
                    
                 
                elif statusCode != 200 and prevUrl != "":
                    #print("-----\nloop:" + str(i+1) +"\n----")
                    
                    #print("test: "+prevUrl)
                    prevUrl = prevUrl.strip("'")
                    #print("test: "+prevUrl)
                    prevUrl = parseURL(prevUrl)
                    #print("Entered Previous URL:" + prevUrl)
                    #print("test1: "+prevUrl)
                    statusCode, prevUrl = processHTTP(prevUrl)
                    #print("prevUrl: " +prevUrl+"\nstatus Code: " +str(statusCode)+"\n----")
                    
                   
                
                else:
                    pass
        
    else:
        sys.exit()

        

def getProtocol(url):
    """
    getProtcol(url) -> (Int)
    gets the protocol being used by the web browser
    """
    protocol = urlparse(url)

    return (protocol.scheme)

def parseURL(url):
    """
    parseURL(url) -> (String, String)
    Handles the parsing of the URL
    e.g. domain.com/path
    """
    newUrl = urlparse(url)

    return (newUrl.netloc, newUrl.path)




def processHTTP(URL):
    """
    processHTTP(URL) -> (Int, String)
    Sets up the TCP connection and sends a GET request to the
    URL. Receives all the data if the Status code == 200 and prints it to a file
    along with Retrieval successful and other header information.
    Else Prints the Temporarily/Permanently Moved/ Retrieval failed message

    """
    #print("PROCESS: " + URL)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host, path = URL
    ServerPort = 80
    
    #connect to Server
    s.connect((host,ServerPort))
    clientInfo = s.getsockname()
    serverInfo = s.getpeername()
    
    print("Client: " + str(clientInfo[0]) +" " + str(clientInfo[1]))
    print("Server: " + str(serverInfo[0]) +" " + str(serverInfo[1]))
    statusCode, location, visitDate, contentType, lastModified, headerCount = headerRequest(host, path, s)
    #print(contentType)
    #Get request
    #request = "GET "+path + "HTTP/1.1\r\nHost: " + host + "\r\nAccept: "+ contentType + "\r\n\r\n"
    if path =="":
        
        request = "GET / "+path + " HTTP/1.1\r\nHost: " + host + "\r\nConnection: close\r\nAccept-Encoding: compress, deflate\r\n\r\n"
    else:
        
        request = "GET "+path + " HTTP/1.1\r\nHost: " + host + "\r\nConnection: close\r\nAccept-Encoding: compress, deflate\r\n\r\n"
    #print("GET REQUEST\n"+request)

    
    #send GET request
    s.sendall(request.encode())
    result=""
    
    if int(statusCode) == 200:
        while True:
            recv = s.recv(4096)
            
            if not recv:
                break
            result += recv.decode()
#print(result)

    if statusCode >= 400 and statusCode < 600:
        print("Retrieval Failed (" + str(statusCode) +")")
        sys.exit()
    if statusCode == 301:
        print("Resource permanently moved to: " + location)
    if statusCode == 302:
        print("Resource temporarily moved to: " + location)

    if int(statusCode) == 200:
        print("Retrieval Successful\nDate Accessed: " + visitDate + "\nLast Modified: "+ lastModified)
        outputFile = "output" + getFileExtension(contentType)
        #saveFile = open('output.txt','w')
        saveFile = open(outputFile,'w')
        printFile = output(result, headerCount)
        saveFile.write(printFile)
        saveFile.close()



    s.close()

    return (statusCode, location)

def output(string, headerCount):
    """
    output(string, headerCount) -> String
    Checks the amount of lines within the header response
    """
    i=0
    #print(string)
    output= ""
    #print(string)
    #print(string.splitlines(True))
    
    for line in string.splitlines(True):
        # print(i)
        if i > headerCount -1 :
            #print(line)
            output += line
        i=i+1
        #print("output: "+output)
    return output



def headerRequest(host,path, skt):
    """
    headerRequest(host,path, skt) -> (String, String, String, String, String, String)
    Takes a host, path and socket, sends a 'HEAD' request. 
    Returns the header values
    
    """
    location=""
    statusCode=""
    visitDate=""
    contentType=""
    lastModified=""
    headerLines= -1
    
    if path =="":
        request = "HEAD / " +path+ " HTTP/1.1\r\nHost: " + host + "\r\nAccept-Encoding: compress, deflate, gzip\r\n\r\n"
    else:
        request = "HEAD " +path+ " HTTP/1.1\r\nHost: " + host + "\r\nAccept-Encoding: compress, deflate, gzip\r\n\r\n"
            #print ("HEAD REQUEST:\n"+request)

    skt.sendall(request.encode())
    result = skt.recv(2096)
    headerLines = len(result.decode().splitlines())
#print("headerLines: "+ str(len(headerLines)))
    
    for line in result.decode().splitlines():
        if line.startswith("HTTP"):
            statusCode = int(line[9:12])
        if line.startswith("Location:"):
            location = line[10:]
        if line.startswith("Date:"):
            visitDate = convToAest(line[6:])
        if line.startswith("Content-Type:"):
            contentType = line[14:]
        if line.startswith("Last-Modified:"):
            lastModified = getLastModified(line)
    return (statusCode,location,visitDate, contentType, lastModified, headerLines)


def getLastModified(line):
    """
    getLastModified(line) -> (String)
    Handles output for last modified 
    """
    lastModified = ""
    if line.startswith("Last-Modified:"):
        lastModified = convToAest(line[15:])
        return lastModified
    else:
        return "not available"

def convToAest(time):
    """
    convToAest(time) -> (DateTime)
    Converts GMT To AEST
    """
    #print(parse(time).tzname())
    #print(time[26:])
    if time[26:29] == "GMT":
        parseTime = parse(time)
        ausTimeZone = tz.gettz('Australia/Brisbane') #AEST = Brisbanes standard time
        parseTime = parseTime.astimezone(ausTimeZone)
        #print(parseTime)
        parsetime = parseTime.strftime("%a %d %b %Y %H:%M:%S %Z")
    #print(parsetime)
    else:
        parsetime = time
    
    return parsetime

def getFileExtension(contentType):
    """
    getFileExtension(contentType) -> (String)
    Gets the file extension from the content type header
    """
    if contentType == "text/plain":
        return ".txt"
    elif contentType == "text/html":
        return ".html"
    elif contentType == "text/css":
        return ".css"
    elif contentType == "text/javascipt" or contentType == "application/javascript":
        return ".js"
    elif contentType == "application/json":
        return ".json"
    elif contentType == "application/ocet-stream":
        return ""
    else:
        return ""
if __name__ == '__main__':
    main()

