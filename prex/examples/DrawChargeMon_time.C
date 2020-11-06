#include <TPaveStats.h>
void DrawChargeMon_time()
{

  gStyle->SetOptStat(0);

  ifstream ifstr("out_time.txt");
  string date, time;
  double charge0, charge1, epoch_start, epoch;

  Int_t nEmpties = 0;
  Double_t lastEntry = 0.0;

  //Int_t nSecs = 86400;
  Int_t nSecs = 86400/3;
  Int_t nSecsExp = 1.184e7;
  Int_t offset = 176;

  Double_t first_epoch = 0.0;
  Double_t last_epoch = 0.0;
  Double_t final_epoch = 366; // or do = last_epoch+1; 
  Double_t total_epoch = final_epoch+15; // or do = last_epoch+1+15; 
  // 366 = number of shifts from Dec 4 - April 4 -> Add 15 for buffer space
  // 330 = number of shifts from Dec 4 - March 23
  // 105 = number of shifts from Dec 4 - January 8
  // 39 = number of shifts from Dec 4 - Dec 17
  Double_t current_epoch = last_epoch;
  Int_t n_weeks = 3;
  Int_t goal = 467;
  Double_t fit_length = n_weeks*7*3;
  Double_t current_week_start = current_epoch - fit_length;

  double sum0 = 0 ;
  double sum1 = 0 ;
  int n=0;

  Int_t tmpBin1 = 0;
  Int_t tmpBin2 = 0;

  TH1F* hsum = new TH1F("hsum", "Charge total vs shift", total_epoch, 0, total_epoch);
  TH1F* hsum1 = new TH1F("hsum1", "Good charge total vs shift", total_epoch, 0, total_epoch);
  TH1F* hsum2 = new TH1F("hsum2", "No data vs shift", total_epoch, 0, total_epoch);
  /*TH1F* hsum = new TH1F("hsum", "Charge total vs shift", Int_t(2.0*31536000.0/nSecs), -31536000/nSecs + offset, 31536000/nSecs + offset);
  TH1F* hsum1 = new TH1F("hsum1", "Good charge total vs shift", Int_t(2.0*31536000.0/nSecs) + offset, -31536000/nSecs, 31536000/nSecs + offset);
  TH1F* hsum2 = new TH1F("hsum2", "No data vs shift", Int_t(2.0*31536000.0/nSecs) + offset, -31536000/nSecs, 31536000/nSecs + offset);
  */

  Int_t run = 0;
  while( ifstr >> run >> date >> time >> epoch_start >> epoch >> charge0 >> charge1 )
    {
      
      epoch = (-1*1580599413.0 + epoch)/nSecs + offset;
      if(n<1) 
      {
        first_epoch = epoch;
        Printf("%f",first_epoch);
      }
	  
      if(charge1 > charge0)
      {
      	cout << "run " << run << " has total charge<good charge: " << charge0 << " " << charge1 << endl;
      }

      charge0 = charge0 * 1.e-6;
      charge1 = charge1 * 1.e-6;

      sum0 = sum0 + charge0;
      sum1 = sum1 + charge1;

      tmpBin1 = hsum->Fill(epoch, sum0);
      tmpBin2 = hsum1->Fill(epoch, sum1);
      //Printf("Bin #%f, Shifts # = %f",tmpBin1,epoch);
      hsum->SetBinContent(hsum->GetBin(tmpBin1),sum0);
      hsum1->SetBinContent(hsum1->GetBin(tmpBin2),sum1);

      last_epoch = epoch;
      current_epoch = epoch;
      current_week_start = current_epoch - fit_length;
      n++;
    }
  for (Int_t j = 0 ; j < hsum->GetNbinsX() ; j++) {
    if (hsum->GetBinContent(j) != 0) {
      lastEntry = hsum->GetBinContent(j);
    }
    else {
      if (first_epoch < hsum->GetBinCenter(hsum->GetBin(j)) && current_epoch > hsum->GetBinCenter(hsum->GetBin(j))) {
        hsum->Fill(hsum->GetBinCenter(hsum->GetBin(j)),lastEntry);
        nEmpties++;
      }
    }
  }
  for (Int_t j = 0 ; j < hsum2->GetNbinsX() ; j++) {
    if (hsum1->GetBinContent(j) != 0) {
      lastEntry = hsum1->GetBinContent(j);
    }
    else {
      if (first_epoch < hsum1->GetBinCenter(hsum1->GetBin(j)) && current_epoch > hsum1->GetBinCenter(hsum1->GetBin(j))) {
        hsum2->Fill(hsum1->GetBinCenter(hsum1->GetBin(j)),lastEntry);
        nEmpties++;
      }
    }
  }

  TCanvas *c2 = new TCanvas("c2","c2", 1000, 600);
  hsum->SetFillStyle(3001);
  hsum->SetFillColor(kBlue);

  hsum1->SetFillStyle(3001);
  hsum1->SetFillColor(kRed);

  hsum2->SetFillStyle(3001);
  hsum2->SetFillColor(kYellow);

  hsum->GetXaxis()->SetRangeUser(0*first_epoch, total_epoch);
  hsum1->GetXaxis()->SetRangeUser(0*first_epoch, total_epoch);
  hsum2->GetXaxis()->SetRangeUser(0*first_epoch, total_epoch);

  hsum->GetXaxis()->SetTitle("Shifts");
  hsum->GetYaxis()->SetTitle("Accumulated charge (C)");

  hsum->Draw();
  hsum1->Draw("same");
  hsum2->Draw("same");

  hsum1->Fit("pol1","QR","",current_week_start,current_epoch);
  TF1* line = (TF1*)hsum1->GetListOfFunctions()->FindObject("pol1");
  line->SetLineColorAlpha(8,0.0);
  line->SetLineWidth(5);
  //TArrow* lineCurrent = new TArrow(current_epoch-n_weeks*7*3,sum1-(n_weeks*7*3+1)*line->GetParameter(1),current_epoch+14,14*line->GetParameter(1)+sum1,0.025,"|>");
  TArrow* lineCurrent = new TArrow(current_week_start,sum1-(n_weeks*7*3+3)*line->GetParameter(1),current_epoch+17,14*line->GetParameter(1)+sum1,0.025,"|>");
  //TArrow* lineCurrent = new TArrow(((TLine*)line)->GetX1(),((TLine*)line)->GetY1(),((TLine*)line)->GetX2(),((TLine*)line)->GetY2(),0.025,"|>");
  lineCurrent->SetLineColorAlpha(8,0.75);
  lineCurrent->SetFillColorAlpha(8,0.25);
  lineCurrent->SetLineWidth(5);
  lineCurrent->SetLineStyle(1);
  lineCurrent->SetAngle(30);
  //lineCurrent->Draw();

  Double_t needed_slope = (goal-sum1)/(final_epoch-current_epoch);

//  TLine* lineFuture = new TLine(current_epoch,sum1,current_epoch+14,needed_slope*14+sum1);
  TArrow* lineFuture = new TArrow(current_epoch,sum1,current_epoch+9,needed_slope*9+sum1,0.04125,"|>");
  lineFuture->SetLineColorAlpha(kRed,1);
  lineFuture->SetFillColorAlpha(kRed,0.3);
  lineFuture->SetLineWidth(4);
  lineFuture->SetLineStyle(7);
  lineFuture->SetAngle(30);
  //lineFuture->Draw();

  gPad->SetGridx(1);
  gPad->SetGridy(1);

  //TLegend *leg = new TLegend(0.425, 0.125, 0.9, 0.375);
  TLegend *leg = new TLegend(0.1, 0.7, 0.55, 0.925);
  leg->AddEntry(hsum, Form("All Charge on Target %.2f C", sum0), "lf");
  //leg->AddEntry(hsum1, Form("Good charge after cuts %.2f C, Goal = %d C", sum1,goal), "lf");
  leg->AddEntry(hsum1, Form("Good charge after cuts %.2f C", sum1), "lf");
  leg->AddEntry(hsum2, Form("Shifts with no data"));
  //leg->AddEntry(lineCurrent, Form("Last %d weeks, %.2f C/shift, %.2f C projected", n_weeks, line->GetParameter(1), (final_epoch-current_epoch)*(line->GetParameter(1))+sum1), "lf");
  //leg->AddEntry(lineFuture, Form("Future rate of %.2f C/shift needed to hit goal",needed_slope));
  leg->Draw("same");

  c2->Print("charge_mon_time.pdf");

}
