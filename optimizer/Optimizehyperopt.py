from hyperopt import hp, tpe, fmin, Trials, STATUS_OK
from CollectorTest import Mainexe
from FeatureSelection import selectParas
import pandas as pd
import sys
import subprocess
import csv
import os
import json
from os import listdir
import atexit
from time import time, strftime, localtime
from datetime import timedelta
import math
import shutil
import platform



space = {}
FlagListFilename = None
collectorName = None
paramResFilename = None
collectorResFilename = "./all_results/default_results.csv"
gcParamResFilename = "./all_results/fid_optimizer_results.csv"
paramResFilename = None
improvResFilename = "./all_results/initial_optimizer_results.csv"
dir_path = os.path.dirname(os.path.realpath(__file__))
latencyResPath = "./jmeter_resource/jmeter_results-measurement-summary.json"
folder_path = dir_path + '/jmeter_resource/'
collectorTestFlagFile = "flags_base.txt"
paramTestFlagFile = "flags.txt"
finalFlagFilename = "./all_results/final_parameter_configuration.txt"
jmeterFlagFile="jmeterFlags.txt"

jmeterMem = None
jmeterCore = None
microMem = None
microCore= None
conc =None
testTime = None
warmUp = None
iterationOpt = None
tuneTime = None
iterationFid = None
jarPath = None

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ------------ to log execution time ---------------------------------

def secondsToStr(elapsed=None):
    if elapsed is None:
        return strftime("%Y-%m-%d %H:%M:%S", localtime())
    else:
        return str(timedelta(seconds=elapsed))


def logger(s, elapsed=None):
    line = "=" * 40
    print(line)
    print(secondsToStr(), '-', s)
    if elapsed:
        print("Elapsed time:", elapsed)
    print(line)
    print()


def endlog():
    end = time()
    elapsed = end - start
    logger("End Program", secondsToStr(elapsed))

def endTime():
    end = time()
    elapsed = end - start
    elapsed=secondsToStr(elapsed)
    return elapsed


# ---------------------------------------------

def ConstructSpace(df):
    for row in df.itertuples():

        if (row.Type == "int" or row.Type == "positive int" or row.Type == "double"):
            if (not (pd.isnull(row.Range))):
                split_range = str(row.Range).split("/")
            else:
                if (sys.maxsize > 2 ** 32):
                    split_range = str(row.OS_64).split("/")
                else:
                    split_range = str(row.OS_32).split("/")

            space[row.Name] = hp.uniform(row.Name, int(split_range[0]), int(split_range[1]))

        elif (row.Type == "bool"):
            space[row.Name] = hp.choice(row.Name, [True, False])

        elif (row.Type == "choice"):
            split_range = str(row.Range).split("_")
            choice_list = []
            for element in split_range:
                choice_list.append(element)
            space[row.Name] = hp.choice(row.Name, choice_list)


def WriteFlags(param):
    global FlagListFilename

    df = pd.read_csv(FlagListFilename)
    if (collectorName == "SerialGC"):
        with open(paramTestFlagFile, "w") as flag_file:
            flagName = "-XX:+UseSerialGC"
            flag_file.write(flagName + " ")
            flagName = "-Xms" + microMem
            flag_file.write(flagName + " ")
            flagName = "-Xmx" + microMem
            flag_file.write(flagName + " ")

            for row in df.itertuples():

                if (row.Type == "bool"):
                    if (param[row.Name]):
                        flagName = "-XX:+" + row.Name
                    else:
                        flagName = "-XX:-" + row.Name

                elif (row.Type == "int" or row.Type == "positive int" or row.Type == "choice"):
                    tempVal = int(float(param[row.Name]))
                    flagName = "-XX:" + row.Name + "=" + str(tempVal)

                flag_file.write(flagName + " ")

    elif (collectorName == "ParallelGC"):
        with open(paramTestFlagFile, "w") as flag_file:
            flagName = "-Xms" + microMem
            flag_file.write(flagName + " ")
            flagName = "-Xmx" + microMem
            flag_file.write(flagName + " ")
            flagName = "-XX:+UseParallelGC"
            flag_file.write(flagName + " ")
            flagName = "-XX:+UseParallelOldGC"
            flag_file.write(flagName + " ")

            for row in df.itertuples():

                if (row.Type == "bool"):
                    if (param[row.Name]):
                        flagName = "-XX:+" + row.Name
                    else:
                        flagName = "-XX:-" + row.Name

                elif (row.Type == "int" or row.Type == "positive int" or row.Type == "choice"):
                    tempVal = int(float(param[row.Name]))
                    flagName = "-XX:" + row.Name + "=" + str(tempVal)

                flag_file.write(flagName + " ")

    elif (collectorName == "CMS"):
        with open(paramTestFlagFile, "w") as flag_file:
            flagName = "-Xms" + microMem
            flag_file.write(flagName + " ")
            flagName = "-Xmx" + microMem
            flag_file.write(flagName + " ")
            flagName = "-XX:+UseConcMarkSweepGC"
            flag_file.write(flagName + " ")

            if (param['CMSPrecleaningEnabled'] == 0):
                param['CMSPrecleanSurvivors2'] = 0
                param['CMSPrecleanSurvivors1'] = 0
                param['CMSPrecleanRefLists2'] = 0
                param['CMSPrecleanRefLists1'] = 0

            for row in df.itertuples():

                if (row.Type == "bool"):
                    if (param[row.Name]):
                        flagName = "-XX:+" + row.Name
                    else:
                        flagName = "-XX:-" + row.Name

                elif (row.Type == "int" or row.Type == "positive int" or row.Type == "choice"):
                    tempVal = int(float(param[row.Name]))
                    flagName = "-XX:" + row.Name + "=" + str(tempVal)

                elif (row.Type == "double"):
                    tempVal = float((param[row.Name]))
                    flagName = "-XX:" + row.Name + "=" + str(tempVal)

                flag_file.write(flagName + " ")

    else:
        with open(paramTestFlagFile, "w") as flag_file:
            flagName = "-Xms" + microMem
            flag_file.write(flagName + " ")
            flagName = "-Xmx" + microMem
            flag_file.write(flagName + " ")
            flagName = "-XX:+UseG1GC"
            flag_file.write(flagName + " ")

            for row in df.itertuples():
                if (row.Type == "bool"):
                    if (param[row.Name]):
                        flagName = "-XX:+" + row.Name
                    else:
                        flagName = "-XX:-" + row.Name

                elif (row.Type == "int" or row.Type == "positive int" or row.Type == "choice"):
                    tempVal = int(float(param[row.Name]))
                    flagName = "-XX:" + row.Name + "=" + str(tempVal)

                elif (row.Type == "double"):
                    tempVal = float((param[row.Name]))
                    flagName = "-XX:" + row.Name + "=" + str(tempVal)

                flag_file.write(flagName + " ")


