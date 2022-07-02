#!/usr/bin/env python
# coding: utf-8

# # Фальсификации выявляемые явкой (Президент РФ 2018 с погрешностью)
# 
# ### Источник данных \ Source
# Сделано на Google Sheets:  https://docs.google.com/spreadsheets/d/1B6mdaLXdB9AK5zFjSPzHq-4Rb2Gx8ZfKrm3jFeqQ1qk/copy
# (нужно создать свою копию)
# Тут показано как это работает: https://youtu.be/fRScTlfZ16c

# In[1]:


#ЗАДАТЬ ЦВЕТ ТОЧЕК
#Официальная Явка без видео
no_video = 'gray'
#Официальная Явка c непросмотренным видео 
video_not_looked = 'whitesmoke'
#Совпало с официальной явкой
video_good = 'darkgreen'
#Совпало НИЖЕ с официальной явки
video_bad = 'red'
#Совпало ВЫШЕ с официальной явки
video_strange = 'goldenrod'

#Расчет волонтеров 2018
info_2018 = 'steelblue'
#Расчет волонтеров 2020
info_2020 = 'blue'


# In[2]:


# #####  Библиотеки и функции

# In[3]:


import numpy as np
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from dash import dcc, html, Input, Output
from jupyter_dash import JupyterDash
from flask_caching import Cache
from base64 import b64encode
import io
TIMEOUT = 60
import plotly.io as pio
pio.templates.default = "plotly_white"

#Импортируем все необходимые библиотеки
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
headers = {'User-Agent': user_agent}

pd.set_option('display.max_columns', None)


# ##### Загрузка данных

# In[4]:


def data_read():
    data = pd.ExcelFile('„Фальсификации выявляемые явкой (Президент РФ 2018 с погрешностью)“ kopija_.xlsx').parse('ЦИК')
    data = data.drop(columns=['Unnamed: 0', 'Unnamed: 14', 'Unnamed: 19'])
    data.columns = data[1:2].values[0]
    data = data[2:] 
    return data


# In[5]:


#data = data_read()


# In[6]:


#data = data.drop(columns=['Число избирателей, включенных в список избирателей',
#                          '% отклонения','Оф явка просмотр < threshhold','Оф явка просмотр >=threshhold','Адрес format'])


# In[7]:


#data.to_csv('falsifications_detected_president_rf_2018.csv', index=False)


# In[8]:


data = pd.read_csv('https://raw.githubusercontent.com/Justlesia/dataviz_golos_president_2018/main/falsifications_detected_president_rf_2018.csv')



data = pd.read_csv('falsifications_detected_president_rf_2018.csv')



# In[9]:


#data.head()


# In[10]:


def flattened(data):
    data_flattened = data.melt(id_vars=['region', 'uik'], value_vars=['Официальная Явка',
                                                                                    'Явка волонтер 2020',
                                                                                    'Явка волонтер 2018'])
    data_flattened = data_flattened[data_flattened['value'] != -1.0]
    
    not_looked = data[data['Оф явка без просмотра']  != -1].pivot_table(index = ['region','uik'],
                                                           values= 'Оф явка без просмотра', aggfunc  = 'count').reset_index()
    data_flattened = data_flattened.merge(not_looked, how = 'left', on = ['region','uik'])
    return data_flattened

data_flattened = flattened(data)


# In[11]:


def replace_and_add(data):
    data_flattened['region_uik'] = data_flattened['region'] + ', ' + data_flattened['uik']
    data_flattened['uik_num'] = data_flattened['uik'].str.replace('УИК №', '')
    return data_flattened

data_flattened = replace_and_add(data_flattened)


# In[12]:


def proverka_fact(sample_data):
    proverka_fact =  sample_data[sample_data[
        'variable'].isin(['Явка волонтер 2018', 'Явка волонтер 2020'])].groupby(['region','uik'])['value'].mean().reset_index()
    proverka_fact = proverka_fact.rename(columns = {'value': 'mean_volunteer'})
    proverka_fact['variable'] = 'Официальная Явка'
    sample_data= sample_data.merge(proverka_fact, how= 'left', on = ['region','uik','variable'])
    return sample_data

sample_data = proverka_fact(data_flattened)


# In[13]:


def sample_data_color(sample_data, lag):

    color_dict = {'Официальная Явка' : no_video, 'Явка волонтер 2018' : info_2018, 'Явка волонтер 2020' : info_2020}

    sample_data['color'] = sample_data['variable']
    sample_data.replace({"color": color_dict}, inplace=True)
    sample_data.head()
    
    sample_data['color'] = sample_data['color'].where(sample_data['Оф явка без просмотра'].isna(), video_not_looked)
    sample_data['color'] = sample_data['color'].where(sample_data['mean_volunteer'].isna(), video_good)
    sample_data['color'] = sample_data['color'].where(np.logical_not(sample_data['value'] > (sample_data['mean_volunteer'] + lag)),video_bad)
    sample_data['color'] = sample_data['color'].where(np.logical_not(sample_data['value'] < (sample_data['mean_volunteer'] - lag)),video_strange)
    return sample_data

