#include <TPaveStats.h>
#include <iomanip>
void DrawChargeMon_projected(Int_t exptID = 2)
{

  gStyle->SetOptStat(0);

  ifstream ifstr("out_time.txt");
  ofstream ofstr("out_shifts.txt");
  string date, time;
  double charge0, charge1, epoch_start, epoch, unix_time_start, unix_time;

  Int_t nEmpties = 0;
  Double_t lastEntry = 0.0;
  Int_t starttime = 0;
  Int_t endtime   = 0;

  //Int_t nSecs = 86400;
  Int_t nSecs = 86400/3;
  Int_t nSecsExp = 1.184e7;
  Int_t offset = 176;
  Int_t startTime = 1575435600; // CREX
  Int_t endTime = 0;
  if (exptID == 1) {
    startTime = 1562284800 + 6*24*3600; // PREX II
  }
  Int_t startTimeDST = startTime-3600;

  Double_t first_epoch = 0.0;
  Double_t last_epoch = 0.0;
  int SumBreakStart = 350;
  int SumBreakLen = 350;
  int SumBreakStop = 750;
  int offset = 0;
  //Double_t final_epoch = 876-SumBreakLen; // or do = last_epoch+1; // 366 = April 4, 372 = April 6, 414 = April 20, 888 = Sept 21
  Double_t final_epoch = 878-SumBreakLen; // or do = last_epoch+1; // 366 = April 4, 372 = April 6, 414 = April 20, 888 = Sept 21
  if (exptID == 1) {
    final_epoch = 200; // PREX II - what is this?
    SumBreakStart = 99999;
  }
  Double_t total_epoch = final_epoch+15; // or do = last_epoch+1+15; 
  // No data between at least 350 and 750 -> Subtract 400

  // 366 = number of shifts from Dec 4 - April 4 -> Add 15 for buffer space
  // 330 = number of shifts from Dec 4 - March 23
  // 105 = number of shifts from Dec 4 - January 8
  // 39 = number of shifts from Dec 4 - Dec 17
  Double_t current_epoch = last_epoch;
  Int_t n_weeks = 2;
  Int_t goal = 467;
  if (exptID == 1) {
    goal = 150; // PREX II ?
  }
  Double_t integrated_good_charge = 0.0;
  Double_t max_efficiency = 0.0;
  Double_t max_shift = 0.0;
  Double_t fit_length = n_weeks*7*3;
  Double_t current_week_start = current_epoch - fit_length;

  double sum0 = 0 ;
  double sum0DST = 0 ;
  double sum1 = 0 ;
  int n=0;

  Int_t tmpBin0 = 0;
  Int_t tmpBin0DST = 0;
  Int_t tmpBin1 = 0;
  Int_t tmpBin2 = 0;

  TH1F* htime = new TH1F("htime", "Time vs shift", total_epoch, startTime, startTime+total_epoch*8*60*60);
  TH1F* htimeDST = new TH1F("htimeDST", "Time DST vs shift", total_epoch, startTimeDST, startTimeDST+total_epoch*8*60*60);
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
    // Beginning of day shift on Feb1 2020. Offset = number of shifts back to beginning of day shift on December 4th
    unix_time_start = epoch_start;
    unix_time = epoch;
    if (epoch_start > 1583643600) {
      epoch_start = epoch_start + 3600;
      epoch = epoch + 3600;
    }

    if(n<1) 
    {
      first_epoch = epoch;
      Printf("First Epoch, UNIX Time: %f, run = %d",first_epoch,run);
      epoch = (-1*startTime + epoch)/(1.0*nSecs);// + offset;
      first_epoch = epoch;
      Printf("First Epoch, Shift Time: %f",first_epoch);
    }
    epoch_start = (-1*startTime + epoch_start)/(1.0*nSecs);// + offset;
    epoch = (-1*startTime + epoch)/(1.0*nSecs);// + offset;

    // Summer break: 
    if (epoch > SumBreakStart && epoch < SumBreakStop) { continue ; }
    if (epoch >= SumBreakStop ) { 
      epoch_start = epoch_start - SumBreakLen; 
      epoch = epoch - SumBreakLen; 
      unix_time = unix_time - SumBreakLen*8*60*60;
      unix_time_start = unix_time_start - SumBreakLen*8*60*60;
    }

    if(charge1 > charge0)
    {
      cout << "run " << run << " has total charge<good charge: " << charge0 << " " << charge1 << endl;
    }

    charge0 = charge0 * 1.e-6;
    charge1 = charge1 * 1.e-6;

    //sum0 = sum0 + charge0;
    //sum1 = sum1 + charge1;

    // Keep track of time
    const Double_t res = 10.0; // Factor of 10 resolution on run length
    Double_t oldSum0 = sum0;
    Double_t oldSum0DST = sum0DST;
    Double_t oldSum1 = sum1;
    sum0 = sum0 + charge0;
    sum0DST = sum0DST + charge0;
    sum1 = sum1 + charge1;
    for (Int_t t = 0 ; t <= (Int_t)res; t++ ) {
      // Find the bin to fill, generously interpolating 1/res of the bins
      tmpBin0 = htime->Fill(unix_time_start+((t/res)*(unix_time-unix_time_start)), oldSum0 + ((t/res)*(charge0)));
      tmpBin0DST = htimeDST->Fill(unix_time_start+((t/res)*(unix_time-unix_time_start)), oldSum0DST + ((t/res)*(charge0)));
      tmpBin1 = hsum->Fill(epoch_start+((t/res)*(epoch-epoch_start)), oldSum0 + ((t/res)*(charge0)));
      tmpBin2 = hsum1->Fill(epoch_start+((t/res)*(epoch-epoch_start)), oldSum1 + ((t/res)*(charge1)));
      // Set that bin's contents to what they should be (regardless of the redundant filling involved above
      htime->SetBinContent(htime->GetBin(tmpBin0), oldSum0 + ((t/res)*(charge0)));
      htimeDST->SetBinContent(htimeDST->GetBin(tmpBin0DST), oldSum0DST + ((t/res)*(charge0)));
      hsum->SetBinContent(hsum->GetBin(tmpBin1), oldSum0 + ((t/res)*(charge0)));
      hsum1->SetBinContent(hsum1->GetBin(tmpBin2), oldSum1 + ((t/res)*(charge1)));
    }

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
  ofstr << "Shift,\tGood Charge,\tTotal Good Charge,\tTime Start,\tTime End,\tEpoch Start,\tEpoch End" << std::endl;
  ofstr << (Int_t)hsum2->GetBinCenter(0) << ",\t" << 0 << ",\t" << 0 << ",\t" << gSystem->GetFromPipe(Form("date --date='@%d'",(Int_t)htime->GetXaxis()->GetBinLowEdge(0))) << ",\t" << gSystem->GetFromPipe(Form("date --date='@%d'",(Int_t)htime->GetXaxis()->GetBinLowEdge(0)+(Int_t)htime->GetXaxis()->GetBinWidth(0))) << ",\t" << (Int_t)htime->GetXaxis()->GetBinLowEdge(0) << ",\t" << (Int_t)htime->GetXaxis()->GetBinLowEdge(0)+(Int_t)htime->GetXaxis()->GetBinWidth(0) << std::endl;
  //ofstr << (Int_t)hsum2->GetBinCenter(0) << ",\t" << 0 << ",\t" << 0 << ",\t" << (Int_t)htime->GetXaxis()->GetBinLowEdge(0) << ",\t" << (Int_t)htime->GetXaxis()->GetBinLowEdge(0)+(Int_t)htime->GetXaxis()->GetBinWidth(0) << std::endl;
      
  for (Int_t j = 0 ; j < hsum2->GetNbinsX() ; j++) {
    // Fill Zeros
    if (j>2 && hsum1->GetBinContent(j)==0 && hsum1->GetBinCenter(hsum1->GetBin(j))<(Int_t)current_epoch) {
      if ((Int_t)htime->GetXaxis()->GetBinLowEdge(j) > 1583643600) {
        startTime = (Int_t)htimeDST->GetXaxis()->GetBinLowEdge(j);
        endTime   = (Int_t)htimeDST->GetXaxis()->GetBinLowEdge(j)+htimeDST->GetXaxis()->GetBinWidth(j);
      }
      else {
        startTime = (Int_t)htime->GetXaxis()->GetBinLowEdge(j);
        endTime   = (Int_t)htime->GetXaxis()->GetBinLowEdge(j)+htime->GetXaxis()->GetBinWidth(j);
      }
      ofstr << (Int_t)hsum1->GetBinCenter(j-1) << ",\t";
      ofstr << setprecision(3) << setw(5) << setfill('0') << 0.0 << ",\t" << setprecision(4) << integrated_good_charge;
      if (startTime > (Int_t)htime->GetXaxis()->GetBinLowEdge(0)+SumBreakStart*8*60*60) { 
        offset = SumBreakLen*8*60*60;
      }
      else {
        offset = 0;
      }
      ofstr << ",\t" << gSystem->GetFromPipe(Form("date --date='@%d'",(Int_t)startTime+offset)) << ",\t" << gSystem->GetFromPipe(Form("date --date='@%d'",(Int_t)endTime+offset));
      ofstr << ",\t" << (Int_t)startTime+offset << ",\t" << (Int_t)endTime+offset << std::endl;
    }
    // Fill Data
    if (hsum1->GetBinContent(j) != 0) {
      lastEntry = hsum1->GetBinContent(j);
      if ((Int_t)htime->GetXaxis()->GetBinLowEdge(j) > 1583643600) {
        starttime = (Int_t)htimeDST->GetXaxis()->GetBinLowEdge(j);
        endtime   = (Int_t)htimeDST->GetXaxis()->GetBinLowEdge(j)+htimeDST->GetXaxis()->GetBinWidth(j);
      }
      else {
        starttime = (Int_t)htime->GetXaxis()->GetBinLowEdge(j);
        endtime   = (Int_t)htime->GetXaxis()->GetBinLowEdge(j)+htime->GetXaxis()->GetBinWidth(j);
      }
      if (j>1 && hsum2->GetBinContent(j-1)!=0 && max_efficiency < (lastEntry - hsum2->GetBinContent(j-1))) {
        max_efficiency = (lastEntry - hsum2->GetBinContent(j-1));
        max_shift = hsum2->GetBinCenter(j-1);
        //Printf("Max efficiency = %f, shift %f",max_efficiency,max_shift);
      }
      else if (j>1 && hsum1->GetBinContent(j-1)!=0 && max_efficiency < (lastEntry - hsum1->GetBinContent(j-1))) {
        max_efficiency = (lastEntry - hsum1->GetBinContent(j-1));
        max_shift = hsum1->GetBinCenter(j-1);
        //Printf("Max efficiency = %f, shift %f",max_efficiency,max_shift);
      }
      if (j>1 && hsum2->GetBinContent(j-1)!=0 && 2.0 < (lastEntry - hsum2->GetBinContent(j-1))) {
        Printf("2+ C: %f, from shift %d",(lastEntry - hsum2->GetBinContent(j-1)),(Int_t)hsum2->GetBinCenter(j-1));
      }
      if (j>1 && hsum1->GetBinContent(j-1)!=0 && 2.0 < (lastEntry - hsum1->GetBinContent(j-1))) {
        Printf("2+ C: %f, from shift %d",(lastEntry - hsum1->GetBinContent(j-1)),(Int_t)hsum1->GetBinCenter(j-1));
      }
      if (j>1 && hsum2->GetBinContent(j-1)!=0 && 0.0 <= (lastEntry - hsum2->GetBinContent(j-1))) {
        integrated_good_charge+=(lastEntry - hsum2->GetBinContent(j-1));
        
        ofstr << (Int_t)hsum2->GetBinCenter(j-1) << ",\t";
        ofstr << setprecision(3) << setw(5) << setfill('0') << (lastEntry - hsum2->GetBinContent(j-1)) << ",\t" << setprecision(4) << integrated_good_charge;
        if (startTime > (Int_t)htime->GetXaxis()->GetBinLowEdge(0)+SumBreakStart*8*60*60) { 
          offset = SumBreakLen*8*60*60;
        }
        else {
          offset = 0;
        }
        ofstr << ",\t" << gSystem->GetFromPipe(Form("date --date='@%d'",(Int_t)starttime+offset)) << ",\t" << gSystem->GetFromPipe(Form("date --date='@%d'",(Int_t)endtime+offset));
        ofstr << ",\t" << (Int_t)starttime+offset << ",\t" << (Int_t)endtime+offset << std::endl;
      }
      if (j>1 && hsum1->GetBinContent(j-1)!=0 && 0.0 <= (lastEntry - hsum1->GetBinContent(j-1))) {
        integrated_good_charge+=(lastEntry - hsum1->GetBinContent(j-1));
        ofstr << (Int_t)hsum1->GetBinCenter(j-1) << ",\t";
        ofstr << setprecision(3) << setw(4) << setfill('0') << (lastEntry - hsum1->GetBinContent(j-1)) << ",\t" << setprecision(4) << integrated_good_charge;
        if (startTime > (Int_t)htime->GetXaxis()->GetBinLowEdge(0)+SumBreakStart*8*60*60) { 
          offset = SumBreakLen*8*60*60;
        }
        else {
          offset = 0;
        }
        ofstr << ",\t" << gSystem->GetFromPipe(Form("date --date='@%d'",(Int_t)starttime+offset)) << ",\t" << gSystem->GetFromPipe(Form("date --date='@%d'",(Int_t)endtime+offset));
        ofstr << ",\t" << starttime+offset << ",\t" << (Int_t)endtime+offset << std::endl;
      }
    }
    else {
      if (first_epoch < hsum1->GetBinCenter(hsum1->GetBin(j)) && current_epoch > hsum1->GetBinCenter(hsum1->GetBin(j))) {
        hsum2->Fill(hsum1->GetBinCenter(hsum1->GetBin(j)),lastEntry);
        nEmpties++;
      }
    }
  }
  Printf("Max efficiency = %f, shift %f",max_efficiency,max_shift);

  TCanvas *c2 = new TCanvas("c2","c2", 1000, 600); //1000 600
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

  gPad->SetGridx(1);
  gPad->SetGridy(1);

  TLegend *leg = new TLegend(0.1, 0.6, 0.55, 0.925);
  leg->AddEntry(hsum, Form("All Charge on Target %.2f C", sum0), "lf");
  leg->AddEntry(hsum1, Form("Good charge after cuts %.2f C, Goal = %d C", sum1,goal), "lf");
  leg->AddEntry(hsum2, Form("Shifts with no data"));
  leg->Draw("same");
  c2->Print("charge_mon_time.pdf");

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
  lineCurrent->Draw();

  Double_t needed_slope = (goal-sum1)/(final_epoch-current_epoch);

//  TLine* lineFuture = new TLine(current_epoch,sum1,current_epoch+14,needed_slope*14+sum1);
  TArrow* lineFuture = new TArrow(current_epoch,sum1,current_epoch+19,needed_slope*19+sum1,0.04125,"|>");
  lineFuture->SetLineColorAlpha(kRed,1);
  lineFuture->SetFillColorAlpha(kRed,0.3);
  lineFuture->SetLineWidth(4);
  lineFuture->SetLineStyle(7);
  lineFuture->SetAngle(30);
  lineFuture->Draw();

  leg->AddEntry(lineCurrent, Form("Last %d weeks, %.2f C/shift, %.2f C projected", n_weeks, line->GetParameter(1), (final_epoch-current_epoch)*(line->GetParameter(1))+sum1), "lf");
  leg->AddEntry(lineFuture, Form("Future rate of %.2f C/shift needed to hit goal",needed_slope));
  leg->Draw("same");

  c2->Print("charge_mon_projected.pdf");

}
