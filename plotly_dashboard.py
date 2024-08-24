import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Load the CSV data
df = pd.read_csv('cleaned_aqi_data.csv')

# Initialize the Dash app
app = dash.Dash(__name__)

# Extract the unique states and cities
states = df['state'].unique()
cities_by_state = {state: df[df['state'] == state]['location'].unique() for state in states}

# Layout of the dashboard
app.layout = html.Div([
    html.H1("Air Quality Dashboard (India)", style={'textAlign': 'center'}),
    
    html.Div([
        html.Label("Select State:"),
        dcc.Dropdown(
            id='state-dropdown',
            options=[{'label': state, 'value': state} for state in states],
            value=states[0]  # Default to the first state
        ),
    ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),

    html.Div([
        html.Label("Select City:"),
        dcc.Dropdown(
            id='city-dropdown',
        ),
    ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),

    dcc.Graph(id='aqi-graph'),
    dcc.Graph(id='pie-chart'),
    
    html.Div([
        dcc.Graph(id='comparison-graph'),
    ], style={'padding': '10px'}),

    # Additional content regarding AQI and guidelines
    html.Div([
        html.H3("AQI Guidelines for Selected City"),
        html.Div(id='aqi-guidelines', style={'padding': '10px', 'backgroundColor': '#f9f9f9', 'borderRadius': '5px'}),
    ], style={'padding': '20px'}),
])

# Update city dropdown based on selected state
@app.callback(
    Output('city-dropdown', 'options'),
    Output('city-dropdown', 'value'),
    Input('state-dropdown', 'value')
)
def update_city_dropdown(selected_state):
    cities = cities_by_state[selected_state]
    return [{'label': city, 'value': city} for city in cities], cities[0]

# Update AQI graph based on selected city
@app.callback(
    Output('aqi-graph', 'figure'),
    Output('pie-chart', 'figure'),
    Input('state-dropdown', 'value'),
    Input('city-dropdown', 'value')
)
def update_aqi_graph(selected_state, selected_city):
    filtered_df = df[(df['state'] == selected_state) & (df['location'] == selected_city)]
    
    # Line graph for pollutants over time
    line_fig = px.line(filtered_df, x='date', y=['so2', 'no2', 'rspm', 'spm', 'pm2_5'], 
                       title=f"AQI Data for {selected_city}")
    line_fig.update_layout(xaxis_title="Date", yaxis_title="Concentration", showlegend=True)
    
    # Pie chart for pollutant concentration distribution
    latest_data = filtered_df.iloc[-1]
    pie_fig = px.pie(values=[latest_data['so2'], latest_data['no2'], latest_data['rspm'], latest_data['spm'], latest_data['pm2_5']],
                     names=['SO2', 'NO2', 'RSPM', 'SPM', 'PM2.5'],
                     title=f"Pollutant Concentration in {selected_city}")
    
    return line_fig, pie_fig

# Update comparison graph for all cities within the state
@app.callback(
    Output('comparison-graph', 'figure'),
    Input('state-dropdown', 'value')
)
def update_comparison_graph(selected_state):
    state_df = df[df['state'] == selected_state]
    
    # Group data by city and calculate the average concentration for each pollutant
    avg_pollutants_by_city = state_df.groupby('location')[['so2', 'no2', 'rspm', 'spm', 'pm2_5']].mean().reset_index()

    # Bar chart for pollutant comparison across cities
    fig = px.bar(avg_pollutants_by_city, x='location', y=['so2', 'no2', 'rspm', 'spm', 'pm2_5'], 
                 title=f"AQI Comparison for Cities in {selected_state}")
    fig.update_layout(xaxis_title="City", yaxis_title="Average Concentration")
    return fig

# Display AQI guidelines for the selected city
@app.callback(
    Output('aqi-guidelines', 'children'),
    Input('city-dropdown', 'value')
)
def update_aqi_guidelines(selected_city):
    return html.Ul([
        html.Li("Avoid outdoor activities if the AQI is unhealthy."),
        html.Li("Wear masks in highly polluted areas."),
        html.Li("Use air purifiers indoors."),
        html.Li("Limit the use of vehicles to reduce emissions."),
        html.Li("Monitor AQI levels regularly if you have respiratory issues."),
    ])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
