#!/bin/bash

echo "$(cat WGS_data/SRA_IDs_Culex)"

for line in $(cat WGS_data/SRA_IDs_Culex); do

fastq-dump --outdir fastq --split-e --skip-technical $line
echo "Downloaded $line"

bwa mem Reference_files_WGS/Culex_quinquefasciatus.CpipJ2.dna.toplevel.fa fastq/${line}_1.fastq fastq/${line}_2.fastq | samtools view -b - | samtools sort -o aligned_${line}.bam
samtools index aligned_${line}.bam

samtools flagstat aligned_${line}.bam > ${line}.txt

echo "Deleted fastq folder"

done
