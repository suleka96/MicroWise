# Import required libraries
import dash
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import ntpath
import os

# get relative data folder
path = dir_path = os.path.dirname(os.path.realpath(__file__))
head, tail = ntpath.split(path)
tempPath = path.replace('dashboard', '')
dataPath = tempPath + "optimizer/all_results/"

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server


# Load data
configData = pd.read_csv(dataPath + "configurations.csv")
gcData = pd.read_csv(dataPath + "final_res.csv")
allImprovData = pd.read_csv(dataPath + "initial_optimizer_results.csv")

# data for left panel
iteration_opt = configData["iteration_opt"].values[0]
iteration_fid = configData["iteration_fid"].values[0]
config_tune_time = str(configData["config_tune_time"].values[0]) + " h"
test_time = str(configData["test_time"].values[0]) + " min"
conc = configData["conc"].values[0]
warmup = str(configData["warmup"].values[0]) + " min"

# data for boxes
micro_mem = str(configData["micro_mem"].values[0]) + " MB"
micro_cores = configData["micro_cores"].values[0]
gcName = gcData["bestGC"].values[0]
if (gcName == "SerialGC"):
    bestCollector = "Serial"
elif (gcName == "ParallelGC"):
    bestCollector = "Parallel"
bestLatency = gcData["optimized_latency"].values[0]
improv = str(int(gcData["improvement"].values[0])) + "%"
defaultLatency = gcData["default_latency"].values[0]
fidIteration = gcData["iteration"].values[0]

# data for graphs
inFID = gcData["in_fid"].values[0]
gcList = ["Default", "Parallel", "Serial", "CMS", "G1", ]
bestLatencyList = []
bestLatencyList.append(defaultLatency)
for row in allImprovData.itertuples():
    if (inFID == "yes" and row.Name == gcName):
        bestLatencyList.append(bestLatency)
    else:
        bestLatencyList.append(row.Curr_Latency)
improvList = ["Parallel", "Serial", "CMS", "G1", ]
improvPercentage = []
for row in allImprovData.itertuples():
    if (inFID == "yes" and row.Name == gcName):
        improvPercentage.append(int(gcData["improvement"].values[0]))
    else:
        improvPercentage.append(int(row.Default_improv))

# 99% latency values of best GC
if (gcName == "SerialGC"):
    if(inFID == "yes"):
        FlagFilename = gcName + "_Param_Res_" + str(fidIteration) + ".csv"
        bestgcvals = pd.read_csv(dataPath + FlagFilename)
    else:
        bestgcvals = pd.read_csv(dataPath + "Serial_Param_Res.csv")
elif (gcName == "ParallelGC"):
    if (inFID == "yes"):
        FlagFilename = gcName + "_Param_Res_" + str(fidIteration) + ".csv"
        bestgcvals = pd.read_csv(dataPath + FlagFilename)
    else:
        bestgcvals = pd.read_csv(dataPath + "Para_Param_Res.csv")
elif (gcName == "CMS"):
    if (inFID == "yes"):
        FlagFilename = gcName + "_Param_Res_" + str(fidIteration) + ".csv"
        bestgcvals = pd.read_csv(dataPath + FlagFilename)
    else:
        bestgcvals = pd.read_csv(dataPath + "CMS_Param_Res.csv")
else:
    if (inFID == "yes"):
        FlagFilename = gcName + "_Param_Res_" + str(fidIteration) + ".csv"
        bestgcvals = pd.read_csv(dataPath + FlagFilename)
    else:
        bestgcvals = pd.read_csv(dataPath + "G1_Param_Res.csv")

latency_bestGC_y = bestgcvals['Per_99'].values
latency_X = bestgcvals.index.values

# 99% latency values of all Phases
gcVals_serial = pd.read_csv(dataPath + "Serial_Param_Res.csv")
latency_serial_y = gcVals_serial['Per_99'].values
gcVals_para = pd.read_csv(dataPath + "Para_Param_Res.csv")
latency_para_y = gcVals_para['Per_99'].values
gcVals_cms = pd.read_csv(dataPath + "CMS_Param_Res.csv")
latency_cms_y = gcVals_cms['Per_99'].values
gcVals_g1 = pd.read_csv(dataPath + "G1_Param_Res.csv")
latency_g1_y = gcVals_g1['Per_99'].values
latency_X = gcVals_g1.index.values



allfidres = []
if (inFID == "yes"):
    FlagFilename = gcName + "_Param_Res_" + str(fidIteration) + ".csv"
    fidVals = pd.read_csv(dataPath + FlagFilename)
    latency_y = fidVals['Per_99'].values
    if (gcName == "SerialGC"):
        latency_serial_y = latency_y
    elif (gcName == "ParallelGC"):
        latency_para_y = latency_y
    elif (gcName == "CMS"):
        latency_cms_y = latency_y
    else:
        latency_g1_y = latency_y


#convergence graph
convG1 = []
convPara=[]
convCMS =[]
convSerial=[]

index = 0
for val in latency_g1_y:
    if(index == 0):
        convG1.append(val)
        tempVal = val
    else:
        if(tempVal>val):
            convG1.append(val)
            tempVal = val
        else:
            convG1.append(tempVal)
    index += 1

index = 0
for val in latency_para_y:
    if(index == 0):
        convPara.append(val)
        tempVal = val
    else:
        if(tempVal>val):
            convPara.append(val)
            tempVal = val
        else:
            convPara.append(tempVal)
    index += 1

index = 0
for val in latency_cms_y:
    if(index == 0):
        convCMS.append(val)
        tempVal = val
    else:
        if(tempVal>val):
            convCMS.append(val)
            tempVal = val
        else:
            convCMS.append(tempVal)
    index += 1

