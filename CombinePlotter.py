import ROOT as r
import os
import numpy as np
from copy import deepcopy
#import tdrstyle, CMS_lumi
r.gROOT.SetBatch(True)
r.gStyle.SetOptStat(False)
r.gStyle.SetPadTickX(1)
r.gStyle.SetPadTickY(1)
r.gStyle.SetEndErrorSize(0)

ColourMapForProcesses = {
    "tw"       : 798,
    "ttbar"    : 633,
#    "ttbartw"  : 633,
    "nonworz"  : 413,
    "vvttv"    : 390,
    "dy"       : 852
}

orderedProcesses = ["nonworz", "vvttv", "dy", "ttbar", "tw"]
orderedLegendFor2Col = ["data", "vvttv", "tw", "nonworz", "ttbar", "postunc", "dy"]
orderedLegendFor1Col = ["data", "tw", "ttbar", "dy", "vvttv", "nonworz", "postunc"]

#### Size of all text in the plots (except legend)
extraSizeForChannelSpam = 2
spamsSize = 22
titleSize = 26
axisLabelsSize = 22

dictNames = {
    "tw"       : "tW",
    "ttbar"    : "t#bar{t}",
    "nonworz"  : "Non-W/Z",
    "vvttv"    : "VV+t#bar{t}V",
    "dy"       : "DY",
    "data"     : "Data",
    "total"    : "Uncertainty",
}

dictRegions = {
    "ch1"      : "1j1b",
    "ch2"      : "2j1b",
    "ch3"      : "2j2b",
}

dictRegionsXaxisLabels = {
    "ch1"      : "BDT discriminant",
    "ch2"      : "BDT discriminant",
    "ch3"      : "Subleading jet #it{p}_{T} (GeV)",
}

dictRegionsYaxisLabels = {
    "ch1"      : "Events",
    "ch2"      : "Events",
    "ch3"      : "Events / 10 GeV",
}

dictBinEdgesRegions = {
    "ch1"      : [0.5,20.5],
    "ch2"      : [0.5,12.5],
    "ch3"      : [30,190],
    #"ch1"      : [0.5,2.5],
    #"ch2"      : [0.5,2.5],
    #"ch3"      : [30,190],
}

dictBinsCenterRegions = {
    "ch1"      : [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],
    "ch2"      : [1,2,3,4,5,6,7,8,9,10,11,12],
    "ch3"      : [35,45,55,65,75,85,95,105,115,125,135,145,155,165,175,185],
}

legendHeigh = {
    "prefit" : {
    "ch1" : 4,
    "ch2" : 4,
    "ch3" : 7,
    },
    "fit_s" : {
    "ch1" : 5,
    "ch2" : 5,
    "ch3" : 9,
    },
}

lumidict     = {"2016" : 36.33,
                "2017" : 41.53,
                "2018" : 59.74,
                "run2" : 138}

def doSpam(text,x1,y1,x2,y2,align=12,fill=False,textSize=0.033,_noDelete={}):
  cmsprel = r.TPaveText(x1,y1,x2,y2,"NDC");
  cmsprel.SetTextSize(textSize);
  cmsprel.SetFillColor(0);
  cmsprel.SetFillStyle(1001 if fill else 0);
  cmsprel.SetLineStyle(2);
  cmsprel.SetLineColor(0);
  cmsprel.SetLineWidth(0);
  cmsprel.SetTextAlign(align);
  cmsprel.SetTextFont(43);
  cmsprel.AddText(text);
  cmsprel.Draw("same");
  _noDelete[text] = cmsprel; ## so it doesn't get deleted by PyROOT                                                                                                                    
  return cmsprel

