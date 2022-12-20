import ROOT as r
import os
from copy import deepcopy
r.gROOT.SetBatch(True)
r.gStyle.SetPadTickX(1)
r.gStyle.SetPadTickY(1)
#r.gStyle.SetOptStat(False)
#r.gStyle.SetEndErrorSize(0)

def Stack(path, mode, processes, colors, names={}, xtit='', ytit='Events', doBlind=False, pathorig=None, outpath='./', chan=None):

  hOrig = None
  if pathorig is None:
    pathorig = path[:path.rfind("/")]
  if not pathorig.endswith("/"):
    pathorig += "/"
  origrootfile = path.split("/")[-1].replace("_fitDiagnosticsHistos", "")
  if chan is None: chan = origrootfile[:-5]
  if not os.path.exists(pathorig + origrootfile):
    print("Original root file not found: " + pathorig + "/" + origrootfile)
    print("We need it to the the original binning and labels!")
  else:
    forig = r.TFile.Open(pathorig + origrootfile, "READ")
    hOrig = forig.Get("data_obs")

  if not outpath.endswith("/"):
    outpath += "/"

  if not os.path.exists(outpath):
    os.makedirs(outpath)

  dirname = 'shapes_fit_s'
  if mode == "prefit":
    dirname = 'shapes_prefit'

  if not isinstance(colors, dict):
    colors = {p:c for p,c in zip(processes, colors)}

  f = r.TFile.Open(path, "READ")
  subdir = f.Get(dirname)
  # list dirs and get the first one
  dirs = list(subdir.GetListOfKeys())
  if len(dirs) == 1:
    subdir = subdir.Get(dirs[0].GetName())

  hstack = r.THStack("stack", "stack")
  for p in reversed(processes):
    h = subdir.Get(p)
    h.SetLineWidth(0)
    h.SetFillColor(colors[p])
    hstack.Add(h)

  hdata = subdir.Get("data") if not doBlind else hstack.GetStack().Last().Clone("Asimov")
  htot = subdir.Get("total") # For uncertainty band

  c = r.TCanvas("c", "c", 800, 800)
  c.Divide(1,2)
  
  pad1 = c.GetPad(1)
  pad1.SetPad(0, 0.25, 1, 1)
  pad1.SetTopMargin(0.065); pad1.SetBottomMargin(0.025); pad1.SetLeftMargin(0.12); pad1.SetRightMargin(0.03)
  pad2 = c.GetPad(2)
  pad2.SetPad(0, 0, 1, 0.25)
  pad2.SetTopMargin(0.06); pad2.SetBottomMargin(0.42); pad2.SetLeftMargin(0.12); pad2.SetRightMargin(0.03)


  pad1.cd()
  hstack.SetTitle("")
  hstack.Draw("hist")
  hstack.GetYaxis().SetTitle(ytit)
  hstack.GetYaxis().SetLabelSize(22)
  hstack.GetYaxis().SetLabelFont(43)
  hstack.GetYaxis().SetTitleSize(30.)
  hstack.GetYaxis().CenterTitle(True)
  hstack.GetYaxis().SetTitleOffset(1.2)
  hstack.GetYaxis().SetTitleFont(43)
  hstack.GetYaxis().SetMaxDigits(4)
  hstack.GetXaxis().SetLabelSize(0.)

  # Uncertainty band
  htot.SetFillColor(r.kGray+2)
  htot.SetFillStyle(3004)
  htot.Draw("e2 same")

  # Draw data as TGraphAsymmErrors
  for i in range(hdata.GetN()):
    hdata.SetPointEXlow (i, 0)
    hdata.SetPointEXhigh(i, 0)
  hdata.Draw("same pe1")
  hdata.SetMarkerStyle(20)
  hdata.SetMarkerSize(1.2)
  hdata.SetLineWidth(1)
  hdata.SetLineColor(r.kBlack)
  hdata.SetMarkerColor(r.kBlack)

  maxval = max(hstack.GetMaximum(), hdata.GetMaximum())
  hstack.SetMaximum(maxval*1.2)



  legend = r.TLegend(0.75, 0.55, 0.99, 0.9)
  legend.SetBorderSize(0)
  legend.SetFillStyle(0)
  legend.SetTextSize(0.04)
  legend.AddEntry(hdata, "Data", "ep")
  for p in (processes):
    legend.AddEntry(subdir.Get(p), dictNames[p], "f")
  legend.Draw("same")

  # CMS label
  texcms = r.TLatex(0, 0, "CMS")
  texcms.SetNDC()
  texcms.SetTextAlign(12)
  texcms.SetTextSize(0.06)
  texcms.SetX(0.12)
  texcms.SetY(0.97)
  texcms.SetTextSizePixels(22)
  texcms.Draw("same")
  
  texprel = r.TLatex(0, 0, "Preliminary")
  texprel.SetNDC()
  texprel.SetTextAlign(12)
  texprel.SetTextSize(0.052)
  texprel.SetX(0.215)
  texprel.SetY(0.965)
  texprel.SetTextFont(52)
  texprel.Draw("same")

  texlumi = r.TLatex(0, 0, lumitex % lumi)
  texlumi.SetNDC()
  texlumi.SetTextAlign(12)
  texlumi.SetTextSize(0.052)
  texlumi.SetX(0.660)
  texlumi.SetY(0.965)
  texlumi.SetTextFont(42)
  texlumi.Draw("same")



  # Draw the ratio plot
  pad2.cd()

  # Ratio plot using TGraphAsymmErrors
  # Get histo grom TGraph
  hdata_ratio = hdata.Clone("hdata_ratio")
  hdata_ratio.SetLineColor(r.kBlack)
  hdata_ratio.SetMarkerStyle(21)
  hdata_ratio.SetMarkerSize(1.2)
  hdata_ratio.SetLineWidth(2)
  
  uncratio = htot.Clone("uncratio")
  uncratio.SetStats(0)
  uncratio.SetTitle("")

  if hOrig is not None:
    # Create an empty histogram to use for the ratio plot with the same binning as the original histogram
    if xtit == '': xtit = hOrig.GetXaxis().GetTitle()
    hRat = r.TH1F("hRat", "hRat", hOrig.GetNbinsX(), hOrig.GetXaxis().GetXmin(), hOrig.GetXaxis().GetXmax())
    uncratio.SetBins(hOrig.GetNbinsX(), hOrig.GetXaxis().GetXmin(), hOrig.GetXaxis().GetXmax())
    hRat.SetTitle("")
    hRat.SetStats(0)
    hRat.SetMinimum(rmin)
    hRat.SetMaximum(rmax)
    hRat.GetYaxis().CenterTitle(True)
    hRat.GetXaxis().SetLabelSize(22)
    hRat.GetYaxis().SetLabelSize(22)
    hRat.GetXaxis().SetLabelFont(43)
    hRat.GetYaxis().SetLabelFont(43)
    hRat.GetYaxis().SetTitle("Data / Pred.")
    hRat.GetYaxis().SetTitleOffset(1.4)
    hRat.GetXaxis().SetTitle(xtit)
    hRat.GetYaxis().SetTitleSize(26)
    hRat.GetYaxis().SetTitleFont(43)
    hRat.GetXaxis().SetTitleOffset(4.0)
    hRat.GetXaxis().SetTitleSize(26)
    hRat.GetXaxis().SetTitleFont(43)
    hRat.GetYaxis().SetRangeUser(rmin, rmax)
    hRat.GetYaxis().SetNdivisions(503)
    hRat.Draw("axis")

  hdata_ratio = hdata.Clone("hdata_ratio")
  for i in range(hdata_ratio.GetN()):
    hdata_ratio.SetPointEXlow (i, 0)
    hdata_ratio.SetPointEXhigh(i, 0)
    hdata_ratio.SetPointEYlow(i, hdata_ratio.GetErrorYlow(i)/htot.GetBinContent(i+1))
    hdata_ratio.SetPointEYhigh(i, hdata_ratio.GetErrorYhigh(i)/htot.GetBinContent(i+1))
    x = hdata_ratio.GetX()[i]
    if hOrig is not None:
      # Take center bin values from original histogram
      x = hOrig.GetXaxis().GetBinCenter(i+1)
    hdata_ratio.SetPoint(i, x, hdata_ratio.GetY()[i]/htot.GetBinContent(i+1))
    uncratio.SetBinContent(i+1, 1)
    uncratio.SetBinError(i+1, htot.GetBinError(i+1)/htot.GetBinContent(i+1))

  uncratio.Draw("e2 same")
  hdata_ratio.Draw("pe1 same")
  outname = "%s_%s"%(chan, mode)
  c.SaveAs(outpath+outname+".png")
  c.SaveAs(outpath+outname+".pdf")