def WriteCsv(param):
    df = pd.read_csv(FlagListFilename)

    with open(paramResFilename, mode='a') as opt_file:
        writer = csv.writer(opt_file, delimiter=',')
        valuList = []

        for row in df.itertuples():
            valuList.append(int(float(param[row.Name])))

        with open(latencyResPath) as json_file:
            data = json.load(json_file)

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


def HyperparameterTuning(param):
    WriteFlags(param)
    subprocess.check_call(['./microwise.sh', microMem, str(microCore), paramTestFlagFile, jmeterMem,str(jmeterCore),str(conc),str(warmUp),str(testTime),jmeterFlagFile])
    WriteCsv(param)
    with open(latencyResPath) as json_file:
        latency_vals = json.load(json_file)
    for file_name in listdir(folder_path):
        if (file_name.endswith('.json') or file_name.endswith('.jtl')):
            os.remove(folder_path + file_name)

    print(latency_vals["HTTP Request"]["p99"])
    return {'loss': latency_vals["HTTP Request"]["p99"], 'status': STATUS_OK}


def findBestCollector():
    global collectorName, FlagListFilename, paramResFilename

    df = pd.read_csv(improvResFilename)
    bestCollector = df[df['Default_Dif'] == df['Default_Dif'].max()]
    collectorName = bestCollector['Name'].values[0]
    tempBestLatency = bestCollector['Curr_Latency'].values[0]

    FlagListFilename, paramResFilename = getFileNames(collectorName)

    for i in range(iterationFid):
        if(i == 0):
                trials = detectFeatureImportance(FlagListFilename, paramResFilename, i+1)
        else:
            elapsed=endTime()
            splitTime=elapsed.split(":")
            elapsedHours=splitTime[0]
            if(elapsedHours<=tuneTime):
                trials = detectFeatureImportance(FlagListFilename, paramResFilename, i + 1)
            else:
                break
        configLatency = min([t['result']['loss'] for t in trials.trials])
        if (tempBestLatency < configLatency):
            break
        else:
            if (i == 0):
                resList = []
                with open(gcParamResFilename, mode='w') as opt_file:
                    writer = csv.writer(opt_file, delimiter=',')
                    resList.append("Iteration")
                    resList.append("Name")
                    resList.append("Curr_Latency")
                    resList.append("GC_Latency")
                    resList.append("Default_Latency")
                    resList.append("Prev_Latency")
                    resList.append("GC_Dif")
                    resList.append("Default_Dif")
                    resList.append("Prev_Dif")
                    resList.append("GC_improv")
                    resList.append("Default_improv")
                    resList.append("Prev_improv")
                    writer.writerow(resList)

            writeGCResults(configLatency, i+1)
            tempBestLatency = configLatency



    # while isLatencyBetter:
    #     trials = detectFeatureImportance(FlagListFilename, paramResFilename, index)
    #     configLatency = min([t['result']['loss'] for t in trials.trials])
    #     if (tempBestLatency < configLatency):
    #         isLatencyBetter = False
    #     else:
    #         if (index == 1):
    #             resList = []
    #             with open(gcParamResFilename, mode='w') as opt_file:
    #                 writer = csv.writer(opt_file, delimiter=',')
    #                 resList.append("Iteration")
    #                 resList.append("Name")
    #                 resList.append("Curr_Latency")
    #                 resList.append("GC_Latency")
    #                 resList.append("Default_Latency")
    #                 resList.append("Prev_Latency")
    #                 resList.append("GC_Dif")
    #                 resList.append("Default_Dif")
    #                 resList.append("Prev_Dif")
    #                 resList.append("GC_improv")
    #                 resList.append("Default_improv")
    #                 resList.append("Prev_improv")
    #                 writer.writerow(resList)
    #
    #         writeGCResults(configLatency, index)
    #         tempBestLatency = configLatency
    #         if (index == iterationFid):
    #             break
    #     index += 1


