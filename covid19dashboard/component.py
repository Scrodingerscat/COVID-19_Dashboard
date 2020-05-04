# -*- coding: utf-8 -*-
import os
import sqlite3
import pandas as pd
import json
import plotly.express as px

# ====================
# Data preparation
# ====================
# Get data from the database
currentpath = os.path.abspath(os.path.dirname(__file__))
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


# Province list and their shortname
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

# color, style, etc
bgcolor = "#f9f9f9"
deathcolor = "#fb6a4a"
confcolor = "#2171b5"
testcolor = "#238b45"

# ====================
# Map graph
# ====================
jsonfolder = "docs"
jsonfile = "canada.json"
jsonpath = os.path.abspath(os.path.join(currentpath, "..", jsonfolder, jsonfile))


def map_fig():

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
# Province graph
# ====================
def pr_fig():
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


# ====================
# Tabs graph
# ====================
def tabs_fig(mode, region):
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
