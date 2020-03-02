#include <TPaveStats.h>
void DrawChargeMon_time_noint()
{

  gStyle->SetOptStat(0);

  ifstream ifstr("out_time.txt");
  string date, time;
  double charge0, charge1, epoch;

  Int_t nEmpties = 0;
  Double_t lastEntry = 0.0;

  //Int_t nSecs = 86400;
  Int_t nSecs = 86400/3;
  Int_t nSecsExp = 1.184e7;
  Int_t offset = 176;

  Double_t first_epoch = 0.0;
  Double_t last_epoch = 0.0;
  Double_t final_epoch = 330; // or do = last_epoch+1; 
  Double_t total_epoch = final_epoch; // or do = last_epoch+1+15; 
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

  // TH1F* hTotalCharge = new TH1F("hTotalCharge", "Charge total vs shift;Days;Accumulated charge (C/Shift)", total_epoch, 0, total_epoch/3);
  // TH1F* hGoodCharge = new TH1F("hGoodCharge", "Good charge total vs shift;Days;Accumulated charge (C/Shift)", total_epoch, 0, total_epoch/3);
  // TH1F* hNoDataShift = new TH1F("hNoDataShift", "No data vs shift;Days;Accumulated charge (C/Shift)", total_epoch, 0, total_epoch/3);
  TH1F* hTotalCharge = new TH1F("hTotalCharge", "Charge total vs shift", total_epoch, 0, total_epoch);
  TH1F* hGoodCharge = new TH1F("hGoodCharge", "Good charge total vs shift", total_epoch, 0, total_epoch);
  TH1F* hNoDataShift = new TH1F("hNoDataShift", "No data vs shift", total_epoch, 0, total_epoch);
  /*TH1F* hTotalCharge = new TH1F("hTotalCharge", "Charge total vs shift", Int_t(2.0*31536000.0/nSecs), -31536000/nSecs + offset, 31536000/nSecs + offset);
    TH1F* hGoodCharge = new TH1F("hGoodCharge", "Good charge total vs shift", Int_t(2.0*31536000.0/nSecs) + offset, -31536000/nSecs, 31536000/nSecs + offset);
    TH1F* hNoDataShift = new TH1F("hNoDataShift", "No data vs shift", Int_t(2.0*31536000.0/nSecs) + offset, -31536000/nSecs, 31536000/nSecs + offset);
  */

  Int_t run = 0;
  while( ifstr >> run >> date >> time >> epoch >> charge0 >> charge1 )
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

      //tmpBin1 = hTotalCharge->Fill(epoch, sum0);
      //tmpBin2 = hGoodCharge->Fill(epoch, sum1);
      tmpBin1 = hTotalCharge->Fill(epoch, charge0);
      tmpBin2 = hGoodCharge->Fill(epoch, charge1);
      //Printf("Bin #%f, Shifts # = %f",tmpBin1,epoch);
      //hTotalCharge->SetBinContent(hTotalCharge->GetBin(tmpBin1),charge0);
      //hGoodCharge->SetBinContent(hGoodCharge->GetBin(tmpBin2),charge1);

      last_epoch = epoch;
      current_epoch = epoch;
      current_week_start = current_epoch - fit_length;
      n++;
    }
  // for (Int_t j = 0 ; j < hTotalCharge->GetNbinsX() ; j++) {
  //   if (hTotalCharge->GetBinContent(j) != 0) {
  //     lastEntry = hTotalCharge->GetBinContent(j);
  //   }
  //   else {
  //     if (first_epoch < hTotalCharge->GetBinCenter(hTotalCharge->GetBin(j)) && current_epoch > hTotalCharge->GetBinCenter(hTotalCharge->GetBin(j))) {
  //       hTotalCharge->Fill(hTotalCharge->GetBinCenter(hTotalCharge->GetBin(j)),lastEntry);
  //       nEmpties++;
  //     }
  //   }
  // }
  for (Int_t j = 0 ; j < hNoDataShift->GetNbinsX() ; j++) {
    if (hGoodCharge->GetBinContent(j) != 0) {
      lastEntry = hGoodCharge->GetBinContent(j);
    }
    else {
      if (first_epoch < hGoodCharge->GetBinCenter(hGoodCharge->GetBin(j)) && current_epoch > hGoodCharge->GetBinCenter(hGoodCharge->GetBin(j))) {
        hNoDataShift->Fill(hGoodCharge->GetBinCenter(hGoodCharge->GetBin(j)),0.1);
        nEmpties++;
      }
    }
  }

  TCanvas *cDrawChargeMon = new TCanvas("cDrawChargeMon","cDrawChargeMon", 1000, 600);
  hTotalCharge->SetFillStyle(3001);
  hTotalCharge->SetFillColor(kBlue);

  hGoodCharge->SetFillStyle(3001);
  hGoodCharge->SetFillColor(kRed);

  hNoDataShift->SetFillStyle(3001);
  hNoDataShift->SetFillColor(kYellow);

  hTotalCharge->GetXaxis()->SetRangeUser(0*first_epoch, total_epoch);
  hGoodCharge->GetXaxis()->SetRangeUser(0*first_epoch, total_epoch);
  hNoDataShift->GetXaxis()->SetRangeUser(0*first_epoch, total_epoch);

  // hTotalCharge->GetXaxis()->SetTitle("Shifts");
  // hTotalCharge->GetYaxis()->SetTitle("Accumulated charge (C)");

  hTotalCharge->Draw();
  hGoodCharge->Draw("same");
  hNoDataShift->Draw("same");

  //hGoodCharge->Fit("pol1","QR","",current_week_start,current_epoch);
  //TF1* line = (TF1*)hGoodCharge->GetListOfFunctions()->FindObject("pol01);
  hGoodCharge->Fit("pol0");
  TF1* line = (TF1*)hGoodCharge->GetListOfFunctions()->FindObject("pol0");
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

  float max =   hTotalCharge->GetMaximum();

  TText *t = new TText(50,max,"Hello World !");
  t->SetTextAlign(33);
  t->SetTextColor(kRed);
  t->SetTextFont(43);
  t->SetTextSize(25);
  t->SetTextAngle(90);
  t->DrawText(7,max,"Commissioning");
  t->DrawText(37,max,"Hall C 1 pass");
  t->DrawText(53,max,"Christmas");
  t->DrawText(114,max,"Hall C 1 pass");
  t->DrawText(137,max,"Target");
  t->DrawText(158,max,"Target");
  t->DrawText(169,max,"Target");
  t->DrawText(188,max,""); // BLA, etc.
  t->DrawText(209,max,"Hall B 1 pass");
  t->DrawText(222,max,"Wien + Downtime");

  Double_t needed_slope = (goal-sum1)/(final_epoch-current_epoch);

  // //  TLine* lineFuture = new TLine(current_epoch,sum1,current_epoch+14,needed_slope*14+sum1);
  // TArrow* lineFuture = new TArrow(current_epoch,sum1,current_epoch+9,needed_slope*9+sum1,0.04125,"|>");
  // lineFuture->SetLineColorAlpha(kRed,1);
  // lineFuture->SetFillColorAlpha(kRed,0.3);
  // lineFuture->SetLineWidth(4);
  // lineFuture->SetLineStyle(7);
  // lineFuture->SetAngle(30);
  // //lineFuture->Draw();

  gPad->SetGridx(1);
  gPad->SetGridy(1);

  TLegend *leg = new TLegend(0.7, 0.7, 0.99, 0.99);
  leg->AddEntry(hTotalCharge, Form("All Charge on Target %.2f C", sum0), "lf");
  //leg->AddEntry(hGoodCharge, Form("Good charge after cuts %.2f C, Goal = %d C", sum1,goal), "lf");
  leg->AddEntry(hGoodCharge, Form("Good charge after cuts %.2f C", sum1), "lf");
  leg->AddEntry(hNoDataShift, Form("Shifts with no data (%i)",nEmpties));
  //leg->AddEntry(lineCurrent, Form("Last %d weeks, %.2f C/shift, %.2f C projected", n_weeks, line->GetParameter(1), (final_epoch-current_epoch)*(line->GetParameter(1))+sum1), "lf");
  //leg->AddEntry(lineFuture, Form("Future rate of %.2f C/shift needed to hit goal",needed_slope));
  leg->Draw("same");

  cDrawChargeMon->Print("charge_mon_time_noint.pdf");

}