def writeGCResults(configLatency, index):
    collector = pd.read_csv(collectorResFilename)

    collectorLatency = 0
    baselineLatency = 0

    for row in collector.itertuples():
        if (row.Name == collectorName):
            collectorLatency = row.Per_99
        elif (row.Name == "Default"):
            baselineLatency = row.Per_99

    if (index == 1):
        difRes = pd.read_csv(improvResFilename)
        prev_Latency = difRes[difRes['Name'] == collectorName]['Curr_Latency'].values[0]
    else:
        difGCRes = pd.read_csv(gcParamResFilename)
        prev_Latency = difGCRes[difGCRes['Iteration'] == (index - 1)]['Curr_Latency'].values[0]

    colectorDif = collectorLatency - configLatency
    baselineDif = baselineLatency - configLatency
    prev_Dif = prev_Latency - configLatency

    collectorRes = (colectorDif / collectorLatency) * 100
    baselineRes = (baselineDif / baselineLatency) * 100
    prev_improv = (prev_Dif / prev_Latency) * 100

    resgcList = []
    with open(gcParamResFilename, mode='a') as opt_file:
        writer = csv.writer(opt_file, delimiter=',')
        resgcList.append(index)
        resgcList.append(collectorName)
        resgcList.append(configLatency)
        resgcList.append(collectorLatency)
        resgcList.append(baselineLatency)
        resgcList.append(prev_Latency)
        resgcList.append(colectorDif)
        resgcList.append(baselineDif)
        resgcList.append(prev_Dif)
        resgcList.append(collectorRes)
        resgcList.append(baselineRes)
        resgcList.append(prev_improv)
        writer.writerow(resgcList)


def detectFeatureImportance(sentFlagListFilename, sentparamResFilename, index):
    global FlagListFilename, paramResFilename

    FlagListFilename = selectParas(sentFlagListFilename, sentparamResFilename, collectorName, index)
    paramResFilename = "./all_results/"+collectorName + "_Param_Res_" + str(index) + ".csv"

    df = pd.read_csv(FlagListFilename)
    ConstructSpace(df)

    with open(paramResFilename, mode='w') as opt_file:
        writer = csv.writer(opt_file, delimiter=',')
        flagList = df['Name'].tolist()
        flagList.append("Mean")
        flagList.append("Stddv")
        flagList.append("Median")
        flagList.append("Per_75")
        flagList.append("Per_90")
        flagList.append("Per_95")
        flagList.append("Per_99")
        flagList.append("Throughput")
        flagList.append("Error")
        writer.writerow(flagList)

    trials = Trials()
    best = fmin(fn=HyperparameterTuning,
                space=space,
                algo=tpe.suggest,
                max_evals=iterationOpt,
                trials=trials)
    print(best)
    return trials


def gcTest():
    flagList = []
    with open(collectorResFilename, mode='w') as opt_file:
        writer = csv.writer(opt_file, delimiter=',')
        flagList.append("Name")
        flagList.append("Mean")
        flagList.append("Stddv")
        flagList.append("Median")
        flagList.append("Per_75")
        flagList.append("Per_90")
        flagList.append("Per_95")
        flagList.append("Per_99")
        flagList.append("Throughput")
        flagList.append("Error")
        writer.writerow(flagList)

    gcList = ["ParallelGC", "SerialGC", "CMS", "G1", "Default"]

    for collector in gcList:
        with open(collectorTestFlagFile, "w") as flag_file:

            flagName = "-Xms" + microMem
            flag_file.write(flagName + " ")
            flagName = "-Xmx" + microMem
            flag_file.write(flagName + " ")

            if (collector == "SerialGC"):
                flagName = "-XX:+UseSerialGC"
                flag_file.write(flagName + " ")
                name = collector
            elif (collector == "ParallelGC"):
                flagName = "-XX:+UseParallelGC"
                flag_file.write(flagName + " ")
                flagName = "-XX:+UseParallelOldGC"
                flag_file.write(flagName + " ")
                name = collector
            elif (collector == "CMS"):
                flagName = "-XX:+UseConcMarkSweepGC"
                flag_file.write(flagName + " ")
                name = collector
            elif (collector == "G1"):
                flagName = "-XX:+UseG1GC"
                flag_file.write(flagName + " ")
                name = collector
            else:
                name = "Default"

        Mainexe(jmeterFlagFile,'./microwise.sh',name, microMem, microCore,jmeterCore,jmeterMem,conc,warmUp,testTime, collectorResFilename, folder_path, collectorTestFlagFile, latencyResPath)