sample_data = sample_data_color(sample_data, 0.05)


# In[14]:


print(sample_data['color'].unique())


# In[15]:


# для кнопки
buffer = io.StringIO()
fig = go.Figure()
html_bytes = buffer.getvalue().encode()
encoded = b64encode(html_bytes).decode()


# In[16]:


# для кнопки
buffer = io.StringIO()
fig = go.Figure()
html_bytes = buffer.getvalue().encode()
encoded = b64encode(html_bytes).decode()


# In[17]:


app = JupyterDash(__name__, external_stylesheets=[dbc.themes.LITERA])

cache = Cache(app.server, config={
    'CACHE_TYPE': 'simple',
    # 'CACHE_DIR': 'cache-directory'
})


# In[18]:




upper_left_controls = dbc.Form([
      html.Div([
          dbc.Label("Участково избирательные участки:", style={'font-weight': 'bold'}),
          dbc.RadioItems(
                  id='all_or_colored', value=1, inline=True,
                  options=[{'label': 'Все', 'value': 1},
                          {'label': 'Только проверенные (видеонаблюдение)', 'value': 0},
                          {'label': 'Один УИК', 'value': 2},
                          ]
              ),
          dbc.Input(
              id='uik_number',
              placeholder='Запишите числовой номер УИК',
              type="number", min=1, max=100000, step=1,
              className="md-3", 
          ),
      ],
      className="md-3"),
    ])



upper_right_controls = dbc.Form([
    html.Div([
        dbc.Label('Данные по явке:', style={'font-weight': 'bold'}),
        dbc.Checklist(
            options = [
                {'label': 'Официальная Явка', 'value': 'Официальная Явка'},
            ],
            value=['Официальная Явка'],
            id = 'types1', style={'color': no_video, 'font-weight': 'bold'}
        ),
        dbc.Checklist(
            options = [
                {'label': 'Явка волонтер 2018', 'value': 'Явка волонтер 2018'},
            ],
            value=['Явка волонтер 2018'],
            id = 'types2', style={'color': info_2018, 'font-weight': 'bold'}
        ),
        dbc.Checklist(
            options = [
                {'label': 'Явка волонтер 2020' , 'value': 'Явка волонтер 2020'}, 
            ],
            value=['Явка волонтер 2020'],
            id = 'types3',style={'color': info_2020, 'font-weight': 'bold'}
        ),
            
        
        
    ], className="md-3"),
])

left_controls = dbc.Form([
    html.Div([
        dbc.Label("Критическая погрешность:", style={'font-weight': 'bold'}),
        dcc.Slider(0.01, 0.15, id='lag', value=0.05, marks={
            0.01: '≥1%',
            0.03: '≥3%',
            0.05: '≥5%',
            0.10: '≥10%',
            0.15: '≥15%',
        }),
        dbc.FormText([
                'Если выявленный процент явки отличается от официального ',
                html.Span('на критическую погрешность и больше, то он выделен цветом, ', style={'color': video_bad}),
                html.Span('если меньше - другим', style={'color': video_good}),
                '. Третьим отмечены точки, где подсчеты дали ',
                html.Span('большую явку, чем официальная', style={'color': video_strange})
            ]),
    ], className="md-3"),

    html.Div([
        dbc.Label('Регион:',style={'font-weight': 'bold'}),

        dbc.RadioItems(
                  id='region_type', value=1,
                  options=[{'label': 'Все', 'value': 1},
                           {'label': 'С видео', 'value': 0}],
                  inline=True
              ),

        dcc.Dropdown(
            options = sample_data['region'].unique(),
            value = ['город Москва'], id = 'region', multi = True
        ),


    ], className="md-3"),
])

disclaimer = html.Div(
    
        dbc.FormText([
                html.Span('(материал произведен совместно с ЦИК РФ и распространён официально признанным агентом иной страны, иной России, Прекрасной России Будущего, лицом, являющимся членом органа (Совета) НКО (Лига Избирателей) выполняющей, по мнению Минюста РФ, функции иностранного агента на сумму 225 рублей 40 копеек, пожертвованных в 2019 году Светланой Доровской, якобы являющейся гражданкой Молдовы, а возможно и России, т.к. она зарегистрирована и проживает в г. Москве).')
            ]),
)


# для кнопки
buffer = io.StringIO()
fig = go.Figure()
html_bytes = buffer.getvalue().encode()
encoded = b64encode(html_bytes).decode()


