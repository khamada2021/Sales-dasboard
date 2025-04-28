import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly.express as px

# Load and prepare data
df = pd.read_csv('Superstore.csv', encoding='latin1')
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['Year'] = df['Order Date'].dt.year
df['Month'] = df['Order Date'].dt.month_name()
df = df.sort_values('Order Date')

# Initialize Dash app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("Superstore Sales Dashboard", 
            style={'textAlign': 'center', 'color': '#2B547E', 'padding': '20px'}),
    
    # Filters
    html.Div([
        dcc.Dropdown(
            id='region-dropdown',
            options=[{'label': 'All Regions', 'value': 'All Regions'}] + 
                    [{'label': region, 'value': region} for region in df['Region'].unique()],
            value='All Regions',
            style={'width': '50%', 'margin': '20px'}
        ),
        dcc.DatePickerRange(
            id='date-picker',
            start_date=df['Order Date'].min(),
            end_date=df['Order Date'].max(),
            display_format='YYYY-MM-DD',
            style={'margin': '20px'}
        )
    ], style={'display': 'flex', 'justifyContent': 'center'}),
    
    # Key Metrics
    html.Div([
        html.Div(f"Total Sales: ${df['Sales'].sum():,.0f}", 
                style={'padding': '20px', 'fontSize': 20, 'background': '#f0f0f0', 'margin': '10px'}),
        html.Div(f"Total Profit: ${df['Profit'].sum():,.0f}", 
                style={'padding': '20px', 'fontSize': 20, 'background': '#f0f0f0', 'margin': '10px'})
    ], style={'display': 'flex', 'justifyContent': 'center'}),
    
    # Graphs
    dcc.Graph(id='sales-trend', style={'margin': '20px', 'height': '500px'}),
    dcc.Graph(id='profit-by-category', style={'margin': '20px', 'height': '500px'})
])

# Callback for sales trend
@app.callback(
    Output('sales-trend', 'figure'),
    [Input('region-dropdown', 'value'),
     Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_sales_trend(selected_region, start_date, end_date):
    filtered_df = df.copy()
    
    if selected_region != 'All Regions':
        filtered_df = filtered_df[filtered_df['Region'] == selected_region]
    
    filtered_df = filtered_df[
        (filtered_df['Order Date'] >= start_date) & 
        (filtered_df['Order Date'] <= end_date)
    ]
    
    monthly_sales = filtered_df.groupby(['Year', 'Month'], observed=False)['Sales'].sum().reset_index()
    
    fig = px.line(
        monthly_sales, 
        x='Month', 
        y='Sales', 
        color='Year',
        title='Monthly Sales Trend',
        markers=True
    )
    fig.update_layout(plot_bgcolor='white', paper_bgcolor='#f9f9f9')
    return fig

# Callback for profit by category
@app.callback(
    Output('profit-by-category', 'figure'),
    [Input('region-dropdown', 'value')]
)
def update_profit_chart(selected_region):
    filtered_df = df.copy()
    if selected_region != 'All Regions':
        filtered_df = filtered_df[filtered_df['Region'] == selected_region]
    
    profit_df = filtered_df.groupby('Category')['Profit'].sum().reset_index()
    
    fig = px.bar(
        profit_df, 
        x='Category', 
        y='Profit',
        title='Profit by Product Category',
        color='Category'
    )
    fig.update_layout(plot_bgcolor='white', paper_bgcolor='#f9f9f9')
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)  # Corrected line for latest Dash versions