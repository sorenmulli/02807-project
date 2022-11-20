#!/bin/sh
#BSUB -q gpuv100
#BSUB -J sentiment
#BSUB -R select[gpu32gb]
#BSUB -gpu num=1
#BSUB -R rusage[mem=20GB]
#BSUB -n 1
#BSUB -W 2:00
#BSUB -o $HOME/joblogs/%J.out
#BSUB -e $HOME/joblogs/%J.err
#BSUB -u s183912@dtu.dk
#BSUB -N

conda deactivate
export PYTHONPATH=$PYTHONPATH:.
module load python3/3.9.11

python3 dkpol/sentiment.py

set -e
git add -A
git commit -m"Calculate sentiment scores for all tweets"
git pull
git push
