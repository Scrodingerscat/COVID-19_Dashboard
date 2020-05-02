# -*- coding: utf-8 -*-
import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import time
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from newsapi.newsapi_client import NewsApiClient
import json
from dotenv import load_dotenv

# app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
app = dash.Dash(__name__)
server = app.server

# ====================
# Set path
# ====================
currentpath = os.path.abspath(os.path.dirname(__file__))
jsonfolder = "docs"
jsonfile = "canada.json"
jsonpath = os.path.abspath(os.path.join(currentpath, "..", jsonfolder, jsonfile))

# ====================
# Data prepare
# ====================
# Get data from the database
dbfolder = "data"
dbfile = "COVID19.db"
dbpath = os.path.abspath(os.path.join(currentpath, "..", dbfolder, dbfile))


def get_data(query):
    conn = sqlite3.connect(dbpath, check_same_thread=False)
    df = pd.read_sql(query, con=conn)
    conn.close()
    if "date" in df.columns:
        df.date = pd.to_datetime(df.date, format="%d-%m-%Y")

    return df


# Province list and shrtname dictionary
query = """SELECT DISTINCT prname FROM 'covid' WHERE pruid!=99;"""
prdf = get_data(query).prname

dicprlist = {
    "Newfoundland and Labrador": "NL",
    "Prince Edward Island": "PE",
    "Nova Scotia": "NS",
    "New Brunswick": "NB",
    "Quebec": "QC",
    "Ontario": "ON",
    "Manitoba": "MB",
    "Saskatchewan": "SK",
    "Alberta": "AB",
    "British Columbia": "BC",
    "Yukon": "YT",
    "Northwest Territories": "NT",
    "Nunavut": "NU",
}

# ====================
# Component prebuild
# ====================
# Calendar build
# calendar = dcc.DatePickerSingle(
#     id="datepicker",
#     min_date_allowed=dt(2019, 1, 1),
#     max_date_allowed=dt.today(),
#     date=str(dt.today()),
# )

# color, style, etc
bgcolor = "#f9f9f9"
deathcolor = "#fb6a4a"
confcolor = "#2171b5"
testcolor = "#238b45"

# Cases by province graph
def prgraph():
    query = """SELECT prname, date, numtotal FROM 'covid';"""
    df = get_data(query)
    df = df.drop_duplicates("prname", keep="last")[
        (df.prname != "Repatriated travellers") & (df.prname != "Canada")
    ]
    df = df.sort_values(by=["numtotal"], ascending=False)

    x = []
    for i in df.prname:
        x.append(dicprlist[i])

    fig = dict(
        {
            "data": [
                {
                    "type": "bar",
                    "x": x,
                    "y": df.numtotal,
                    "text": df.numtotal,
                    "textposition": "auto",
                }
            ],
            "layout": {
                "margin": {"r": 30, "t": 30, "l": 30, "b": 30},
                "plot_bgcolor": bgcolor,
                "paper_bgcolor": bgcolor,
                # "height": 344,
                "yaxis": {"showgrid": False},
            },
            # "paper_bgcolor": bgcolor
            # "margin": {"r": 0, "t": 0, "l": 0, "b": 0},
        }
    )

    return fig


# Tabs graph
def tabsgraph(mode, region):
    # Conditions
    if mode == "newtotal":
        gtype = "bar"
        text = "New Reported Cases in " + region
        color = confcolor
    elif mode == "newdeaths":
        gtype = "bar"
        text = "New Reported Deaths in " + region
        color = deathcolor
    elif mode == "numtotal":
        gtype = "line"
        text = "Cumulative Cases in " + region
        color = confcolor
    elif mode == "numdeaths":
        gtype = "line"
        text = "Cumulative Deaths in " + region
        color = deathcolor
    elif mode == "newtested":
        gtype = "bar"
        text = "Daily Tested number in " + region
        color = testcolor
    elif mode == "numtested":
        gtype = "line"
        text = "Total Tested number in " + region
        color = testcolor

    # Prepare data
    query = """SELECT date, numtotal, numdeaths, numtested FROM 'covid' WHERE prname='{}';""".format(
        region
    )
    df1 = get_data(query)
    df2 = (
        df1[["numtotal", "numdeaths", "numtested"]]
        .diff()
        .rename(
            columns={"numdeaths": "newdeaths", "numtotal": "newtotal", "numtested": "newtested"}
        )
    )
    df = pd.concat([df1, df2], axis=1)

    # Create fig
    fig = dict(
        {
            "data": [{"type": gtype, "x": df["date"], "y": df[mode], "marker": {"color": color}}],
            "layout": {
                "title": {"text": text},
                "height": 280,
                "margin": {"r": 50, "t": 50, "l": 50, "b": 50},
            },
        }
    )

    return fig


