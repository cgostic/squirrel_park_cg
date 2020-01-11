import altair as alt
import pandas as pd
import json
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], assets_folder = "assets")
app.config['suppress_callback_exceptions'] = True

server = app.server

app.title = 'Squirrel App CG Version'

 # load the data
csv = pd.read_csv('data/squirrel_count.csv')
sort_order = list(csv.sort_values(by = ['Unique_Squirrel_ID'])['sitename_short'])
with open('data/squirrel_plots.json') as data_file:
    b_json_count = json.load(data_file)
squirrel_json = alt.Data(values = b_json_count['features'])

# Plot width and height, title font size, axislabel font size
w = 600
h = 400
tfs = 20
atfs = 18
lfs = 16

## Plotting function
def make_plot(y_axis = 'Running_or_Chasing'):
    """
    Plot making function that contains four sub-functions to plot each of the 4 graphs in the app.

    Parameters
    ----------
    y_axis : character
        Drop-down menu selection value for the "plot_bar_behavior" sub-function to update the behavior plot 

    Returns
    -------
    chart
        The combined plot of the 4 sub-plots.
    """

    brush = alt.selection_multi(fields = ['properties.sitename_short'],
        resolve='global')
    #sort_order = list(csv.sort_values(by = ['Unique_Squirrel_ID'])['sitename_short'])
    ##################################
    # PLOT MAP of SQUIRREL COUNT
    ##################################
    def plot_map_total_count(selection):
        # Plot of squirrel count
        base_map = alt.Chart(squirrel_json).mark_geoshape(
            stroke='black',
            strokeWidth=1
        ).encode(
        ).properties(
            width=w,
            height=h
        )

        # Add Choropleth Layer
        choropleth = (alt.Chart(squirrel_json, 
                                title = "Central Park Squirrel Distribution: 2018 Census")
        .mark_geoshape()
        .add_selection(selection)
        .encode(
        # SELECTION SINGLE CONDITIONS -- Color is grey if not selected
            color = alt.condition(selection, 
                                'properties.Unique_Squirrel_ID:Q', 
                                alt.value('grey'),
                title = 'Squirrel\nCount',
                scale=alt.Scale(scheme='greens'),
                legend = alt.Legend(labelFontSize = 16, 
                                    titleFontSize = 14, 
                                    tickCount = 5)),
            opacity=alt.condition(selection, 
                                alt.value(0.8), 
                                alt.value(0.1)),
            tooltip = [alt.Tooltip('properties.sitename:N', 
                                title="Park Region"), 
                alt.Tooltip('properties.Unique_Squirrel_ID:Q', 
                            title="Squirrel Count")]
        ))
        
        return(base_map + choropleth)


    ##########################################
    # PLOT TOTAL SQUIRREL COUNT
    ##########################################
    def plot_bar_total_count(selection):
        count_bar = (alt.Chart(squirrel_json, 
                            title = 'Squirrel Count by Park Region')
        .mark_bar()
        .add_selection(selection)
        .encode(
            x = alt.X('properties.sitename_short:N',
                sort = sort_order, 
                title = "Park Region", 
                axis=alt.Axis(ticks = False,
                titleFontSize = atfs, labels = False)),
            y = alt.Y('properties.Unique_Squirrel_ID:Q', 
                title = "Squirrel Count", 
                axis = alt.Axis(labelFontSize = lfs, 
                                titleFontSize = atfs)),
            color = alt.Color('properties.Unique_Squirrel_ID:Q',
                            scale=alt.Scale(scheme='greens'),
                            legend=None),

        # SELECTION SINGLE CONDITIONS -- opacity is 0.2 if not selected
            opacity = alt.condition(selection, 
                                    alt.value(1.0), 
                                    alt.value(0.2)),
            tooltip = [alt.Tooltip('properties.sitename:N', 
                                title="Park Region"), 
                alt.Tooltip('properties.Unique_Squirrel_ID:Q', 
                            title="Squirrel Count")])
        .properties(width = w, height = h))   
        return(count_bar)
    plot_bar_total_count(brush)

    ################################################
    # PLOT DIFFERENCE in COUNT by TIME OF DAY
    ################################################
    def plot_bar_count_diff(selection):
        area_count_shift = (alt.Chart(squirrel_json)
        .mark_bar()
        .add_selection(selection)
        .encode(
            alt.X('properties.sitename_short:N',
                axis=alt.Axis(
                    labels=False, 
                    ticks = False,
                    title = "Park Region",
                    titleFontSize = atfs),
                    sort = sort_order),
            alt.Y('properties.Count_diff (AM - PM):Q', 
                title = "Count Difference (AM - PM)", 
                axis = alt.Axis(labelFontSize = lfs, 
                                titleFontSize = atfs)),
            opacity = alt.condition(selection, 
                                    alt.value(1.0), 
                                    alt.value(0.2)),
            color=alt.condition(
                # If count is negative, color bar blue. If positive, red.
                alt.datum['properties.Count_diff (AM - PM)'] > 0,
                alt.value("darkred"),  # The positive color
                alt.value("steelblue")  # The negative color
            ),
            tooltip = [alt.Tooltip('properties.sitename:N', title="Park Region"), 
                    alt.Tooltip('properties.Count_diff (AM - PM):Q', title="Count difference")]
        ).properties(title = "Squirrel Count by Park Region: AM vs. PM",
                    width = w,
                    height = h))
        return(area_count_shift)
    plot_bar_count_diff(brush)


    # ###################################
    # # PLOT BEHAVIOR by PARK AREA
    # ###################################
    def plot_bar_behavior(selection, y_axis = y_axis):
        b_chart = (alt.Chart(squirrel_json)
            .mark_bar(color = 'gray')
            .add_selection(selection)
            .encode(alt.X('properties.sitename_short:N', 
                    title = "Park Region", sort = sort_order, 
                    axis=alt.Axis(
                        labels=False,
                        titleFontSize = atfs,
                        ticks = False)), 
                    alt.Y('properties.'+y_axis+':Q', 
                            title = 'Squirrel Count', 
                            axis = alt.Axis(labelFontSize = lfs,
                            titleFontSize = atfs)),
                    opacity = alt.condition(brush, 
                                        alt.value(1.0), 
                                        alt.value(0.2)),
                    tooltip = [alt.Tooltip('properties.sitename:N', title="Park Region"), 
                            alt.Tooltip('properties.'+y_axis+':Q', title = "Count "+y_axis.replace('_',' '))]
                )
            .properties(title = "Squirrel Behavior by Park Region: "+y_axis.replace('_',' '),
                        width = w,
                        height = h))
        return b_chart


    # Create selection conditions and link plots by setting resolve = 'global'
    brush = alt.selection_multi(fields = ['properties.sitename_short'],
        resolve='global'
    )

    # source (code): https://www.districtdatalabs.com/altair-choropleth-viz

    # Render stacked plots
    chart = (((plot_map_total_count(brush) | plot_bar_total_count(brush)) & 
            (plot_bar_behavior(brush, y_axis) | plot_bar_count_diff(brush)))
            .configure_title(fontSize = 24)
            .configure_view(fill = "white"))

    # source (code): https://www.districtdatalabs.com/altair-choropleth-viz

    return (chart
        .configure(padding = {"left": 0, "top": 0, "right": 0, "bottom": 0})
        .configure_legend(offset = -15, 
                            orient = 'none', 
                            legendX = 10, 
                            legendY = 40 , 
                            gradientLength = 300, 
                            titleFontSize = 12)
        .configure_title(fontSize = tfs, anchor = 'middle'))
                            

