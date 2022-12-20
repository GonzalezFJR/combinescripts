from ROOT import TFile
import re, os
from math import floor

class DatacardModifier:

  def SetPath(self, path):
    if not path.endswith('/'): path += '/'
    self.path = path

  def SetOutPath(self, outpath):
    if not outpath.endswith('/'): outpath += '/'
    self.outpath = outpath

  def SetDatacardName(self, name):
    self.datacname = name
 
  def SetOutSuf(self, o):
    self.outsuf = o

  def SetDatacOutName(self, name):
    self.datacoutname = name

  def open(self):
    if self.verbose: print('[DatacardModifier] Opening card: %s'%(self.path+self.datacname))
    self.f = open(self.path+self.datacname, 'r+')
    self.lines= self.f.readlines();
    self.f.close()

  def GetDataText(self):
    text = ''
    for line in self.lines: text += line
    return text

  def save(self):
    fout = open(self.outpath + self.datacoutname, 'w')
    fout.write(self.GetDataText())
    fout.close()
    if self.verbose: print('[DatacardModifier] Modified datacard: %s%s'%(self.outpath, self.datacoutname))
   
  def AddLine(self, line, nline=-1):
    if nline == -1: nline = len(self.lines)
    self.lines.insert(nline, line)

  def FindLineStart(self, string, isWord=False):
    nline = 0
    for line in self.lines:
      if isWord:
        if line.startswith(string+' '): return nline
      elif line.startswith(string):     return nline
      nline += 1
    return nline

  def RmLineStart(self, string, isWord=True):
    nlin = self.FindLineStart(string,True)
    if nlin < len(self.lines):
      self.lines.pop(nlin)

  def AddLineAfter(self, line, string):
    nline = self.FindLineStart(string)+1
    self.AddLine(line, nline)

  def ReplaceLabel(self, unclabel, newunclabel, exactword=True):
    for i in range(len(self.lines)):
      if not unclabel in self.lines[i]: continue
      if exactword: self.lines[i] = re.sub(r'\b({0})\b'.format(unclabel), newunclabel, self.lines[i])
      else: self.lines[i].replace(unclabel, newunclabel)

  def GetProcessesInCard(self):
    """ process DY ttW VV ttZ Nonprompt tW tt_test stop_test """
    for i in range(len(self.lines)):
      if not self.lines[i].startswith('process '): continue
      line = self.lines[i][len('process '):].replace('\n', '')
      while line.endswith(' '): line = line[:-1]
      while line.startswith(' '): line = line[1:]
      processes = line.split(' ')
      processes = [p for p in processes if p != '']
      return processes

  def GetUncInCard(self):
    ''' Uncertainties '''
    fromThisLine = False
    uncertainties = []
    for i in range(len(self.lines)):
      if self.lines[i].startswith('rate ') and not fromThisLine: 
        fromThisLine = True
        continue
      if not fromThisLine: continue
      if 'autoMCStats' in self.lines[i]: continue
      if self.lines[i].startswith('-') or self.lines[i].startswith('#'): continue
      if self.lines[i].replace(' ', '') == '': continue
      unc = self.lines[i].split(' ')[0]
      uncertainties.append(unc)
    return uncertainties

  def GetShapeUncInCard(self):
    fromThisLine = False
    uncertainties = []
    for i in range(len(self.lines)):
      if self.lines[i].startswith('rate ') and not fromThisLine: 
        fromThisLine = True
        continue
      if not fromThisLine: continue
      if 'autoMCStats' in self.lines[i]: continue
      if self.lines[i].startswith('-') or self.lines[i].startswith('#'): continue
      if self.lines[i].replace(' ', '') == '': continue
      unc = self.lines[i].split(' ')[0]
      line = self.lines[i]
      while ('  ' in line): line = line.replace('  ', ' ')
      shape = line.split(' ')[1]
      if shape != 'shape': continue
      uncertainties.append(unc)
    return uncertainties

  def GetUncProcessDic(self):
    fromThisLine = False
    uncDic = {}
    processes = self.GetProcessesInCard()
    for i in range(len(self.lines)):
      if self.lines[i].startswith('rate ') and not fromThisLine: 
        fromThisLine = True
        continue
      if not fromThisLine: continue
      if 'autoMCStats' in self.lines[i]: continue
      if self.lines[i].startswith('-') or self.lines[i].startswith('#'): continue
      if self.lines[i].replace(' ', '') == '': continue
      unc = self.lines[i].split(' ')[0]
      line = self.lines[i]
      while ('  ' in line): line = line.replace('  ', ' ')
      shape = line.split(' ')[1]
      if shape != 'shape': continue
      val = line.replace('\n', '').split(' ')[2:]
      pr = []
      for i in range(len(val)):
        if val[i] == '1': pr.append(processes[i])
      uncDic[unc] = pr
    return uncDic



  def GetProcessesMask(self, processes):
    allpr = self.GetProcessesInCard()
    if not isinstance(processes, list) and ',' in processes: processes = processes.replace(' ', '').split(',')
    elif not isinstance(processes, list): processes = [processes]
    mask = ''
    for pr in allpr:
      mask += ('- ' if not pr in processes else '1 ')
    return mask
    
  def SetUncOnlyToProcess(self, unclabel, process, pdf='shape'):
    strnums = self.GetProcessesMask(process)
    for i in range(len(self.lines)):
      if not self.lines[i].startswith(unclabel+' '): continue
      self.lines[i] = '%s %s %s\n'%(unclabel, pdf, strnums)
      return

  def UncForAllProcesses(self, label, unc=1.0, form='%1.3f'):
    line = '%s %s\n'%(label, (form%unc+' ')*self.nprocesses)
    return line

  def RenameSystInHistos(self, syst, newSyst):
    f = TFile.Open(self.rootfile, 'UPDATE')
    for pr in self.processes:
      for direc in ['Up', 'Down']:
        name    = "%s_%s%s"%(pr,    syst, direc)
        newname = "%s_%s%s"%(pr, newSyst, direc)
        if hasattr(f, name):
          if int(self.verbose) >= 2: print('Renaming histo: %s --> %s'%(name, newname))
          h = getattr(f, name).Clone(newname)
          h.Write()
    f.Close()

  def RemoveNegativeYields(self, processes, syst):
    if isinstance(processes, str):
      processes = [processes] if not ',' in processes else processes.replace(' ', '').split(',')
    if isinstance(syst, str):
      syst= [syst] if not ',' in syst else syst.replace(' ', '').split(',')
    f = TFile.Open(self.rootfile, 'UPDATE')
    for pr in processes:
      names = [pr]
      for s in syst:
        for direc in ['Up', 'Down']:
          name    = "%s_%s%s"%(pr, s, direc)
          names.append(name)
      for name in names:  
        if hasattr(f, name):
          h = f.Get(name)
          n = h.GetNbinsX()
          for i in range(0, n+1):
            c = h.GetBinContent(i)
            e = h.GetBinError(i)
            if c<=0: 
              h.SetBinContent(i, 1e-6)
              h.SetBinError(i, min(e,c/2))
            if   e<=0: h.SetBinError(i, c/2)
            elif e>3*c: h.SetBinError(i, c)
          h.Write()
    f.Close()

  def ReplacePathToFiles(self, oldpath, newpath):
    for i in range(len(self.lines)):
      if not oldpath in self.lines[i]: continue
      self.lines[i] = self.lines[i].replace(oldpath, newpath)

  def ScaleProcess(self, processes, syst, factor=1):
    if isinstance(processes, str):
      processes = [processes] if not ',' in processes else processes.replace(' ', '').split(',')
    if isinstance(syst, str):
      syst= [syst] if not ',' in syst else syst.replace(' ', '').split(',')
    f = TFile.Open(self.rootfile, 'UPDATE')
    for pr in processes:
      names = [pr]
      for s in syst:
        for direc in ['Up', 'Down']:
          name    = "%s_%s%s"%(pr, s, direc)
          names.append(name)
      for name in names:
        if hasattr(f, name):
          h = f.Get(name)
          if int(self.verbose) >= 2: print('Scaling %s by %1.2f'%(name, factor))
          h.Scale(factor)
          h.Write()
    f.Close()

  def AddHistos(self, histo, name = ''):
    if isinstance(histo, list):
      if isinstance(name, list):
        for h,n in zip(histo, name): self.AddHistos(h,n)
      else:
        for h in histo: self.AddHistos(h, '')
      return
    if name != '': histo.SetName(name)
    f = TFile.Open(self.rootfile, 'UPDATE')
    histo.Write()
    f.Close()

  def init(self):
    self.open()
    self.processes = []
    for line in self.lines:
      if line.startswith('rate '):
        self.nprocesses = len(filter(lambda x : x!= '', line[5:].split(' ')))
      if line.startswith('process ') and self.processes == []:
        self.processes = filter(lambda x : x!='', line[8:].split(' '))
      if line.startswith('shapes '):
        for w in filter(lambda x : x!='', line[7:].split(' ')):
          if w.endswith('.root'): 
            if self.outsuf != '': 
              origFile = w
              w = w[:-5] + '_' + self.outsuf + '.root'
              os.system('cp %s%s %s%s'%(self.path, origFile, self.path, w))
              if self.verbose: print('[DatacardModifier] Moving file to %s'%(self.path+w))
            self.rootfile = self.path+w if not w.startswith('/') else w
    
  def __init__(self, path, datacname, newname = '', outpath = None, verbose=False, outsuf=''):
    self.SetPath(path)
    self.SetDatacardName(datacname)
    self.SetOutPath(outpath if outpath!=None else path)
    self.SetDatacOutName(newname if newname != '' else datacname)
    self.verbose = verbose
    self.SetOutSuf(outsuf)
    self.init()
   

