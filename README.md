# covid-report

parse_worldometer.py:
  Reports key parameters about COVID-19 progression in specified regions.  Downloads html using curl and parses file.
  Optional command line args:
    --global=True/False (generates reports for countries) or --us=True/False (generates report for states in USA)

rate_estimate_analysis.py:
  Runs a simulation that examines multiple methods of estimating CFR (case fatality rate).
  CFR is a key number in estimating the impact of a pandemic.  
  My experimental version is labeled as "CFR_Lag", the notes at the top of the file give more details.
  This version attempts to compensate for recoveries that have not yet occurred by omitting fatalities which have occurred sooner than a recovery would have (given the same infection time).
