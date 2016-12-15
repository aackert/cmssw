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
#------------------------------------------------------------------
def readAndFill(filename, treename, h):
    print "==> reading %s" % filename
    # open ntuple (see histutil.py for implementation)
    ntuple = Ntuple(filename, treename)
    # loop over ntuple
    for rownumber, event in enumerate(ntuple):
        h.Fill(event.P, event.Ih, 1.0)
        if rownumber % 2000 == 0:
            print rownumber
            #print(event.P,event.Ih)
    #h.Scale(1.0/h.Integral())
#------------------------------------------------------------------
def readAndFillAgain(filename, treename, reader, which, c, h):
    ntuple = Ntuple(filename, treename)
    inputvars = vector('double')(2)
    
    # loop over ntuple
    for rownumber, event in enumerate(ntuple):
        inputvars[0] = event.P
        inputvars[1] = event.Ih
       
        
        # evaluate discriminant
        D = reader.GetMvaValue(inputvars)
        h.Fill(D, 1.0)

        if rownumber % 1000 == 0:
            c.cd()
            h.Draw("hist")
            c.Update()
    #h.Scale(1.0/h.Integral())
#------------------------------------------------------------------
def main():
    print "="*80
    # set up a standard graphics style	
    setStyle()

    xbins = 10
    xmin  =  0.0
    xmax  =  2000.0

    ybins = 10
    ymin  =  0.0
    #ymax  =  1.0
    ymax = 30.0

    zbins = 42
    zmin = -2.1
    zmax = 2.1

#    fieldx = 'deltaetajj'; varx = '#Delta#eta_{jj}'
#    fieldy = 'massjj';     vary = 'm_{jj}'
#    fieldx = 'Pt';  varx = 'p_T (GeV)'
#    fieldy = 'I';  vary = 'I'
    fieldx = 'P'; varx = 'p (GeV)'
    fieldy = 'Ih'; vary = 'Ih'
    fieldz = 'eta'; varz = 'eta'

    msize= 0.15
    #Data13TeV_Run2015TOY_Gluino_13TeV_M1000_f10_10000_2_events.root

    signame = "Gluino_13TeV_M1000_f10"
    #signame2 = "Data13TeV_Run2015TOY_3963evt_Dregion_Gluino_13TeV_M1600_f10_SigCuts_Ias0100_Pt80"
    signame2 = "Data13TeV_Run2015Dregion"  # this is also where you put the comparison file
    bkgname = "Data13TeV_Run2015TOY_3982evts_Dregion"
    #bkgname = "Data13TeV_Run2015DregionTOY_method1_badeta_TEST" #bkg file name to test/plot (not training file)
    weightfilename = "Gluino_13TeV_M2000_f10"

    switchsig = False  # is the signal file to test different then the signal used to train?
    switchTOY = True  # is it a toy bkg file?
    switchsigvsig = False  # is the training done on signal MC used for both signal and bkg?
    weightswitch = 1 # 1 = Ih vs p , 2 = Ias vs pt
    mergedfile = False  # is the signal file you want to run over a merged file that you created?
    scaleswitch = False # do you want to normalize the plots to unit area?
    combinedswitch = True  #draw sig & bkg == False or draw sig,bkg,&combined file == True
    bkgvbkgswitch = True #do you want to compare TOY bkg with real data file?
    etaswitch = False #do you want to compare eta as well?
    layers = 10 #number of hidden layers
    weightfiledefault = True #true means weightfile same as signal file

    if(weightfiledefault):
        weightfilename = signame

    sigtreename    = signame+"TEST"
    bkgtreename = "Data13TeV/HscpCandidates"
    #weightname  = "weight"
    sigfilename = '../../../Data/Type0/TEST/Histos_%s_%sTESTING.root' %(signame,signame)
    bkgfilename = '../../../Data/Type0Data/Histos_Data13TeV_Run2015.root'
    
    mergedtreename = "MergedHscpCandidates"
    mergedfilename = '../../../Data/%s.root' %signame2
    
    
    #if(switchsig == True):
    #    sigtreename = signame2+"TEST"
    #    sigfilename = '../../../Data/Type0/TEST/Histos_%s_%sTESTING.root' %(signame2,signame2)
         
    if(switchTOY == True):
        bkgtreename = "TOYdata"
        bkgfilename = '../../../Data/TOY/%s.root' %bkgname

    if(bkgvbkgswitch):
        mergedtreename = bkgtreename
        mergedfilename = '../../../Data/Type0Data/%s.root' %signame2
    
    if(switchsigvsig == True):
        bkgtreename = signame2+"/TEST"
        bkgfilename = '../../../Data/Type0/TEST/Histos_%s_%sTESTING.root' %(signame2,signame2)

    if(mergedfile == True):
        sigtreename = mergedtreename
        sigfilename = mergedfilename


    # pick discriminant

    which = 'MLP'

    # read in trained MLP class

    numlayers = '%ilayers' %(layers)

    if( weightswitch == 1):
        code = 'weights/Ihpweights/%s/%s_IhvP_%s.class.C' % (numlayers,signame,which)
        if(switchsig):
            code = 'weights/Ihpweights/%s/%s_IhvP_%s.class.C' % (numlayers,weightfilename,which)
    if( weightswitch == 2):
        code = 'weights/Iasptweights/%s/%s_IasvPt_%s.class.C' % (numlayers,signame,which)
        if(switchsig):
            code = 'weights/Iasptweights/%s/%s_IasvPt_%s.class.C' % (numlayers,weightfilename,which)