button = html.Div(
    [
                  dbc.Button("Скачать как HTML", 
                  id="download",
                  href="data:text/html;base64," + encoded,
                  download="plotly_graph.html",
                  className="me-1",
                  #external_link=True
                  ),
    ]
)


# In[19]:


app.layout = dbc.Container([
    dbc.NavbarSimple(
        brand="Фальсификации выявляемые явкой (Президент РФ 2018 с погрешностью)", 
        className='mb-3'
    ),
    dbc.Row(
        [
        dbc.Col(upper_left_controls, md=8),
        dbc.Col(upper_right_controls, md=4),         
        ],
        align="upper",
    ),

    dbc.Row(
        [
            dbc.Col([
                    html.Div(
                        [left_controls],
                        className="p-3 bg-light border rounded-3"
                    ),
                    button,
                ],
                md=4,
            ),
            dbc.Col(dcc.Graph(id="graph"), md=8),
        ],
        align="center",
    ),
    
    dbc.Row([
        dbc.Col(
        [
          disclaimer
        ] , 
        align="left")
    ]),
])


# In[20]:


@cache.memoize(timeout=TIMEOUT)
def query_data():
    data = pd.read_csv('falsifications_detected_president_rf_2018.csv')
    data_flattened = flattened(data)
    data_flattened = replace_and_add(data_flattened)
    sample_data = proverka_fact(data_flattened)
    return sample_data.to_json(date_format='iso', orient='split')


@app.callback(
    Output("graph", "figure"),
    Output("region", "options"),
    Output("download", "href"),
    Input("all_or_colored", "value"),
    Input("region", "value"),
    Input("lag", "value"),
    Input("uik_number", "value"),
    Input("types1", "value"),
    Input("types2", "value"),
    Input("types3", "value"),
    Input("region_type", "value"),
)
def modify(all_or_colored, region, lag, uik_number, types1, types2, types3, region_type):
    
    types = []
    types.extend(types1)
    types.extend(types2)
    types.extend(types3)
    
    big_sample_data = pd.read_json(query_data(), orient='split')

    if region_type == 1:
        region_list = big_sample_data['region'].unique()
    else:
        region_list = big_sample_data[big_sample_data['variable'] != 'Официальная Явка']['region'].unique()

    sample_data = big_sample_data[big_sample_data['region'].isin(region)].copy()
    sample_data = sample_data_color(sample_data, lag)
    sample_data = sample_data[sample_data['variable'].isin(types)]

    if all_or_colored == 0:
        sample_data = sample_data[sample_data['color'].isin([no_video, video_not_looked]) == False]
    elif all_or_colored == 2:
        try:
            sample_data = sample_data[sample_data['uik_num'] == int(uik_number)]
        except ValueError:
            sample_data = sample_data

    data_no_video = sample_data[sample_data['color'].isin([no_video])]
    data_video_not_looked = sample_data[sample_data['color'].isin([video_not_looked])]
    data_color = sample_data[sample_data['color'].isin([no_video, video_not_looked]) == False]

    # Add traces

    trace_list = []

    if len(data_no_video) > 0:
        trace_list += [go.Scatter(y=data_no_video['value'], x=data_no_video['region_uik'],
                                  mode='markers',
                                  name='без видео в архиве',
                                  marker=dict(color=data_no_video['color']),
                                  marker_line=dict(color=data_no_video['color'], width=1),
                                  )]

    if len(data_video_not_looked) > 0:
        trace_list += [go.Scatter(y=data_video_not_looked['value'], x=data_video_not_looked['region_uik'],
                                  mode='markers',
                                  name='ждет проверки',
                                  marker=dict(color=data_video_not_looked['color']),
                                  marker_line=dict(color=data_video_not_looked['color'], width=1),
                                  )]

    if len(data_color) > 0:
        for k in data_color['region_uik']:
            dt = sample_data[sample_data['region_uik'] == k]
            trace_list += [go.Scatter(y=dt['value'], x=dt['region_uik'],
                                      mode='lines+markers',
                                      name='видео проверено',
                                      line=dict(color=dt['color'].values[0], width=2),
                                      marker=dict(color=dt['color'])
                                      )]
    layout = go.Layout(
        paper_bgcolor=video_not_looked
    )

    fig = go.Figure(data=trace_list, layout=layout)
    fig.update_xaxes(categoryarray=sample_data['region_uik'].unique(), showticklabels=False)
    fig.update_yaxes(range=[0, 1.1], tickformat=".0%")
    fig.update_traces(showlegend=False, marker_line_width=0.5, marker_size=10)

    # сохраним нашу фигуру
    buffer = io.StringIO()
    fig.write_html(buffer)
    html_bytes = buffer.getvalue().encode()
    encoded = b64encode(html_bytes).decode()

    return fig, region_list, "data:text/html;base64," + encoded


app.run_server(mode="inline")


#if __name__ == '__main__':
#     app.run_server(mode="external")

