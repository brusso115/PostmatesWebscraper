import pandas as pd
import numpy as np
import plotly
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.io as plt_io
from matplotlib.pyplot import cm

app = dash.Dash(__name__)

# ---------- Import and clean data, set token (importing csv into pandas)
# Plotly Express
token = 'pk.eyJ1IjoiYmJydXNzbzExNSIsImEiOiJja29qY2x4Z2wwMnk3MnBvNzRldXo2a2J2In0.6zgZNfkLxe6DylEBbMglZA'
postmates = pd.read_csv("postmates_all.csv")
postmates = postmates.loc[:, ~postmates.columns.str.contains('^Unnamed')]

# Add scale column to scale favorites column
postmates_grouped = postmates.groupby(['Name', 'Category']).mean().reset_index()
fav_scaled = (postmates_grouped["Favorites"].max() - postmates_grouped["Favorites"].min()) / 16
postmates_grouped["scale"] = (postmates_grouped["Favorites"] - postmates_grouped[
    "Favorites"].min()) / fav_scaled + 1


# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.H1("Postmates Restaurant Data", style={'text-align': 'center', 'backgroundColor':'rgb(17,17,17)', 'color': 'white'}),

    dcc.Dropdown(id="slct_category",
                 options=[{'label': i, 'value': i} for i in np.unique(np.array(postmates['Category'].values))],
                 multi=True,
                 value=[],
                 style={'backgroundColor': 'rgb(51,52,50)', 'color': 'rgb(51,52,50)', 'border': 'rgb(17,17,17)'}
    ),

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='postmates_map',figure={}),



])

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    Output(component_id='postmates_map', component_property='figure'),
    [Input(component_id='slct_category', component_property='value')]
)
def update_graph(option_slctd):

    if option_slctd == []:
        postmatesGrouped = postmates_grouped[postmates_grouped['Category'].isin(list(postmates_grouped['Category']))]
    else:
        postmatesGrouped = postmates_grouped[postmates_grouped['Category'].isin(option_slctd)]

    fig = px.scatter_mapbox(postmatesGrouped, lat="Latitude", lon="Longitude",
                            size="scale", hover_name="Name", hover_data=["Favorites"], color="Category", zoom=10,
                            height=800, template="plotly_dark",
                            )
    fig.update_layout(mapbox_style="dark", mapbox_accesstoken=token)
    fig.update_traces(marker={'sizemin': 4})
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.update_layout(uirevision=True)

    return fig

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)