index = 0
for val in latency_serial_y:
    if(index == 0):
        convSerial.append(val)
        tempVal = val
    else:
        if(tempVal>val):
            convSerial.append(val)
            tempVal = val
        else:
            convSerial.append(tempVal)
    index += 1


# Create global chart template
mapbox_access_token = "pk.eyJ1IjoiamFja2x1byIsImEiOiJjajNlcnh3MzEwMHZtMzNueGw3NWw5ZXF5In0.fk8k06T96Ml9CLGgKmk81w"

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(lon=-78.05, lat=42.54),
        zoom=7,
    ),
)

# Create app layout
app.layout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("dash-logo_1.png"),
                            id="microwise-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "MicroWise",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Optimization Overview", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),

            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            "Optimization Configurations",
                            className="sub-menu",
                        ),
                        html.H6(
                            iteration_opt,
                            className="val-item"
                        ),
                        html.P(
                            "Number of Optimization Iterations",
                            className="val-title"
                        ),
                        html.H6(
                            iteration_fid,
                            className="val-item"
                        ),
                        html.P(
                            "Number of Feature Importance Detection Iterations",
                            className="val-title"
                        ),
                        html.H6(
                            config_tune_time,
                            className="val-item"
                        ),
                        html.P(
                            "Tuning Time",
                            className="val-title"
                        ),
                        html.H6(
                            test_time,
                            className="val-item"
                        ),
                        html.P(
                            "Test Time",
                            className="val-title"
                        ),
                        html.H6(
                            conc,
                            className="val-item"
                        ),
                        html.P(
                            "Number of Concurrent Users",
                            className="val-title"
                        ),
                        html.H6(
                            warmup,
                            className="val-item"
                        ),
                        html.P(
                            "Warm-up Time",
                            className="val-title"
                        ),

                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),

                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.H6(bestCollector), html.P("Selected Garbage Collector")],
                                    id="gc",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(defaultLatency), html.P("Default Latency")],
                                    id="default-lat",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(bestLatency), html.P("Optimized Latency")],
                                    id="best-lat",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(improv), html.P("Improvement percentage")],
                                    id="improv",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(micro_mem), html.P("Microservice Memory")],
                                    id="mem",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(micro_cores), html.P("Microservice CPU cores")],
                                    id="cores",
                                    className="mini_container",
                                ),

                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        html.Div(
                            [dcc.Graph(
                                id='example',
                                figure={
                                    'data': [
                                        {'x': gcList, 'y': bestLatencyList, 'type': 'bar', 'name': 'Cars'}
                                    ],
                                    'layout': {
                                        'title': 'Best 99% Latency Value Comparison'
                                    }
                                }
                            )],
                            id="Bar1tGraphContainer",
                            className="pretty_container",
                        )
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(
                        id='example2',
                        figure={
                            'data': [
                                {'x': latency_X, 'y': latency_bestGC_y, 'type': 'line', 'name': 'Best GC'}
                            ],
                            'layout': {
                                'title': 'Explored 99% Latency Values of Best performing GC'
                            }
                        }
                    )],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(
                        id='aggregate_graph',
                        figure={
                            'data': [
                                {'x': latency_X, 'y': latency_para_y, 'type': 'scatter', 'mode': 'lines',
                                 'name': 'Parallel',
                                 'line': {"color": "#F9ADA0"}},
                                {'x': latency_X, 'y': latency_g1_y, 'type': 'scatter', 'mode': 'lines', 'name': 'G1',
                                 'line': {"color": "#849E68"}},
                                {'x': latency_X, 'y': latency_serial_y, 'type': 'scatter', 'mode': 'lines',
                                 'name': 'Serial',
                                 'line': {"color": "#59C3C3"}},
                                {'x': latency_X, 'y': latency_cms_y, 'type': 'scatter', 'mode': 'lines', 'name': 'CMS',
                                 'line': {"color": "#92d8d8"}}
                            ],
                            'layout': {
                                'title': 'Comparison of Explored 99% Latency Values'
                            }
                        }
                    )],
                    className="pretty_container five columns",
                )
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(

                    [dcc.Graph(
                        id='example_2',
                        figure={
                            'data': [
                                {'x': improvList, 'y': improvPercentage, 'type': 'bar', 'name': 'Cars'}
                            ],
                            'layout': {
                                'title': 'Improvement Percentage Comparison'
                            }
                        }
                    )],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(
                        id='aggregate_graph_1',
                        figure={
                            'data': [
                                {'x': latency_X, 'y': convPara, 'type': 'scatter', 'mode': 'lines',
                                 'name': 'Parallel',
                                 'line': {"color": "#F9ADA0"}},
                                {'x': latency_X, 'y': convG1, 'type': 'scatter', 'mode': 'lines', 'name': 'G1',
                                 'line': {"color": "#849E68"}},
                                {'x': latency_X, 'y': convSerial, 'type': 'scatter', 'mode': 'lines',
                                 'name': 'Serial',
                                 'line': {"color": "#59C3C3"}},
                                {'x': latency_X, 'y': convCMS, 'type': 'scatter', 'mode': 'lines', 'name': 'CMS',
                                 'line': {"color": "#92d8d8"}}
                            ],
                            'layout': {
                                'title': 'Convergence graph of 99% Latency Values'
                            }
                        }
                    )],
                    className="pretty_container five columns",
                )
            ],
            className="row flex-display",
        ),

    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)

# Main
if __name__ == "__main__":
    app.run_server(debug=True)