def producePlots(year, region, path):
  
  def addLegendEntries(orderList): 
    for entry in orderList:
      if entry in orderedProcesses:
        h = subdir.Get(entry)
        legend.AddEntry(h,dictNames[h.GetName()],"f") 
      elif entry == "data":
        legend.AddEntry(gr_forLegend,dictNames[gr.GetName()],"PE")
      elif entry == "postunc":
        legend.AddEntry(htotal,"Uncertainty" if key=="fit_s" else dictNames[htotal.GetName()],"f")
      elif entry == "preunc":
        legend.AddEntry(preFitHistsUnc[dire],"Prefit unc.","f")
      elif entry == "ratio":
        legend.AddEntry(preFitHists[dire],"Prefit Data / Pred.","l")
    

  
  preFitHists = {}
  preFitHistsUnc = {}
  for key in ["prefit", "fit_s"]:
    filename = path + "/fitDiagnostics{y}_{r}.root".format(y = year, r = region)
    outpath = path + "/plots_result_{y}_{r}/".format(y = year, r = region)
    #Directories with the pre or postfit results
    maindir = "shapes_%s" %(key)
    f = r.TFile.Open(filename)
    # Extract the fit result
    rooFit = f.Get("fit_s")
    rooFitList = rooFit.floatParsFinal()
    for param in rooFitList:
      if param.GetName() == "r":
        r_tW = param.getVal()
        break
              
    # Change to the directory containing the prefit/postfit plots
    shapes = f.Get(maindir)
    shapes.cd()
    				
	  # This directory contains a list with the different channels
    dirs = shapes.GetListOfKeys()
    dirnames = []
    for dire in dirs:
      dirnames.append(dire.GetName())
				
    for dire in dirnames:
      c = r.TCanvas("canvas", "",  600, 600)
      topSpamSize     = 1.1
      c.SetTopMargin(c.GetTopMargin() * topSpamSize)
      c.Divide(1,2)    		        
      
      p1 = c.GetPad(1)    		        
      p1.SetPad(0, 0.25, 1, 1)
      p1.SetTopMargin(0.055)
      p1.SetBottomMargin(0.025)
      p1.SetLeftMargin(0.16)
      p1.SetRightMargin(0.03)
	        		        
      p2 = c.GetPad(2)
      p2.SetPad(0, 0, 1, 0.25)
      p2.SetTopMargin(0.06)
      p2.SetBottomMargin(0.42)
      p2.SetLeftMargin(0.16)
      p2.SetRightMargin(0.03)
	        		        
	
      subdir = shapes.Get(dire)
      subdir.cd()
      hstack = r.THStack()
      #We define the legend
      textSize = 0.05616
      height = textSize*1.15*legendHeigh[key][dire]
      if dire != "ch3":
        legend = r.TLegend(.38, .9-height, .88, .91) #0.85 for the first number in the CMGTools plotter
      else:
        legend = r.TLegend(.6, .9-height, .8, .91) #0.85 for the first number in the CMGTools plotter
      legend.SetBorderSize(0)
      legend.SetFillColor(0)
      legend.SetShadowColor(0)
      legend.SetFillStyle(0)
      legend.SetTextFont(42)
      legend.SetTextSize(textSize)
      legend.SetNColumns(1)
      
      #TotalHisto MC
      htotal = subdir.Get("total")

      # Get the data points
      gr = subdir.Get("data")
      dataNpoints = gr.GetN()
      datapointsY = gr.GetY()
      datapointsX = gr.GetX()
      uncpointsHigh = gr.GetEYhigh()
      uncpointsLow = gr.GetEYlow()
      gr.SetMarkerStyle(8)
      # Get the data/MC
      ratio_hist = deepcopy(gr.Clone("ratiohist"))
      gr_forLegend = r.TH1F("dataPoints", "", 1,0.5,1.5)
      gr_forLegend.SetMarkerStyle(8)
      

      #Remove horizontal error bars
      for i in range(dataNpoints):
        gr.SetPointEXlow(i,0)
        gr.SetPointEXhigh(i,0)
        if htotal.GetBinContent(i+1) != 0:
          ratio_hist.SetPoint(i,dictBinsCenterRegions[dire][i],datapointsY[i]/htotal.GetBinContent(i+1))
          ratio_hist.SetPointEYhigh(i,uncpointsHigh[i]/htotal.GetBinContent(i+1))
          ratio_hist.SetPointEYlow(i,uncpointsLow[i]/htotal.GetBinContent(i+1))
          ratio_hist.SetPointEXhigh(i,0)
          ratio_hist.SetPointEXlow(i,0)
      if key == "prefit":        
        ratioPreFit = r.TH1F("ratioPreFit_%s" %dire, "ratioPreFit_%s" %dire, len(dictBinsCenterRegions[dire]),dictBinEdgesRegions[dire][0],dictBinEdgesRegions[dire][1])
        for bin in range(1, len(dictBinsCenterRegions[dire]) + 1):
          ratioPreFit.SetBinContent(bin, datapointsY[bin - 1]/htotal.GetBinContent(bin))
        
        preFitHists[dire] = deepcopy(ratioPreFit)
      
      #legend.AddEntry(gr_forLegend,dictNames[gr.GetName()],"PE")
      for histoName in orderedProcesses:
        h = subdir.Get(histoName) 
        h.GetXaxis().SetLabelSize(0)
        h.SetLineColor(1)
        h.SetLineWidth(0)
        h.SetFillColor(ColourMapForProcesses[histoName])
        hstack.Add(h)
	    
