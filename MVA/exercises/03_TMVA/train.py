#!/usr/bin/env python
#----------------------------------------------------------------------
# File: train.py
# Description: example of classification with TMVA
# Created: 01-June-2013 INFN SOS 2013, Vietri sul Mare, Italy, HBP
#   adapted for CMSDAS 2015 Bari HBP
#----------------------------------------------------------------------
import os, sys, re
from math import *
from string import *
from time import sleep
from array import array
from histutil import *
from ROOT import *
#----------------------------------------------------------------------
def getTree(filename, treename):
    hfile = TFile(filename)
    if not hfile.IsOpen():
        print "** can't open file %s" % filename
        sys.exit()
    tree = hfile.Get(treename)
    if tree == None:
        print "** can't find tree %s" % treename
        sys.exit()
    return (hfile, tree)
#----------------------------------------------------------------------
#----------------------------------------------------------------------
def main():
    print "\n", "="*80
    print "\tclassification with TMVA"
    print "="*80

    sigvsig = False  #True = Two signal files (one 'sig', one 'bkg')   False = Normal one sig and one bkg
    
    IasvPt = False  #True = IasvsPt   False = IhvsP

    Type2 = False #Type2 ntuples?

    signame ="Stop_13TeV_M800"
    sigtreename = "%sTRAIN" %signame

    bkgtreename = "Data"

    # get signal and background data for training/testing
    #sigfilename = '/afs/cern.ch/work/a/aackert/private/CMSSW_7_4_14_oldv2/src/SUSYBSMAnalysis/HSCP/test/AnalysisCode/Results/Type0/Histos_%s_%s.root' %(signame,signame)
    #sigfilename = '/afs/cern.ch/work/a/aackert/private/CMSSW_7_4_14_oldv2/src/TRAIN/Histos_%s_%sTRAIN.root' %(signame,signame)
    #bkgfilename = '../../../Data13TeV_Run2015_256868TOY.root'
    #bkgfilename = 'Data13TeV_Run2015TOY_4047evt_Dregion.root'
    #bkgfilename = '/afs/cern.ch/work/a/aackert/private/CMSSW_7_4_14_oldv2/src/SUSYBSMAnalysis/HSCP/test/AnalysisCode/Results/Type0/Histos_%s_%s.root' %(bkgname,bkgname)
    sigfilename = '../../../Data/Type0/TRAIN/Histos_%s_%sTRAIN.root' %(signame,signame)
    #bkgfilename = '/Users/andrewackert/Desktop/work/HSCP/Data/Data13TeV_Run2015Dregion.root'
    bkgfilename = '../../../Data/Type0TOY/Data13TeV_Run2015DregionTOY_TRAIN_25K.root'
    sigFile, sigTree = getTree(sigfilename, sigtreename)
    bkgFile, bkgTree = getTree(bkgfilename, bkgtreename)
    
    typename = "IasvPt"
    if(IasvPt==False):
        typename = "IhvP"
    if(Type2==True):
        typename = "IasvPtvTOF"
        if(IasvPt==False):
            typename = "IhvPvTOF"
    
    # everything is done via a TMVA factory
    outputFile = TFile("TMVA_%s_%s.root"%(signame,typename), "recreate")
    factory = TMVA.Factory("%s_%s"%(signame,typename), outputFile,
                           "!V:Transformations=I;N;D")
    if(sigvsig==True):
        factory = TMVA.Factory("%s_%s_sigvsig"%(signame,typename),outputFile,
                              "!V:Transformations=I;N;D")
#    sigTree.Scan("eta")
#    print "ok1"
#    bkgTree.Scan("eta")
#    print "ok2"
#    exit(0)

    # define input variables
    if(IasvPt==True):
        factory.AddVariable("Pt", 'F')
        factory.AddVariable("I", 'F')
        factory.AddVariable("eta", 'F')
        if(Type2==True):
            factory.AddVariable("TOF", 'F')
    if(IasvPt==False):
        factory.AddVariable("P", 'F')
        factory.AddVariable("Ih", 'F')
        factory.AddVariable("eta", 'F')
        if(Type2==True):
            factory.AddVariable("TOF", 'F')

    # define from which trees data are to be taken
    factory.AddSignalTree(sigTree)
    factory.AddBackgroundTree(bkgTree)

    # remove problematic events and specify how
    # many events are to be used
    # for training and testing
    if(IasvPt==True):
        factory.PrepareTrainingAndTestTree(TCut("I>0.1"),
                                       "nTrain_Signal=3000:"\
                                       "nTest_Signal=1000:"\
                                       "nTrain_Background=3000:"\
                                       "nTest_Background=1000:"\
                                       "!V" )
    if(IasvPt==False):
        factory.PrepareTrainingAndTestTree(TCut("Ih>0.0"),
                                       "nTrain_Signal=3000:"\
                                       "nTest_Signal=1000:"\
                                       "nTrain_Background=3000:"\
                                       "nTest_Background=1000:"\
                                       "!V" )

    # define multivariate methods to be run
    factory.BookMethod( TMVA.Types.kMLP,
                        "MLP",
                        "!H:!V:"\
                        "VarTransform=N:"\
                        "HiddenLayers=10:"\
                        "TrainingMethod=BFGS")

    #factory.BookMethod( TMVA.Types.kBDT,
    #                    "BDT",
    #                    "!V:"\
    #                    "BoostType=AdaBoost:"\
    #                    "NTrees=500:"\
    #                    "nEventsMin=100:"\
    #                    "nCuts=50")
  
    factory.TrainAllMethods()  
    factory.TestAllMethods()
    factory.EvaluateAllMethods()
    
    outputFile.Close()
#----------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\nciao"