def GetDiffSystNom(hnom, up, down=None):
  nb = hnom.GetNbinsX()
  updif = [0]*(nb+1)
  dodif = [0]*(nb+1)
  for i in range(nb+1):
    n = hnom.GetBinContent(i)
    u = up.GetBinContent(i)
    # Add overflow
    if i == nb:
      n += hnom.GetBinContent(i+1)
      u += up  .GetBinContent(i+1)
    updif[i] = ((u-n)/n) if n != 0 else 0
    if down!=None:
      d = down.GetBinContent(i)
      if i == nb: d+=down.GetBinContent(i+1)
      dodif[i] = ((d-n)/n) if n != 0 else 0
    else: dodif[i] = -updif[i]
  return updif, dodif

def ApplyDifsToNom(hnom, difup, difdo, syst='', name='', doAbsolute=False):
  nb = hnom.GetNbinsX()
  if name!='': hnom.SetName(name)
  else       : name = hnom.GetName()
  hup = hnom.Clone(name+'_%sUp'%syst)
  hdo = hnom.Clone(name+'_%sDown'%syst)
  nbvar = len(difup)
  div = (nb)/(nbvar-1)
  for i in range(nb+1):
    val = hnom.GetBinContent(i)
    ibin = int(floor((i-1)/div)+1) 
    if doAbsolute:
      rup = val+difup[ibin]
      rdo = val+(difdo[ibin] if difdo[ibin] < 0 else (-difdo[ibin]))
    else:
      rup = val*( (1+difup[ibin]))# if difup[i] > 0 else (1-difup[i]))
      rdo = val*( (1+difdo[ibin]))# if difdo[i] < 0 else (1-difdo[i]))
    hup.SetBinContent(i, rup)
    hdo.SetBinContent(i, rdo)
  return hnom, hup, hdo
    
