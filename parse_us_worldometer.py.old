import re
import subprocess


fa = re.findall

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
subprocess.call('curl https://www.worldometers.info/coronavirus/country/us > /tmp/coronavirus-us.txt 2>/dev/null',shell=True)

# Store column headers
with open('header.txt') as f:
  headerStr = f.read()
headers = [i.strip('\n ') for i in headerStr.split(',')]

def floatFromText(s):
  return float(''.join(fa('[0-9]+',s)))

# Extract data relevant to a particular state (or other line in the table)
def getValues(state):
  section = fa('<tr.{,100}?>.{,5}?'+state+' ?</td>.{1,1000}?</tr>',s,re.DOTALL)
  #section = fa('<tr.{,100}?></td.{0,25}?> ?'+state+' ?</td>.{1,1000}?</tr>',s,re.DOTALL)
  if len(section) > 0:
    section = section[0]
  else:
    section = ''
  return [i.strip('\n ') for i in fa('<td.*?>(.*?)</td>',section,re.DOTALL)]

def findAndPrintStates():
  snippets = fa('<tr.{0,100}?>.{1,50}?</td>',s,re.DOTALL)
  for i in snippets: print i

# Read the text from the web retrieval
with open('/tmp/coronavirus-us.txt') as f:
  s = f.read()

# Find cases in regions of interest
for region in ['USA Total','California','Utah','Idaho','Montana','New York','Pennsylvania','Florida','Ohio']:
  print(codes.BOLD + codes.MAGENTA + region+':' + codes.RESET)
  # Calculate additional parameters
  vals = getValues(region)
  totalCasesStr = vals[headers.index('Total Cases')]
  totalCases = float(totalCasesStr.replace(',',''))
  totalDeathsStr = vals[headers.index('Total Deaths')]
  totalDeaths = float(totalDeathsStr.replace(',',''))
  activeCasesStr = vals[headers.index('Active Cases')]
  activeCases = float(activeCasesStr.replace(',',''))
  recoveredCases = totalCases - (activeCases + totalDeaths)	# Compute recoveries
  totalResolved = totalCases - activeCases			# Compute resolved (also equals recoveries + deaths)
  deathsPercentResolved = totalDeaths/totalResolved*100		# Percent of resolved cases which were fatalities
  recoveredPercentResolved = 100-deathsPercentResolved		# Percent of resolved cases which were recoveries
  # Display the data
  for i,j in enumerate([i for i in vals]):
    txt = '  %20s   %s' %(headers[i],j[:30])
    # Add information after 'Total Deaths' section
    if(headers[i] == 'Total Deaths'):
      # Calculate CFR, statistics on resolved cases
      txt += ' CFR: %.2f%% Resolved: %s (%s%.2f%%%s Fatal, %s%.2f%%%s Recovered)' %(
              totalDeaths/totalCases*100, '{:,.0f}'.format(totalResolved),
              codes.RED,   deathsPercentResolved,    codes.RESET,
              codes.GREEN, recoveredPercentResolved, codes.RESET)
    # Add information after 'Active Cases' section
    elif(headers[i] == 'Active Cases'):
      txt += ' %sActive: %.2f%% Resolved: %.2f%%%s' %(
              codes.RESET, activeCases/totalCases*100, totalResolved/totalCases*100, codes.RESET)
    # Do not print out sources information here
    elif(headers[i] == 'Source'):
      continue
    print(txt)
  print('')
  # End of 'for i,j in enumerate([i for i in vals]):'
# End of 'for region in...'
