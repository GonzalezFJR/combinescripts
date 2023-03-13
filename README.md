# Setting up
You need to be in a CMSSW environment and you need to have combine installed. This repo has been tested whitin a CMSSW\_10\_2\_13 env.

## Combine cards

Execute:

    combineCards.py *.txt > datacard.txt

## Fit cross section

Edit the script to select the nuisances that you want to freeze, especially to split between systematics and statistics.

    source fitxsec.sh datacard.txt

## Impacts

Atention: remove the '.txt' at the end of the datacard name

    source estimateImpact.sh datacard

Or for Asimov

    estimateImpact_Asimov.sh datacard

Edit the file to change the estimate signal mu, for example.
To remove the stat unc from impacts, use:

    python rmStatUncFromImpJson.py # by default, impacts.json is taken

And plot again the impacts with

    plotImpacts.py -i impacts_nostat.json -o impacts

Or custom inputs with:

    python customImpacts.py -i impacts.json --asimov-input impacts_asimov.json --per-page 10 --onlyfirstpage -o impacts_custom -t rename.json

where 'rename.json' is a json dict with rename options for nuisances.

## Plotting

First, run fit diagnosis

    combine -M FitDiagnostics 02dec2022/datacard.txt --saveShapes --saveWithUncertainties -n "Histos" -m 0 --expectSignal 1

Then use the plotting script:

