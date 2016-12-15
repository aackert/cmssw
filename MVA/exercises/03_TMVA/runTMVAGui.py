#!/usr/bin/env python
import sys
from ROOT import *
argv = sys.argv[1:]
if len(argv) > 0:
    rootfile = argv[0]
else:
    rootfile = "TMVA.root"
TROOT.SetMacroPath("$HOME/CMSDAS15/tmva/test")
gROOT.LoadMacro("$HOME/CMSDAS15/tmva/test/TMVAGui.C")
print "\n==> reading Root file", rootfile
TMVAGui(rootfile)
gApplication.Run()



