from sklearn.ensemble import RandomForestRegressor
import pandas as pd



def DimentionReduction(FlagListFilename,paramResFilename,collectorName,iteration):
    dataframe = pd.read_csv(paramResFilename)
    df = dataframe.drop(['Mean','Stddv','Median', 'Per_90','Per_95', 'Throughput', 'Per_75', 'Error'], axis=1)

    labels = df.iloc[:, :-1]
    target = df.iloc[:, -1]

    original_flag_vals = pd.read_csv(FlagListFilename)

    X = labels.values
    Y = target.values

    model = RandomForestRegressor(n_estimators=10)
    model.fit(X, Y)

    priority_list = (model.feature_importances_).tolist()
    minList = sorted(priority_list)
    minParas = minList[:5]

    for para in minParas:
        for val in priority_list:
            if(val == para):
                rowIndex = priority_list.index(val)
                original_flag_vals.drop(original_flag_vals.index[rowIndex], inplace=True)
                break
        else:
            continue


    createFileNameString="./all_results/Mod_JVMFlags_"+collectorName+"_Para_"+str(iteration)+".csv"
    original_flag_vals.to_csv(createFileNameString, index=False, sep=',', encoding='utf-8')

    return createFileNameString

def selectParas(FlagListFilename,paramResFilename,collectorName,iteration):

    resultFlagFileName= DimentionReduction(FlagListFilename,paramResFilename,collectorName,iteration)
    return resultFlagFileName