def getImprovementPercentage(trials, collector):
    collectorResRows = pd.read_csv(collectorResFilename)

    collectorLatency = 0
    baselineLatency = 0

    for row in collectorResRows.itertuples():
        if (row.Name == collector):
            collectorLatency = row.Per_99
        elif (row.Name == "Default"):
            baselineLatency = row.Per_99

    bestConfigLatency = min([t['result']['loss'] for t in trials.trials])

    colectorDif = collectorLatency - bestConfigLatency
    baselineDif = baselineLatency - bestConfigLatency

    collectorRes = (colectorDif / collectorLatency) * 100
    baselineRes = (baselineDif / baselineLatency) * 100

    resList = []
    with open(improvResFilename, mode='a') as opt_file:
        writer = csv.writer(opt_file, delimiter=',')
        resList.append(collector)
        resList.append(bestConfigLatency)
        resList.append(collectorLatency)
        resList.append(baselineLatency)
        resList.append(colectorDif)
        resList.append(baselineDif)
        resList.append(collectorRes)
        resList.append(baselineRes)
        writer.writerow(resList)

def getFileNames(collector):
    if (collector == "SerialGC"):
        FlagListFilename = "JVMFlags_GC_Serial.csv"
        paramResFilename = "./all_results/Serial_Param_Res.csv"
    elif (collector == "ParallelGC"):
        FlagListFilename = "JVMFlags_GC_Para.csv"
        paramResFilename = "./all_results/Para_Param_Res.csv"
    elif (collector == "CMS"):
        FlagListFilename = "JVMFlags_GC_CMS.csv"
        paramResFilename = "./all_results/CMS_Param_Res.csv"
    else:
        FlagListFilename = "JVMFlags_GC_G1.csv"
        paramResFilename = "./all_results/G1_Param_Res.csv"

    return FlagListFilename,paramResFilename



def paraTest():
    global FlagListFilename, paramResFilename, collectorName

    resList = []
    with open(improvResFilename, mode='w') as opt_file:
        writer = csv.writer(opt_file, delimiter=',')
        resList.append("Name")
        resList.append("Curr_Latency")
        resList.append("GC_Latency")
        resList.append("Default_Latency")
        resList.append("GC_Dif")
        resList.append("Default_Dif")
        resList.append("GC_improv")
        resList.append("Default_improv")
        writer.writerow(resList)

    gcList = ["ParallelGC", "SerialGC", "CMS", "G1"]

    for collector in gcList:
        FlagListFilename, paramResFilename = getFileNames(collector)
        collectorName = collector

        df = pd.read_csv(FlagListFilename)
        ConstructSpace(df)

        with open(paramResFilename, mode='w') as opt_file:
            writer = csv.writer(opt_file, delimiter=',')
            flagList = df['Name'].tolist()
            flagList.append("Mean")
            flagList.append("Stddv")
            flagList.append("Median")
            flagList.append("Per_75")
            flagList.append("Per_90")
            flagList.append("Per_95")
            flagList.append("Per_99")
            flagList.append("Throughput")
            flagList.append("Error")
            writer.writerow(flagList)

        trials = Trials()
        best = fmin(fn=HyperparameterTuning,
                    space=space,
                    algo=tpe.suggest,
                    max_evals=iterationOpt,
                    trials=trials)
        print(best)
        getImprovementPercentage(trials, collector)

def writeFinalResult(nameCollector,default,latencyBest,improv,inFID):
    optimalLabelList = []
    optimalLabelList.append("bestGC")
    optimalLabelList.append("default_latency")
    optimalLabelList.append("optimized_latency")
    optimalLabelList.append("improvement")
    optimalLabelList.append("in_fid")

    optimalValList = []
    optimalValList.append(nameCollector)
    optimalValList.append(default)
    optimalValList.append(latencyBest)
    optimalValList.append(improv)
    optimalValList.append(inFID)


    with open("all_results/final_res.csv", mode='w') as opt_file:
        writer = csv.writer(opt_file, delimiter=',')
        writer.writerow(optimalLabelList)
        writer.writerow(optimalValList)