# Map figure
def mapfig():

    with open(jsonpath, "r") as response:
        geojson = json.load(response)

    query = """SELECT prname, numtotal FROM 'covid' WHERE pruid!=1 AND pruid!=99;"""
    df = get_data(query)
    df = df.drop_duplicates("prname", keep="last")

    fig = px.choropleth_mapbox(
        df,
        geojson=geojson,
        color="numtotal",
        locations="prname",
        featureidkey="properties.name",
        center={"lat": 63.070750, "lon": -94.386280},
        mapbox_style="carto-positron",
        zoom=2.5,
        color_continuous_scale=px.colors.sequential.Blues,
        labels={"numtotal": "Total Cases", "prname": "Province"},
        height=600,
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},)

    return fig


# ====================
# Html layout
# ====================
# Layout build
app.layout = html.Div(
    children=[
        # Header
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("dash-logo.png"),
                            id="plotly-image",
                            style={"height": "80px", "width": "auto", "margin-bottom": "25px",},
                        )
                    ],
                    className="four columns",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3("COVID-19 Dashboard Canada",),
                                html.H5("Made by Wayne Yin", style={"margin-top": "0px"}),
                            ]
                        )
                    ],
                    className="four columns",
                    id="title",
                ),
                html.Div(
                    id="date",
                    style={"text-align": "right", "margin-right": "15px"},
                    className="four columns",
                ),
                dcc.Interval(id="dateupdate", interval=1 * 1000, n_intervals=0)
                # html.Div(
                #     [
                #         html.A(
                #             html.Button("Learn More", id="learn-more-button"),
                #             href="https://plot.ly/dash/pricing/",
                #         )
                #     ],
                #     className="one-third column",
                #     id="button",
                # ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        # First Row
        html.Div(
            className="row flex-display",
            children=[
                # Left Column
                html.Div(
                    className="four columns",
                    children=[
                        # Selector
                        html.Div(
                            className="pretty_container",
                            id="cross-filter-options",
                            children=[
                                html.H6("Select Region", className="control_label"),
                                dcc.Dropdown(
                                    id="dropdown",
                                    options=[{"label": i, "value": i} for i in prdf],
                                    value="Canada",
                                    clearable=False,
                                ),
                                # html.P("Select Date", className="control_label"),
                                # calendar,
                            ],
                        ),
                        # Last update Time
                        html.Div(
                            className="row flex-display",
                            children=[
                                html.Div(
                                    # [html.H5(id="lastupdate")],
                                    [
                                        html.H5(
                                            "Last Update: "
                                            + time.strftime("%Y-%m-%d", time.localtime())
                                        )
                                    ],
                                    className="mini_container container-display",
                                ),
                                # dcc.Interval(
                                #     # id="dailyupdate", interval=1000 * 1 * 60 * 60 * 6, n_intervals=0
                                #     id="dbupdate",
                                #     interval=1000 * 1 * 60 * 60 * 8,
                                #     n_intervals=0,
                                # ),
                            ],
                        ),
                        # Important Info Row1
                        html.Div(
                            className="row flex-display",
                            children=[
                                html.Div(
                                    [html.Label("New Cases (24H)"), html.H4(id="newtotal"),],
                                    id="newcase",
                                    className="mini_container container-display",
                                ),
                                html.Div(
                                    [html.Label("New Deaths (24H)"), html.H4(id="newdeaths"),],
                                    id="newdeath",
                                    className="mini_container container-display",
                                ),
                                html.Div(
                                    [html.Label("New Tested (24H)"), html.H4(id="newtested"),],
                                    id="newtest",
                                    className="mini_container container-display",
                                ),
                            ],
                        ),
                        # Important Info Row2
                        html.Div(
                            className="row flex-display",
                            children=[
                                html.Div(
                                    [html.P("Total Cases"), html.H4(id="numtotal")],
                                    id="totalcase",
                                    className="mini_container container-display",
                                ),
                                html.Div(
                                    [html.P("Total Deaths"), html.H4(id="numdeaths")],
                                    id="totaldeath",
                                    className="mini_container container-display",
                                ),
                                html.Div(
                                    [html.P("Total Tested"), html.H4(id="numtested")],
                                    id="totaltest",
                                    className="mini_container container-display",
                                ),
                            ],
                        ),
                    ],
                ),
                # Right Column
                html.Div(
                    id="right-column",
                    className="eight columns",
                    children=[
                        html.Div(
                            className="pretty_container",
                            children=[
                                html.H5("Total Cases by Province and Territory"),
                                dcc.Graph(id="prgraph"),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        # Second Row
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id="mapgraph", className="pretty_container"),
                        dcc.Interval(
                            id="dailyupdate", interval=1000 * 1 * 60 * 60 * 6, n_intervals=0
                        ),
                        html.Div(id="news", className="pretty_container",),
                        dcc.Interval(id="hourlyupdate", interval=1000 * 1 * 60 * 60, n_intervals=0),
                    ],
                    className="seven columns",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Tabs(
                                    [
                                        dcc.Tab(
                                            label="New Cases",
                                            children=[dcc.Graph(id="dailycases")],
                                        ),
                                        dcc.Tab(
                                            label="Cumulative Cases",
                                            children=[dcc.Graph(id="cumucases")],
                                        ),
                                    ],
                                ),
                            ],
                            className="pretty_container",
                        ),
                        html.Div(
                            [
                                dcc.Tabs(
                                    [
                                        dcc.Tab(
                                            label="New Deaths",
                                            children=[dcc.Graph(id="dailydeaths")],
                                        ),
                                        dcc.Tab(
                                            label="Cumulative Deaths",
                                            children=[dcc.Graph(id="cumudeaths")],
                                        ),
                                    ],
                                ),
                            ],
                            className="pretty_container",
                        ),
                        html.Div(
                            [
                                dcc.Tabs(
                                    [
                                        dcc.Tab(
                                            label="New Tested",
                                            children=[dcc.Graph(id="dailytested")],
                                        ),
                                        dcc.Tab(
                                            label="Cumulative Tested",
                                            children=[dcc.Graph(id="cumutested")],
                                        ),
                                    ],
                                ),
                            ],
                            className="pretty_container",
                        ),
                    ],
                    className="five columns",
                ),
            ],
            className="row flex-display",
        ),
    ],
    id="maincontainer",
    style={"display": "flex", "flex-direction": "column"},
)

