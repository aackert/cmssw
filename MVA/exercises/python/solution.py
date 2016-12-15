#-----------------------------------------------------------------------------
# Solutions to CMSDAS 2015 exercises
# Created: 18-Jan-2015 Harrison B. Prosper
#-----------------------------------------------------------------------------
import os, sys, re
from array import array
from string import split, strip, atoi, atof, replace, joinfields
from math import *
from ROOT import *
#-----------------------------------------------------------------------------
class LadderPlot:
    def __init__(self, xmin, xmax, ymin, ymax,
                 color=kRed,
                 hullcolor=kBlack,
                 hullwidth=3):
        self.cuts = []
        self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax
        self.color=color
        self.hullcolor=hullcolor
        self.hullwidth=hullwidth
        
    def add(self, Z, R2, MR):
        # sort all cut-points in this ladder cut
        # in increasing R2 (y-axis value)
        cutpoints = [None]*len(R2)
        for ii in xrange(len(R2)):
            cutpoints[ii] = (R2[ii], MR[ii])
        cutpoints.sort()

        # find outer hull by picking cut-points such that
        # MR decreases monotonically
        outerhull = [cutpoints[0]]
        for ii in xrange(1, len(cutpoints)):
            y0, x0 = outerhull[-1] # (R2 = y, MR = x)
            y1, x1 = cutpoints[ii]
            if x1 < x0:
                outerhull.append(cutpoints[ii])

        self.cuts.append((Z, outerhull, cutpoints))    

    def plot(self, cutpoint, xmax, ymax, color):
        x = array('d')
        y = array('d')
        yy, xx = cutpoint
        y.append(ymax); x.append(xx)
        y.append(yy);   x.append(xx)
        y.append(yy);   x.append(xmax)
        poly = TPolyLine(len(x), x, y)
        poly.SetLineWidth(1)
        poly.SetLineColor(color)
        return poly
        
    def draw(self):
        cuts = self.cuts
        xmin, xmax, ymin, ymax = self.xmin, self.xmax, self.ymin, self.ymax
        color = self.color
        hullcolor = self.hullcolor
        plot = self.plot
        
        # order ladder cuts in decreasing (Z) significance
        cuts.sort()
        cuts.reverse()

        plots = []
        nladders = 1 # choose best ladder for now
        for ii in range(nladders):
            Z, outerhull, cutpoints = cuts[ii]

            # plot all cut-points of current ladder
            for cutpoint in cutpoints:
                plots.append(plot(cutpoint,
                                  xmax, ymax,
                                  color))
                plots[-1].Draw('l same')

            # plot all outer hull
            for ii, cutpoint in enumerate(outerhull):
                print "\tR2 > %10.3f && MR > %10.1f" % cutpoint
                if ii == 0:
                    ymax, xx = outerhull[ii+1]
                elif ii < len(outerhull)-1:
                    yy, xmax = outerhull[ii-1]                    
                    ymax, xx = outerhull[ii+1]
                else:
                    yy, xmax = outerhull[ii-1]
                    ymax = self.ymax
                    
                plots.append(plot(cutpoint,
                                  xmax, ymax,
                                  self.hullcolor))
                plots[-1].SetLineWidth(self.hullwidth)
                plots[-1].Draw('l same')                
        self.plots = plots
