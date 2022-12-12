import json
jsonfile = 'impacts.json'
outfile = 'impacts_nostat.json'

with open(jsonfile, 'r') as f:
  d = json.load(f)

params = []
newd = d.copy()
for i,par in enumerate(d['params']):
  if not par['name'].startswith('prop_bin'): 
    #print('Removing: ', par['name'])
    #newd['params'].remove(par)
    params.append(par)

newd['params'] = params
with open(outfile, 'w') as f:
  json.dump(newd, f, indent=2)
