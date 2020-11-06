import os
import sys
import time
import math
import argparse
import requests
import subprocess
from itertools import repeat
from multiprocessing import Pool


def ftp_Download(ENAEntry,DLParameters):

    try:
        # Work this outbased on 80% network speed divided by number of parallel
        ExpDownloadSpeedBytes = DLParameters.IndividualMaxBandwidth

        # Using Error Code to determine if download was or was not a success
        ErrorCode = 0

        # For Paired End Reads
        if DLParameters.Paired == True:
            ITER = ['1','2']
        else:
            ITER = ['1']

        for i in ITER:

            if DLParameters.Paired == True:
                FFpath='{0}_{1}.fastq.gz'.format(ENAEntry,i)
            else:
                FFpath='{0}.fastq.gz'.format(ENAEntry)

            outputlog = '{0}_{1}_wget_log.txt'.format(ENAEntry,i)

            dir1 = ENAEntry[:6]
            if len(ENAEntry)==9:
                uri='wget --user anonymous --output-file={3} ftp://ftp.sra.ebi.ac.uk/vol1/fastq/{0}/{1}/{4}'.format(dir1,ENAEntry,i,outputlog,FFpath)
            elif len(ENAEntry)==10:
                dir2 = "00"+ENAEntry[9:11]
                uri="wget --user anonymous --output-file={4} ftp://ftp.sra.ebi.ac.uk/vol1/fastq/{0}/{1}/{2}/{5}".format(dir1,dir2,ENAEntry,i,outputlog,FFpath)


            # Run the command which wont wait
            RunningCommand = subprocess.Popen(uri.split(' '))

            # Sleep 60 before checking log and starting 15 second checks
            # to ensure enough time for FTP Request
            time.sleep(60)

            # Download Speed Logging
            LowSpeedTime = 0
            LogChecking = True
            FilePresentCheck = False

            while LogChecking == True:

                # Read in Log File
                WgetLogCheck = open(outputlog,'r')
                LogLines = WgetLogCheck.readlines()


                # If First Check
                if FilePresentCheck == False:
                    FilePresentCheck = True
                    for LogLine in LogLines:
                        if 'No such file' in LogLine:
                            ErrorCode = 1
                            print(ENAEntry, 'No Such File')
                            return


                # If Download Complete
                if 'saved' in LogLines[-2]:
                    LogChecking = False
                    os.remove(outputlog)
                    if i == '2':
                        ErrorCode = 0
                        print(ENAEntry, 'Download Complete')
                        return

                # If Download In Progress
                else:
                    TempDownloadSpeeds = []
                    for TempLine in LogLines[-10:-1]:
                        LastLineSectionOfInterest = TempLine.split('%')[-1]
                        CleanLastLineSectionOfInterest = [pop for pop in LastLineSectionOfInterest.split(' ') if pop != '']

                        # Extract Download Speed
                        DownloadSpeed = CleanLastLineSectionOfInterest[0]
                        DownloadSpeedBytes = 0

                        # Convert to Bytes -- TIDY THIS UP LATER
                        if DownloadSpeed[-1].lower() == 'k':
                            DownloadSpeedBytes = float(DownloadSpeed[:-1]) * 1000

                        elif DownloadSpeed[-1].lower() == 'm':
                            DownloadSpeedBytes = float(DownloadSpeed[:-1]) * 1000 * 1000

                        elif DownloadSpeed[-1].lower() == 'g':
                            DownloadSpeedBytes = float(DownloadSpeed[:-1]) * 1000 * 1000 * 1000

                        TempDownloadSpeeds.append(DownloadSpeedBytes)


                    FinalDownloadSpeed = sum(TempDownloadSpeeds)/len(TempDownloadSpeeds)

                    if FinalDownloadSpeed < ExpDownloadSpeedBytes:
                        LowSpeedTime += 15

                        # Low speed experienced consecutively
                        if LowSpeedTime >= DLParameters.RestartTime:

                            # Kill command as download speed too slow
                            RunningCommand.kill()

                            # Remove Existing Log file
                            os.remove(outputlog)

                            # Reset Lower speed time
                            LowSpeedTime = 0

                            # Start running new wget command in attempt to improve download speed
                            NewUriList = ['wget','-c'] + uri.split(' ')[1:]
                            RunningCommand = subprocess.Popen(NewUriList)

                    # Reset the Speed Counter i.e. need consecutively lower
                    # speed so if faster speed achieved reset the clock.
                    else:
                        LowSpeedTime = 0

                    # Again sleep for 15 seconds before rechecking log
                    time.sleep(15)
                    LogChecking = True
    except:
        print(ENAEntry, 'Download Fail')
        return


################################################################################
################################################################################
################################################################################
################################################################################

parser = argparse.ArgumentParser()
parser.add_argument('--ID', help='', required=True)
parser.add_argument('--SamplesFile', help='', required=True)
parser.add_argument('--Paired', help='',default=True,type=bool)
parser.add_argument('--TotalMaxBandwidth', help='',default=50000000,type=int)
parser.add_argument('--RestartTime', help='',default=180,type=int)
parser.add_argument('--Threads', help='',default=1 ,type=int)
DownloadParameters = parser.parse_args()
DownloadParameters.IndividualMaxBandwidth = DownloadParameters.TotalMaxBandwidth/DownloadParameters.Threads

# Write all print statements to Log File
log_file = open("{}_Download.log".format(DownloadParameters.ID),"w")
sys.stdout = log_file


# Extracting ERR Codes List
CleanERRCodeList = []
ERRList = open(DownloadParameters.SamplesFile,'r')
for i in ERRList.readlines():
    ci = i.strip().replace('\n','')
    CleanERRCodeList.append(ci)


# Split download of ERR into parallel threads

FTPDownloadInput = list(zip(CleanERRCodeList,
                            [DownloadParameters]*len(CleanERRCodeList)))




if __name__ == '__main__':
    with Pool(int(DownloadParameters.Threads)) as p:
        p.starmap(ftp_Download,FTPDownloadInput)