######################################################################################################
######################################################################################################
######################################################################################################

colors = {"tW":798, "tt":633, "QCD":413, "WJets":390, "DY":852}
processes = ['tt', 'tW', 'WJets', 'DY', 'QCD']

dictNames = {
    "tt"    : "t#bar{t}",
    "tW"       : "tW",
    "WJets"  : "W+Jets",
    "QCD"    : "QCD",
    "DY"       : "Drell-Yan",
    "data"     : "Data",
    "total"    : "Uncertainty",
}

pathdiag = 'tt5TeVljets/02dec2022/combine/medianDRjj_m_g5j2b_fitDiagnosticsHistos.root'
pathorig = 'tt5TeVljets/02dec2022/'
rmin = 0.5;
rmax = 1.5;
lumi = 302.;
lumitex = "%1.0f pb^{-1} (5.02 TeV)";

import os, sys, argparse

parser = argparse.ArgumentParser(description='Draw plots from FitDiagnostics')
parser.add_argument('rootfile', help='Input file')
parser.add_argument('-p', '--path', default='', help='Path to combine rootfile')
parser.add_argument('-o', '--outpath', dest='outpath', default='.', help='Path to output plots')
parser.add_argument('-m', '--mode', default='prefit', help='Verbosity level')
parser.add_argument('--blind', action='store_true', help='Blind data')

args = parser.parse_args()
rootfile = args.rootfile
outpath = args.outpath
mode = args.mode
blind = args.blind
pathorig = args.path

if not outpath.endswith('/'):
    outpath += '/'


pathdiag = rootfile
if os.path.isdir(pathdiag):
  for f in os.listdir(pathdiag):
    if not f.endswith('.root'): continue
    path = os.path.join(pathdiag, f)
    Stack(path, mode, processes, colors, pathorig=pathorig, outpath=outpath)
else:
  Stack(pathdiag, mode, processes, colors, pathorig=pathorig, outpath=outpath)

# Example:
# python DrawPlots.py tt5TeVljets/02dec2022/combine/ -p tt5TeVljets/02dec2022/ -o /nfs/fanae/user/juanr/www/public/tt5TeV/ljets/14dec2022/combine_plots/ -m postfit