def writeBestParams():
    if (os.path.exists(gcParamResFilename)):
        df = pd.read_csv(gcParamResFilename)
        maxIteration = df[df['Iteration'] == df['Iteration'].max()]
        nameCollector = maxIteration['Name'].values[0]
        latencyBest = maxIteration['Curr_Latency'].values[0]
        default = maxIteration['Default_Latency'].values[0]
        improv = maxIteration['Default_improv'].values[0]
        iteration = maxIteration['Iteration'].values[0]

        writeFinalResult(nameCollector,default,latencyBest,improv,"yes")

        if (nameCollector == "SerialGC"):
            FlagFilename = "./all_results/Mod_JVMFlags_" + nameCollector + "_Para_" + str(iteration) + ".csv"
            paramFilename = "./all_results/"+nameCollector + "_Param_Res_" + str(iteration) + ".csv"
        elif (nameCollector == "ParallelGC"):
            FlagFilename = "./all_results/Mod_JVMFlags_" + nameCollector + "_Para_" + str(iteration) + ".csv"
            paramFilename = "./all_results/"+nameCollector + "_Param_Res_" + str(iteration) + ".csv"
        elif (nameCollector == "CMS"):
            FlagFilename = "./all_results/Mod_JVMFlags_" + nameCollector + "_Para_" + str(iteration) + ".csv"
            paramFilename = "./all_results/"+nameCollector + "_Param_Res_" + str(iteration) + ".csv"
        else:
            FlagFilename = "./all_results/Mod_JVMFlags_" + nameCollector + "_Para_" + str(iteration) + ".csv"
            paramFilename = "./all_results/"+nameCollector + "_Param_Res_" + str(iteration) + ".csv"

    else:

        df = pd.read_csv(improvResFilename)
        collectorBest = df[df['Default_Dif'] == df['Default_Dif'].max()]
        nameCollector = collectorBest['Name'].values[0]
        latencyBest = collectorBest['Curr_Latency'].values[0]
        default = collectorBest['Default_Latency'].values[0]
        improv = collectorBest['Default_improv'].values[0]
        FlagFilename, paramFilename = getFileNames(collectorName)

        writeFinalResult(nameCollector, default, latencyBest, improv,"no")


    df = pd.read_csv(paramFilename)
    bestParams = df[df['Per_99'] == latencyBest]
    bestParams = bestParams.drop(
        ['Mean', 'Stddv', 'Median', 'Per_90', 'Per_95', 'Per_99', 'Throughput', 'Per_75', 'Error'], axis=1)

    bestParams = bestParams.iloc[0].values.tolist()

    df = pd.read_csv(FlagFilename)
    listIndex = 0
    if (nameCollector == "SerialGC"):
        with open(finalFlagFilename, "w") as flag_file:
            flagName = "-XX:+UseSerialGC"
            flag_file.write(flagName + " ")

            for row in df.itertuples():
                if (row.Type == "bool"):
                    if (bestParams[listIndex]):
                        flagName = "-XX:+" + row.Name
                    else:
                        flagName = "-XX:-" + row.Name

                elif (row.Type == "int" or row.Type == "positive int" or row.Type == "choice"):
                    flagName = "-XX:" + row.Name + "=" + str(bestParams[listIndex])

                listIndex += 1
                flag_file.write(flagName + " ")

    elif (nameCollector == "ParallelGC"):
        with open(finalFlagFilename, "w") as flag_file:
            flagName = "-XX:+UseParallelGC"
            flag_file.write(flagName + " ")
            flagName = "-XX:+UseParallelOldGC"
            flag_file.write(flagName + " ")

            for row in df.itertuples():

                if (row.Type == "bool"):
                    if (bestParams[listIndex]):
                        flagName = "-XX:+" + row.Name
                    else:
                        flagName = "-XX:-" + row.Name

                elif (row.Type == "int" or row.Type == "positive int" or row.Type == "choice"):
                    flagName = "-XX:" + row.Name + "=" + str(bestParams[listIndex])

                listIndex += 1
                flag_file.write(flagName + " ")

    elif (nameCollector == "CMS"):
        with open(finalFlagFilename, "w") as flag_file:
            flagName = "-XX:+UseConcMarkSweepGC"
            flag_file.write(flagName + " ")

            for row in df.itertuples():

                if (row.Type == "bool"):
                    if (bestParams[listIndex]):
                        flagName = "-XX:+" + row.Name
                    else:
                        flagName = "-XX:-" + row.Name

                elif (row.Type == "int" or row.Type == "positive int" or row.Type == "choice"):
                    flagName = "-XX:" + row.Name + "=" + str(bestParams[listIndex])

                elif (row.Type == "double"):
                    flagName = "-XX:" + row.Name + "=" + str(bestParams[listIndex])

                listIndex += 1
                flag_file.write(flagName + " ")

    else:
        with open(finalFlagFilename, "w") as flag_file:
            flagName = "-XX:+UseG1GC"
            flag_file.write(flagName + " ")

            for row in df.itertuples():
                if (row.Type == "bool"):
                    if (bestParams[listIndex]):
                        flagName = "-XX:+" + row.Name
                    else:
                        flagName = "-XX:-" + row.Name

                elif (row.Type == "int" or row.Type == "positive int" or row.Type == "choice"):
                    flagName = "-XX:" + row.Name + "=" + str(bestParams[listIndex])

                elif (row.Type == "double"):
                    flagName = "-XX:" + row.Name + "=" + str(bestParams[listIndex])

                listIndex += 1
                flag_file.write(flagName + " ")

