import pandas as pd

from bokeh.layouts import row, widgetbox
from bokeh.palettes import Spectral5, RdBu11
from bokeh.plotting import curdoc, figure
from bokeh.models import (
  GMapPlot, GMapOptions, ColumnDataSource, Circle, DataRange1d,
    PanTool, WheelZoomTool, BoxSelectTool, LassoSelectTool, ResetTool, HoverTool,
    Select)

def read_buoy_latest_data(fname):
    """Handy function to read and cleanup the buoy data files."""
    col_names = ['station', 'latitude', 'longitude', 'year', 'month', 'day', 'hour', 'minute', 'wind_direction', 'wind_speed',
             'wind_gust', 'wave_height', 'dominant_wave_period', 'average_wave_period',
             'dominant_wave_direction', 'pressure', '3hr_pressure_tendency', 'temperature', 'water_temperature', 'dewpoint',
             'visibility', 'tide']

    widths = [5, 8, 9, 5, 3, 3, 3, 3, 4, 6, 6, 5, 4, 5, 4, 7, 6, 6, 6, 6, 5, 7]

    df = pd.read_fwf(fname, skiprows=2, na_values='MM', names=col_names, widths=widths)

    df['time'] = pd.to_datetime(df[['year', 'month', 'day', 'hour', 'minute']])

    # Using inplace means the return is None and the dataframe is simply modified.
    df.drop(['year', 'month', 'day', 'hour', 'minute'], axis='columns', inplace=True)


    df.reset_index(drop=True, inplace=True)

    return df

df = read_buoy_latest_data('latest_obs.txt') #http://www.ndbc.noaa.gov/data/latest_obs/

SIZES = list(range(1, 10, 1))
COLORS = RdBu11

dropdown_options = ['temperature', 'wind_speed']

def create_figure():


    sz = [3 for x in range(len(df['temperature'].values))]
    if size.value != 'None':
        groups = pd.cut(df['temperature'].values, len(SIZES))
        sz = [SIZES[xx] for xx in groups.codes]

    c = ["#000000" for x in range(len(df['temperature'].values))]
    if color.value != 'None':
        print("recoloring on: ", color.value)
        groups = pd.cut(df[color.value].values, len(COLORS))
        c = [COLORS[xx] for xx in groups.codes]

    print("SIZE: ", sz)
    source = ColumnDataSource(
        data=dict(
            lat=df['latitude'],
            lon=df['longitude'],
            temperature=df['temperature'],
            wind_speed=df['wind_speed'],
            wind_gust=df['wind_gust'],
            time=df['time'],
            buoy=df['station'],
            dewpoint=df['dewpoint'],
            colors=c,
            sizes=sz
        )
    )


    map_options = GMapOptions(lat=30.29, lng=-97.73, map_type='terrain', zoom=3)

    hover = HoverTool(
            tooltips=[
                ('Buoy', '@buoy'),
                ('Temperature', '@temperature{(0.0)}'),
                ('Dewpoint', '@dewpoint{(0.0)}')
            ])

    plot = GMapPlot(
        x_range=DataRange1d(), y_range=DataRange1d(), map_options=map_options, tools=[hover]
    )
    plot.title.text = "Buoy Network"

    # For GMaps to function, Google requires you obtain and enable an API key:
    #
    #     https://developers.google.com/maps/documentation/javascript/get-api-key
    #
    # Replace the value below with your personal API key:
    plot.api_key = "AIzaSyD_3AC8-tQeyVBsujeDF1GTQuE2GtkboXM"


    circle = Circle(x="lon", y="lat", size='sizes', fill_alpha=0.8, line_color=None, fill_color='colors')
    #circle = Circle(x="lon", y="lat", size=9, fill_alpha=0.8, line_color=None, fill_color='colors')
    plot.add_glyph(source, circle)

    plot.add_tools(PanTool(), WheelZoomTool(), BoxSelectTool(), LassoSelectTool(), ResetTool())
    plot.toolbar.logo = None

    return plot


def update(attr, old, new):
    layout.children[1] = create_figure()

size = Select(title='Size', value='None', options=['None'] + dropdown_options)
size.on_change('value', update)

color = Select(title='Color', value='None', options=['None'] + dropdown_options)
color.on_change('value', update)

controls = widgetbox([color, size], width=200)
layout = row(controls, create_figure())

curdoc().add_root(layout)
curdoc().title = "NDBC Realtime Buoy Data by Unidata"
