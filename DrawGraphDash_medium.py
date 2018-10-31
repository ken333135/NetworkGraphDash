# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 16:49:11 2018

@author: jingwenken
"""

import pandas as pd

df = pd.read_csv('assoc_rules_medium.csv')
df['itemset'] = df['itemset'].apply(lambda x: x.replace('(',''))
df['itemset'] = df['itemset'].apply(lambda x: x.replace(')',''))
df['itemset'] = df['itemset'].apply(lambda x: x.replace(' ',''))
df['itemset'] = df['itemset'].apply(lambda x: x.split(','))
df.sort_values(['count'],ascending=False,inplace=True)

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go

import networkx as nx

num_nodes = 2000
edge = df['itemset'][:num_nodes]

#create graph G
G = nx.Graph()
#G.add_nodes_from(node)
G.add_edges_from(edge)
#get a x,y position for each node
pos = nx.layout.spring_layout(G)

#add a pos attribute to each node
for node in G.nodes:
    G.nodes[node]['pos'] = list(pos[node])

##from the docs, create a random geometric graph for test
#G=nx.random_geometric_graph(200,0.125)
pos=nx.get_node_attributes(G,'pos')


dmin=1
ncenter=0
for n in pos:
    x,y=pos[n]
    d=(x-0.5)**2+(y-0.5)**2
    if d<dmin:
        ncenter=n
        dmin=d

p=nx.single_source_shortest_path_length(G,ncenter)

#Create Edges
edge_trace = go.Scatter(
    x=[],
    y=[],
    line=dict(width=0.5,color='#888'),
    hoverinfo='none',
    mode='lines')

for edge in G.edges():
    x0, y0 = G.node[edge[0]]['pos']
    x1, y1 = G.node[edge[1]]['pos']
    edge_trace['x'] += tuple([x0, x1, None])
    edge_trace['y'] += tuple([y0, y1, None])

node_trace = go.Scatter(
    x=[],
    y=[],
    text=[],
    mode='markers',
    hoverinfo='text',
    marker=dict(
        showscale=True,
        # colorscale options
        #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
        #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
        #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
        colorscale='YlGnBu',
        reversescale=True,
        color=[],
        size=10,
        colorbar=dict(
            thickness=15,
            title='Node Connections',
            xanchor='left',
            titleside='right'
        ),  
        line=dict(width=2)))

for node in G.nodes():
    x, y = G.node[node]['pos']
    node_trace['x'] += tuple([x])
    node_trace['y'] += tuple([y])

#add color to node points
for node, adjacencies in enumerate(G.adjacency()):
    node_trace['marker']['color']+=tuple([len(adjacencies[1])])
    node_info = 'Name: ' + str(adjacencies[0]) + '<br># of connections: '+str(len(adjacencies[1]))
    node_trace['text']+=tuple([node_info])


################### START OF DASH APP ###################

app = dash.Dash()

# to add ability to use columns
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})


fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title='<br>Network Graph of '+str(num_nodes)+' rules',
                titlefont=dict(size=16),
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[ dict(
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002 ) ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

app.layout = html.Div([
                html.Div(dcc.Graph(id='Graph',figure=fig)),
                html.Div(className='row', children=[
                    html.Div([html.H2('Overall Data'),
                              html.P('Num of nodes: ' + str(len(G.nodes))),
                              html.P('Num of edges: ' + str(len(G.edges)))],
                              className='three columns'),
                    html.Div([
                            html.H2('Selected Data'),
                            html.Div(id='selected-data'),
                        ], className='six columns')
                    ])
                ])


@app.callback(
    Output('selected-data', 'children'),
    [Input('Graph','selectedData')])
def display_selected_data(selectedData):
    num_of_nodes = len(selectedData['points'])
    text = [html.P('Num of nodes selected: '+str(num_of_nodes))]
    for x in selectedData['points']:
#        print(x['text'])
        material = x['text'].split('<br>')[0][7:]
        text.append(html.P(str(material)))
    return text

if __name__ == '__main__':
    app.run_server(debug=True)