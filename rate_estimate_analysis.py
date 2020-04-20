from datetime import datetime, timedelta
import random
from matplotlib import pyplot as plt
import os
import math
import time

# Future tasks:
#   Include unaccounted recoveries
#   Include naturally immune?

class pandemicInfo:
  actualCFR      = 0.05			# Likelihood that infection is fatal
  populationSize = 100000		# Total population for simulation
  recoverySpread = 3                    # Range for recovery times (+/-) [days]
  fatalitySpread = 1                    # Range for fatality times (+/-) [days]
  recoveryBase   = 14                   # Time from infection to recovery [days]
  fatalityBase   = 5                    # Time from infection to fatality [days]
  infectionRatio = 0.60			# Portion of population that becomes infected
  beta		 = 2			# Shape parameter (higher beta implies tighter spread of infection dates)

def runSimulation(doPrint=False,params=pandemicInfo(),showPlots=False):
  # Define simulation parameters
  firstPossible  = datetime(2020,1,1)	# First possible date for contracting virus
  lastPossible   = datetime(2020,6,30)	# Last date of simulated outbreak
  actualCFR      = params.actualCFR
  populationSize = params.populationSize
  recoverySpread = params.recoverySpread
  fatalitySpread = params.fatalitySpread
  recoveryBase   = params.recoveryBase
  fatalityBase   = params.fatalityBase
  beta 		 = params.beta
  infectionRatio = params.infectionRatio

  # Average time difference between a fatality vs a countable recovery
  deathRecoveryDelta  = recoveryBase - fatalityBase

  tdelta = lastPossible - firstPossible
  lengthDays = tdelta.days

  # Compute characteristic time
  R = 0.01 						   # (1-R)*100% of infections to occur by last day (lastPossible)
  eta = float(lengthDays) / ( (-math.log(R))**(1./beta))   # eta = t/(-ln(R)^(1/beta)

  recoverableStartDates = []
  recoverableResolveDates = []
  fatalStartDates = []
  fatalResolveDates = []
  uninfectedCount = []

  caseCount = []
  tStart = time.time()
  # Loop through days
  for i in range(lengthDays):
    # Determine expected number of infected
    t = float(i)
    ratioInfected = (1-math.exp(-((t/eta)**beta))) - (1-math.exp(-(((t-1)/eta)**beta)))
    ratioInfected *= infectionRatio
    infections = float(populationSize)*ratioInfected/(1-R)

    caseCount.append(infections)

    # Separate fatal and recoverable infections
    fatalInfections = int(round(actualCFR * infections))
    recoverableInfections = int(round((1.-actualCFR)*infections))
    
    # Append fatal and recoverable start dates
    recoverableStartDates = recoverableStartDates + [firstPossible+timedelta(i)]*recoverableInfections
    recoverableResolveDates = recoverableResolveDates + [firstPossible+timedelta(i)+timedelta(recoveryBase + (random.random()-.5)*recoverySpread) for d in range(recoverableInfections)]
    fatalStartDates = fatalStartDates + [firstPossible+timedelta(i)]*fatalInfections
    fatalResolveDates = fatalResolveDates+[firstPossible+timedelta(i)+timedelta(fatalityBase+(random.random()-0.5)*fatalitySpread) for d in range(fatalInfections)]

  totalInfections = len(fatalStartDates)+len(recoverableStartDates)
  
  print('(Remove after testing) infections: %s (%4.1f%% of population) fatal: %s (%4.2f%% of cases) recovered: %s' %(
	 '{:,}'.format(totalInfections), float(totalInfections)/populationSize*100, '{:,}'.format(len(fatalStartDates)),
         float(len(fatalStartDates))/totalInfections*100,'{:,}'.format(len(recoverableStartDates)) ) )
  
  # Plot new cases for verification
  plt.figure()
  plt.plot(range(lengthDays),caseCount)
  plt.savefig(os.path.expanduser('~/case-count-simulation.png'))
  print('(Remove after testing) Saved plot to '+os.path.expanduser('~/case-count-simulation.png'))

  # For each reporting day, calculate different CFRs (simple CFR, resolved-only CFR, lagging resolved-only CFR)
  reportDates = [firstPossible + timedelta(i) for i in range(lengthDays+25)]
  deathsSimple           = []
  recoveriesSimple       = []
  deathsLag		 = []
  recoveriesLag  	 = []
  casesSimple		 = []
  CFR_Simple             = []
  CFR_Resolved		 = []
  CFR_Lag		 = []
  CFR_True		 = []
  percentActive	 	 = []

  for j in reportDates:
    deathCountSimple	= len([day for day in fatalResolveDates if day <= j])
    recoveryCountSimple = len([day for day in recoverableResolveDates if day <= j])

    recoveryCountLag    = recoveryCountSimple
    deathCountLag       = len([day for day in fatalResolveDates if day <= j-timedelta(deathRecoveryDelta)])

    caseCountSimple	= len([day for day in fatalStartDates if (day <= j)])
    caseCountSimple     += len([day for day in recoverableStartDates if (day<=j)])

    # Count all prior deaths and current cases that will result in deaths
    deathCountTrue      = len([day for day in fatalStartDates if day <= j])

    deathsSimple.append(deathCountSimple)
    recoveriesSimple.append(recoveryCountSimple)
    deathsLag.append(deathCountLag)
    recoveriesLag.append(recoveryCountLag)
    casesSimple.append(caseCountSimple)
    uninfectedCount.append(populationSize-caseCountSimple)

    CFR_Simple.append(float(deathCountSimple)/float(max([caseCountSimple,1]))*100)
    CFR_Resolved.append(float(deathCountSimple)/(max([deathCountSimple+recoveryCountSimple,1]))*100)
    CFR_Lag.append(float(deathCountLag)/(max([deathCountLag+recoveryCountLag,1]))*100)
    CFR_True.append(float(deathCountTrue)/max([caseCountSimple,1])*100)

    percentActive.append(100.0-float(deathCountSimple+recoveryCountSimple)/max([caseCountSimple,1])*100)

    dayStr = datetime.strftime(j,'%Y-%m-%d')


    if(doPrint):
      print('%s %6d deaths (%6d lag) %6d recoveries %6d cases CFR (simple,resolved,lag,true): %4.2f%% %4.2f%% %4.2f%% %4.2f%%  active: %4.2f%%' %(
              dayStr,deathCountSimple,deathCountLag,recoveryCountSimple,caseCountSimple, 
              CFR_Simple[-1],CFR_Resolved[-1],CFR_Lag[-1],CFR_True[-1],percentActive[-1] ) )
  tEnd = time.time()
  print('%.2f seconds to complete simulation.' %(tEnd-tStart))

  # Plot results
  homePath = os.path.expanduser('~/')
  days = [(i-reportDates[0]).days for i in reportDates]
  plt.figure()
  plt.plot(days,CFR_Simple,label='CFR Simple')
  plt.plot(days,CFR_Resolved,label='CFR Resolved')
  plt.plot(days,CFR_Lag,label='CFR Lag')
  plt.plot(days,CFR_True,label='CFR True')
  plt.plot(days,percentActive,label='% Active')
  plt.title('CFR by Multiple Methods')
  plt.legend()
  figpath = homePath + 'CFR-simulation.png'
  plt.savefig(figpath)
  print('Saved plot to %s' %figpath)

  plt.figure()
  plt.plot(days,CFR_Simple,label='CFR Simple')
  plt.plot(days,CFR_Resolved,label='CFR Resolved')
  plt.plot(days,CFR_Lag,label='CFR Lag')
  plt.plot(days,CFR_True,label='CFR True')
  plt.plot(days,percentActive,label='% Active')
  plt.title('CFR by Multiple Methods')
  plt.ylim([0,.2])
  plt.legend()
  figpath = homePath + 'CFR-simulation-select.png'
  plt.savefig(figpath)
  print('Saved plot to %s' %figpath)
  
  plt.figure()
  plt.plot(days,deathsSimple,label='Simple')
  plt.plot(days,deathsLag,label='Lag')
  plt.plot(days,uninfectedCount,label='Uninfected')
  plt.plot(days,recoveriesSimple,label='Recovered')
  plt.legend()
  figpath = homePath + 'Deaths-simulation.png'
  plt.savefig(figpath)
  print('Saved plot to %s' %figpath)

  if(showPlots):
    plt.show()
# End runSimulation()

if __name__ == '__main__':
  runSimulation(doPrint=False)