#    gROOT.ProcessLine(".L %s" % code)
    if( switchsigvsig ):
        code = "weights/Ihpweights/%s/%s_sigvsig_%s.class.C" % (numlayers,signame,which)

    if(etaswitch):
        if( weightswitch == 1):
            code = 'weights/Ihpetaweights/%s/%s_IhvP_%s.class.C' % (numlayers,signame,which)
            if(switchsig):
                code = 'weights/Ihpetaweights/%s/%s_IhvP_%s.class.C' % (numlayers,weightfilename,which)
        if( weightswitch == 2):
            code = 'weights/Iasptetaweights/%s/%s_IasvPt_%s.class.C' % (numlayers,signame,which)
            if(switchsig):
                code = 'weights/Iasptetaweights/%s/%s_IasvPt_%s.class.C' % (numlayers,weightfilename,which)
#    gROOT.ProcessLine(".L %s" % code)                                                                                                
    if( switchsigvsig ):
        code = "weights/Ihpweights/%s_sigvsig_%s.class.C" % (signame,which)


    gROOT.ProcessLine(".L %s" % code)
    inputnames = vector('string')(2)
    inputnames[0] = fieldx
    inputnames[1] = fieldy


    reader = eval('Read%s(inputnames)' % which)
    
    # ---------------------------------------------------------
    # make 2-D surface plot
    # ---------------------------------------------------------

    c  = TCanvas("fig_%s_%s" %(signame,which), "", 10, 10, 500, 500)
    # divide canvas canvas along x-axis
    c.Divide(2, 2)

    # Fill signal histogram
    hsig = mkhist2('hsig', varx, vary,
                   xbins, xmin, xmax,
                   ybins, ymin, ymax)
    hsig.SetMarkerSize(msize)
    hsig.SetMarkerColor(kCyan+1)        
    readAndFill(sigfilename, sigtreename, hsig)

    # Fill background histogram
    hbkg = mkhist2('hbkg', varx, vary,
                   xbins, xmin, xmax,
                   ybins, ymin, ymax)
    hbkg.SetMarkerSize(msize)
    hbkg.SetMarkerColor(kMagenta+1)        
    readAndFill(bkgfilename, bkgtreename, hbkg)

    # Fill Mixed(merged) file histogram
    hmerged = mkhist2('hmerged', varx, vary,
                      xbins, xmin, xmax,
                      ybins, ymin, ymax)
    hmerged.SetMarkerSize(msize)
    hmerged.SetMarkerColor(kBlack)
    readAndFill(mergedfilename, mergedtreename, hmerged)


    # make some plots

    xpos = 0.30
    ypos = 0.85
    tsize= 0.05

    # --- signal

    c.cd(1)