#validate configuration inputs
def validate(identifier, value):
    global conc, testTime, warmUp, iterationOpt, tuneTime, iterationFid, jarPath, jmeterMem, jmeterCore, microMem, microCore

    if(identifier!="jarPath"):

        if(identifier=="microMem"):
            if (value == ""):
                print(bcolors.FAIL +"ERROR: Memory allocation of Microservice container needs to be defined"+ bcolors.ENDC)
                return False
            elif (not value.isdigit()):
                print(bcolors.FAIL +"ERROR: The value needs to be a positive integer"+ bcolors.ENDC)
                return False
            elif(int(value) == 0):
                print(bcolors.FAIL +"ERROR: Memeory allocation of Microservice container cannot be 0"+ bcolors.ENDC)
                return False
            else:
                microMem = value+"m"
                return True

        elif (identifier == "jmeterMem"):
            if (value == ""):
                print(bcolors.FAIL +"ERROR: Memory allocation of JMeter container needs to be defined"+ bcolors.ENDC)
                return False
            elif (not value.isdigit()):
                print(bcolors.FAIL + "ERROR: The value needs to be a positive integer" + bcolors.ENDC)
                return False
            elif(int(value) == 0):
                print(bcolors.FAIL +"ERROR: Memeory allocation of JMeter container cannot be 0"+ bcolors.ENDC)
                return False
            else:
                jmeterMem = value+ "m"
                return True

        elif (identifier == "microCore"):
            if (value == ""):
                print(bcolors.FAIL +"ERROR: CPU allocation of Microservice container needs to be defined"+ bcolors.ENDC)
                return False
            elif (not value.isdigit()):
                print(bcolors.FAIL +"ERROR: The value needs to be a positive integer"+ bcolors.ENDC)
                return False
            elif(int(value) ==0):
                print(bcolors.FAIL +"ERROR: CPU allocation of Microservice container cannot be 0"+ bcolors.ENDC)
                return False
            else:
                microCore = int(value)
                return True

        elif (identifier == "jmetercore"):
            if (value == ""):
                print(bcolors.FAIL +"ERROR: CPU allocation of JMeter container needs to be defined"+ bcolors.ENDC)
                return False
            elif (not value.isdigit()):
                print(bcolors.FAIL + "ERROR: The value needs to be a positive integer" + bcolors.ENDC)
                return False
            elif(int(value) ==0):
                print(bcolors.FAIL +"ERROR: CPU allocation of JMeter container cannot be 0"+ bcolors.ENDC)
                return False
            else:
                jmeterCore = int(value)
                return True

        elif(identifier=="concurrentUsers"):
            if (value == ""):
                print(bcolors.FAIL +"ERROR: Number of conccurrent users need to be defined"+ bcolors.ENDC)
                return False
            elif (not value.isdigit()):
                print(bcolors.FAIL +"ERROR: The value needs to be a positive integer"+ bcolors.ENDC)
                return False
            elif(int(value) ==0):
                print(bcolors.FAIL +"ERROR: Number of concurrent users cannot be 0"+ bcolors.ENDC)
                return False
            elif(jmeterCore<=2 and int(value)>500 ):
                print(bcolors.FAIL +"ERROR: Invalid number of concurrent users"+ bcolors.ENDC)
            else:
                conc = int(value)
                return True

        elif(identifier == "testTime"):
            if (value == ""):
                print(bcolors.FAIL +"ERROR: Test time needs to be defined"+ bcolors.ENDC)
                return False
            elif (not value.isdigit()):
                print(bcolors.FAIL +"ERROR: The value needs to be a positive integer"+ bcolors.ENDC)
                return False
            elif(int(value) ==0):
                print(bcolors.FAIL +"ERROR: Test time cannot be 0"+ bcolors.ENDC)
                return False
            else:
                testTime = 60 * int(value)
                return True

        elif (identifier == "warmUp"):
            if (value == ""):
                print(bcolors.FAIL +"ERROR: Warm-up time needs to be defined"+ bcolors.ENDC)
                return False
            elif (not value.isdigit()):
                print(bcolors.FAIL +"ERROR: The value needs to be a positive integer"+ bcolors.ENDC)
                return False
            elif (int(value) == 0):
                print(bcolors.FAIL +"ERROR: Warm-up time cannot be 0"+ bcolors.ENDC)
                return False
            elif ((60 * int(value))>testTime):
                print(bcolors.FAIL +"ERROR: Warm-up time cannot be greater than test time"+ bcolors.ENDC)
                return False
            elif((60 * int(value)) > int(testTime/2)):
                print(bcolors.FAIL +"ERROR: Defined warm up time may cause inaccurate results. Please define a lower warmup time"+ bcolors.ENDC)
                return False
            else:
                warmUp = int(value)
                return True

        elif (identifier == "iterationsOpt"):
            if (value == ""):
                print(bcolors.FAIL +"ERROR: Number of optimization iterations need to be defined"+ bcolors.ENDC)
                return False
            elif (not value.isdigit()):
                print(bcolors.FAIL +"ERROR: The value needs to be a positive integer"+ bcolors.ENDC)
                return False
            elif (int(value) == 0):
                print(bcolors.FAIL +"ERROR: Number of optimization iterations cannot be 0"+ bcolors.ENDC)
                return False
            else:
                iterationOpt = int(value)
                return True

        elif (identifier == "tuneTime"):
            if (value == ""):
                print(bcolors.FAIL +"ERROR: Tuning time needs to be defined"+ bcolors.ENDC)
                return False
            elif (not value.isdigit()):
                print(bcolors.FAIL +"ERROR: The value needs to be a positive integer"+ bcolors.ENDC)
                return False
            elif (int(value) == 0):
                print(bcolors.FAIL +"ERROR: Tuning time cannot be 0"+ bcolors.ENDC)
                return False
            elif ((3600 * int(value))<testTime):
                print(bcolors.FAIL +"ERROR: Tuning time cannot be less than test time"+ bcolors.ENDC)
                return False
            elif(int(value) < timeEstimation()):
                print(bcolors.FAIL +"ERROR: Defined tuning time cannot be less than the estimated tuning time"+ bcolors.ENDC)
                return False
            elif (int(value) < timeEstimation()+2):
                print(bcolors.FAIL +"ERROR: Defined tuning time should be 2 hours or more ahead of estimated tuning time"+ bcolors.ENDC)
                return False
            else:
                tuneTime = 3600 * int(value)
                return True

        elif (identifier == "iterationFid"):
            if (value == ""):
                print(bcolors.FAIL +"ERROR: Number of feature importance detection iterations need to be defined"+ bcolors.ENDC)
                return False
            elif (not value.isdigit()):
                print(bcolors.FAIL +"ERROR: The value needs to be a positive integer"+ bcolors.ENDC)
                return False
            elif (int(value) == 0):
                print(bcolors.FAIL +"ERROR: Number of feature importance detection iterations cannot be 0"+ bcolors.ENDC)
                return False
            else:
                iterationFid = int(value)
                return True
    else:
        if (value == ""):
            print(bcolors.FAIL + "ERROR: Microservice jar path needs to be defined" + bcolors.ENDC)
            return False
        else:
            if(os.path.exists(value)):
                jarPath = value
                return True
            else:
                print(bcolors.FAIL +"ERROR: Microservice jar path does not exist"+ bcolors.ENDC)
                return False

