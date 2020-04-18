class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

print(bcolors.OKGREEN + 'green' + bcolors.ENDC)
print(bcolors.OKBLUE  + 'blue'  + bcolors.ENDC)
print(bcolors.FAIL    + 'fail'  + bcolors.FAIL)
