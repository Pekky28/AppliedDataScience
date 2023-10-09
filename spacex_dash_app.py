# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Get a list of unique launch sites
launch_sites = spacex_df['Launch Site'].unique()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    dcc.Dropdown(
        id='site-dropdown',  # Unique identifier for the Dropdown
        options=[{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
        value='ALL',  # Default value when the app starts
        placeholder="Select a Launch Site here",  # Placeholder text
        searchable=True  
    ),
    
    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    
    # TASK 3: Add a slider to select payload range
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',  
        min=0,                
        max=10000,            
        step=1000,            
        marks={0: '0', 10000: '10,000'},  
        value=[min_payload, max_payload]  
    ),
    
    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Define callback to update pie chart based on selected launch site
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(selected_site):
    if selected_site == 'ALL':
        title = 'Total Success Launches for All Sites'
        # Count the number of successful and failed launches for each site
        success_counts = []
        failed_counts = []
        site_colors = []
        for site in launch_sites:
            site_df = spacex_df[spacex_df['Launch Site'] == site]
            success_count = site_df[site_df['class'] == 1]['class'].count()
            failed_count = site_df[site_df['class'] == 0]['class'].count()
            success_counts.append(success_count)
            failed_counts.append(failed_count)
            site_colors.append(site)
        
        # Create a pie chart figure with different colors for each site
        fig = px.pie(
            values=success_counts + failed_counts,
            names=site_colors + site_colors,
            title=title,
            labels={'names': 'Launch Site'},
            color_discrete_sequence=px.colors.qualitative.Set3
        )
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]  # Filter data for the selected site
        title = f'Success vs. Failed Launches for {selected_site}'

        # Count the number of successful and failed launches in the filtered DataFrame
        success_count = filtered_df[filtered_df['class'] == 1]['class'].count()
        failed_count = filtered_df[filtered_df['class'] == 0]['class'].count()

        # Create a pie chart figure for the selected site
        fig = px.pie(
            values=[success_count, failed_count],
            names=['Success', 'Failed'],
            title=title,
            labels={'class': 'Launch Outcome'},
            color_discrete_map={1: 'green', 0: 'red'}
        )

    return fig

# TASK 4: Define callback to update scatter chart based on selected launch site and payload range
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    if selected_site == 'ALL':
        filtered_df = spacex_df  
        title = 'Correlation Between Payload and Launch Success for All Sites'
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]  # Filter data for the selected site
        title = f'Correlation Between Payload and Launch Success for {selected_site}'

    filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= payload_range[0]) & (filtered_df['Payload Mass (kg)'] <= payload_range[1])]

    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=title,
        labels={'class': 'Launch Outcome'},
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
