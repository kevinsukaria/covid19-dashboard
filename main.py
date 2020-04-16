import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from function import refresh_data, generate_geo
from feeds import refresh_news
from layout_components import update_cards, news_cards_generator, country_filtering

dash_link = 'https://plotly.com/dash/'
ln_link = 'https://www.linkedin.com/in/kevin-sukaria-23a155137/'
PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"
Covid_API = "https://rapidapi.com/Gramzivi/api/covid-19-data/endpoints"
News_API = 'https://newsapi.org/'
GCP_link = 'https://cloud.google.com/appengine/'
github = 'https://github.com/kevinsukaria/covid19-dashboard.git'

metas = [
    {'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}
]
external_stylesheets = [dbc.themes.DARKLY]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, meta_tags=metas)
app.title = 'COVID-19 Dashboard'
app.config['suppress_callback_exceptions'] = True
server = app.server
df, df_region, table = refresh_data()
query = 'corona'
source = ''

dashboard = html.Div([
    dbc.Row([
        dbc.Col(dbc.Row([
            html.H3(['Worldwide Cases : ', 'Loading...']),
            dbc.Button("Refresh", color="primary", id='data_refresh', className='button hidden'),
        ]), id="main-col-1", lg=7, md=12, ),

        dbc.Col([
            html.H3("Today's News", style={'margin-left': '0.5em'}),
            dbc.Row([
                dbc.Col(
                    dbc.Input(type="search", placeholder="Search today's news", id="search_bar", autoComplete='off'),
                    width=10),
                dbc.Col(dbc.Button("Refresh", color="primary", id='news_refresh'), width=2),
            ], id='news_search'),
            html.Div(html.H3('Loading...'), id='news-feeds')
        ], id="main-col-2", lg=5, md=12)
    ]),

], id='container fluid')

about = dbc.Jumbotron([
    html.H2('Global COVID-19 Dashboard'),
    html.H4(['Created by : ', html.A('Kevin Sukaria', href=ln_link)], className='lead'),
    html.Hr(className="my-2"),
    html.P([
        """
        This dashboard is built with """, html.A('Dash', href=dash_link), """, an open source Python framework that allows 
        developer to build interactive web application or data visualization in pure Python. COVID-19 data source that 
        are used for this dashboard are acquired
        from """, html.A('COVID-19 Data API', href=Covid_API), """, which collects information from several reliable 
        sources such as Johns Hopkins CSSE, CDC, and WHO and is refreshed every 15 minutes. News feed are powered by 
        """, html.A('News API', href=News_API), """, which provide access to news from from all around the globe in 
        various language. For this dashboard, only news in English language are retrieved. The free tier
         of the news API is 500 requests per day so if you find that the news feed is not working anymore, it might be that 
         the endpoint has reached its requests limit. This Web Application 
        is hosted using """, html.A('Google App Engine', href=GCP_link), """ service.
        """
    ]),
    html.Br(),
    html.P(
        """
        This dashboard is born from the creator's attempt to leverage the current COVID-19 pandemic situation to learn something 
         new and useful. Therefore, the goal of this dashboard is mainly for learning purpose and not in any way 
         attempts to replace or even mislead users from official sources. When in doubt, always refer back to official source 
         of your own respective country.
        """
    ),
    html.Br(),
    html.P([
        """
        Hopefully this dashboard can provide new insights on the current pandemic situation or  
        inspire people to stay productive and view the current situation as a learning opportunity. The source code for
        this project is available on my """, html.A('github', href=github), """
        """
    ]),

    html.Br(),
    html.P(
        """
        Stay productive and stay safe :) 
        """
    ),

])

app.layout = \
    html.Div([
        html.H4(html.Strong('GLOBAL COVID-19 DASHBOARD'), id='title'),
        dbc.Tabs(
            [
                dbc.Tab(dashboard, label="Dashboard"),
                dbc.Tab(about, label="About"),
            ]
        )
    ])


@app.callback(
    Output('news-feeds', 'children'),
    [Input('news_refresh', 'n_clicks')],
    state=[State('search_bar', 'value')]
)
def update_news_feed(n_clicks, input1):
    if input1 == None:
        input1 = query
    try:
        news_feed = refresh_news(input1, source)
        news_cards = news_cards_generator(news_feed)
    except:
        news_cards = html.H1('No news found')
    return news_cards


@app.callback(
    Output('main-col-1', 'children'),
    [
        Input('data_refresh', 'n_clicks'),
    ]
)
def update_data(n_clicks):
    global df
    global table
    df, df_region, table = refresh_data()
    output = [
        update_cards(df),
        dcc.Graph(
            id='geo-chart',
            figure=generate_geo(df),
            animate=False
        ),
        html.H3('Regional Information'),
        dbc.Table.from_dataframe(table, striped=True, bordered=True, hover=True, responsive=True),
    ]
    return output


@app.callback([
    Output('metric-title', 'children'),
    Output('metric', 'children'),
    Output('geo-chart', 'figure'),
],
    [Input('dropdown', 'value')])
def country_filter(value):
    if value == (None or 'Worldwide'):
        value = 'Worldwide'
        filtered_df = df
        filtered_region = df
    else:
        filtered_df = df[df.country == value]
        try:
            filtered_region = df[df['sub-region'] == filtered_df['sub-region'].values[0]]
        except:
            filtered_df = df
            filtered_region = df
    filtered_title, filtered_cards = country_filtering(filtered_df, value)
    filtered_figure = generate_geo(filtered_region)
    return filtered_title, filtered_cards, filtered_figure


if __name__ == '__main__':
    app.run_server(debug=False)
