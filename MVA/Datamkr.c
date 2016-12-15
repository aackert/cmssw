#include <stdio.h>
#include <cmath>
#include <iostream>
#include <vector>
#include <algorithm>
#include <cstdlib>

#include "TFile.h"
#include "TTree.h"
#include "TH1.h"
#include "TRandom.h"

using namespace std;

void Datamkr(){
    
    ///// user assigned variables ///////
    
  string input ="Data13TeV_Run2015_256868";
    float CutIas = 0.300;
    float CutPt = 65.0;
    int maxdata = 3700;
    string output = input;

    bool BCregionswitch = false;
    /////// variables ////////////////
    float pt;
    float Ias;
    vector<float> ptlist;
    vector<float> Iaslist;
    float newpt;
    float newIas;
    
    /////////////////File variables//////////////////
    //    string inputfile = "SUSYBSMAnalysis/HSCP/test/AnalysisCode/Results/Type0/Histos_"+input+".root";
    string inputfile = "../Data/Type0/Histos_"+input+".root";
    TFile *f = new TFile(inputfile.c_str());
    
    string outputfile = output+"TOY.root";
    TFile *fout = new TFile(outputfile.c_str(),"RECREATE");
    fout->cd();
    TTree *tout = new TTree("TOYdata", "random toy data");
    tout->Branch("Pt",&newpt,"Pt/F");
    tout->Branch("I",&newIas,"I/F");
    
    
    //////////////////////////////////
    
    f->cd();
    string treename = "Data13TeV/HscpCandidates";
    TTree *t1 = (TTree*)f->Get(treename.c_str());
    //    t1->cd();
    cout << "Setting branches" << endl;
    
    t1->SetBranchAddress("I",&Ias);
    t1->SetBranchAddress("Pt",&pt);
    /// loop over the entries, add them all to the vector
    /// then select random Ias, and then select a random pt
    /// making sure the random values are above the cuts.
    int nentries = t1->GetEntries();
    for( int ihscp = 0; ihscp < nentries; ihscp++){
        t1->GetEntry(ihscp);
	if( Ias < CutIas ){
	  ptlist.push_back(pt);
	  Iaslist.push_back(Ias);
	}
    }
    
    /// loop this a number of times (maybe half of nentries)
    cout << "making new psuedo data"<<endl;
    srand (time(NULL));

    for( int i = 0; i < maxdata;){
      cout << i << endl;
      //  TRandom *rand1 = new TRandom;
      //  TRandom *rand2 = new TRandom;
      //  TRandom *seed1 = new TRandom;
      //  TRandom *seed2 = new TRandom;
      // srand (time(NULL));
     
        int randnom1;
        int randnom2;
        bool cond1 = false;
        bool cond2 = false;
        bool cond3 = false;
        int ct = 0;
        do{
	  //seed1->SetSeed(0);
	  //seed2->SetSeed(0);
	  //rand1->SetSeed(seed1);
	  //rand2->SetSeed(seed2);
	  // randnom1 = rand1->Integer(nentries);
	  // randnom2 = rand2->Integer(nentries);
	  randnom1 = rand()%ptlist.size();
	  randnom2 = rand()%Iaslist.size();
	  if(BCregionswitch){
            if( ptlist[randnom1] < CutPt){ cond1 = true; cond3 = true;}
            if( Iaslist[randnom2] < CutIas){ cond2 = true; cond3 = true;}
            if( cond1==true && cond2==true){ cond3 = false;}
	  }
            ct++;
        }
        while( (cond3 == false) && (randnom1 != randnom2) );
        //if(ct > 100){cout << "do-while loop line 69 is continuing too long" << endl;exit(0);}
	if( newpt > CutPt && newIas > CutIas){
	  cout << i << " " << randnom1 <<" " << newpt << " " << randnom2 << " " << newIas << endl;
	}
        newpt = ptlist[randnom1];
        newIas = Iaslist[randnom2];
        
        // write out the above new variables to the new data file.
	if( cond3 == true){
	  fout->cd();
	  tout->Fill();
	  i++;
	}
    }
    tout->Write();
}
