import subprocess
import os
import csv
import json
from os import listdir

def WriteCsv(collector,latencyResPath,collectorResFilename):

    with open(collectorResFilename, mode='a') as opt_file:
        writer = csv.writer(opt_file, delimiter=',')
        valuList=[]
        with open(latencyResPath) as json_file:
            data = json.load(json_file)
            valuList.append(collector)
            valuList.append(data["HTTP Request"]["mean"])
            valuList.append(data["HTTP Request"]["stddev"])
            valuList.append(data["HTTP Request"]["median"])
            valuList.append(data["HTTP Request"]["p75"])
            valuList.append(data["HTTP Request"]["p90"])
            valuList.append(data["HTTP Request"]["p95"])
            valuList.append(data["HTTP Request"]["p99"])
            valuList.append(data["HTTP Request"]["throughput"])
            valuList.append(data["HTTP Request"]["errors"])
            writer.writerow(valuList)
            print(data["HTTP Request"]["p99"])


def Mainexe(jmeterFlagFile,executableFile,collector,microMem, microCore,jmeterCore,jmeterMem,conc,warmUp,testTime,collectorResFilename,folder_path,collectorTestFlagFile,latencyResPath):
    subprocess.check_call([executableFile, microMem, str(microCore), collectorTestFlagFile, jmeterMem,str(jmeterCore),str(conc),str(warmUp),str(testTime),jmeterFlagFile])
    WriteCsv(collector,latencyResPath,collectorResFilename)
    for file_name in listdir(folder_path):
        if (file_name.endswith('.json') or file_name.endswith('.jtl')):
            os.remove(folder_path + file_name)