#      for histoName in reversed(orderedProcesses):
#        h = subdir.Get(histoName) 
#        if histoName == "tw":
#          legend.AddEntry(h,dictNames[h.GetName()] + " (#mu = %1.2f)" %round(r_tW, 2),"f")
#        else:
#          legend.AddEntry(h,dictNames[h.GetName()],"f")
      p1.cd()
					
      hstack.Draw("hist")
      hstack.GetXaxis().SetLabelSize(0)
      hstack.GetYaxis().SetTitleOffset(1.8)
      hstack.SetMaximum(hstack.GetMaximum()*1.5)
      hstack.GetYaxis().SetTitle(dictRegionsYaxisLabels[dire])
      hstack.GetYaxis().SetLabelSize(axisLabelsSize)
      hstack.GetYaxis().SetLabelFont(43)
      hstack.GetYaxis().SetTitleSize(titleSize)
      hstack.GetYaxis().SetTitleFont(43)
      hstack.GetYaxis().SetMaxDigits(4)
      
      hstack.GetXaxis().SetRange(1,len(dictBinsCenterRegions[dire]))


      # now draw error bands
      htotal.SetFillStyle(3444)
      htotal.SetFillColor(r.kGray+2)
      htotal.SetMarkerStyle(0)
      htotal.SetMarkerColor(920)
      htotal.SetLineWidth(0)
      #legend.AddEntry(htotal,"Postfit unc." if key=="fit_s" else dictNames[htotal.GetName()],"f")
      htotal.Draw("E2 same")

      # now draw data
      gr.GetXaxis().SetLabelSize(0)
      gr.Draw("p E same")


      legend.Draw("same")      
      # Ratio plot
      p2.cd()
      lin = r.TLine(dictBinEdgesRegions[dire][0], 1, dictBinEdgesRegions[dire][1], 1)
      lin.SetLineWidth(1)
      lin.SetLineColor(1)
      lin.SetLineStyle(2)

      #ratio_hist = r.TGraphAsymmErrors(dataNpoints,datapointsX,np.array(datapointsYRatio,dtype='float64'),gr.GetEXlow(),gr.GetEXhigh(),np.array(uncpointsLowRatio,dtype='float64'),np.array(uncpointsHighRatio,dtype='float64'))
      
      #print(dir(ratio_hist))

			
      		
      #ratio_hist = ratio_hist.Divide(htotal,ratio_hist,'pois')
								
      #ratio_hist.SetLineWidth()
      ratio_hist.SetMarkerStyle(20)
      ratio_hist.SetMarkerSize(1)
	
      htotalNoErr = deepcopy(htotal.Clone("ratiounc"))
      htotalErr = deepcopy(htotal.Clone("ratiouncErr"))
      for i in range(1, htotalNoErr.GetNbinsX()+1):
        htotalNoErr.SetBinError(i, 0)
      
      htotalErr.Divide(htotalNoErr)
      htotalErr.SetTitle("")
      #htotalErr.SetFillColorAlpha(r.kCyan)
      htotalErr.SetBins(len(dictBinsCenterRegions[dire]),dictBinEdgesRegions[dire][0],dictBinEdgesRegions[dire][1])

      if key == "prefit": 
        preFitHistsUnc[dire] = deepcopy(htotalErr)

      #for i in range(1,htotalErr.GetNbinsX()+1):
      #  htotalErr.SetBins(i,dictBinsCenterRegions[dire][i-1]-0.5,dictBinsCenterRegions[dire][i-1]+0.5)
      #htotalErr.GetXaxis().SetRange(dictRangeRegions[dire][0],dictRangeRegions[dire][1])
      
      hAuxForAxis = r.TH1F("axis","", len(dictBinsCenterRegions[dire]),dictBinEdgesRegions[dire][0],dictBinEdgesRegions[dire][1])
      hAuxForAxis.SetMarkerSize(0)
      hAuxForAxis.GetXaxis().SetLabelSize(axisLabelsSize)
      hAuxForAxis.GetYaxis().SetLabelSize(axisLabelsSize)
      hAuxForAxis.GetXaxis().SetLabelFont(43)
      hAuxForAxis.GetYaxis().SetLabelFont(43)
      hAuxForAxis.GetYaxis().SetTitle("Data / Pred.     ")
      hAuxForAxis.GetYaxis().SetTitleOffset(1.8)
      hAuxForAxis.GetXaxis().SetTitle(dictRegionsXaxisLabels[dire])
      hAuxForAxis.GetYaxis().SetTitleSize(titleSize)
      hAuxForAxis.GetYaxis().SetTitleFont(43)
      hAuxForAxis.GetXaxis().SetTitleOffset(4.0)
      hAuxForAxis.GetXaxis().SetTitleSize(titleSize)
      hAuxForAxis.GetXaxis().SetTitleFont(43)
      hAuxForAxis.GetYaxis().SetRangeUser(0.8 if dire=="ch3" else 0.94 , 1.2 if dire=="ch3" else 1.06)
      hAuxForAxis.GetYaxis().SetNdivisions(503)
      hAuxForAxis.GetYaxis().CenterTitle(True)
      hAuxForAxis.Draw("axis")
      if key == "fit_s":
        preFitHistsUnc[dire].SetFillStyle(1001)
        preFitHistsUnc[dire].SetFillColorAlpha(r.kAzure, 0.35)
        preFitHistsUnc[dire].SetLineColor(r.kBlack)
        preFitHistsUnc[dire].SetLineWidth(0)
        #legend.AddEntry(preFitHistsUnc[dire],"Prefit unc.","f")
        ######preFitHistsUnc[dire].Draw("E2 same")	
        preFitHists[dire].SetLineColor(2)
        preFitHists[dire].SetLineWidth(2)
        #legend.AddEntry(preFitHists[dire],"Prefit Data/Pred.","l")
        ######preFitHists[dire].Draw("same")
      
      
      if dire != "ch3":
        legend.SetNColumns(2)
        addLegendEntries(orderedLegendFor2Col)
      else:
        addLegendEntries(orderedLegendFor1Col)
        
      htotalErr.Draw("e2 same")	
      lin.Draw("same L")
      ratio_hist.Draw("p E same")	

      p1.cd()
      #doSpam('#splitline{#scale[1.1]{#bf{CMS}}}{#scale[0.9]{#it{Preliminary}}}',.2, .845, .35, .885,textSize = 22)
      doSpam('#scale[1.1]{#bf{CMS}}',.2, .845, .35, .885,textSize = spamsSize)
      keyname = key
      if keyname == "fit_s": keyname = "postfit"
      doSpam(str(lumidict[year]) + " fb^{-1} (13 TeV)",0.7, .963, .975, .99,textSize = spamsSize*0.98)
      if dire == "ch3":
        doSpam("e^{#pm}#mu^{#mp} (" + dictRegions[dire] + ")", .365, .845, .55, .885, textSize = spamsSize + extraSizeForChannelSpam)
      else:
        doSpam("#splitline{ e^{#pm}#mu^{#mp}}{(" + dictRegions[dire] + ")}", .2, .700, .35, .740, textSize = spamsSize + extraSizeForChannelSpam)
	
      if not os.path.exists(outpath): os.system("mkdir -p %s"%outpath)
      c.SaveAs("%s/%s_%s.png"%(outpath,keyname,dire))
      c.SaveAs("%s/%s_%s.pdf"%(outpath,keyname,dire))
      c.Close()
  return