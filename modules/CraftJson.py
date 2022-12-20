import json
import os
import sys
from math import sqrt
import pandas as pd
import ROOT

fname = 'data.csv'
columns = ['bin', 'chan', 'mu', 'stat', 'syst', 'tot', 'statUp', 'statDo', 'systUp', 'systDo', 'totUp', 'totDo', 'tt', 'tW', 'WJets', 'QCD', 'DY', 'Total bkg', 'Data']

def read(fname):
    if not os.path.exists(fname):
        return {}
    with open(fname, 'r') as f:
       return json.load(f)

def write(fname, data):
    with open(fname, 'w') as f:
        json.dump(data, f, indent=2)

def readcsv(fname):
    if not os.path.exists(fname):
        return pd.DataFrame(columns=columns)
    return pd.read_csv(fname)

def writecsv(fname, df):
    df.to_csv(fname, index=False)

def GetYields(fname, bin, chan):
    df = readcsv(fname)
    cols = ['tt', 'tW', 'WJets', 'QCD', 'DY', 'Total bkg', 'Data']
    if len(df[(df['bin'] == bin) & (df['chan'] == chan)]) > 0:
        return df[(df['bin'] == bin) & (df['chan'] == chan)][cols].values[0]
    return None

def LoadFromScan(fname, bin, chan, txtname='outputfit.txt'):
    df = readcsv(fname)
    mu=0; statUp=0; statDo=0; systUp=0; systDo=0; totUp=0; totDo=0;
    syst=0; stat=0; tot=0;
    with open(txtname, 'r') as f:
        lines = f.readlines()
        mu = lines[0].replace(' ', '').split(':')[1]
        _, statUp, statDo = lines[1].replace(' ', '').split(':')
        _, systUp, systDo = lines[2].replace(' ', '').split(':')
        mu = float(mu); statUp = float(statUp); statDo = float(statDo); systUp = float(systUp); systDo = float(systDo); 
        totUp = sqrt(statUp**2 + systUp**2)
        totDo = sqrt(statDo**2 + systDo**2)
        stat = (statDo+statUp)/2
        syst = (systDo+systUp)/2
        tot = (totDo+totUp)/2

    # Check if the row already exists for bin and chan
    if len(df[(df['bin'] == bin) & (df['chan'] == chan)]) > 0:
        yields = GetYields(fname, bin, chan)
        df.loc[(df['bin'] == bin) & (df['chan'] == chan)] = [bin, chan, mu, stat, syst, tot, statUp, statDo, systUp, systDo, totUp, totDo, yields[0], yields[1], yields[2], yields[3], yields[4], yields[5], yields[6]]
    else:
        df.loc[len(df)] = [bin, chan, mu, stat, syst, tot, statUp, statDo, systUp, systDo, totUp, totDo, 0, 0, 0, 0, 0, 0, 0]
    writecsv(fname, df)

def LoadYields(fname, bin, chan, rootfile):
  f = ROOT.TFile.Open(rootfile)
  tt = f.Get('tt').Integral()
  tW = f.Get('tW').Integral()
  WJets = f.Get('WJets').Integral()
  QCD = f.Get('QCD').Integral()
  DY = f.Get('DY').Integral()
  totalbkg = tW + WJets + QCD + DY
  data = f.Get('data_obs').Integral()
  df = readcsv(fname)
  if len(df[(df['bin'] == bin) & (df['chan'] == chan)]) > 0:
    df[(df['bin'] == bin) & (df['chan'] == chan)][['tt', 'tW', 'WJets', 'QCD', 'DY', 'Total bkg', 'Data']] = [tt, tW, WJets, QCD, DY, totalbkg, data]
  else:
    df.loc[len(df)] = [bin, chan, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, tt, tW, WJets, QCD, DY, totalbkg, data]
  writecsv(fname, df)


import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--path', '-p', type=str, help='Path to csv file', default='data.csv')
parser.add_argument('--bin', '-b', type=str, help='bin name e.g. medianDRjj_m_4j2b')
parser.add_argument('--chan', '-c', type=str, help='channel e or m', default=None)
parser.add_argument('--rootfile', '-r', type=str, default=None)
parser.add_argument('--scan', '-s', type=str, default=None)

args = parser.parse_args()
path = args.path
b = args.bin
chan = args.chan
rootfile = args.rootfile
txtfile = args.scan

if chan is None: chan = b.split('_')[1]

if __name__ == '__main__':
    if rootfile is not None:
        LoadYields(path, b, chan, rootfile)
    if txtfile is not None:
        LoadFromScan(path, b, chan, txtfile)