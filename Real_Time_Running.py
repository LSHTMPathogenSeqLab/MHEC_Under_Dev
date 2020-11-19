'''
NEED TO ADD IN CHECK TO MAKE SURE THE FILE HAS FINISHED DOWNLOADING
'''


import subprocess
import glob
import multiprocessing
import collections
import os
import argparse
import time

def JodyFastqToVCF(RunID, Parameters):

	# Check to see if file is still downloading
	# as dont want to start the pipeline too
	# early

	F1P = os.path.getsize('./{}_1.fastq.gz'.format(RunID))
	F2P = os.path.getsize('./{}_2.fastq.gz'.format(RunID))
	time.sleep(20)
	if (os.path.getsize('./{}_1.fastq.gz'.format(RunID)) != F1P):
		return
	if (os.path.getsize('./{}_2.fastq.gz'.format(RunID)) != F2P):
		return

	# If File Pair Have Downloaded successfully run Jody Pipeline

	LogOne = 'echo {} >> ./logs/Accounted_Samples.log'.format(RunID)
	subprocess.call([LogOne],shell=True)


	ProcessLog = open("./{}_Process.log".format(RunID), "w")
	PipCommand = 'fastq2vcf.py all --read1 {0}_1.fastq.gz --read2 {0}_2.fastq.gz --ref {1} --prefix {0}'.format(RunID,
																											   Parameters.ReferenceFile)
	subprocess.call([PipCommand],stdout=ProcessLog,stderr=ProcessLog,shell=True)

	ProcessLog.close()


	return RunID

################################################################################
################################################################################
################################################################################




parser = argparse.ArgumentParser()
parser.add_argument('--ID', help='', required=True)
parser.add_argument('--SamplesFile', help='', required=True)
parser.add_argument('--ReferenceFile', help='', required=True)
parser.add_argument('--DownloadThreads', help='',type=int,default=1)
parser.add_argument('--AnalysisThreads', help='',type=int,default=1)
Parameters = parser.parse_args()


if not os.path.exists('logs'):
	os.makedirs('logs')


# Extract Samples
SampleList = []
SamplesFile = open(Parameters.SamplesFile,'r')
for i in SamplesFile.readlines():
	ci = i.strip().replace('\n','')
	SampleList.append(ci)

# Adjust analysis threads depending on sample list i.e. in scenario
# where less samples than threads
SamplesListLen = len(SampleList)
if SamplesListLen < Parameters.AnalysisThreads:
	Parameters.AnalysisThreads = SamplesListLen


# Create Log Files
AccountLog = open('./logs/Accounted_Samples.log','w')
AccountLog.close()
ProcessedLog = open('./logs/Processed_Samples.log','w')
ProcessedLog.close()


# Begin Download
DownloadCommand = 'python MultiSampleDownload.py --ID {0} --SamplesFile {1} --Threads {2}'.format(Parameters.ID,
																								  Parameters.SamplesFile,
																								  Parameters.DownloadThreads)

subprocess.Popen([DownloadCommand],shell=True)


# Begin Listener
TerminationBoolean = False
while TerminationBoolean == False:

	FastqIDList = [x.split('_')[0] for x in glob.glob('*.fastq.gz')]
	IDsofI = [item for item, count in collections.Counter(FastqIDList).items() if count == 2]

	AFSF = open('./logs/Accounted_Samples.log','r')
	ASFL = AFSF.readlines()
	if len(ASFL) != 0:
		AFS = [x.replace('\n','') for x in ASFL]
	else:
		AFS = []

	CFID = [ID for ID in IDsofI if ID not in AFS]

	if len(CFID) >= Parameters.AnalysisThreads:

		# Limit CFID to number of threads available to call function
		CFID = CFID[:Parameters.AnalysisThreads]

		MPI = list(zip(CFID,
					[Parameters]*Parameters.AnalysisThreads))

		with multiprocessing.Pool(processes=Parameters.AnalysisThreads) as p:
			CompleteIDs = p.starmap(JodyFastqToVCF,MPI)

			for CID in CompleteIDs:
				LogTwo = 'echo {} >> ./logs/Processed_Samples.log'.format(RunID)
				subprocess.call(LogTwo,shell=True)

	time.sleep(60)
	CompleteFilesCount = len(glob.glob('Error/*_Process.log') + glob.glob('Success/*_Process.log'))
	if CompleteFilesCount == len(SampleList):
		TerminationBoolean == True

	if os.path.isfile('STOP.log')==True:
		print('Pipeline Terminating')
		TerminationBoolean = True






##### Emma edit attempts ####
for Folder in ['Error','Success']:
	os.mkdir(Folder)

files = glob.glob("*_Process.log")

for i in files:
	file = open(i,'r')
	fileslines = file.readlines()
	if 'Failed' in ' '.join(fileslines):
		shutil.move(i, "./Error/")
	else:
		shutil.move(i, "./Success/")



#Trying to make pipeline stop when correct number of files
#Doesnt work - different number of files produced




onlyfiles_error = next(os.walk('./Error'))[2]
onlyfiles_success = next(os.walk('./Success'))[2]
file_count = onlyfiles_error + onlyfiles_success

correct_no

if (file_count == len(SampleList))
	print('Pipeline Terminating')
	TerminationBoolean = True

