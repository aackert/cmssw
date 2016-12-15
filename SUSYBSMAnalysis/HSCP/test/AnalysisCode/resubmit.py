#! /usr/bin/env python

import os
import commands
import glob
import time

indir = "Results/"
jobfilesdir = "FARM/inputs/" 
cmdfile = "FARM/inputs/HscpAnalysis.cmd"
samplesFiles = "Analysis_Samples.txt"
types = set()

def initProxy():
   print "Init Proxy check"
   if(not os.path.isfile(os.path.expanduser('~/x509_user_proxy/x509_proxy')) or ((time.time() - os.path.getmtime(os.path.expanduser('~/x509_user_proxy/x509_proxy')))>600)):
      print "You are going to run on a sample over grid using either CRAB or the AAA protocol, it is therefore needed to initialize your grid certificate"
      #os.system('mkdir -p ~/x509_user_proxy; voms-proxy-init --voms cms -valid 192:00 --out ~/x509_user_proxy/x509_proxy')#allmust be done in the same command to avoid environement problems.  Note that the first sourcing is only needed in Louvain
      os.system('mkdir -p ~/x509_user_proxy; voms-proxy-init --voms cms -valid 192:00 --out ~/x509_user_proxy/x509_proxy')

for root, dirs, files in os.walk(indir):
    print root
    if "old" in root: continue
    if "Type" not in root: continue
    if "EXCLUSION" in root: continue
    anaType = int(root.split("/")[-1].replace("Type",""))
    types.add(anaType)

todo = []
with open(samplesFiles) as ifile:
    for iline, l in enumerate(ifile):
        line = l.strip()
        if len(line)==0 or line[0]=='#' : continue
        spl = [l.strip().strip('"') for l in line.split(",")]
        expectedFileName= "Histos_{}_{}.root".format(spl[2], spl[3])
        sampleString = "ANALYSE_{}_to_{}".format(iline, iline)
        for t in types:
            fp = indir+"Type{}".format(t)+"/"+expectedFileName
            if not os.path.isfile(fp) or os.path.getsize(fp)<1024:
                typeString = ", {},".format(t)
                for root, _, files in os.walk(jobfilesdir):
                    for f in files:
                        if "_HscpAnalysis.sh" not in f: continue
                        contents = open(os.path.join(root, f)).read()
                        if sampleString not in contents or typeString not in contents:
                            continue
                        todo.append(f)

with open(cmdfile) as f:
   initProxy()
   for l in f:
        line = l.strip()
        for t in todo:
            if t in line:
                print line
                os.system(line)
                break