# ====================
# Callbacks
# ====================
# db update
# @app.callback(Output("lastupdate", "children"), [Input("dbupdate", "n_intervals")])
# def lastupdate(n):
#     print(n)
#     return html.H5("Last Update: " + dbupdate.dbupdate())


# Date update
@app.callback(Output("date", "children"), [Input("dateupdate", "n_intervals")])
def date_update(n):
    date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return html.H5(date)


# Tabs update
@app.callback(
    [
        Output("dailycases", "figure"),
        Output("cumucases", "figure"),
        Output("dailydeaths", "figure"),
        Output("cumudeaths", "figure"),
        Output("dailytested", "figure"),
        Output("cumutested", "figure"),
    ],
    [Input("dropdown", "value"), Input("dailyupdate", "n_intervals")],
)
def tabs_update(region, n):
    return (
        tabsgraph("newtotal", region),
        tabsgraph("numtotal", region),
        tabsgraph("newdeaths", region),
        tabsgraph("numdeaths", region),
        tabsgraph("newtested", region),
        tabsgraph("numtested", region),
    )


# Info No. update
@app.callback(
    [
        Output("newtotal", "children"),
        Output("newdeaths", "children"),
        Output("newtested", "children"),
        Output("numtotal", "children"),
        Output("numdeaths", "children"),
        Output("numtested", "children"),
    ],
    [Input("dropdown", "value"), Input("dailyupdate", "n_intervals")],
)
def info_update(region, n):
    query = """SELECT date, numtotal, numdeaths, numtested FROM 'covid' WHERE prname='{}';""".format(
        region
    )
    df1 = get_data(query)
    df2 = (
        df1[["numtotal", "numdeaths", "numtested"]]
        .diff()
        .rename(
            columns={"numdeaths": "newdeaths", "numtotal": "newtotal", "numtested": "newtested"}
        )
    )
    df = pd.concat([df1, df2], axis=1)
    df = df[df.date == max(df.date)]

    return (
        df.newtotal,
        df.newdeaths,
        df.newtested,
        df.numtotal,
        df.numdeaths,
        df.numtested,
    )


# Map and prgraph daily update
@app.callback(
    [Output("mapgraph", "figure"), Output("prgraph", "figure"),],
    [Input("dailyupdate", "n_intervals")],
)
def daily_update(n):
    return (mapfig(), prgraph())


# News update
@app.callback(Output("news", "children"), [Input("hourlyupdate", "n_intervals")])
def news_update(n):
    load_dotenv()
    api_key = os.environ.get("NEWS_API_KEY")
    newsapi = NewsApiClient(api_key=api_key)
    top_headlines = newsapi.get_top_headlines(
        q="covid-19", language="en", country="ca", page_size=10
    )
    article = top_headlines["articles"]
    news = [html.H5("News about Covid-19 in Canada")] + [
        html.H6(html.A(i["title"], href=i["url"], target="_blank")) for i in article
    ]
    return news


if __name__ == "__main__":
    app.run_server(debug=True)
