import dash
from dash import dcc, html, Input, Output, State
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objs as go

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the app layout and link the external CSS file
app.layout = html.Div([
    html.Link(
        rel='stylesheet',
        href='/assets/styles.css'  # Correct path to your CSS file
    ),
    html.H1("Stock Candlestick Chart", className="page-header custom-header"),
    html.Div([
        html.Label("Select Stock Symbol:", className="label custom-primary"),
        dcc.Input(id="input-symbol", type="text", value="AAPL", className="input"),
    ]),
    html.Div([
        html.Label("Select Date Range:", className="label custom-primary"),
        dcc.DatePickerRange(
            id="date-picker",
            start_date="2022-01-01",
            end_date="2022-12-31",
            className="date-picker",
        ),
    ]),
    html.Div([
        # User Settings: Customize chart appearance
        html.Label("Chart Settings:", className="label custom-primary"),
        dcc.Checklist(
            id="chart-settings",
            options=[
                {'label': 'Show Moving Averages', 'value': 'show-ma'},
                {'label': 'Show Volume', 'value': 'show-volume'},
            ],
            className="custom-checkbox",
            value=[],
        ),
    ]),
    html.Button("Update Chart", id="update-button", n_clicks=0, className="button custom-secondary"),
    dcc.Graph(id="candlestick-graph"),
    html.Div(id="error-message", className="error-message"),

    # Data Insights: Daily Price Change chart
    dcc.Graph(id="daily-price-change-graph", className="insights-graph"),

    # Include a link to download the example file
    html.Div([
        html.Label("Download Example File:", className="label custom-primary"),
        html.A(
            "Download",
            href="/assets/example.pdf",  # Specify the path to your file in the "assets" folder
            target="_blank",
            className="download-link",
        ),
    ]),
])

# Define a callback function for the candlestick chart
@app.callback(
    Output('candlestick-graph', 'figure'),
    Output('error-message', 'children'),
    Output('daily-price-change-graph', 'figure'),  # Data Insights
    Input('update-button', 'n_clicks'),
    State('input-symbol', 'value'),
    State('date-picker', 'start_date'),
    State('date-picker', 'end_date'),
    State('chart-settings', 'value'),  # User Settings
)
def update_candlestick_chart(n_clicks, selected_symbol, start_date, end_date, chart_settings):
    if n_clicks > 0:
        try:
            # Fetch historical data using yfinance
            df = yf.download(selected_symbol, start=start_date, end=end_date)

            # Calculate 50-day and 200-day moving averages if selected in User Settings
            show_ma = 'show-ma' in chart_settings
            if show_ma:
                df['50-day MA'] = ta.sma(df['Close'], length=50)
                df['200-day MA'] = ta.sma(df['Close'], length=200)

            # Create a candlestick chart using Plotly
            figure = go.Figure(data=[go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Candlesticks',
            )])

            # Overlay the moving averages on the chart if selected in User Settings
            if show_ma:
                figure.add_trace(go.Scatter(
                    x=df.index,
                    y=df['50-day MA'],
                    mode='lines',
                    name='50-day MA',
                ))

                figure.add_trace(go.Scatter(
                    x=df.index,
                    y=df['200-day MA'],
                    mode='lines',
                    name='200-day MA',
                ))

            figure.update_layout(
                title=f'Candlestick Chart for {selected_symbol}',
                xaxis_title='Date',
                yaxis_title='Price',
                xaxis_rangeslider_visible=False,
                # Change the background color of the chart
                paper_bgcolor='lightgray',  # Specify your desired background color
            )

            # Data Insights: Daily Price Change chart
            daily_price_change_figure = go.Figure(data=[go.Bar(
                x=df.index,
                y=df['Close'] - df['Open'],
                name='Daily Price Change',
            )])
            daily_price_change_figure.update_layout(
                title='Daily Price Change',
                xaxis_title='Date',
                yaxis_title='Price Change',
            )

            return figure, "", daily_price_change_figure
        except Exception as e:
            return go.Figure(), f"Error: {str(e)}", go.Figure()

    else:
        return go.Figure(), "", go.Figure()

if __name__ == '__main__':
    app.run_server(debug=True)