#Estimate tuning time
def timeEstimation():
    estmateJmeterTime = (testTime * iterationOpt) * 5
    pauseTimes = (iterationOpt * 45) * 5
    estimateTime = math.ceil((estmateJmeterTime+pauseTimes)/3600)
    return estimateTime

#Accept configuration inputs
def setConfiguration():
    response = False
    print( bcolors.HEADER + "NOTE: When defining the Memory and CPU allocation please consider the host machine's CPU and Memory capacities"+bcolors.ENDC)
    print("\n"+"*************************************")
    while not response:
        jmeterMem = input("JMeter Memory (MB): ")
        response = validate("jmeterMem", jmeterMem)

    response = False
    print("\n""*************************************")
    while not response:
        jmetercore = input("JMeter Cores: ")
        response = validate("jmetercore", jmetercore)

    response = False
    print("\n"+"*************************************")
    while not response:
        microMem = input("Microservice Memory (MB): ")
        response = validate("microMem", microMem)

    response = False
    print("\n"+"*************************************")
    while not response:
        microCore = input("Microservice Cores: ")
        response = validate("microCore", microCore)

    response = False
    print("\n"+"*************************************")
    while not response:
        conc = input("Number of Concurrent Users: ")
        response = validate("concurrentUsers", conc)

    response = False
    print("\n"+"*************************************")
    while not response:
        testTime = input("Test Time (min): ")
        response = validate("testTime", testTime)

    response = False
    print("\n"+"*************************************")
    while not response:
        warmUp = input("Warm-up Time (min): ")
        response = validate("warmUp", warmUp)

    response = False
    print("\n"+"*************************************")
    print( bcolors.HEADER +"NOTE: We reccommend that you define number of optimization iterations as 10 or greater for better results"+bcolors.ENDC)
    while not response:
        iterationOpt = input("Optimization Iterations: ")
        response = validate("iterationsOpt", iterationOpt)

    response = False
    print("\n"+"*************************************")
    while not response:
        iterationFid = input("Number of Feature Importance Detection Iterations: ")
        response = validate("iterationFid", iterationFid)

    response = False
    print("\n"+"*************************************")
    print(bcolors.HEADER +"Please enter the absolute path of Microservice jar"+bcolors.ENDC)
    while not response:
        jarPath = input("Microservice jar Path: ")
        response = validate("jarPath", jarPath)

    response = False
    print("\n"+"*************************************")
    timeEstimate = timeEstimation()
    print(bcolors.HEADER +"NOTE: The estimated tuning time is around " + str(timeEstimate) + " hours. We reccommend that you define a duration 2 hours or more ahead of the estimation."+bcolors.ENDC)
    while not response:
        tuneTime = input("Max tuning time (hours): ")
        response = validate("tuneTime", tuneTime)

    writeConfigurations()


