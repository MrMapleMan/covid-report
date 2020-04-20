import re
import subprocess
import sys
import datetime
import os

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
  outputFile = 'us-covid-table.csv'
else:
  site = 'https://www.worldometers.info/coronavirus/'
  siteSaveFile = '/tmp/coronavirus-global.txt'
  headerFile = 'header-global.txt'
  outputFile = 'global-covid-table.csv'
subprocess.call('curl '+site+' > '+siteSaveFile+' 2>/dev/null',shell=True)

# Store column headers
with open(headerFile) as f:
  headerStr = f.read()
headers = [i.strip('\n ') for i in headerStr.split(',')]
headersLength = len(headers)

outputFile = '/tmp/'+outputFile
dataSeparator = ';'

# Save headers to csv
with open(outputFile,'w+') as f:
  f.write(dataSeparator.join(headers)+'\n')

def floatFromText(s):
  return float(''.join(fa('[0-9]+',s)))

# Extract data relevant to a particular state (or other line in the table)
def getValues(state):
  section = fa('<tr.{,200}?'+state+' ?(?:</a>)?.{1,1000}?</tr>',s,re.DOTALL)[0]
  section = section[section.find('</td>'):]	# Remove first element of table HTML
  vals_without_state = [i.strip('\n ') for i in fa('<td.*?>(.*?)(?:</a>)?</td>',section,re.DOTALL)]
  return [state] + vals_without_state	# Prepend state name to list and return it

def findAndPrintStates():
  snippets = fa('<tr.{0,100}?>.{1,50}?</td>',s,re.DOTALL)
  for i in snippets: print i

# Read the text from the web retrieval
with open(siteSaveFile) as f:
  s = f.read()

# Find cases in regions of interest
if us:
  regions = ['USA Total','California','Utah','Ohio','New York','Louisiana','Florida','Pennsylvania','Minnesota','South Carolina']
else:
  regions = ['World','USA','Spain','Italy','China','Iran','India','S. Korea','Canada','Ireland']
for region in regions:
  print(codes.BOLD + codes.MAGENTA + region+':' + codes.RESET)
  vals = getValues(region)
  with open(outputFile,'a') as f:
    f.write(dataSeparator.join(vals)+'\n')

  # Calculate additional parameters
  searchList = ['Total Cases','Total Deaths','Active Cases','Serious/Critical']
  if us:
    searchList.pop(searchList.index('Serious/Critical'))
  stringsOfInterest = [vals[headers.index(i)] for i in searchList]
  deathsPerMillionStr = vals[headers.index('Deaths/1M pop')]
  deathsPerMillion = float(deathsPerMillionStr) if deathsPerMillionStr != '' else 0
  if not us:
    totalCases,totalDeaths,activeCases,seriousCases = [float(i.replace(',','')) if not i == '' else 0 for i in stringsOfInterest]
  else:
      totalCases,totalDeaths,activeCases = [float(i.replace(',','')) if not i == '' else 0 for i in stringsOfInterest]
  recoveredCases = totalCases - (activeCases + totalDeaths)	# Compute recoveries
  totalResolved = totalCases - activeCases			# Compute resolved (also equals recoveries + deaths)
  deathsPercentResolved = totalDeaths/totalResolved*100		# Percent of resolved cases which were fatalities
  recoveredPercentResolved = 100-deathsPercentResolved		# Percent of resolved cases which were recoveries
  # Display the data
  for i,j in enumerate([i for i in vals[:headersLength]]):
    txt = '  {:>20s}  {:<10s}  '.format(headers[i],j[:30])
    # Add information after 'Total Deaths' section
    if(headers[i] == 'Total Deaths'):
      # Calculate CFR, statistics on resolved cases
      txt += '(CFR: %.2f%% Resolved: %s [%s%.2f%%%s Fatal, %s%.2f%%%s Recovered])' %(
              totalDeaths/totalCases*100, '{:,.0f}'.format(totalResolved),
              codes.RED,   deathsPercentResolved,    codes.RESET,
              codes.GREEN, recoveredPercentResolved, codes.RESET)
    # Add information after 'Active Cases' section
    elif(headers[i] == 'Active Cases'):
      txt += '(%sActive: %.2f%% Resolved: %s%.2f%%%s)' %(
              codes.RESET, activeCases/totalCases*100, codes.BLUE,totalResolved/totalCases*100, codes.RESET)
    elif('Serious' in headers[i]):
      percentSerious = seriousCases/activeCases*100
      txt += '(%sSerious/Critical: %.2f%% Mild: %.2f%%%s)' %(codes.RESET, percentSerious, 100-percentSerious, codes.RESET)
    elif('Deaths/1M' in headers[i]):
      txt += '(%s%.3f%% of population%s)' %(codes.RESET, deathsPerMillion*1E-6*100, codes.RESET)
    # Do not print out sources information here
    elif(headers[i] == 'Source'):
      continue
    print(txt)
  print('')
  # End of 'for i,j in enumerate([i for i in vals]):'
# End of 'for region in...'

print('From '+codes.BLUE+codes.BOLD+site+codes.RESET+' (retrieved %s).' %(datetime.datetime.strftime(datetime.datetime.now(),'%m-%d-%Y at %H:%M:%S')))

# Save a timestamped copy of the file
if os.path.isfile(outputFile):
  dtString = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
  firstIdx = outputFile.rfind('/')+1
  lastIdx  = outputFile.rfind('.')   
  copyName = outputFile[firstIdx:lastIdx] + '.' + dtString
  subprocess.call('mkdir -p ~/covid-data',shell=True)                           # Ensure that directory path exists
  subprocess.call('cp '+outputFile+' ~/covid-data/'+copyName, shell=True)       # Copy file to desired location
