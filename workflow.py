# Execute this one the datacards are ready!! That is: neg weights are fixed and datacards redone.
path = 'tt5TeVljets/02dec2022/'
outpath = 'tt5TeVljets/02dec2022/combine/'
webpath = '/nfs/fanae/user/juanr/www/public/tt5TeV/ljets/15dec2022/'
doComb = True
doEach = True
scans = True
impacts = False
impactsAsimov = False
fitdiag = False
plotSyst = False

import os,sys, argparse

argparser = argparse.ArgumentParser(description='Run combine')
argparser.add_argument('-p', '--path', help='Path to datacards', default=path)
argparser.add_argument('-o', '--outpath', help='Path to output', default=outpath)
argparser.add_argument('-w', '--webpath', help='Path to web', default=webpath)
argparser.add_argument('--pretend', help='Pretend to run', action='store_true')

args = argparser.parse_args()
path = args.path
outpath = args.outpath
webpath = args.webpath
pretend = args.pretend

### Functions
def run(command, pretend=False):
  print("Running comand: \n  > " + command)
  if pretend:
    print('...pretending...')
  else:
    os.system(command)

def CheckDir(path):
  if not path.endswith('/'):
    path += '/'
  if not os.path.exists(path):
    os.makedirs(path)
  return path

Fit = lambda card : 'sh fitxsec.sh ' + card
FitAsimov = lambda card : 'sh fitxsec_asimov.sh ' + card
Impacts = lambda card : 'sh estimateImpact.sh ' + card[:-4]
ImpactsAsimov = lambda card : 'sh estimateImpact_Asimov_signal1.sh ' + card[:-4]
FitDiag = lambda card : 'combine -M FitDiagnostics %s --saveShapes --saveWithUncertainties -n "Histos" -m 0 --expectSignal 1' % card
PlotSyst = lambda card, outpath, chan : 'python modules/PlotSyst.py %s -o %s -c %s' % (card, outpath, chan)

### Check paths
if not path.endswith('/'): path += '/'
outpath = CheckDir(outpath)
webpath = CheckDir(webpath)

current_dir = os.getcwd()
print('Running in directory: %s' % current_dir)
os.chdir(current_dir)

### Get the datacards
datanames = []
for f in os.listdir(path):
    if f.endswith('.txt') and f.startswith('dat_'):
        datanames.append(path+f)

if scans and doEach:
  os.system('rm data.csv')

if doEach:
 for card in datanames:
  chan = card.split('/')[-1][4:-4]

  # Fit xsec for each channel
  if scans:
    command = Fit(card)
    run(command, pretend)
    woutpath = CheckDir(webpath + 'scans/')
    for form in {'pdf', 'png'}:
      os.rename('scan.%s' % form, '%s%s_scan.%s' % (woutpath, chan, form))

    # Asimov fit
    command = FitAsimov(card)
    run(command, pretend)
    woutpath = CheckDir(webpath + 'scans/')
    for form in {'pdf', 'png'}:
      os.rename('scan.%s' % form, '%s%s_scan_asimov.%s' % (woutpath, chan, form))

    # Store in a table
    command = 'python modules/CraftJson.py -b %s -s outputfit.txt -r %s%s.root'%(chan, path, chan)
    run(command, pretend)

  # Impacts in each channel
  if impacts: 
    command = Impacts(card)
    run(command, pretend)
    woutpath = CheckDir(webpath + 'impacts/')
    os.rename('impacts.pdf', '%s%s_impacts.pdf' % (woutpath, chan))

  if impactsAsimov: 
    command = ImpactsAsimov(card)
    run(command, pretend)
    woutpath = CheckDir(webpath + 'impacts/')
    os.rename('impacts.pdf', '%s%s_impactsAsimov.pdf' % (woutpath, chan))

  # FitDiagnostic in each channel
  if fitdiag: 
    command = FitDiag(card)
    run(command, pretend)
    os.rename('fitDiagnosticsHistos.root', '%s%s_fitDiagnosticsHistos.root' % (outpath, chan))
    woutpath = CheckDir(webpath + 'plots/prefit/')
    command = "python DrawPlots.py %s -p %s -o %s -m prefit"%(outpath, path, woutpath)
    run(command, pretend)
    woutpath = CheckDir(webpath + 'plots/postfit/')
    command = "python DrawPlots.py %s -p %s -o %s -m postfit"%(outpath, path, woutpath)
    run(command, pretend)

  if plotSyst:
    woutpath = CheckDir(webpath + 'plots/syst/')
    command = PlotSyst(card, woutpath, chan)
    run(command, pretend)


### Combination
if doComb:
  chan = 'combination'

  # Combine cards

  datanames = []
  for f in os.listdir(path):
    if f.endswith('.txt') and f.startswith('dat_'):
        datanames.append(f)
  combcardName = 'datacard_comb.txt'
  command = 'combineCards.py ' + ' '.join(datanames) + ' > ' + combcardName
  os.chdir(path)
  run(command, pretend)
  card = path+combcardName
  os.chdir(current_dir)

  # Fit xsec 
  if scans:
    command = Fit(card)
    run(command, pretend)
    woutpath = CheckDir(webpath + 'scans/')
    for form in {'pdf', 'png'}:
      os.rename('scan.%s' % form, '%s%s_scan.%s' % (woutpath, chan, form))

    # Asimov fit
    command = FitAsimov(card)
    run(command, pretend)
    woutpath = CheckDir(webpath + 'scans/')
    for form in {'pdf', 'png'}:
      os.rename('scan.%s' % form, '%s%s_scan_asimov.%s' % (woutpath, chan, form))

    # Store in a table
    command = 'python modules/CraftJson.py -b %s -c l -s outputfit.txt'%(chan)
    run(command, pretend)

  # Impacts in each channel
  if impacts: 
    command = Impacts(card)
    run(command, pretend)
    woutpath = CheckDir(webpath + 'impacts/')
    os.rename('impacts.pdf', '%s%s_impacts.pdf' % (woutpath, chan))

  if impactsAsimov: 
    command = ImpactsAsimov(card)
    run(command, pretend)
    woutpath = CheckDir(webpath + 'impacts/')
    os.rename('impacts.pdf', '%s%s_impactsAsimov.pdf' % (woutpath, chan))


# Draw Table
if scans:
  command = "python DrawTable.py data.csv -o %s"%(webpath)
  run(command, pretend)
