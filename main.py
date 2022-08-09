import pandas as pd
import plotly.graph_objs as go
from dash import Dash, html, dcc, Output, Input, dash_table

df = pd.read_csv('raw_data.csv')
downloadable_pivot_df = pd.read_csv('pivot_data.csv')
filtered_df_columns = ['server.city', 'server.region', 'suspicious_or_invalid', 
                       'total', 'percent_invalid']

# Needed to run range in range slider to logarithmic scale
def transform_value(value):
    return 10 ** value

app = Dash(__name__)
server = app.server

# Set up the layout of the dashboard
app.layout = html.Div(
    children=[
        dcc.Graph(id='graph'),
        dcc.RangeSlider(0, 6, id='non-linear-range-slider',
        marks={i: '{:,}'.format(10 ** i) for i in range(6)},
        value=[1, 100000], dots=False, step=0.01, updatemode='drag'),
        html.Div(id='output-container-range-slider-non-linear', 
                 style={'margin-top': 5}),
        html.Button("Download CSV", id="btn_csv"),
        dcc.Download(id="download-dataframe-csv"),
        html.P(),
        dash_table.DataTable(
            id="table-container",
            columns=[{'name': i, 'id': i} for i in filtered_df_columns],
            data=df.to_dict("records"),
            style_header={'height': 'auto', 'width':'180px', 'maxWidth': '180px', 
                          'minWidth': '180px'},
            style_cell={'textAlign': 'left', 'padding': '0px', 'fontSize': 12, 
                        'font': 'Arial'})])

# Function to show + activate downloan button
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    prevent_initial_call=True,)
def show_download_button(n_clicks):
    return dcc.send_data_frame(downloadable_pivot_df.to_csv, 
                               "downloadable_pivot.csv")

# Main graph
@app.callback(
    Output('graph', 'figure'),
    Input('non-linear-range-slider', 'value'))
def update_output_graph(value):
    transformed_value = [transform_value(v) for v in value]
    min_value = min(transformed_value)
    max_value = max(transformed_value)
    if max_value >= 1000000:
        max_value = 1000000
    
    df_pivot = df.pivot(index=['server.city', 'server.region', 'lat', 'long'], 
                        columns='validity', values='hits').reset_index()
    df_pivot.fillna(0, inplace=True)

    df_pivot['invalid'] = df_pivot['invalid'].astype(int)
    df_pivot['suspicious'] = df_pivot['suspicious'].astype(int)
    df_pivot['unknown'] = df_pivot['unknown'].astype(int)
    df_pivot['valid'] = df_pivot['valid'].astype(int)

    df_pivot['unknown_or_valid'] = df_pivot['valid']  + df_pivot['unknown']
    df_pivot['suspicious_or_invalid'] = df_pivot['invalid']  + df_pivot['suspicious']
    df_pivot['total'] = df_pivot['invalid'] + df_pivot['suspicious'] + df_pivot['unknown'] + df_pivot['valid']
    df_pivot['percent_invalid'] = df_pivot['suspicious_or_invalid'] / df_pivot['total'] * 100
    
    df_pivot = df_pivot.sort_values(by='total', ascending=False)
    df_pivot['percent_invalid'] = df_pivot['percent_invalid'].round(3)
    
    df_pivot['text'] = df_pivot['server.city'] + ", " +  df_pivot['server.region'] +\
                        '<br>Lat: ' + df_pivot['lat'].astype(str) + ' Lon: ' + df_pivot['long'].astype(str) +\
                        '<br>Invalid Hits: ' + df_pivot['suspicious_or_invalid'].astype(str) +\
                        '<br>Hits: ' + df_pivot['total'].astype(str) +\
                        '<br>Invalid: ' + df_pivot['percent_invalid'].astype(str)+"%"

    slices = [(0, 5), (6, 10), (11, 15), (16, 20), (21, 100)]

    first_slice = [x[0] for x in slices]
    hex_colors = ['#2b83ba', '#abdda4', '#ffffbf', '#fdae61', '#d7191c']

    colors = dict(zip(first_slice, hex_colors))

    scale = 100
    fig = go.Figure()
    
    filtered_df = df_pivot[(df_pivot['total'] >= min_value) & 
                           (df_pivot['total'] < max_value)]

    for slice_ in slices:
        start_slice = slice_[0]
        end_slice = slice_[1]
        sliced_df = filtered_df[(filtered_df['percent_invalid'] >= start_slice) & 
                             (filtered_df['percent_invalid'] < end_slice)]

        fig.add_trace(go.Scattergeo(
            locationmode = 'USA-states',
            lat = sliced_df['lat'],
            lon = sliced_df['long'],
            text = sliced_df['text'],
            name = "{}% - {}% Invalid".format(start_slice, end_slice),
            marker = dict(
                size = sliced_df['total'] / scale,
                line_color='rgb(40,40,40)',
                line_width=0.5,
                sizemode = 'area',
                color = colors[start_slice],
                opacity = 0.9)))

        fig.update_layout(
                title_text = 'Invalid Impressions by Location'+\
                             '<br>(Click legend to toggle traces)',
                showlegend = True,
                height = 600,
                width = 1400,
                geo = dict(
                    scope = 'usa',
                    landcolor = 'rgb(217, 217, 217)'))
        
    return fig

