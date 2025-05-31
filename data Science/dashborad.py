import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Sample SpaceX launch data (replace this with your actual spacex_df)
spacex_df = pd.read_csv('.//spacex_launch_dash.csv')

launch_sites = spacex_df['Launch Site'].unique()
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
                   [{'label': site, 'value': site} for site in launch_sites]

min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': '40px'}),

    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),

    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload]
    ),

    dcc.Graph(id='success-pie-chart'),

    dcc.Graph(id='success-payload-scatter-chart')  # Scatter plot for TASK 4
])

@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        success_counts = spacex_df[spacex_df['class'] == 1] \
            .groupby('Launch Site').size().reset_index(name='success count')

        fig = px.pie(
            success_counts,
            values='success count',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]

        outcome_counts = filtered_df['class'].value_counts().reset_index()
        outcome_counts.columns = ['class', 'count']
        outcome_counts['class'] = outcome_counts['class'].map({1: 'Success', 0: 'Failure'})

        fig = px.pie(
            outcome_counts,
            values='count',
            names='class',
            title=f'Success vs Failure Launches for site {entered_site}'
        )
        return fig

@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    # Filter data by payload range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]

    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df, x='Payload Mass (kg)', y='class',
            color='Booster Version Category',
            title='Payload vs. Outcome for All Sites',
            labels={'class': 'Launch Outcome (0=Fail, 1=Success)'}
        )
        return fig
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]

        fig = px.scatter(
            filtered_df, x='Payload Mass (kg)', y='class',
            color='Booster Version Category',
            title=f'Payload vs. Outcome for Site {entered_site}',
            labels={'class': 'Launch Outcome (0=Fail, 1=Success)'}
        )
        return fig

if __name__ == '__main__':
    app.run(debug=True, port=8051)

booster_success_rate = spacex_df.groupby('Booster Version Category')['class'].mean().sort_values(ascending=False)
print(booster_success_rate)
