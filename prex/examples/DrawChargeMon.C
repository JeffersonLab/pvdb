void DrawChargeMon()
{

  gStyle->SetOptStat(0);

  ifstream ifstr("out.txt");
  int run;
  string date, time;
  double charge0, charge1;

  TH1F* hsum = new TH1F("hsum", "Charge total vs run", 6600, 3000+0.5,9550+0.5);
  TH1F* hsum1 = new TH1F("hsum1", "Good charge total vs run", 6600, 3000+0.5, 9550+0.5);

  // for debugging/sanity check
  auto tg = new TGraph();
  auto tg1 = new TGraph();
  auto tg_diff = new TGraph();

  double sum0 = 0 ;
  double sum1 = 0 ;
  int n=0;

  int first_run;
  int last_run;
  double lastEntry0 = 0.0;
  double lastEntry1 = 0.0;
  while( ifstr >> run >> date >> time >> charge0 >> charge1 )
  {

    if(n<1)
      first_run = run;

    if(charge1 > charge0)
      cout << "run " << run << " has total charge<good charge: " << charge0 << " " << charge1 << endl;

    charge0 = charge0 * 1.e-6;
    charge1 = charge1 * 1.e-6;

    sum0 = sum0 + charge0;
    sum1 = sum1 + charge1;

    hsum->Fill(run, sum0);
    hsum1->Fill(run, sum1);

    tg->SetPoint(n, run, charge0);
    tg1->SetPoint(n, run, charge1);

    tg_diff->SetPoint(n, run, sum0 - sum1);

    last_run = run;      
    n++;
  }

  for (Int_t j = 0 ; j < hsum->GetNbinsX() ; j++) {
    if (hsum->GetBinContent(j) != 0) {
      lastEntry0 = hsum->GetBinContent(j);
    }   
    else {
      hsum->Fill(hsum->GetBinCenter(hsum->GetBin(j)),lastEntry0);
    }
  }
  for (Int_t j = 0 ; j < hsum1->GetNbinsX() ; j++) {
    if (hsum1->GetBinContent(j) != 0) {
      lastEntry1 = hsum1->GetBinContent(j);
    }   
    else {
      hsum1->Fill(hsum1->GetBinCenter(hsum1->GetBin(j)),lastEntry1);
    }
  }

  /*
  TCanvas* c1 = new TCanvas("c1", "c1");
  c1->cd(1);
  tg->SetMarkerStyle(3);
  tg1->SetMarkerStyle(23);
  tg->Draw("ap");
  tg1->Draw("p");
  c1->cd();
  tg_diff->Draw("apl");
  */

  TCanvas *c2 = new TCanvas("c2","c2", 1000, 600);
  hsum->SetFillStyle(3001);
  hsum->SetFillColor(kBlue);

  hsum1->SetFillStyle(3001);
  hsum1->SetFillColor(kRed);

  hsum->GetXaxis()->SetRangeUser(first_run, last_run+1);
  hsum1->GetXaxis()->SetRangeUser(first_run, last_run+1);

  hsum->GetXaxis()->SetTitle("Run Number");
  hsum->GetYaxis()->SetTitle("Accumulated charge (C)");

  hsum->Draw();
  hsum1->Draw("same");
  gPad->SetGridx(1);
  gPad->SetGridy(1);

  TLegend *leg = new TLegend(0.2, 0.65, 0.65, 0.8);
  leg->AddEntry(hsum, Form("Charge all %.2f C (last run count: %d)", sum0, last_run), "lf");
  leg->AddEntry(hsum1, Form("Good charge %.2f C (last run count: %d)", sum1, last_run), "lf");
  leg->Draw("same");

  c2->Print("charge_mon.pdf");
  c2->SaveAs("charge.png");
}
