# Execute this one the datacards are ready!! That is: neg weights are fixed and datacards redone.
dirname = '02mar23_JESsplit' # '10jan2023_newMVA15var'
path = 'tt5TeVljets/'+dirname+'/' 
outpath = 'tt5TeVljets/' + dirname + '/plots/'
webpath = '/nfs/fanae/user/juanr/www/public/tt5TeV/ljets/' + dirname + '/combine/'
doComb = True
doComb2l = False
doEach = False
scans = True
impacts = False
impactsAsimov = True
fitdiag = False
plotSyst = False
doMergeLeps = False

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

def RmStatFromImpactsJson(jsonname):
  command = 'python rmStatUncFromImpJson.py %s' % (jsonname)
  out = jsonname[:-5] + '_nostat.json'
  return out

def GetGoodImpacts(jsonname, asimovjsonname=None, outname=None):
  jsnoname = RmStatFromImpactsJson(jsonname)
  if asimovjsonname is not None:
    asimovjsonname = RmStatFromImpactsJson(asimovjsonname)
  else:
    asimovjsonname = jsonname
  if outname is None:
    outname = jsonname[:-5] + '_custom'
  command = "python customImpacts.py -i %s --asimov-input %s --per-page 15 --onlyfirstpage -o %s -t rename.json"%(jsonname, asimovjsonname, outname)
  return outname



### Check paths
if not path.endswith('/'): path += '/'
outpath = CheckDir(outpath)
webpath = CheckDir(webpath)

current_dir = os.getcwd()
print('Running in directory: %s' % current_dir)
os.chdir(current_dir)

### Get the datacards
datanames = []
datanamesem = []
for f in os.listdir(path):
    if f.endswith('.txt') and f.startswith('dat_') :
      if doMergeLeps:
        if '_l_' in f:
          datanames.append(path+f)
        else:
          datanamesem.append(path+f)
      else:
        if '_l_' in f:
          continue
        else:
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
    if f.endswith('.txt') and f.startswith('dat_') and not '_l_' in f:
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

# Comb with 2l
if doComb2l:
  datanames = []
  dilepCardName = 'datacard_counts_em_g2jets.txt'
  chan = 'combWithDilep'
  for f in os.listdir(path):
    if f.endswith('.txt') and f.startswith('dat_') and not '_l_' in f:
        datanames.append(f)
  if not os.path.isfile(path + '/' + dilepCardName):
    print('ERROR: datacard: %s does not exist'%dilepCardName)
    exit()
  combcardName = 'datacard_comb_withDilep.txt'
  command = 'combineCards.py ' + ' '.join(datanames) + ' ' + dilepCardName + ' > ' + combcardName
  os.chdir(path)
  run(command, pretend)
  card = path+combcardName
  os.chdir(current_dir)

  # Scans
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

  # Impacts
  if impacts:
    command = Impacts(card)
    run(command, pretend)
    woutpath = CheckDir(webpath + 'impacts/')
    os.rename('impacts.pdf', '%s%s_impacts.pdf' % (woutpath, chan))
    os.rename('impacts.json', '%s_impacts.json' % (chan))
    jsonName = '%s_impacts.json' % (chan)


  # Impacts Asimov
  if impactsAsimov:
    command = ImpactsAsimov(card)
    run(command, pretend)
    woutpath = CheckDir(webpath + 'impacts/')
    os.rename('impacts.pdf', '%s%s_impactsAsimov.pdf' % (woutpath, chan))
    jsonAsimName = '%s_impactsAsimov.json' % (chan)
    os.rename('impacts.json', jsonAsimName)
    customname = GetGoodImpacts(jsonAsimName)

# Draw Table
if scans:
  command = "python DrawTable.py data.csv -o %s"%(webpath)
  run(command, pretend)
