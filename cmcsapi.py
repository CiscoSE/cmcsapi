import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from ConfigParser import SafeConfigParser
import xml.etree.ElementTree as ET
from collections import defaultdict



print "CMCS API Testing"
print "----------------"

# Get hold of the configuration file (cmcsapi.ini)
CONFIG_FILE = "cmcsapi.ini"

cfg = SafeConfigParser()

cfg.read(CONFIG_FILE)

# Read the application specific paramters

requests.packages.urllib3.disable_warnings(InsecureRequestWarning
                                           )
try:
    username = cfg.get("application","username")
    password = cfg.get("application","password")
    cmcs_ip = cfg.get("application","cmcs_ip")
except:
    print "Error reading cmcsapi.ini. Please create cmcsapi.ini"
    exit()

print "Username: "+username
print "CMCS Server: "+cmcs_ip


print "\nLogging into CMCS @ "+cmcs_ip+ " using userid: " + username

# Create the URL to request the client_credentials or token from the CMCS Server
URL='https://'+cmcs_ip+':8001/nccmws/api/v1/Token?grant-type=client_credentials'

try:
    ret=requests.get(URL, verify=False, auth=HTTPBasicAuth(username, password))
except:

    print "Unable to connect to CMCS Server "+cmcs_ip+" to get Client Credentials"
    exit()

# Parse out the access token for the remaining queries
access_token = ret.content
at = access_token.split(" ")[1]

print "\nClient Credentials Access Token received: "+ at

# Setup the XML Query to request the GetDevices function from the CMCS Server

payload = {"Authorization":"Bearer "+at,"Cache-Control":"no-cache", "Content-Type":'application/x-www-form-urlencoded' }

xmlreq = """<?xml version="1.0" encoding="UTF-8"?>
<Request requestId="17622">
     <Manage>
        <Get>
            <DeviceList all="true" brief="true"/>
        </Get>
     </Manage>
</Request>"""


req="request="+xmlreq


URL='https://'+cmcs_ip+':8001/nccmws/api/v1/Request'

try:
    ret=requests.post(URL, verify=False, headers=payload, data=req )
except:
    print "Unable to communicate to CMCS to post data."
    exit()


count = 0
database =[]
d = defaultdict(int)


root=ET.fromstring(ret.content)

# Parse through the remaining data and store the relevant data in a dictionary to count the different items

for elem in root.getiterator(tag='Device'):
    SerialNumber = str(elem.find('SerialNumber').text)
    HostName = str(elem.find('HostName').text)
    Model = str(elem.find('Model').text)
    Version = str(elem.find('Version').text)

    d[Model] += 1
    key = elem.find('SerialNumber').text
    database.append((key, elem))

    count=count+1

# Display the summary of the data.

print '\n{0:40} {1}'.format("PART NUMBER","COUNT")
print '{0:40} {1}'.format("---------------------------------------","-----")
for info in sorted(d):
    print '{0:40} {1}'.format(info,d[info])
print "\nTotal Device Count: " + str(count)


