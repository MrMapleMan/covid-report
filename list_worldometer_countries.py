import re
import subprocess
import sys
import datetime

fa = re.findall
us = False

if len(sys.argv) > 1:
  # Save args with hyphens, spaces, equal signs removed
  argsModified = [i.lower().replace('-','').replace(' ','') .replace('=','')for i in sys.argv]
  if 'globaltrue' in argsModified or 'usfalse' in argsModified:
    us = False
  elif 'globalfalse' in argsModified or 'ustrue' in argsModified:
    us = True

# Store escape codes for terminal output
class codes:
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Download worldometers latest info
if us:
  site = 'https://www.worldometers.info/coronavirus/country/us'
  siteSaveFile = '/tmp/coronavirus-us.txt'
  headerFile = 'header.txt'
else:
  site = 'https://www.worldometers.info/coronavirus/'
  siteSaveFile = '/tmp/coronavirus-global.txt'
  headerFile = 'header-global.txt'
subprocess.call('curl '+site+' > '+siteSaveFile+' 2>/dev/null',shell=True)

# Store column headers
with open(headerFile) as f:
  headerStr = f.read()
headers = [i.strip('\n ') for i in headerStr.split(',')]
headersLength = len(headers)

# Extract data relevant to a particular state (or other line in the table)
def getValues(state):
  section = fa('<tr.{,200}?'+state+' ?(?:</a>)?.{1,1000}?</tr>',s,re.DOTALL)[0]
  section = section[section.find('</td>'):]	# Remove first element of table HTML
  vals_without_state = [i.strip('\n ') for i in fa('<td.*?>(.*?)(?:</a>)?</td>',section,re.DOTALL)]
  return [state] + vals_without_state	# Prepend state name to list and return it

def findStates():
  return fa('<tr.{0,100}?>(.{1,50}?)</td>',s,re.DOTALL)
  

# Read the text from the web retrieval
with open(siteSaveFile) as f:
  s = f.read()

# List all available regions
states = findStates()
states = list(set(states))  # Remove duplicates
states = [i.strip('\n\r ') for i in states]
for i in sorted(states): print(i)
