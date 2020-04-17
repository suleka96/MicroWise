# Import required libraries
import pickle
import copy
import pathlib
import dash
import math
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import ntpath
import os

import threading

# Multi-dropdown options
from controls import COUNTIES, WELL_STATUSES, WELL_TYPES, WELL_COLORS

# get relative data folder
path = dir_path = os.path.dirname(os.path.realpath(__file__))
head, tail = ntpath.split(path)
tempPath = path.replace('dashboard', '')
dataPath = tempPath + "optimizer/all_results/"
# data_path = tempPath.joinpath("optimizer/all_results").resolve()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# Create controls
county_options = [
    {"label": str(COUNTIES[county]), "value": str(county)} for county in COUNTIES
]

well_status_options = [
    {"label": str(WELL_STATUSES[well_status]), "value": str(well_status)}
    for well_status in WELL_STATUSES
]

well_type_options = [
    {"label": str(WELL_TYPES[well_type]), "value": str(well_type)}
    for well_type in WELL_TYPES
]

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

#99% latency values of best GC
if (gcName == "SerialGC"):
    bestgcvals = pd.read_csv(dataPath + "Serial_Param_Res.csv")
elif (gcName == "ParallelGC"):
    bestgcvals = pd.read_csv(dataPath + "Para_Param_Res.csv")
elif (gcName == "CMS"):
    bestgcvals = pd.read_csv(dataPath + "CMS_Param_Res.csv")
else:
    bestgcvals = pd.read_csv(dataPath + "G1_Param_Res.csv")

latency_bestGC_y = bestgcvals['Per_99'].values
latency_X = bestgcvals.index.values

#99% latency values of all Phases
gcVals_serial = pd.read_csv(dataPath + "Serial_Param_Res.csv")
latency_serial_y = gcVals_serial['Per_99'].values
gcVals_para = pd.read_csv(dataPath + "Para_Param_Res.csv")
latency_para_y = gcVals_para['Per_99'].values
gcVals_cms = pd.read_csv(dataPath + "CMS_Param_Res.csv")
latency_cms_y = gcVals_cms['Per_99'].values
gcVals_g1 = pd.read_csv(dataPath + "G1_Param_Res.csv")
latency_g1_y = gcVals_g1['Per_99'].values
latency_X = gcVals_g1.index.values

allfidres=[]
if(inFID == "yes"):
    fidData = pd.read_csv(dataPath + "fid_optimizer_results.csv")
    dataFrameLength=(len(fidData.index)-1)
    FlagFilename = "Mod_JVMFlags_" + gcName + "_Para_" + str(dataFrameLength) + ".csv"
    fidVals = pd.read_csv(dataPath + FlagFilename)
    latency_y = fidVals['Per_99'].values
    if (gcName == "SerialGC"):
        latency_serial_y=latency_y
    elif (gcName == "ParallelGC"):
        latency_para_y = latency_y
    elif (gcName == "CMS"):
        latency_cms_y = latency_y
    else:
        latency_g1_y = latency_y











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
                                {'x': latency_X, 'y': latency_para_y, 'type': 'scatter', 'mode': 'lines', 'name': 'Parallel',
                                 'line': {'shape': "spline", "smoothing": "1", "color": "#F9ADA0"}},
                                {'x': latency_X, 'y': latency_g1_y, 'type': 'scatter', 'mode': 'lines', 'name': 'G1',
                                 'line': {'shape': "spline", "smoothing": "1", "color": "#849E68"}},
                                {'x': latency_X, 'y': latency_serial_y, 'type': 'scatter', 'mode': 'lines', 'name': 'Serial',
                                 'line': {'shape': "spline", "smoothing": "1", "color": "#59C3C3"}},
                                {'x': latency_X, 'y': latency_cms_y, 'type': 'scatter', 'mode': 'lines', 'name': 'CMS',
                                 'line': {'shape': "spline", "smoothing": "1", "color": "#92d8d8"}}
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

    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)