#    hsig.Scale(1.0/hsig.Integral())
    hsig.SetMinimum(0)
    hsig.Draw('p')
    s1 = Scribe(xpos, ypos, tsize)
#    s1.write('VBF #rightarrow H #rightarrow ZZ #rightarrow 4l')
    s1.write('Signal')
    c.Update()

    # --- background

    c.cd(2)
    hbkg.Draw('p')
    s2 = Scribe(xpos, ypos, tsize)
#    s2.write('ggF #rightarrow H #rightarrow ZZ #rightarrow 4l')
    s2.write('Background')
    c.Update()        

    # --- p(S|x) = p(x|S) / [p(x|S) + p(x|B)]

    hD = hsig.Clone('hD')
    hsum = hsig.Clone('hSum')
    hsum.Add(hbkg)
    hD.Divide(hsum)
    hD.SetMinimum(0)
    hD.SetMaximum(1)

    c.cd(3)
    hD.Draw('cont1')
    s3 = Scribe(xpos, ypos, tsize)
    s3.write('D(%s, %s) (actual)' % (varx, vary))
    c.Update()

    # ---------------------------------------------------------
    h1 = mkhist2("h1", varx, vary,
                 xbins, xmin, xmax,
                 ybins, ymin, ymax)                 
    h1.SetMinimum(0)

    # compute discriminant at a grid of points

    xstep = (xmax-xmin)/xbins
    ystep = (ymax-ymin)/ybins

    inputvars = vector('double')(2)
    
    for i in xrange(xbins):
        # x is a Python variable. Be sure
        # to set its doppelganger within Root
        x = xmin + (i+0.5)*xstep
        inputvars[0] = x
        for j in xrange(ybins):
            y = ymin + (j+0.5)*ystep
            inputvars[1] = y
            D = reader.GetMvaValue(inputvars)
            h1.Fill(x, y, D)

    # plot MVA approximation to discriminant
    c.cd(4)
    h1.Draw('cont1')
    s4 = Scribe(xpos, ypos, tsize)
    s4.write('D(%s, %s) (%s)' % (varx, vary, which))
    c.Update()

    c.SaveAs(".pdf")
    c.SaveAs(".png")
    # ---------------------------------------------------------
    # plot distributions of D
    # ---------------------------------------------------------

    print "Making Plots"

    c1  = TCanvas("fig_%s_D_%s" %(signame,which), "fig_%s_D_%s",
                  510, 310, 500, 500)

    xm = 0
    if which == "BDT": xm = -1.0
    
    ndivisions = 25
        
    hs = mkhist1("hs", "D(%s, %s)" % (varx, vary), "Entries", ndivisions, xm, 1)
    hs.SetFillColor(kCyan+1)
    hs.SetFillStyle(3001)
    readAndFillAgain(sigfilename, sigtreename, reader, which, c1, hs)

    sleep(2)

    hb = mkhist1("hb", "D(%s, %s)" % (varx, vary), "Entries", ndivisions, xm, 1)
    hb.SetFillColor(kMagenta+1)
    hb.SetFillStyle(3001)
    readAndFillAgain(bkgfilename, bkgtreename, reader, which, c1, hb)

    sleep(2)
    
    hm = mkhist1("hm", "D(%s, %s)" % (varx, vary), "Entries", ndivisions, xm, 1)
    #hm.SetFillColor(kBlack)
    hm.SetLineColor(kBlack)
    hm.SetLineWidth(3)
    #hm.SetFillStyle(3001)
    readAndFillAgain(mergedfilename, mergedtreename, reader, which, c1, hm)

    #hszoom

    #hbzoom

    #hmzoom
    
    hsname = "Signal"
    hbname = "Background"
    hmname = "Sig+Bkg mix"
    if(bkgvbkgswitch):
        hmname = "Data sample"


    l1 = TLegend(0.4,0.75,0.6,0.9)
    l1.AddEntry(hs,hsname,"lf")
    l1.AddEntry(hb,hbname,"lf")
    l1.AddEntry(hm,hmname,"lf")

    c1.cd()
    if(scaleswitch):
        hs.Scale(1.0/hs.Integral())
        hb.Scale(1.0/hb.Integral())
    if(bkgvbkgswitch and scaleswitch==False):
        #hm.Scale(1.0/hm.Integral())
        hs.Scale(1.0*hm.Integral()/hs.Integral())
        hb.Scale(1.0*hm.Integral()/hb.Integral())
    if(bkgvbkgswitch and scaleswitch):
        hm.Scale(1.0/hm.Integral()) 
    if(combinedswitch == False):
        hs.Draw('hist')
        hb.Draw('hist same')
    if(combinedswitch):
        hs.Draw('hist')
        hb.Draw('hist same')
        hm.Draw('hist same')
    l1.Draw()
    c1.Update()
    c1.Modified()
    c1.SaveAs(".png")
    c1.SaveAs(".pdf")


    c2  = TCanvas("fig_%s_D_%s_log" %(signame,which), "fig_%s_D_%s_log",
                  510, 310, 500, 500)
    c2.cd()
    c2.SetLogy()
    #hs.Scale(1.0/hs.Integral())
    #hb.Scale(1.0/hb.Integral())
    if(scaleswitch):
        hm.SetMinimum(0.001)
        hb.SetMinimum(0.001)
        hs.SetMinimum(0.001)
    if(scaleswitch == False):
        hm.SetMinimum(0.05)
        hb.SetMinimum(0.05)
        hs.SetMinimum(0.05)
    hm.Sumw2()
    hb.Sumw2()
    hs.Sumw2()
    if(combinedswitch == False):
        hs.Draw('hist')
        hb.Draw('hist same')
    if(combinedswitch == True):
        hs.Draw('hist')
        hb.Draw('hist same')
        hm.Draw('hist same')
    l1.Draw()
    c2.Update()
    c2.Modified()
    c2.SaveAs(".png")
    c2.SaveAs(".pdf")

    if(combinedswitch == True):
        print "Making combined plots"
        c3  = TCanvas("fig_%s_D_%s_Log_Ratio" %(signame,which), "fig_%s_D_%s_Log_Ratio", 800,800)
        c3.cd()
        pad1 = TPad("pad1","pad1",0,0.35,1,1.0) #upper pad
        pad1.SetBottomMargin(0.01)
        pad1.Draw()
        pad1.cd()
        pad1.SetLogy()
        l1.Draw()
        hs.SetStats(0)
        hs.GetXaxis().SetLabelSize(0.)
        hs.Draw('hist')
        hb.Draw('hist same')
        hm.Draw('hist same')
        axis = TGaxis(-5, 20, -5, 220, 20,220,510,"")
        axis.SetLabelFont(43)
        axis.SetLabelSize(15)
        axis.Draw()

        c3.cd()
        pad2 = TPad("pad2","pad2",0,0.05,1.0,0.30)
        pad2.SetTopMargin(0.01)
        pad2.SetBottomMargin(0.2)
        pad2.Draw()
        pad2.cd()
        pad2.SetGridy()
        #hratio = TH1( "hratio", "D(%s, %s)" % (varx, vary), "", 50, xm, 1)
        hratio = hm.Clone("hratio")
        hratio.SetLineColor(kBlack)
        hratio.SetMinimum(-0.2)
        hratio.SetMaximum(2.5)
        hratio.Sumw2()
        hratio.SetStats(0)
        hratio.Divide(hb)
        hratio.Sumw2()
        hratio.SetMarkerStyle(21)
        hratio.GetYaxis().SetTitle("ratio mix/bkg")
        hratio.GetYaxis().SetNdivisions(505)
        hratio.GetYaxis().SetTitleSize(20)
        hratio.GetYaxis().SetTitleFont(43)
        hratio.GetYaxis().SetTitleOffset(1.55)
        hratio.GetYaxis().SetLabelFont(43)
        hratio.GetYaxis().SetLabelSize(15)
        hratio.GetYaxis().SetAxisColor(kBlack)
        hratio.GetXaxis().SetTitleSize(20)
        hratio.GetXaxis().SetTitleFont(43)
        hratio.GetXaxis().SetTitleOffset(4.)
        hratio.GetXaxis().SetLabelFont(43)
        hratio.GetXaxis().SetLabelSize(15)
        hratio.Draw()
        pad2.RedrawAxis()
        c3.Update()
        c3.Modified()
        c3.SaveAs(".png")
        c3.SaveAs(".pdf")

        c4 = TCanvas("fig_%s_D_%s_Diff" %(signame,which), "fig_%s_D_%s_Diff", 800,800)
        hdiff = hm.Clone("hdiff")
        hdiff.Add(hb,-1)
        hdiff.Sumw2()
        hdiff.SetMarkerStyle(21)
        hdiff.Draw()
        c4.Update()
        c4.Modified()
        c4.SaveAs(".png")
        c4.SaveAs(".pdf")

        c4b = TCanvas("fig_%s_D_%s_Ratio" %(signame,which), "fig_%s_D_%s_Ratio", 800,800)
        hratio2 = hm.Clone("hratio2")
        hratio2.Sumw2()
        hratio2.Divide(hb)
        hratio2.SetMarkerColor(kBlack)
        hratio2.SetMarkerStyle(21)
        hratio2.Draw()
        c4b.Update()
        c4b.Modified()
        c4b.SaveAs(".png")
        c4b.SaveAs(".pdf")
        

        c5  = TCanvas("fig_%s_D_%s_Log_Ratio_zoom" %(signame,which), "fig_%s_D_%s_Log_Ratio_zoom", 800,800)
        c5.cd()
        pad1 = TPad("pad1","pad1",0,0.35,1,1.0) #upper pad
        pad1.SetBottomMargin(0.01)
        pad1.Draw()
        pad1.cd()
        pad1.SetLogy()

        hs.SetStats(0)
        hs.GetXaxis().SetLabelSize(0.)
        hs.GetXaxis().SetRangeUser(0.5,1.0)
        hs.Draw('hist')
        hb.Draw('hist same')
        hm.Draw('hist same')
        axis = TGaxis(-5, 20, -5, 220, 20,220,510,"")
        axis.SetLabelFont(43)
        axis.SetLabelSize(15)
        axis.Draw()

        c5.cd()
        pad2 = TPad("pad2","pad2",0,0.05,1.0,0.30)
        pad2.SetTopMargin(0.01)
        pad2.SetBottomMargin(0.2)
        pad2.Draw()
        pad2.cd()
        pad2.SetGridy()
        #hratio = TH1( "hratio", "D(%s, %s)" % (varx, vary), "", 50, xm, 1)
        hratio.GetXaxis().SetRangeUser(0.5,1.0)
        hratio.SetMinimum(-0.2)
        hratio.SetMaximum(5)
        hratio.Draw()
        pad2.RedrawAxis()
        c5.Update()
        c5.Modified()
        c5.SaveAs(".png")
        c5.SaveAs(".pdf")

        c6 = TCanvas("fig_%s_D_%s_Diff_zoom" %(signame,which), "fig_%s_D_%s_Diff_zoom", 800,800)
        hdiff.GetXaxis().SetRangeUser(0.5,1.0)
        hdiff.Draw()
        c6.Update()
        c6.Modified()
        c6.SaveAs(".png")
        c6.SaveAs(".pdf")


    #sleep(10)
#----------------------------------------------------------------------
main()
