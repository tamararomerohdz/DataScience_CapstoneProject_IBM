# Import required libraries
from dash import Dash, dcc, html
import dash.dependencies as dd
import pandas as pd
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("Datasets/spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Initialize the Dash app
# 
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                options=[{'label': 'All Sites', 'value': 'ALL'}] + 
                                [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()], 
                                value='ALL',  # Default value
                                placeholder="Select a Launch Site here", searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                #Add the serialized spacex_df data as a dcc.Store component
                                dcc.Store(id='spacex-data', data=spacex_df.to_dict('records')),
                                
                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                min=0, max=10000, step=2500,
                                marks={i: str(i) for i in range(0, 10001, 2500)},
                                value=[min_payload, max_payload]),
                                html.Br(),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# Client-side callback (JavaScript function)
app.clientside_callback(
    """
    function(selected_site, spacex_data) {
        if (!spacex_data) return {data: [], layout: {title: "No Data Available"}};
        
        if (selected_site === 'ALL') {
            let total = {};
            spacex_data.forEach(row => {
                total[row['Launch Site']] = (total[row['Launch Site']] || 0) + row['class'];
            });
            let names = Object.keys(total);
            let values = Object.values(total);
            return {
                data: [{
                    type: 'pie',
                    labels: names,
                    values: values,
                }],
                layout: {
                    title: 'Total Success Launches by Site'
                }
            };
        } else {
            let filtered_data = spacex_data.filter(row => row['Launch Site'] === selected_site);
            let success = filtered_data.filter(row => row['class'] === 1).length;
            let failure = filtered_data.length - success;
            return {
                data: [{
                    type: 'pie',
                    labels: ['Success', 'Failure'],
                    values: [success, failure],
                }],
                layout: {
                    title: `Success vs. Failure for site ${selected_site}`
                }
            };
        }
    }
    """,
    dd.Output('success-pie-chart', 'figure'),
    [dd.Input('site-dropdown', 'value'),
     dd.Input('spacex-data', 'data')]  # Pass data from dcc.Store
)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)