#
# # Helper functions
# def human_format(num):
#     if num == 0:
#         return "0"
#
#     magnitude = int(math.log(num, 1000))
#     mantissa = str(int(num / (1000 ** magnitude)))
#     return mantissa + ["", "K", "M", "G", "T", "P"][magnitude]
#
#
# def filter_dataframe(df, well_statuses, well_types):
#     dff = df[
#         df["Well_Status"].isin(well_statuses)
#         & df["Well_Type"].isin(well_types)
#         & (df["Date_Well_Completed"] > dt.datetime( 1, 1))
#         & (df["Date_Well_Completed"] < dt.datetime( 1, 1))
#     ]
#     return dff
#
#
# def produce_individual(api_well_num):
#     try:
#         points[api_well_num]
#     except:
#         return None, None, None, None
#
#     index = list(
#         range(min(points[api_well_num].keys()), max(points[api_well_num].keys()) + 1)
#     )
#     gas = []
#     oil = []
#     water = []
#
#     for year in index:
#         try:
#             gas.append(points[api_well_num][year]["Gas Produced, MCF"])
#         except:
#             gas.append(0)
#         try:
#             oil.append(points[api_well_num][year]["Oil Produced, bbl"])
#         except:
#             oil.append(0)
#         try:
#             water.append(points[api_well_num][year]["Water Produced, bbl"])
#         except:
#             water.append(0)
#
#     return index, gas, oil, water
#
#
# def produce_aggregate(selected):
#
#     index = list(range(max(1985), 2016))
#     gas = []
#     oil = []
#     water = []
#
#     for year in index:
#         count_gas = 0
#         count_oil = 0
#         count_water = 0
#         for api_well_num in selected:
#             try:
#                 count_gas += points[api_well_num][year]["Gas Produced, MCF"]
#             except:
#                 pass
#             try:
#                 count_oil += points[api_well_num][year]["Oil Produced, bbl"]
#             except:
#                 pass
#             try:
#                 count_water += points[api_well_num][year]["Water Produced, bbl"]
#             except:
#                 pass
#         gas.append(count_gas)
#         oil.append(count_oil)
#         water.append(count_water)
#
#     return index, gas, oil, water
#
#
# # Create callbacks
# app.clientside_callback(
#     ClientsideFunction(namespace="clientside", function_name="resize"),
#     Output("output-clientside", "children"),
#     [Input("count_graph", "figure")],
# )
#
#
# @app.callback(
#     Output("aggregate_data", "data"),
#     [
#         Input("well_statuses", "value"),
#         Input("well_types", "value")
#     ],
# )
# def update_production_text(well_statuses, well_types, year_slider):
#
#     dff = filter_dataframe(df, well_statuses, well_types, year_slider)
#     selected = dff["API_WellNo"].values
#     index, gas, oil, water = produce_aggregate(selected, year_slider)
#     return [human_format(sum(gas)), human_format(sum(oil)), human_format(sum(water))]
#
#
# # Radio -> multi
# @app.callback(
#     Output("well_statuses", "value"), [Input("well_status_selector", "value")]
# )
# def display_status(selector):
#     if selector == "all":
#         return list(WELL_STATUSES.keys())
#     elif selector == "active":
#         return ["AC"]
#     return []
#
#
# # Radio -> multi
# @app.callback(Output("well_types", "value"), [Input("well_type_selector", "value")])
# def display_type(selector):
#     if selector == "all":
#         return list(WELL_TYPES.keys())
#     elif selector == "productive":
#         return ["GD", "GE", "GW", "IG", "IW", "OD", "OE", "OW"]
#     return []
#
#
# # Slider -> count graph
# @app.callback(Output("year_slider", "value"), [Input("count_graph", "selectedData")])
# def update_year_slider(count_graph_selected):
#
#     if count_graph_selected is None:
#         return [1990, 2010]
#
#     nums = [int(point["pointNumber"]) for point in count_graph_selected["points"]]
#     return [min(nums) + 1960, max(nums) + 1961]


# Selectors -> well text
# @app.callback(
#     Output("well_text", "children"),
#     [
#         Input("well_statuses", "value"),
#         Input("well_types", "value"),
#         Input("year_slider", "value"),
#     ],
# )
# def update_well_text(well_statuses, well_types, year_slider):
#
#     dff = filter_dataframe(df, well_statuses, well_types, year_slider)
#     return dff.shape[0]