# "Output Div" to show the values of the slider
@app.callback(
    Output('output-container-range-slider-non-linear', 'children'),
    Input('non-linear-range-slider', 'value'))
def update_output_div(value):
    transformed_value = [transform_value(v) for v in value]
    min_value = min(transformed_value)
    max_value = max(transformed_value)
    if max_value >= 1000000:
        max_value = 1000000

    return 'Value Slider: Sort Geo Plots and Data Table by number of hits.'+\
           'Min hits per area: {:,}, Max hits per area: {:,}. '.format(
        int(round(min_value,0)),
        int(round(max_value,0)))

# Update Data Table to match what is on the Geo Scatter Plot
@app.callback(
    Output("table-container", "data"), 
    Input("non-linear-range-slider", "value"))
def update_display_table(value):
    transformed_value = [transform_value(v) for v in value]
    min_value = min(transformed_value)
    max_value = max(transformed_value)
    if max_value >= 1000000:
        max_value = 1000000

    df_pivot = df.pivot(index=['server.city', 'server.region', 'lat', 'long'], 
                        columns='validity', values='hits').reset_index()

    df_pivot.fillna(0, inplace=True)

    df_pivot['invalid'] = df_pivot['invalid'].astype(int)
    df_pivot['suspicious'] = df_pivot['suspicious'].astype(int)
    df_pivot['unknown'] = df_pivot['unknown'].astype(int)
    df_pivot['valid'] = df_pivot['valid'].astype(int)

    df_pivot['unknown_or_valid'] = df_pivot['valid']  + df_pivot['unknown']
    df_pivot['suspicious_or_invalid'] = df_pivot['invalid']  + df_pivot['suspicious']
    df_pivot['total'] = df_pivot['invalid'] + df_pivot['suspicious'] + df_pivot['unknown'] + df_pivot['valid']
    df_pivot['percent_invalid'] = df_pivot['suspicious_or_invalid'] / df_pivot['total'] * 100

    df_pivot = df_pivot.sort_values(by='total', ascending=False)
    df_pivot['percent_invalid'] = df_pivot['percent_invalid'].round(3)

    filtered_df = df_pivot[(df_pivot['total'] >= min_value) & (df_pivot['total'] < max_value)]

    filtered_df = filtered_df[['server.city', 'server.region', 'suspicious_or_invalid', 'total', 'percent_invalid']].reset_index()

    return filtered_df.to_dict('records')

if __name__ == "__main__":
    app.run_server()
