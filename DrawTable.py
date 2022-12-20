# Example
# python DrawTable.py data.csv -o /nfs/fanae/user/juanr/www/public/tt5TeV/ljets/15dec2022_noMVA/

import os, sys, argparse
import pandas as pd
import numpy as np

parser = argparse.ArgumentParser(description='Draw table')
parser.add_argument('path', help='Path to table')
parser.add_argument('-c', '--columns', dest='columns', default=None, help='Columns to draw')
parser.add_argument('-o', '--outpath', dest='outpath', default=None, help='Path to output')

args = parser.parse_args()
path = args.path
columns = args.columns
outpath = args.outpath

if columns is not None:
    columns = columns.replace('  ', '').split(',')
else:
    columns = ['bin', 'chan', 'mu', 'stat', 'syst', 'systUp', 'systDo', 'tot', 'tt', 'Total bkg', 'Data']

def DrawHTML(path, columns, outpath=None):
    df = pd.read_csv(path, sep=',')
    df = df[columns]
    if 'chan' in df.columns:
        # group by channels
        #df = df.groupby('chan')
        pass
    df = df.round(2)
    # Order first by channel and then by bin
    df = df.sort_values(by=['chan', 'bin'])
    df.to_html(path[:-4]+'.html', index=False)
    if outpath is not None:
        os.system('cp %s %s' % (path[:-4]+'.html', outpath))

if __name__ == '__main__':
    DrawHTML(path, columns, outpath=outpath)
