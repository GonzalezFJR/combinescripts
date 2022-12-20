# For the moment (I think) it only works with single-channel datacards
# Example
# python modules/PlotSyst.py  tt5TeVljets/02dec2022/dat_medianDRjj_e_4j1b.txt -o /nfs/fanae/user/juanr/www/public/tt5TeV/ljets/15dec2022/plots/uncertainties/ -c e_4j1b

import DatacarModifier as DM

def PlotSyst(path, outpath, datacard=None):
  if datacard is None and not os.path.isdir(path):
    datacard = path[path.rfind('/')+1:]
    path = path[:path.rfind('/')+1]
  dm = DM.DatacardModifier(path, datacard)
  processes = dm.GetProcessesInCard()
  syst = dm.GetShapeUncInCard()
  dic = dm.GetUncProcessDic()

  for proc in processes:
    for s in syst:
        if proc in dic[s]:
          PlotSystBand(dm.rootfile, proc, s, outpath)

import ROOT
ROOT.gROOT.SetBatch(True)
def PlotSystBand(rootfile, pr, syst, outpath):
    f = ROOT.TFile.Open(rootfile)
    nom = f.Get(pr)
    up = f.Get(pr+'_'+syst+'Up')
    down = f.Get(pr+'_'+syst+'Down')
    nom.SetLineColor(ROOT.kBlack); up.SetLineColor(ROOT.kRed); down.SetLineColor(ROOT.kBlue)
    nom.SetLineWidth(2); up.SetLineWidth(2); down.SetLineWidth(2)
    nom.SetStats(0); up.SetStats(0); down.SetStats(0)
    c = ROOT.TCanvas('c', 'c', 800, 600)
    c.Divide(2,1)
    p1 = c.GetPad(1)
    p1.SetPad(0, 0.3, 1, 1); p1.SetTopMargin(0.1); p1.SetBottomMargin(0.02); p1.SetLeftMargin(0.1); p1.SetRightMargin(0.02)
    p2 = c.GetPad(2)
    p2.SetPad(0, 0, 1, 0.3); p2.SetTopMargin(0.02); p2.SetBottomMargin(0.2); p2.SetLeftMargin(0.1); p2.SetRightMargin(0.02)
    c.cd(1)
    nom.SetTitle("%s %s"%(pr, syst))
    nom.GetXaxis().SetTitleSize(0.)
    nom.GetXaxis().SetLabelSize(0.)
    nom.SetMaximum( 1.1*max(nom.GetMaximum(), up.GetMaximum(), down.GetMaximum()) )
    nom.SetMinimum( 0.9*min(nom.GetMinimum(), up.GetMinimum(), down.GetMinimum()) )
    nom.Draw('l')
    up.Draw('l same')
    down.Draw('l same')
    c.cd(2)
    rup = up.Clone()
    rup.Divide(nom)
    rup.SetTitleSize(0.)
    rup.SetTitle('')
    rup.GetXaxis().SetTitleSize(0.1)
    rup.GetXaxis().SetLabelSize(0.1)
    rup.GetYaxis().SetTitleSize(0.1)
    rup.GetYaxis().SetLabelSize(0.1)
    rdown = down.Clone()
    rdown.Divide(nom)
    rup.Draw('l')
    rdown.Draw('l same')
    # Set max and min
    rup.SetMaximum( 1.1*max(rup.GetMaximum(), rdown.GetMaximum()) )
    rup.SetMinimum( 0.9*min(rup.GetMinimum(), rdown.GetMinimum()) )
    opath = outpath+'/'+pr + '/'
    if not os.path.isdir(opath):
        os.makedirs(opath)
    c.SaveAs(opath + syst + '.png')
    c.SaveAs(opath + syst + '.pdf')

import argparse
import os, sys
parser = argparse.ArgumentParser(description='Plot systematics')
parser.add_argument('path', help='path')
parser.add_argument('-o', '--outpath', dest='outpath', default='.', help='Output path')
parser.add_argument('-d', '--datacard', dest='datacard', default=None, help='Datacard')
parser.add_argument('-c', '--channel', default=None)

args = parser.parse_args()
path = args.path
outpath = args.outpath
datacard = args.datacard
chan = args.channel

if chan is not None: outpath = outpath + '/' + chan + '/'

if __name__ == '__main__':
  PlotSyst(path, outpath, datacard)
        