#!/usr/bin/env python
# coding: utf-8

# # Фальсификации выявляемые явкой (Президент РФ 2018 с погрешностью)
# 
# ### Источник данных \ Source
# Сделано на Google Sheets:  https://docs.google.com/spreadsheets/d/1B6mdaLXdB9AK5zFjSPzHq-4Rb2Gx8ZfKrm3jFeqQ1qk/copy
# (нужно создать свою копию)
# Тут показано как это работает: https://youtu.be/fRScTlfZ16c

# #####  Библиотеки и функции
import numpy as np
import pandas as pd


# ##### Загрузка данных
def data_read():
    data = pd.ExcelFile('„Фальсификации выявляемые явкой (Президент РФ 2018 с погрешностью)“ kopija_.xlsx').parse('ЦИК')
    data = data.drop(columns=['Unnamed: 0', 'Unnamed: 14', 'Unnamed: 19'])
    data.columns = data[1:2].values[0]
    data = data[2:]
    return data


def flattened(data):
    data_flattened = data.melt(id_vars=['region', 'uik'], value_vars=['Официальная Явка',
                                                                      'Явка волонтер 2020',
                                                                      'Явка волонтер 2018'])
    data_flattened = data_flattened[data_flattened['value'] != -1.0]

    not_looked = data[data['Оф явка без просмотра'] != -1].pivot_table(index=['region', 'uik'],
                                                                       values='Оф явка без просмотра',
                                                                       aggfunc='count').reset_index()
    data_flattened = data_flattened.merge(not_looked, how='left', on=['region', 'uik'])
    return data_flattened


def replace_and_add(data_flattened):
    data_flattened['region_uik'] = data_flattened['region'] + ', ' + data_flattened['uik']
    data_flattened['uik_num'] = data_flattened['uik'].str.replace('УИК №', '')
    return data_flattened


def proverka_fact(sample_data):
    data_proverka_fact = sample_data[sample_data[
        'variable'].isin(['Явка волонтер 2018', 'Явка волонтер 2020'])].groupby(['region', 'uik'])[
        'value'].mean().reset_index()
    data_proverka_fact = data_proverka_fact.rename(columns={'value': 'mean_volunteer'})
    data_proverka_fact['variable'] = 'Официальная Явка'
    sample_data_full = sample_data.merge(data_proverka_fact, how='left', on=['region', 'uik', 'variable'])
    return sample_data_full


# длинное чтение из оригинального экселя
# (https://docs.google.com/spreadsheets/d/1B6mdaLXdB9AK5zFjSPzHq-4Rb2Gx8ZfKrm3jFeqQ1qk/copy)
# и сохранение в формат csv
# data = data_read()
# data.to_csv('falsifications_detected_president_rf_2018.csv', index=False)

def query_data():
    try:
        data = pd.read_csv('falsifications_detected_president_rf_2018.csv')
    except:
        data = pd.read_csv(
            'https://raw.githubusercontent.com/Justlesia/dataviz_golos_president_2018/main/falsifications_detected_president_rf_2018.csv')
    data_flattened = flattened(data)
    data_flattened = replace_and_add(data_flattened)
    return proverka_fact(data_flattened)


data_to_viz = query_data()
data_to_viz.to_csv('data_to_viz.csv', index=False)