app.layout = html.Div([
        # First column        
        html.Div(
            children=[
                html.Div(className = "app-logo", children = [
                    html.Img(src='https://i.ibb.co/F78bQB2/logo-2.png', width = 200)
                ]),
                html.Div(className = "app-side-panel-intro", children = [
                    html.H5('Guide your observance of the famous squirrels of Central Park, NY')
                ]),
                dcc.Markdown(className = "app-panel-list", children = [
                    """
                    - Hover over any chart value to see details
                    - Click a region on any chart to highlight across all charts
                    - Shift + click to select multiple regions at once
                    """
                ]),
                html.Div(className = "app-behavior-intro", children = [
                    html.H5('Select a Behavior to'),
                    html.H5('Display:')
                    ]),
                html.Div(className = "app-behavior-dd", children = [
                    dcc.Dropdown(
                        id='dd-chart',
                        options=[
                            {'label': 'Running or Chasing', 'value': 'Running_or_chasing'},
                            {'label': 'Climbing', 'value': 'Climbing'},
                            {'label': 'Eating or Foraging', 'value': 'Eating_or_foraging'},
                            {'label': 'Vocalizing', 'value': 'Vocalizations'},
                            {'label': 'Approaches Humans', 'value': 'Approaches'},
                                ],
                        value = 'Running_or_chasing',
                        clearable = False,
                        style=dict(width='95%',
                                    verticalAlign="middle",
                                    fontSize = 18
                                    )
                            )
                    ]),
                html.Div(className = "app-behavior-arrow", children = [
                    html.Img(src="https://upload.wikimedia.org/wikipedia/commons/8/8e/Simpleicons_Interface_arrow-pointing-to-right.svg", width = 50)
                ])
        ], style={'width': '15%', 'display': 'inline-block', 'vertical-align': 'top'}),
        # 2nd column
        html.Div(className = 'app-graphs',
                children = [
                    html.Iframe(
                        sandbox='allow-scripts',
                        id='plot',
                        height='955',
                        width='1400',
                        style={'border-width': '0px'},
                        # Call plot function
                        srcDoc = make_plot().to_html()
                        ),
                    html.Div(className = 'app-graph-notes-red', children = [
                        html.P('* Red indicates more squirrels in the morning.')
                        ]),
                    html.Div(className = 'app-graph-notes-blue', children = [
                        html.P('* Blue indicates more squirrels in the afternoon')
                        ])
                        ], style={'width': '84%', 'display': 'inline-block'}),                 
        # html.Div(className = 'app-graph-notes-red', children = [
        #     html.P('* Red indicates more squirrels in the morning.')
        #     ]),
        # html.Div(className = 'app-graph-notes-blue', children = [
        #     html.P('* Blue indicates more squirrels in the afternoon')
        #     ]),
        dcc.Markdown(className = "app-footer", children = [
                    """
                    #### Visit the [Github Repository](https://github.com/cgostic/squirrel_app_CG)  

                    #### Sources: 
                    - [The Central Park Squirrel Census](https://www.thesquirrelcensus.com/)
                    - [NYC OpenData](https://data.cityofnewyork.us/Environment/2018-Central-Park-Squirrel-Census-Squirrel-Data/vfnx-vebw) 
                    - [Squirrel Image,](https://www.trzcacak.rs/myfile/full/50-509839_squirrel-black-and-white-free-squirrel-clipart-cartoon.png) [ Arrow Image](https://commons.wikimedia.org/wiki/File:Simpleicons_Interface_arrow-pointing-to-right.svg)
                    
                    #### Contributions:  
                    - The original version of this app was created with Roc Zhang and Lori Feng as a group project in UBC's Master of Data Science Program. The original app can be viewed [here](https://dsci-532-group203-milestone2.herokuapp.com/), and the original Github repository can be viewed [here](https://github.com/UBC-MDS/DSCI-532_group-203_Lab1-2).
                    """
                ])
    ])

@app.callback(
    dash.dependencies.Output('plot', 'srcDoc'),
    [dash.dependencies.Input('dd-chart', 'value')])

def update_plot(yaxis_column_name):
    '''
    Takes in an xaxis_column_name and calls make_plot to update our Altair figure
    '''
    updated_plot = make_plot(yaxis_column_name).to_html()
    return updated_plot


if __name__ == '__main__':
    app.run_server(debug=True)

