import re
import subprocess

fa = re.findall

# Store color escape codes
class colors:
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Download worldometers latest info
subprocess.call('curl https://www.worldometers.info/coronavirus/ > /tmp/worldometers.txt 2>/dev/null',shell=True)

def floatFromText(s):
  return float(''.join(fa('[0-9]+',s)))

# Read the text from the web retrieval
with open('/tmp/worldometers.txt') as f:
  s = f.read()

# Find total cases
totalCasesWithCommas = fa('Coronavirus Cases.{1,250}?(\d+,\d{3}(?:,\d{3}){,5})',s,re.DOTALL)[0]
totalCases = floatFromText(totalCasesWithCommas)

# Find deaths
fatalCasesWithCommas = fa('Deaths.{1,250}?(\d+,\d{3}(?:,\d{3}){,5})',s,re.DOTALL)[0]
fatalCases = floatFromText(fatalCasesWithCommas)

# Find recoveries
recoveredCasesWithCommas = fa('Recovered.{1,550}?(\d+,\d{3}(?:,\d{3}){,5})',s,re.DOTALL)[0]
recoveredCases = floatFromText(recoveredCasesWithCommas)

# Total recovered and percentages
resolvedCases = fatalCases + recoveredCases
percentResolved = resolvedCases/totalCases*100
percentFatal = fatalCases / resolvedCases * 100
percentRecovered = 100 - percentFatal

# Find active cases
activeCasesWithCommas = fa('Active Cases.{1,550}?(\d+,\d{3}(?:,\d{3}){,5})',s,re.DOTALL)[0]
activeCases = floatFromText(activeCasesWithCommas)
percentActive = activeCases / totalCases * 100

# Separate mild and severe
mildCasesWithCommas = fa('(\d+,\d{3}(?:,\d{3}){,5})</span>.{,200}?in Mild Condition',s,re.DOTALL)[0]
mildCases = floatFromText(mildCasesWithCommas)
percentMild = mildCases / activeCases * 100
severeCasesWithCommas = fa('(\d+,\d{3}(?:,\d{3}){,5})</span>.{,200}?Serious or Critical',s,re.DOTALL)[0]
severeCases = floatFromText(severeCasesWithCommas)
percentSevere = severeCases / activeCases * 100

print('\nTotal cases: %s' %(colors.BOLD+colors.GREEN+'{:,}'.format(int(totalCases))+colors.RESET) )

print('\nActive cases: %s (%.2f%% of total)\n\t(Severe: %s [%.2f%%] Mild: %s [%.2f%%])' %(
      activeCasesWithCommas, percentActive,
      colors.BOLD+colors.RED+severeCasesWithCommas+colors.RESET, percentSevere,
      colors.BOLD+colors.GREEN+mildCasesWithCommas+colors.RESET, percentMild) )

print('\nResolved cases: %s (%.2f%% of total)\n\t(Fatal: %s (%.2f%%) Recovered: %s (%.2f%%))' %(
      '{:,}'.format(int(resolvedCases)), percentResolved, 
      colors.BOLD+colors.RED+fatalCasesWithCommas+colors.RESET, percentFatal,
      colors.BOLD+colors.GREEN+recoveredCasesWithCommas+colors.RESET, percentRecovered) )