# @app.callback(
#     [
#         Output("gasText", "children"),
#         Output("oilText", "children"),
#         Output("waterText", "children"),
#     ],
#     [Input("aggregate_data", "data")],
# )
# def update_text(data):
#     return data[0] + " mcf", data[1] + " bbl", data[2] + " bbl"
#
#
# # Selectors -> main graph
# @app.callback(
#     Output("main_graph", "figure"),
#     [
#         Input("well_statuses", "value"),
#         Input("well_types", "value")
#     ],
#     [State("lock_selector", "value"), State("main_graph", "relayoutData")],
# )
# def make_main_figure(
#     well_statuses, well_types, selector, main_graph_layout
# ):
#
#     dff = filter_dataframe(df, well_statuses, well_types)
#
#     traces = []
#     for well_type, dfff in dff.groupby("Well_Type"):
#         trace = dict(
#             type="scattermapbox",
#             lon=dfff["Surface_Longitude"],
#             lat=dfff["Surface_latitude"],
#             text=dfff["Well_Name"],
#             customdata=dfff["API_WellNo"],
#             name=WELL_TYPES[well_type],
#             marker=dict(size=4, opacity=0.6),
#         )
#         traces.append(trace)
#
#     # relayoutData is None by default, and {'autosize': True} without relayout action
#     if main_graph_layout is not None and selector is not None and "locked" in selector:
#         if "mapbox.center" in main_graph_layout.keys():
#             lon = float(main_graph_layout["mapbox.center"]["lon"])
#             lat = float(main_graph_layout["mapbox.center"]["lat"])
#             zoom = float(main_graph_layout["mapbox.zoom"])
#             layout["mapbox"]["center"]["lon"] = lon
#             layout["mapbox"]["center"]["lat"] = lat
#             layout["mapbox"]["zoom"] = zoom
#
#     figure = dict(data=traces, layout=layout)
#     return figure
#
#
# # Main graph -> individual graph
# @app.callback(Output("individual_graph", "figure"), [Input("main_graph", "hoverData")])
# def make_individual_figure(main_graph_hover):
#
#     layout_individual = copy.deepcopy(layout)
#
#     if main_graph_hover is None:
#         main_graph_hover = {
#             "points": [
#                 {"curveNumber": 4, "pointNumber": 569, "customdata": 31101173130000}
#             ]
#         }
#
#     chosen = [point["customdata"] for point in main_graph_hover["points"]]
#     index, gas, oil, water = produce_individual(chosen[0])
#
#     if index is None:
#         annotation = dict(
#             text="No data available",
#             x=0.5,
#             y=0.5,
#             align="center",
#             showarrow=False,
#             xref="paper",
#             yref="paper",
#         )
#         layout_individual["annotations"] = [annotation]
#         data = []
#     else:
#         data = [
#             dict(
#                 type="scatter",
#                 mode="lines+markers",
#                 name="Gas Produced (mcf)",
#                 x=index,
#                 y=gas,
#                 line=dict(shape="spline", smoothing=2, width=1, color="#fac1b7"),
#                 marker=dict(symbol="diamond-open"),
#             ),
#             dict(
#                 type="scatter",
#                 mode="lines+markers",
#                 name="Oil Produced (bbl)",
#                 x=index,
#                 y=oil,
#                 line=dict(shape="spline", smoothing=2, width=1, color="#a9bb95"),
#                 marker=dict(symbol="diamond-open"),
#             ),
#             dict(
#                 type="scatter",
#                 mode="lines+markers",
#                 name="Water Produced (bbl)",
#                 x=index,
#                 y=water,
#                 line=dict(shape="spline", smoothing=2, width=1, color="#92d8d8"),
#                 marker=dict(symbol="diamond-open"),
#             ),
#         ]
#         layout_individual["title"] = dataset[chosen[0]]["Well_Name"]
#
#     figure = dict(data=data, layout=layout_individual)
#     return figure
#
#
# # Selectors, main graph -> aggregate graph
# @app.callback(
#     Output("aggregate_graph", "figure"),
#     [
#         Input("well_statuses", "value"),
#         Input("well_types", "value"),
#         Input("main_graph", "hoverData"),
#     ],
# )
# def make_aggregate_figure(well_statuses, well_types, main_graph_hover):
#
#     layout_aggregate = copy.deepcopy(layout)
#
#     if main_graph_hover is None:
#         main_graph_hover = {
#             "points": [
#                 {"curveNumber": 4, "pointNumber": 569, "customdata": 31101173130000}
#             ]
#         }
#
#     chosen = [point["customdata"] for point in main_graph_hover["points"]]
#     well_type = dataset[chosen[0]]["Well_Type"]
#     dff = filter_dataframe(df, well_statuses, well_types)
#
#     selected = dff[dff["Well_Type"] == well_type]["API_WellNo"].values
#     index, gas, oil, water = produce_aggregate(selected)
#
#     data = [
#         dict(
#             type="scatter",
#             mode="lines",
#             name="Gas Produced (mcf)",
#             x=index,
#             y=gas,
#             line=dict(shape="spline", smoothing="2", color="#F9ADA0"),
#         ),
#         dict(
#             type="scatter",
#             mode="lines",
#             name="Oil Produced (bbl)",
#             x=index,
#             y=oil,
#             line=dict(shape="spline", smoothing="2", color="#849E68"),
#         ),
#         dict(
#             type="scatter",
#             mode="lines",
#             name="Water Produced (bbl)",
#             x=index,
#             y=water,
#             line=dict(shape="spline", smoothing="2", color="#59C3C3"),
#         ),
#     ]
#     layout_aggregate["title"] = "Aggregate: " + WELL_TYPES[well_type]
#
#     figure = dict(data=data, layout=layout_aggregate)
#     return figure
#
#
# # Selectors, main graph -> pie graph
# @app.callback(
#     Output("pie_graph", "figure"),
#     [
#         Input("well_statuses", "value"),
#         Input("well_types", "value")
#     ],
# )
# def make_pie_figure(well_statuses, well_types):
#
#     layout_pie = copy.deepcopy(layout)
#
#     dff = filter_dataframe(df, well_statuses, well_types)
#
#     selected = dff["API_WellNo"].values
#     index, gas, oil, water = produce_aggregate(selected)
#
#     aggregate = dff.groupby(["Well_Type"]).count()
#
#     data = [
#         dict(
#             type="pie",
#             labels=["Gas", "Oil", "Water"],
#             values=[sum(gas), sum(oil), sum(water)],
#             name="Production Breakdown",
#             text=[
#                 "Total Gas Produced (mcf)",
#                 "Total Oil Produced (bbl)",
#                 "Total Water Produced (bbl)",
#             ],
#             hoverinfo="text+value+percent",
#             textinfo="label+percent+name",
#             hole=0.5,
#             marker=dict(colors=["#fac1b7", "#a9bb95", "#92d8d8"]),
#             domain={"x": [0, 0.45], "y": [0.2, 0.8]},
#         ),
#         dict(
#             type="pie",
#             labels=[WELL_TYPES[i] for i in aggregate.index],
#             values=aggregate["API_WellNo"],
#             name="Well Type Breakdown",
#             hoverinfo="label+text+value+percent",
#             textinfo="label+percent+name",
#             hole=0.5,
#             marker=dict(colors=[WELL_COLORS[i] for i in aggregate.index]),
#             domain={"x": [0.55, 1], "y": [0.2, 0.8]},
#         ),
#     ]
#     layout_pie["title"] = "Production Summary: {} to {}".format(
#         1, 4
#     )
#     layout_pie["font"] = dict(color="#777777")
#     layout_pie["legend"] = dict(
#         font=dict(color="#CCCCCC", size="10"), orientation="h", bgcolor="rgba(0,0,0,0)"
#     )
#
#     figure = dict(data=data, layout=layout_pie)
#     return figure
#
#
# # Selectors -> count graph
# @app.callback(
#     Output("count_graph", "figure"),
#     [
#         Input("well_statuses", "value"),
#         Input("well_types", "value"),
#     ],
# )
# def make_count_figure(well_statuses, well_types):
#
#     layout_count = copy.deepcopy(layout)
#
#     dff = filter_dataframe(df, well_statuses, well_types, [1960, 2017])
#     g = dff[["API_WellNo", "Date_Well_Completed"]]
#     g.index = g["Date_Well_Completed"]
#     g = g.resample("A").count()
#
#     colors = []
#     for i in range(1960, 2018):
#         if i >= int(1) and i < int(4):
#             colors.append("rgb(123, 199, 255)")
#         else:
#             colors.append("rgba(123, 199, 255, 0.2)")
#
#     data = [
#         dict(
#             type="scatter",
#             mode="markers",
#             x=g.index,
#             y=g["API_WellNo"] / 2,
#             name="All Wells",
#             opacity=0,
#             hoverinfo="skip",
#         ),
#         dict(
#             type="bar",
#             x=g.index,
#             y=g["API_WellNo"],
#             name="All Wells",
#             marker=dict(color=colors),
#         ),
#     ]
#
#     layout_count["title"] = "Completed Wells/Year"
#     layout_count["dragmode"] = "select"
#     layout_count["showlegend"] = False
#     layout_count["autosize"] = True
#
#     figure = dict(data=data, layout=layout_count)
#     return figure


# Main
if __name__ == "__main__":
    app.run_server(debug=True)