def writeDockerFile():
    with open("Dockerfile", "w") as flag_file:
        javaImport = "FROM openjdk:8-jdk-alpine"
        flag_file.write(javaImport + "\n")
        microservice="ADD  "+jarPath+" /usr/src/microwise/"
        flag_file.write(microservice + "\n")
        wordir="WORKDIR /usr/src/microwise"
        flag_file.write(wordir + "\n")
        port = "EXPOSE 8080"
        flag_file.write(port + "\n")
        jarFimeName= os.path.basename(jarPath)
        cmdexe= "CMD java $JAVA_OPTIONS -jar "+jarFimeName
        flag_file.write(cmdexe)

def writeJMeterFlags():
    with open(jmeterFlagFile, "w") as flag_file:
        flagName = "-Xms" + jmeterMem
        flag_file.write(flagName + " ")
        flagName = "-Xmx" + jmeterMem
        flag_file.write(flagName + " ")

def makeDir():
    dirPath = os.path.dirname(os.path.realpath(__file__))
    current_os = platform.system()
    baseName = "all_results"

    if current_os == 'Linux' or current_os == 'Darwin':
        filePath = dirPath + '/' + baseName


    elif current_os == 'Windows':
        filePath = dirPath + '\\' + baseName

    if os.path.exists(filePath):
        print("deleting existing directory")
        shutil.rmtree(filePath)

    if not os.path.exists(filePath):
        print("path doesn't exist. creating..")
        os.makedirs(filePath)

def writeConfigurations():
    configNameList = []
    configNameList.append("iteration_opt")
    configNameList.append("iteration_fid")
    configNameList.append("config_tune_time")
    configNameList.append("test_time")
    configNameList.append("conc")
    configNameList.append("warmup")
    configNameList.append("micro_mem")
    configNameList.append("micro_cores")

    configValList=[]
    configValList.append(iterationOpt)
    configValList.append(iterationFid)
    configValList.append(int(tuneTime/3600))
    configValList.append(int(testTime)/60)
    configValList.append(conc)
    configValList.append(warmUp)
    configValList.append(microMem)
    configValList.append(microCore)


    with open("all_results/configurations.csv", mode='w') as opt_file:
        writer = csv.writer(opt_file, delimiter=',')
        writer.writerow(configNameList)
        writer.writerow(configValList)


if __name__ == "__main__":
    print("\n")
    print("___ ___  ____   __  ____   ___   __    __  ____ _____   ___")
    print("|   |   ||    | /  ]|    \ /   \ |  |__|  ||    / ___/  /  _]")
    print("| _   _ | |  | /  / |  D  )     ||  |  |  | |  (   \_  /  [_ ")
    print("|  \_/  | |  |/  /  |    /|  O  ||  |  |  | |  |\__  ||    _]")
    print("|   |   | |  /   \_ |    \|     ||  `  '  | |  |/  \ ||   [_ ")
    print("|   |   | |  \     ||  .  \     | \      /  |  |\    ||     |")
    print("|___|___||____\____||__|\_|\___/   \_/\_/  |____|\___||_____|")
    print("\n")

    print("*****************************************************************************")
    print("Welcome to MicroWise!!!" + "\n")
    print("MicroWise is an Autonomic JVM Optimization Framework for Microservices")
    print("We strive to find you the best GC configuration for your Microservice")
    print("*****************************************************************************" + "\n")

    print("Insert Tuning Configurations..."+ "\n" )
    makeDir()
    setConfiguration()

    print("\n"+"Initiate Tuning....." + "\n")


    start = time()
    writeJMeterFlags()
    writeDockerFile()
    gcTest()
    paraTest()
    findBestCollector()
    writeBestParams()
    atexit.register(endlog)
    logger("Start Program")
    subprocess.check_call(['./dashboard.sh'])


