# Emma & Matts Vector Pipeline

## Introduction

This is a scrappy pipeline for downloading and aligning publicly available
paired-end runs for a given target organism.


## Installation

```
git clone https://github.com/emmacollins01/WGS.git

cd ./WGS
bash Install.sh

conda activate emmawgs

# Then in install jodys pipeline

git clone https://github.com/pathogenseq/fastq2matrix.git
cd fastq2matrix
python setup.py install



```

## Running

Ensure the conda emmawgs environment is active

```
conda activate emmawgs
```

Next navigate inside the WGS directory and create a text ile containing the
run accession numbers of interest, like in the example samples.txt file. This
will be used to run the pipeline.

Example Command

```
python Real_Time_Running.py --ID Test --SamplesFile Samples.txt --ReferenceFile PlasmoDB-46_Pfalciparum3D7_Genome.fasta --DownloadThreads 4 --AnalysisThreads 20
```

## Parameter Breakdown

* **ID** = The ID associated with this given analysis run.
* **SamplesFile** = Path to a plain text file containing the run accession IDs of interest.
* **ReferenceFile** = Path to reference file to use in alignment.
* **DownloadThreads** = Number of processes assigned to download the runs of interest.
* **AnalysisThreads** = Number of processes assigned to analyse the runs of interest.


## To Do

* **Kraken**
* **Compression** - File specific for storage optimisation
* **Pause** - Enabling pausing + restart functionality
* **Enhanced Logging** - Enhance logging of files etc
* **File Organisation** - Enhance file organisation
