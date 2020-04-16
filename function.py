import requests
import pandas as pd
from plotly.subplots import make_subplots
from plotly import graph_objects as go

url = "https://covid-19-data.p.rapidapi.com/country/all"

headers = {
    'x-rapidapi-host': "covid-19-data.p.rapidapi.com",
    'x-rapidapi-key': "896405cd4dmsh37ab260e7e7121dp1bdf68jsnb713de9f2bb8"
}
br = '<br>'


def refresh_data():
    response = requests.request("GET", url, headers=headers)
    region = pd.read_csv('mapping.csv')
    region.columns = ['country', 'id', 'region', 'sub-region']
    df = pd.DataFrame(data=response.json())
    df.drop(['latitude', 'longitude'], axis=1, inplace=True)
    df = pd.merge(df, region, on=['country'])
    df.dropna(inplace=True)
    df = df[df['confirmed'] != 0]
    df = df.sort_values(['region', 'sub-region'])
    df_region = df.groupby(by=['region'], as_index=False).sum()
    df_subregion = df.groupby(by=['region', 'sub-region'], as_index=False).sum()

    def add_columns(a):
        a['active'] = a.confirmed - a.recovered - a.critical - a.deaths
        a['a'] = round(a.active / a.confirmed, 2)
        a['b'] = round(a.recovered / a.confirmed, 2)
        a['c'] = round(a.critical / a.confirmed, 2)
        a['d'] = round(a.deaths / a.confirmed, 2)
        return a

    def add_columns_region(a):
        a['active'] = a.confirmed - a.recovered - a.critical - a.deaths
        a['a'] = round(a.active / a.confirmed, 2) * 100
        a['b'] = round(a.recovered / a.confirmed, 2) * 100
        a['c'] = round(a.critical / a.confirmed, 2) * 100
        a['d'] = round(a.deaths / a.confirmed, 2) * 100
        return a

    def table_format_percentage(column):
        column = column.astype(int).astype(str) + ' %'

    def table_format_separator(column):
        table[column] = table.apply(lambda x: f'{x[column]:,}', axis=1)

    df = add_columns(df)
    # df_region = add_columns_region(df_region)
    # df_subregion = add_columns_region(df_subregion)
    df_subregion['active'] = df_subregion.confirmed - df_subregion.recovered - df_subregion.critical - df_subregion.deaths
    table = df_subregion.copy()
    table.columns = [
        'Region', 'Sub-Region', 'Confirmed', 'Recovered', 'Critical', 'Deaths', 'Active',
        # '% Active', '% Recovered', '% Critical', '% Death'
    ]
    table_format_separator('Confirmed')
    table_format_separator('Recovered')
    table_format_separator('Critical')
    table_format_separator('Deaths')
    table_format_separator('Active')
    # table['% Active'] = table['% Active'].astype(int).astype(str) + ' %'
    # table['% Recovered'] = table['% Recovered'].astype(int).astype(str) + ' %'
    # table['% Critical'] = table['% Critical'].astype(int).astype(str) + ' %'
    # table['% Death'] = table['% Death'].astype(int).astype(str) + ' %'


    return df, df_region, table


def generate_geo(df):
    text = (
            df['country'] + br + br +
            'Confirmed  : ' + df.apply(lambda x: f'{x.confirmed:,}', axis=1) + br +
            'Active         : ' + df.apply(lambda x: f'{x.active:,}', axis=1) + br +
            'Recovered  : ' + df.apply(lambda x: f'{x.recovered:,}', axis=1) + br +
            'Critical        : ' + df.apply(lambda x: f'{x.critical:,}', axis=1) + br +
            'Deaths        : ' + df.apply(lambda x: f'{x.deaths:,}', axis=1) + br +
            '% Active         : ' + df.apply(lambda x: f"{x.a:.0%}", axis=1) + br +
            '% Recovered : ' + df.apply(lambda x: f"{x.b:.0%}", axis=1) + br +
            '% Critical        : ' + df.apply(lambda x: f"{x.c:.0%}", axis=1) + br +
            '% Deaths       : ' + df.apply(lambda x: f"{x.d:.0%}", axis=1)
    )

    geo_fig = go.Figure(data=go.Choropleth(
        locationmode='country names',
        locations=df['country'],
        z=df['confirmed'],
        colorscale='bupu',
        marker_line_color='darkgrey',
        marker_line_width=1,
        zmax=df.confirmed.quantile(q=0.95),
        zmin=0,
        text=text,
        name='',
        hovertemplate='%{text}',
        showscale=False,
    ))
    geo_fig.update_layout(
        autosize=True,
        hoverlabel=dict(
            font_size=13,
        ),
        showlegend=False,
        margin=dict(t=0, r=0, b=0, l=0, autoexpand=True),
        paper_bgcolor="rgba(0,0,0,0)",
        geo=dict(showframe=False,
                 showcoastlines=False,
                 projection_type='natural earth',
                 bgcolor='rgba(0,0,0,0)',
                 ),
    )

    geo_fig.update_geos(
        fitbounds="locations",
        visible=False,
        lataxis_showgrid=False,
        lonaxis_showgrid=False,
        showocean=False,
    )

    return geo_fig


def generate_pie(df_region):
    colors = ['orange', 'green', 'red', 'purple']
    labels = ['% Active', '% Recovered', '% Critical', '% Death']
    specs = [[{'type': 'domain'} for i in range(5)]]
    pie_fig = make_subplots(rows=1, cols=5, specs=specs, subplot_titles=df_region['region'])
    row = 1
    for val in range(5):
        pie_fig.add_trace(
            go.Pie(
                labels=labels,
                values=[df_region.a[val], df_region.b[val], df_region.c[val], df_region.d[val]],
                name=df_region.region[val],
                title=f'{df_region.confirmed[val]:,}' + br + 'Confirm Cases',
                textinfo='none'
            ),
            row, val + 1
        )

    pie_fig.update_traces(
        hole=.6,
        hoverinfo="label+percent+name",
        marker=dict(colors=colors)
    )
    pie_fig.update_layout(
        title={'font': {'size': 14}},
        autosize=True,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color='white'),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return pie_fig


def generate_bar():
    values = ['% Active', '% Recovered', '% Critical', '% Death']
    colors = ['orange', 'green', 'red', 'black']
    bar_fig = go.Figure()
    for i in range(4):
        fig.add_trace(go.Bar(
            y=table_per['Sub-Region'].iloc[::-1],
            x=table_per[values[i]],
            name=values[i],
            orientation='h',
            marker=dict(
                color=colors[i],
                line=dict(color='rgba(255, 255, 255, 1)', width=1)
            )
        ))

    bar_fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        barmode='stack',
        legend_orientation="h",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return bar_fig
