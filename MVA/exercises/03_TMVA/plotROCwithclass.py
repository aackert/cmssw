#!/usr/bin/env python
#------------------------------------------------------------------
#- File: plot.py
#- Description: plot results of training with TMVA
#  Created: 01-Jun-2013 INFN SOS 2013, Vietri sul Mare, Italy, HBP
#    adapt to CMSDAS 2015 Bari HBP
#------------------------------------------------------------------
import os, sys
from histutil import *
from time import sleep
from array import array
from ROOT import *
import ROOT
import numpy as np
#------------------------------------------------------------------
def readAndFill(filename, treename, h):
    print "==> reading %s" % filename
    # open ntuple (see histutil.py for implementation)
    ntuple = Ntuple(filename, treename)
    # loop over ntuple
    for rownumber, event in enumerate(ntuple):
        h.Fill(event.Pt, event.I, 1.0)
        if rownumber % 500 == 0:
            print rownumber
    h.Scale(1.0/h.Integral())
#------------------------------------------------------------------
def readAndFillAndCut(filename, treename, reader, which, cut):
    ntuple = Ntuple(filename, treename)
    inputvars = vector('double')(2)
    
    # loop over ntuple
    i = 0
    
    for rownumber, event in enumerate(ntuple):
        
        inputvars[0] = event.Pt
        inputvars[1] = event.I
        
        # evaluate discriminant
        D = reader.GetMvaValue(inputvars)

        if D > cut:
            i+=1

    return i
#------------------------------------------------------------------
def main():
    print "="*80
    # set up a standard graphics style	
    setStyle()

    xbins = 10
    xmin  =  0.0
    xmax  =  500.0

    ybins = 10
    ymin  =  0.0
    ymax  =  1.0

#    fieldx = 'deltaetajj'; varx = '#Delta#eta_{jj}'
#    fieldy = 'massjj';     vary = 'm_{jj}'
    fieldx = 'Pt';  varx = 'p_T (GeV)'
    fieldy = 'I';  vary = 'I'

    Icut = 0.1
    Ptcut = 80.0

    signame = "Gluino_13TeV_M1000"
    #bkgname = "Data13TeV_Run2015TOY"
    bkgname = "Data13TeV_Run2015TOY_3982evts_Dregion"
    sigtreename    = signame+"TEST"
    bkgtreename = "TOYdata"
    weightname  = "weight"
    sigfilename = '../../../Data/Type0/TEST/Histos_%s_%sTESTING.root' %(signame,signame)
    bkgfilename = '../../../Data/TOY/%s.root' %(bkgname)
    # pick discriminant

    which = 'MLP'

    # read in trained MLP class
    #code = 'weights/Iasptweights/%s_IasvPt_%s.class.C' % (signame,which)
    code = 'weights/Ihpweights/%s_IhvP_%s.class.C' % (signame,which)
    gROOT.ProcessLine(".L %s" % code)

    inputnames = vector('string')(2)
    inputnames[0] = fieldx
    inputnames[1] = fieldy
    reader = eval('Read%s(inputnames)' % which)

     # loop over cuts
#    cuts[20] = {0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.}

#    percent = [[0 for i in range(20)] for j in range(2)]
    ncuts = 100
    sigpercent = np.zeros(ncuts-1)
    bkgpercent = np.zeros(ncuts-1)
    sigcount = 0
    bkgcount = 0
    sigtotal = 0
    bkgtotal = 0
#    ntuplesig = Ntuple(sigfilename, sigtreename)
#    ntuplebkg = Ntuple(bkgfilename, bkgtreename)
    for intuple in range(0,2):
        if intuple == 0:
            ntuplect = Ntuple(sigfilename, sigtreename)
        if intuple == 1:
            ntuplect = Ntuple(bkgfilename, bkgtreename)
        for rownumber, event in enumerate(ntuplect):
            if intuple == 0:
                sigtotal += 1
            if intuple == 1:
                bkgtotal += 1
            if( event.I > Icut and event.Pt > Ptcut ):
                if intuple == 0:
                    sigcount += 1
                if intuple == 1:
                    bkgcount += 1

    print( 'Signal ct = %i, Signal Total = %i, Frac = %f') %(sigcount,sigtotal, 1.0*sigcount/sigtotal)
    print( 'Bkg ct = %i, Bkg Total = %i, Frac = %f') %(bkgcount, bkgtotal, 1.0*bkgcount/bkgtotal)

    for i in range(1,ncuts):
        cut = i*1.0/ncuts
        #ntuple1.append(Ntuple(sigfilename, sigtreename))
        #ntuple2.append(Ntuple(bkgfilename, bkgtreename))
        inputvars = vector('double')(2)

        for j in range(0,2):
            total = 0
            count = 0
            if j == 0:
                ntuple = Ntuple(sigfilename, sigtreename)
            if j == 1:
                ntuple = Ntuple(bkgfilename, bkgtreename)
            for rownumber, event in enumerate(ntuple):
                total+=1
                #inputvars[0] = event.Pt
                #inputvars[1] = event.I
                inputvars[0] = event.P
                inputvars[1] = event.Ih
                # evaluate discriminant
                D = reader.GetMvaValue(inputvars)

                #passes cut
                if D >= cut:
                    count+=1
            #print("%i,%i") %(i,j)
            #print(percent[i-1][j])
            if j == 0:
                sigpercent[i-1]=(1.0*count/total)
            if j == 1:
                bkgpercent[i-1]=(1.0*count/total)
            
            #percent[j][i-1]=(1.0*count/total)        
            #print('Cut = %2.2f, Total = %i, Pass cut = %i, Percent = %f' ) %(cut,total,count, percent[j][i-1])
   
    c1 = TCanvas("%s_%s_ROCcurve"%(signame,which),"ROC curve", 800,800)
    c1.cd()
    
    g1 = ROOT.TGraph(len(sigpercent),bkgpercent,sigpercent)
    g1.SetTitle("ROC curve")
    g1.GetXaxis().SetTitle("Bkg Eff")
    g1.GetXaxis().SetNdivisions(5)
    g1.GetYaxis().SetTitle("Sig Eff")
    g1.SetMarkerStyle(21)
    g1.Draw("AP")
    c1.Update()
    c1.Modified()
    c1.SaveAs(".pdf")
    c1.SaveAs(".png")
    c1.SaveAs(".C")
    
    #if the above works correctly, make a loop over different cuts, and save the passing efficiency to an array and fill a Tgraph with it.
    #need to find the passing efficiency for a signal sample and a background sample. So I'm not sure if I should use the background and signal samples, but should avoid doing it on the same samples it was trained on.
#----------------------------------------------------------------------
main()
