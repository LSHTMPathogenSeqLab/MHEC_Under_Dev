#!/bin/bash
conda env create -f Environment.yml
conda activate fastq2matrix
git clone https://github.com/pathogenseq/fastq2matrix.git
cd fastq2matrix
python setup.py install
