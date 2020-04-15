import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

dash_link = 'https://plotly.com/dash/'
twitter_link = 'https://developer.twitter.com/en/docs/api-reference-index'
ln_link = 'https://www.linkedin.com/in/kevin-sukaria-23a155137/'
PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

header = html.Div()

def news_cards_generator(news_feed):
    news_cards = \
        [

            dbc.Col(dbc.Card([
                dbc.CardBody(dbc.Row([
                    dbc.Col([
                        html.A(html.H5(val['title']), href=val['url']),
                        html.P(['Source : ', val['source_name']], style={'margin': '0.1em'}),
                    ], width=9),
                    dbc.Col(html.Img(src=val['img'], style={'width': '100%'}), width=3)
                ])),

            ]), className='news-cards')

            for val in news_feed]
    return news_cards


# def news_carousel(news_feed):
#     carousel_items = []
#     i = 0
#     state = ' active'
#     for val in news_feed:
#         if i > 0:
#             state = ''
#
#         item = \
#             html.Div([
#                 html.Img(src=val['img']),
#                 html.Div([
#                     html.A(html.H3(val['title']), href=val['url']),
#                     html.P(val['desc']),
#                     html.Em(
#                         (to_datetime(val['published']) + dt.timedelta(hours=7)).strftime('%A %d %B %Y | %H:%M GMT+7'))
#                 ]),
#
#             ], className="carousel-item" + state)
#         carousel_items.append(item)
#         i += 1
#
#     carousel_inner = html.Div(carousel_items, className="carousel-inner")
#
#     prev = html.A(html.Span(className="carousel-control-prev-icon"),
#                   className="carousel-control-prev",
#                   href="#news-carousel",
#                   role="button",
#                   **{'data-slide': 'prev'})
#
#     next = html.A(html.Span(className="carousel-control-next-icon"),
#                   className="carousel-control-next",
#                   href="#news-carousel",
#                   role="button",
#                   **{'data-slide': 'next'})
#
#     news_carousel = html.Div([
#         carousel_inner,
#         prev,
#         next
#     ], id='news-carousel', className="carousel slide", **{'data-ride': 'carousel'})
#     return news_carousel


def update_cards(df):
    confirmed = f'{int(round(df.confirmed.sum() / 1)):,}'
    active = f'{int(round(df.active.sum() / 1)):,}'
    recovered = f'{int(round(df.recovered.sum() / 1)):,}'
    critical = f'{int(round(df.critical.sum() / 1)):,}'
    deaths = f'{int(round(df.deaths.sum() / 1)):,}'
    metric = (active, recovered, critical, deaths)
    label = ('Active', 'Recovered', 'Critical', 'Deaths')
    cards = \
        html.Div([
            dbc.Row([
                dbc.Col(html.H3('Worldwide Cases : ' + confirmed, id='metric-title'), md=8, xs=12),
                dbc.Col(dbc.Row([

                    html.Div(dcc.Dropdown(
                        id='dropdown',
                        options=
                        [{'label': 'Worldwide', 'value': 'Worldwide'}] +
                        [{'label': val, 'value': val} for val in
                         df.country.sort_values(ascending=True).values],
                        placeholder='Country filter',
                    ), id='dropdown_div'),
                    dbc.Button("Refresh", color="primary", id='data_refresh')
                ]), md=4, id='country-search', className="row justify-content-center"),

            ], id='dashboard_title'),

            dbc.CardDeck(
                [
                    dbc.Card(
                        html.Div([
                            html.P(lab, className='metric_text'),
                            html.H4(met, className='metric_text'),
                        ], className='metric_body'
                        ), className='card border-0'
                    ) for met, lab in zip(metric, label)
                ], id='metric'
            )
        ])
    return cards


def country_filtering(df, value):
    confirmed = f'{int(round(df.confirmed.sum() / 1)):,}'
    active = f'{int(round(df.active.sum() / 1)):,}'
    recovered = f'{int(round(df.recovered.sum() / 1)):,}'
    critical = f'{int(round(df.critical.sum() / 1)):,}'
    deaths = f'{int(round(df.deaths.sum() / 1)):,}'
    metric = (active, recovered, critical, deaths)
    label = ('Active', 'Recovered', 'Critical', 'Deaths')
    try:
        filtered_metric_title = value + ' Cases : ' + confirmed
    except:
        filtered_metric_title = 'Worldwide Cases : ' + confirmed
    filtered_cards = [
        dbc.Card(
            html.Div([
                html.P(lab, className='metric_text'),
                html.H4(met, className='metric_text'),
            ], className='metric_body'
            ), className='card border-0'
        ) for met, lab in zip(metric, label)
    ]
    return filtered_metric_title, filtered_cards
