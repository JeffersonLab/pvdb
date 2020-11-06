void DrawChargeMon_TGraph() { 
  //style block
  gStyle->SetOptStat(0);
  gStyle->SetNdivisions(505,"x");
  gStyle->SetNdivisions(505,"y");
  gStyle->SetLabelSize(0.05,"xy");
  gStyle->SetTitleSize(0.06,"xy");
  gStyle->SetTitleOffset(1.0,"x");
  gStyle->SetTitleOffset(1.0,"y");
  gStyle->SetPadTopMargin(0.1);
  gStyle->SetPadRightMargin(0.06);
  gStyle->SetPadBottomMargin(0.14);
  gStyle->SetPadLeftMargin(0.14);
  gStyle->SetMarkerStyle(20);
  gStyle->SetMarkerSize(0.1);
  gStyle->SetStatX(0.92);
  gStyle->SetStatY(0.89);
  gStyle->SetStatH(0.25);
  gStyle->SetStatW(0.25);
  gStyle->SetStatBorderSize(0);

  // use th1 as frame for tgraph
  TH1F *h = new TH1F("hframe","Charge Tracking;;Accumulated Charge (C)",50, 0, 2*1.35e7); 
  TDatime da(2019,12,04,12,00,00); //is the first day of crex; 
  h->GetXaxis()->SetTimeDisplay(1);
  h->GetXaxis()->SetTimeFormat("%b %d");
  h->GetXaxis()->SetTimeOffset(da.Convert());

  TGraph *gh_raw = new TGraph(); 
  TGraph *gh_cut = new TGraph(); 

  string runnumber, date, time;
  double tot_raw=0, tot_cut=0;
  double timestamp_start, timestamp, raw, good; 
  TTimeStamp timestamp0(2019,12,04,12,00,00,0,0,0); 
  int start = timestamp0.GetSec(); 
  //TTimeStamp timestamp1(2020,04,20,12,00,00,0,0,0); 
  // Summer break -> Sept 21
  TTimeStamp timestamp1(2020,09,21,12,00,00,0,0,0); 
  int end = timestamp1.GetSec(); 

  TTimeStamp timestampSummerStart(2020,03,26,03,00,00,0,0,0); 
  int Sstart = timestampSummerStart.GetSec(); 
  TTimeStamp timestampSummerEnd(2020,08,05,12,00,00,0,0,0); 
  int Send = timestampSummerEnd.GetSec(); 

  // read in the charge file 
  ifstream infile("out_time.txt"); 
  while(infile>>runnumber>>date>>time>>timestamp_start>>timestamp>>raw>>good){
  // COVID Summer
  //  if (timestamp > Sstart) {
  //    timestamp_start = timestamp_start - (Send-Sstart);
  //    timestamp = timestamp - (Send-Sstart);
  //  }

    tot_raw+=raw; 
    tot_cut+=good; 
    gh_raw->SetPoint(gh_raw->GetN(), timestamp - start, tot_raw/1e6); 
    gh_cut->SetPoint(gh_raw->GetN(), timestamp - start, tot_cut/1e6); 
  } 

  TCanvas *cc = new TCanvas("cc","cc",650,500); 
  h->Draw(); 
  h->GetYaxis()->SetRangeUser(0,500); 
  //gh_raw->SetMarkerStyle(7); 
  //gh_cut->SetMarkerStyle(7); 
  gh_raw->SetMarkerColor(kBlue); 
  gh_cut->SetMarkerColor(kRed); 
  gh_raw->SetLineWidth(2); 
  gh_cut->SetLineWidth(2); 
  gh_raw->SetLineColor(kBlue); 
  gh_cut->SetLineColor(kRed); 
  gh_raw->Draw("lp"); 
  gh_cut->Draw("lp");

  // goal is drawn as star
  TGraph *goal = new TGraph();
  //goal->SetPoint(0, end-start, 460); // is 460C precise?
  goal->SetPoint(0, end-start, 467);
  goal->SetMarkerStyle(29); 
  goal->SetMarkerSize(2);
  goal->SetMarkerColor(kRed); 
  goal->Draw("p"); 

  // goal is drawn as line
  //TLine *ln = new TLine(0, 0.,end-start, 460.); 
  //ln->SetLineWidth(2);
  //ln->SetLineColor(kGreen); 
  //ln->Draw("same"); 

  TLegend *lg = new TLegend(0.20, 0.7, 0.45, 0.89); 
  lg->SetFillColor(0);
  lg->SetBorderSize(0); 
  lg->AddEntry(goal, "Goal","p"); 
  lg->AddEntry(gh_raw,"Raw","l"); 
  lg->AddEntry(gh_cut,"Good","l"); 
  lg->Draw();

  cc->SaveAs("charge_mon_tgraph.pdf");

}
