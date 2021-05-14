import pandas as pd
import numpy as np
import plotly
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import plotly.io as plt_io
from matplotlib.pyplot import cm

app = dash.Dash(__name__)

# ---------- Import and clean data, set token (importing csv into pandas)
# Plotly Express
token = 'pk.eyJ1IjoiYmJydXNzbzExNSIsImEiOiJja29qY2x4Z2wwMnk3MnBvNzRldXo2a2J2In0.6zgZNfkLxe6DylEBbMglZA'
postmates = pd.read_csv("postmates_all6.csv")
postmates = postmates.loc[:, ~postmates.columns.str.contains('^Unnamed')]

postmatesBOW = pd.read_csv("postmates_BOW.csv")
#postmatesBOW = postmates.loc[:, ~postmatesBOW.columns.str.contains('^Unnamed')]
print(postmatesBOW.columns)


# Add scale column to scale favorites column
postmates_grouped = postmates.groupby(['Name', 'Category', 'Latitude', 'Longitude']).mean().reset_index()
fav_scaled = (postmates_grouped["Favorites"].max() - postmates_grouped["Favorites"].min()) / 16
postmates_grouped["scale"] = (postmates_grouped["Favorites"] - postmates_grouped[
    "Favorites"].min()) / fav_scaled + 1

#Train model
count = CountVectorizer()
countVec = count.fit(postmatesBOW['BagOfWords'])
count_matrix = countVec.transform(postmatesBOW['BagOfWords'])

#Plot map figure
fig = px.scatter_mapbox(postmates_grouped, lat="Latitude", lon="Longitude",
                        size="scale", hover_name="Name", hover_data=["Favorites"], color="Category", zoom=10,
                        height=800, template="plotly_dark",
                        )
fig.update_layout(mapbox_style="dark", mapbox_accesstoken=token)
fig.update_traces(marker={'sizemin': 4})
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.update_layout(uirevision=True)

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.H1("Postmates Restaurant Data", style={'text-align': 'center', 'backgroundColor':'rgb(17,17,17)', 'color': 'white'}),

    html.Div(id='output_container', children=[]),
    #html.Br(),

    dcc.Graph(id='postmates_map', figure=fig),

    #html.Br(),

    html.H1("Find Food Your In The Mood For", style={'text-align': 'center', 'backgroundColor':'rgb(17,17,17)', 'color': 'white'}),

    dcc.Input(
        id='meal_description',
        placeholder='Describe the meal you are in the mood for...',
        type='text',
        value='',
        style={'height': '40px','backgroundColor':'rgb(51, 52, 50)','border': 'rgb(17,17,17)',
               'border-radius': '5px', 'width':'99%','color':'white','padding-left':'10px'},
        #return fig
    ),

    html.Br(),
    html.Br(),

    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in postmates.columns[[0, 4, 5, 6]]],
        #data=postmates.to_dict('records'),
        style_cell={
            'whiteSpace': 'normal',
            'height': 'auto',
            'backgroundColor': 'rgb(17, 17, 17)',
            'color': 'white'
        },
        style_header={
            'backgroundColor': 'rgb(30, 30, 30)',
            'fontWeight': 'bold'
        },
        style_cell_conditional=[

            {'if': {'column_id': 'Name'},
                'textAlign': 'left'},

            {'if': {'column_id': 'MenuItem'},
             'textAlign': 'left'},

            {'if': {'column_id': 'MenuItemDescription'},
             'textAlign': 'left'},

            {'if': {'column_id': 'Name'},
                  'width': '15%'},
        ],

        style_as_list_view=True
    )

])

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
'''
@app.callback(
    Output(component_id='postmates_map', component_property='figure')
    #[Input(component_id='slct_category', component_property='value')]
)
def update_graph():
    
    if option_slctd == []:
        postmatesGrouped = postmates_grouped[postmates_grouped['Category'].isin(list(postmates_grouped['Category']))]
    else:
        postmatesGrouped = postmates_grouped[postmates_grouped['Category'].isin(option_slctd)]
    

    postmatesGrouped = postmates_grouped.copy()

    fig = px.scatter_mapbox(postmatesGrouped, lat="Latitude", lon="Longitude",
                            size="scale", hover_name="Name", hover_data=["Favorites"], color="Category", zoom=10,
                            height=800, template="plotly_dark",
                            )
    fig.update_layout(mapbox_style="dark", mapbox_accesstoken=token)
    fig.update_traces(marker={'sizemin': 4})
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.update_layout(uirevision=True)

    return fig
'''

@app.callback(
    Output(component_id='table', component_property='data'),
    [Input(component_id='meal_description', component_property='value')]
)
def update_table(meal_description):

    postmatesBOWCopy = postmatesBOW.copy()

    user_input = [meal_description]
    count_matrix_inp = countVec.transform(user_input)

    cosine_sim = cosine_similarity(count_matrix, count_matrix_inp)
    most_similar = cosine_sim[:, 0].argsort(axis=0)[::-1]

    postmatesBOWCopy = postmatesBOWCopy.iloc[most_similar].head(50)

    return postmatesBOWCopy.to_dict('records')

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)

