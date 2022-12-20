from modules.DatacarModifier import DatacardModifier as DM

import os, sys, argparse

parser = argparse.ArgumentParser(description='Fix datacard for combine')
parser.add_argument('-i', '--input', dest='input', default=None, help='Input datacard')
parser.add_argument('-p', '--path', dest='path', default='', help='Path to datacard')
parser.add_argument('-v', '--verbose', dest='verbose', default=3, help='Verbosity level')
parser.add_argument('-s', '--sufix', dest='sufix', default='', help='Sufix for output datacard')


args = parser.parse_args()
path = args.path
datacard = args.input
verbose = args.verbose
sufix = args.sufix

if path == '' and '/' in datacard:
    path = datacard[:datacard.rfind('/')+1]
    datacard = datacard[datacard.rfind('/')+1:]


def RmWeightsDatacard(path, datacard, verbose=3, sufix=''):

  dm = DM(path, datacard, verbose=verbose, outsuf=sufix)
  processes = dm.GetProcessesInCard()
  syst = dm.GetShapeUncInCard()

  for proc in processes:
    dm.RemoveNegativeYields(proc, syst)


if __name__ == '__main__':

  if path != '' and datacard is None:
    for f in os.listdir(path):
        if f.endswith('.txt'):
            RmWeightsDatacard(path, f, verbose=verbose, sufix=sufix)
  else:
    RmWeightsDatacard(path, datacard, verbose=verbose, sufix=sufix)