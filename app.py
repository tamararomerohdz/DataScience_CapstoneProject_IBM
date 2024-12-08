from dash import Dash, dcc, html
import dash.dependencies as dd
import pandas as pd
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("Datasets/spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Initialize the Dash app
app = Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] +
                [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()], 
        value='ALL',  # Default value
        placeholder="Select a Launch Site here", searchable=True),
    html.Br(),

    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # Store data in the browser to avoid reloading it
    dcc.Store(id='spacex-data', data=spacex_df.to_dict('records')),

    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=2500,
        marks={i: str(i) for i in range(0, 10001, 2500)},
        value=[min_payload, max_payload]),
    html.Br(),

    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Add the client-side callback for the pie chart
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
     dd.Input('spacex-data', 'data')]
)

# Add the client-side callback for the scatter chart
app.clientside_callback(
    """
    function(selected_site, payload_range, spacex_data) {
        if (!spacex_data) return {data: [], layout: {title: "No Data Available"}};
        
        // Filter the data by payload range
        let filtered_data = spacex_data.filter(row => 
            row['Payload Mass (kg)'] >= payload_range[0] && 
            row['Payload Mass (kg)'] <= payload_range[1]
        );
        
        if (selected_site !== 'ALL') {
            filtered_data = filtered_data.filter(row => row['Launch Site'] === selected_site);
        }

         // Create scatter plot data
        return {
            data: [{
                type: 'scatter',
                x: filtered_data.map(row => row['Payload Mass (kg)']),
                y: filtered_data.map(row => row['class']),
                mode: 'markers',
                marker: {
                    color: filtered_data.map(row => row['Booster Version Category']),
                    colorscale: 'Viridis',  // Using Viridis colorscale
                    showscale: true,  // Display the color scale
                    colorbar: {
                        title: 'Booster Version Category'  // Adding a colorbar with a title
                    }
                },
                name: 'Launch Success'
            }],
            layout: {
                title: 'Correlation between Payload and Success for Selected Site',
                xaxis: { title: 'Payload Mass (kg)' },
                yaxis: { title: 'Success (1) / Failure (0)' },
                showlegend: true,  // Show the legend
                legend: {
                    orientation: 'h',  // Horizontal layout for legend
                    x: 0.5,  // Center the legend
                    xanchor: 'center',
                    y: -0.2,  // Position the legend below the plot
                    yanchor: 'top'
                }
            }
        };
    }
    """,
    dd.Output('success-payload-scatter-chart', 'figure'),
    [dd.Input('site-dropdown', 'value'),
     dd.Input('payload-slider', 'value'),
     dd.Input('spacex-data', 'data')]
)

if __name__ == '__main__':
    app.run_server(debug=False)

