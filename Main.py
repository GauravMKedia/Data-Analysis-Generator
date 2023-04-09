#!/usr/bin/env python
# coding: utf-8

import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objs as go
import seaborn as sns
import warnings
import math
from datetime import datetime
from sklearn.impute import SimpleImputer
import datetime as dt
from itertools import combinations
from collections import Counter
import dash
import pickle
import jupyter_dash
import plotly.io as pio
import plotly.offline as pyo
from dash import Dash, html, dcc
warnings.filterwarnings("ignore")
plt.rcParams["figure.figsize"] = (15,6)
plt.rcParams['figure.dpi'] = 70




data = pd.read_csv('/assets/train.csv')




# This is Color Map for doing RFM Analysis
color_map = {
    'Top Customer': '#636efa',
    'High Value Customer': '#ef553b',
    'Medium Value Customer': '#00cc96',
    'Low Value Customer':'#ab63fa',
    'Lost Customer':'#19d3f3',
    'NO Purchase':'#ffa15a'
}




# This color scheme is for plotting heatmap of Retention Analysis
heatmap_color_scheme_low = [
    (0,"#27159D"),
    (0.0001, "#0F0071"),
    (0.005,"#1B088C"),
    (0.01,"#470086"),
    (0.05,"#840AA5"),
    (0.1,"#B03089"),
    (0.2,"#D15073"),
    (0.4,"#F89641"),
    (0.6,"#F6B536"),
    (0.8,"#F4D12D"),
    (1,'#F2F222')
]

heatmap_color_scheme_high = [
    (0,"#27159D"),
    (0.00000001, "#0F0071"),
    (0.1,"#1B088C"),
    (0.2,"#470086"),
    (0.3,"#840AA5"),
    (0.5,"#B03089"),
    (0.7,"#D15073"),
    (0.9,"#F89641"),
    (1,'#F2F222')
]




# This functionm will return Year and Month for a data value
# Here month number 1 means January, 2 means feb as if we consider april as month 1 for numbering(only) then working changes
def get_year_int(df, column):
   year = df[column].dt.year
   month = df[column].dt.month
   return year, month




# This function will return quarter number for column provided
def get_quarter(x):
    if x==1 or x==2 or x==3:
        return 4
    elif x==4 or x==5 or x==6:
        return 1
    elif x==7 or x==8 or x==9:
        return 2
    elif x==10 or x==11 or x==12:
        return 3




# Data Dictionary to be Written in a file for creating Dashboard
main_data_dict={}
overall_dict={}
state_dict={}
product_dict={}
rfm_dict={}
ret_dict={}
segment_dict={}
cross_sell_dict={}




# PreProcessing of Data




# Extracting only important column from out data in df which will be used for different analysis
# This need to be edited according to data provided

# Here we have remove column like ship mode and ship date
df = data[['Order ID','Product Name','Sub-Category','Category','Product ID','Region','State','City','Country','Segment','Customer Name','Customer ID','Order Date','Sales']].copy()




# Renaming the Columns
# Please edit the name of column as required 
# Column Name needed are :
# BillDate
# Quantity
# UnitRate
# State
# Name (Customer Name)
# PL1,PL2,PL3.... (This is for differnt product level if present in data)
# PC (For Product Category)
# OrderID
# Segment
# BasePrice (Revenue)
# ProductDetail (Detailed description of products)




df.rename(columns = {'Order ID':'OrderID','Order Date':'BillDate','Customer Name':'CustomerName','Category':'PL1','Sub-Category':'PL2','Sales':'BasePrice','Product Name':'ProductDetail'}, inplace = True)




# Please Specify the Column Present in df
# If Column is present the 1 else 0.
cdict= {
    "BillDate": 1,
    "Quantity": 0,
    "UnitRate": 0,
    "BillDate": 1,
    "State": 1,
    "CustomerName": 1,
    "PC":1,
    "PL":1,
    "OrderID":1,
    "Segment":1,
    "BasePrice":1,
    "ProductDetail":1,
    "ExtraAnalysis":0, # Make this 1 if you want to do some more analysis for some differnt column which can be done using col_analysis function shown example around line 1200
}




# Converting Object data type to String
# Do this if needed
if cdict['Quantity']==1:
    df['Quantity']=df['Quantity'].astype(str)
    df['Quantity'] = df['Quantity'].str.replace(',', '', regex=True)
    df['Quantity'] = df['Quantity'].astype(float)

if cdict['UnitRate']==1:
    df['UnitRate']=df['UnitRate'].astype(str)
    df['UnitRate'] = df['UnitRate'].str.replace(',', '', regex=True)
    df['UnitRate']=df['UnitRate'].astype(float)

if cdict['BasePrice']==1:
    df['BasePrice']=df['BasePrice'].astype(str)
    df['BasePrice'] = df['BasePrice'].str.replace(',', '', regex=True)
    df['BasePrice'] = df['BasePrice'].astype(float)




# Changing Bill Date object to datetime format
if cdict['BillDate']==1:
    df.BillDate = pd.to_datetime(df.BillDate)
    df[df['BillDate'].isna()]
    df.dropna(subset=['BillDate'], inplace=True)




# Removing the Negative Base Price Values
if cdict['BasePrice']==1:
    df = df[df.BasePrice > 0]




# Adding year and month column in df data
if cdict['BillDate']==1:
    df['Year'],df['Month']=get_year_int(df,'BillDate')
    df['Quarter']=df.apply(lambda x: get_quarter(x['Month']), axis=1)




# General Variable containing all years
# This will contain all the general Information needed to change according to data provided

# Using above output of differnt year fill this array
years=['2014-15','2015-16','2016-17','2017-18','2018-19']
first_years=['2014','2015','2016','2017','2018']
start_years=['14','15','16','17','18']
short_years=['14-15','15-16','16-17','17-18','18-19']

# This means that the last year data is incomplete so some plots will not be made for the last year in data
data_incomplete_year_count=1


quarters=['1','2','3','4']
full_quarters=['Quarter 1','Quarter 2','Quarter 3','Quarter 4']
months=['Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec','Jan','Feb','Mar']
Customer_Seg=["Top","High","Medium","Low","Lost"]
Customer_Segment=["Top Customer","High Value Customer","Medium Value Customer","Low Value Customer","Lost Customer"]


# This is variable for containig figure number of each plot
fig_num=1
main_fig_num=1




if cdict['BillDate']==1:
    # Creating different database for each year seperately
    for y in start_years:
        temp='df_'+str(y)
        x=int(y)+1
        exec(f"{temp}=df.loc[(df['BillDate'] >= '20{y}-04-01') & (df['BillDate'] <= '20{x}-03-31')]")




# Yearly Analysis
if cdict['BasePrice'] and cdict['BillDate']:
    # Making another copy of Data for doing Yearly analysis
    # For this section we will be working on ya and ya_18,ya_19,....
    ya=df.copy() 
    for y in start_years:
            temp='ya_'+str(y)
            temp2='df_'+str(y)
            exec(f"{temp}={temp2}.copy()")




    # Making a data frame ya_year where total revenue of each year is present
    ya_year=pd.DataFrame({'Year':[],'BasePrice':[]})
    temp=0
    for y in years:
        x='df_'+str(start_years[temp])
        x=eval(x).BasePrice.sum()
        ll={'Year':y,'BasePrice':x}
        ya_year=ya_year.append(ll,ignore_index=True)
        temp=temp+1





    fig_num=main_fig_num
    temp_fig='fig_'+str(fig_num)
    fig_num+=1;
    title="Revenue of Each Year"
    exec(f"{temp_fig}=go.Figure()")
    exec(f"{temp_fig}=px.bar(ya_year,x='Year',y='BasePrice')")
    exec(f"{temp_fig}.update_layout(title=title,title_font_size=24)")
    # For data Transfer
    fig_dict={}
    fig_dict["Total"]=[eval(temp_fig),ya_year]
    overall_dict[title]=fig_dict




    main_fig_num=fig_num




    # Creating ya_Mix dataframe containg revenue per month for each year
    ya_mix=pd.DataFrame()
    ind=0
    for y in start_years:
        temp='ya_'+str(y)
        temp=eval(temp).groupby('Month').BasePrice.sum().to_frame(name=f'BasePrice{short_years[ind]}').reset_index()
        ind=ind+1
        if ya_mix.empty:
            ya_mix=temp
        else:
            ya_mix = pd.merge(ya_mix,temp, on='Month',how='outer').fillna(0)    




    title="Revenue Per Month Of Each Year"
    fig_num=main_fig_num
    fig_num=fig_num+1;
    temp_fig='fig_'+str(fig_num)
    exec(f"{temp_fig}=go.Figure()")
    for y in short_years:
        temp='BasePrice'+str(y)
        exec(f"{temp_fig}.add_trace(go.Scatter(x=ya_mix['Month'], y=ya_mix[temp], mode='lines', name=f'Price{y}'))")
    exec(f"{temp_fig}.update_layout(title=title,title_font_size=24)")

    # For data Transfer
    fig_dict={}
    fig_dict["Year"]=[eval(temp_fig),ya_mix]
    overall_dict[title]=fig_dict




    main_fig_num=fig_num




    # Creating ya_Mix dataframe containg revenue per month for each year
    ya_quarter=pd.DataFrame()
    ind=0
    for y in start_years:
        temp='ya_'+str(y)
        temp=eval(temp).groupby('Quarter').BasePrice.sum().to_frame(name=f'BasePrice{short_years[ind]}').reset_index()
        ind=ind+1
        if ya_quarter.empty:
            ya_quarter=temp
        else:
            ya_quarter = pd.merge(ya_quarter,temp, on='Quarter',how='outer').fillna(0)
    ya_quarter = ya_quarter.sort_values(by='Quarter', ascending=True)




    title="Revenue Per Quarter of Each Year"
    fig_num=main_fig_num
    temp_fig='fig_'+str(fig_num)
    fig_num=fig_num+1;
    exec(f"{temp_fig}=go.Figure()")
    for y in short_years:
        exec(f"{temp_fig}.add_trace(go.Scatter(x=ya_quarter['Quarter'],y=ya_quarter[f'BasePrice{y}'],name=f'BasePrice{y}'))")
    exec(f"{temp_fig}.update_layout(title='Revenue Per Quarter in Each Year',title_font_size=24)")

    # For data Transfer
    fig_dict={}
    fig_dict["Quarter"]=[eval(temp_fig),ya_quarter]
    overall_dict[title]=fig_dict




    main_fig_num=fig_num




    # Assigning Overall Dictionary in Main_Data
    main_data_dict["Overall Analysis"]=overall_dict




# State Analysis
if cdict['BasePrice'] and cdict['State'] and cdict['BillDate']:




    # Making another copy of Data for doing State analysis
    st=df.copy() 
    for y in start_years:
        temp='st_'+str(y)
        temp2='df_'+str(y)
        exec(f"{temp}={temp2}.copy()")




    # Dropping all the Column where state in null
    st.dropna(subset=['State'], inplace=True)
    for y in start_years:
        temp='st_'+str(y)
        exec(f"{temp}.dropna(subset=['State'], inplace=True)")




    # Contain all the states name
    states=st['State'].unique()




    # Overall Revenue of each state
    title="Revenue per State"
    fig_num=main_fig_num
    temp_fig='fig_'+str(fig_num)
    fig_num=fig_num+1;
    exec(f"{temp_fig}=go.Figure()")
    state_sale_all=st.groupby("State").BasePrice.sum().sort_values(ascending = False).reset_index()
    exec(f"{temp_fig}=px.bar(state_sale_all,x='State',y='BasePrice')")
    exec(f"{temp_fig}.update_layout(title=title,title_font_size=24)")

    # For data Transfer
    fig_dict={}
    fig_dict["Total"]=[eval(temp_fig),state_sale_all]
    state_dict[title]=fig_dict




    main_fig_num=fig_num




    # State_Sale17 contain reveue of each state for year 2017-18
    # Creating ya_Mix dataframe containg revenue per month for each year
    state_sale_mix=pd.DataFrame()
    ind=0
    for y in start_years:
        temp='st_'+str(y)
        temp=eval(temp).groupby('State').BasePrice.sum().sort_values(ascending = False).to_frame(name=f'BasePrice{short_years[ind]}').reset_index()
        ind=ind+1
        if state_sale_mix.empty:
            state_sale_mix=temp
        else:
            state_sale_mix= pd.merge(state_sale_mix,temp, on='State',how='outer').fillna(0)






    title="Revenue Per State of Each Year"
    fig_num=main_fig_num
    temp_fig='fig_'+str(fig_num)
    fig_num=fig_num+1;
    exec(f"{temp_fig}=go.Figure()")
    for y in short_years:
        exec(f"{temp_fig}.add_trace(go.Bar(x=state_sale_mix['State'],y=state_sale_mix[f'BasePrice{y}'],name=f'BasePrice{y}'))")
    exec(f"{temp_fig}.update_layout(title=title,title_font_size=24)")

    # For data Transfer
    fig_dict={}
    fig_dict["Year"]=[eval(temp_fig),state_sale_mix]
    state_dict[title]=fig_dict




    main_fig_num=fig_num




    st_all_quarter=df.groupby(['State','Quarter']).BasePrice.sum().sort_values(ascending = False).to_frame(name='PriceAll').reset_index()
    st_all_q_mix=pd.DataFrame()
    for q in quarters:
        temp=pd.DataFrame()
        temp=st_all_quarter.loc[st_all_quarter['Quarter'] == int(q)][['State','PriceAll']]
        temp.rename(columns = {'PriceAll':f'Quarter {q}'}, inplace = True)
        if st_all_q_mix.empty:
            st_all_q_mix=temp
        else:
            st_all_q_mix= pd.merge(st_all_q_mix,temp, on='State',how='outer').fillna(0)





    # Here Revenue of Each State in Quarter 1 and 2 is more as in 2017-2022 data there is only Q1&Q2 data for year 2022 so some more value get added to Q1&Q2 and not in Q3&Q4
    title="Revenue Per State of Each Quarter"
    fig_num=main_fig_num
    temp_fig='fig_'+str(fig_num)
    fig_num=fig_num+1;
    exec(f"{temp_fig}=go.Figure()")
    for f in full_quarters:
        exec(f"{temp_fig}.add_trace(go.Bar(x=st_all_q_mix['State'],y=st_all_q_mix[f],name=f))")
    exec(f"{temp_fig}.update_layout(title=title,title_font_size=24)")

    # For data Transfer
    fig_dict={}
    fig_dict["Quarter"]=[eval(temp_fig),st_all_q_mix]
    state_dict[title]=fig_dict




    main_fig_num=fig_num




    ind=0
    for year in start_years:
        fetch_data='df_'+str(year)
        work_data='st_'+str(year)+'_quarter'
        exec(f"{work_data}={fetch_data}.groupby(['State','Quarter']).BasePrice.sum().sort_values(ascending = False).to_frame(name=f'Price{short_years[ind]}').reset_index()")
        main_data='st_'+str(year)+'_q_mix'
        exec(f"{main_data}=pd.DataFrame()")

        for q in quarters:
            temp=pd.DataFrame()
            temp=eval(work_data).loc[eval(work_data)['Quarter'] == int(q)][['State',f'Price{short_years[ind]}']]
            temp.rename(columns = {f'Price{short_years[ind]}':f'Quarter {q}'}, inplace = True)
            if eval(main_data).empty:
                exec(f"{main_data}=temp")
            else:
                exec(f"{main_data}= pd.merge({main_data},temp, on='State',how='outer').fillna(0)")
        for q in full_quarters:
            if q not in eval(main_data).columns:
                exec(f"{main_data}[q] = 0")
        exec(f"{main_data}['Year']='{years[ind]}'")
        ind=ind+1





    i=0
    fig_num=main_fig_num
    title=f"Revenue Per State Of Each Quarter For Each Year"
    fig_dict={}
    for y in start_years:
        sub_title=f"Revenue Per State of Each Quarter in {years[i]}"
        temp_fig='fig_'+str(fig_num)
        fig_num=fig_num+1;
        exec(f"{temp_fig}=go.Figure()")
        temp='st_'+str(y)+'_q_mix'
        for f in full_quarters:
            exec(f"{temp_fig}.add_trace(go.Bar(x=eval(temp)['State'],y=eval(temp)[f],name=f))")
        exec(f"{temp_fig}.update_layout(title=sub_title,title_font_size=24)")
        # For data Transfer
        fig_dict[f"Year:{y}"]=[eval(temp_fig),eval(temp)]
        i=i+1
    state_dict[title]=fig_dict




    main_fig_num=fig_num




    title=f"Revenue Per Year Of Each Quarter For Each State"
    fig_num=main_fig_num
    fig_dict={}
    for st in states:
        temp = pd.DataFrame()
        for y in start_years:
            main_data='st_'+str(y)+'_q_mix'
            if temp.empty:
                temp=eval(main_data).loc[eval(main_data)['State']==st]
            else:
                temp=temp.append(eval(main_data).loc[eval(main_data)['State']==st],ignore_index=True)
        if temp.empty==False:
            temp_fig='fig_'+str(fig_num)
            fig_num=fig_num+1;
            exec(f"{temp_fig}=go.Figure()")
            for f in full_quarters:
                exec(f"{temp_fig}.add_trace(go.Bar(x=temp['Year'],y=temp[f],name=f))")
            exec(f"{temp_fig}.update_layout(title='Revenue of {st} per Quarter in Each Year',title_font_size=24)")
            fig_dict[f"State:{st}"]=[eval(temp_fig),temp]
    state_dict[title]=fig_dict




    main_fig_num=fig_num




    main_data_dict['State Analysis']=state_dict



# Segment Analysis
if cdict['BasePrice'] and cdict['Segment'] and cdict['BillDate']:




    # Making another copy of Data for doing Segment analysis
    seg=df.copy() 
    for y in start_years:
        temp='seg_'+str(y)
        temp2='df_'+str(y)
        exec(f"{temp}={temp2}.copy()")




    # Dropping all the Column where SEGMENT in null
    seg.dropna(subset=['Segment'], inplace=True)
    for y in start_years:
        temp='seg_'+str(y)
        exec(f"{temp}.dropna(subset=['Segment'], inplace=True)")




    # Segment contain name of all Segment in data
    segments=seg['Segment'].unique()




    # Overall Revenue of each Segment
    title="(Bar) Revenue Per Segment"
    fig_num=main_fig_num
    temp_fig='fig_'+str(fig_num)
    fig_num=fig_num+1;
    exec(f"{temp_fig}=go.Figure()")
    segment_sale_all=seg.groupby("Segment").BasePrice.sum().sort_values(ascending = False).to_frame(name=f'BasePrice').reset_index()
    exec(f"{temp_fig}=px.bar(segment_sale_all,x='Segment',y='BasePrice')")
    exec(f"{temp_fig}.update_layout(title=title,title_font_size=24)")
    fig_dict={}
    fig_dict["Total"]=[eval(temp_fig),segment_sale_all]
    segment_dict[title]=fig_dict

    # Pie Plot
    title="(Pie) Revenue Per Segment"
    fig_num=main_fig_num
    temp_fig='fig_'+str(fig_num)
    fig_num=fig_num+1;
    exec(f"{temp_fig}=go.Figure()")
    exec(f"{temp_fig} = px.pie(segment_sale_all, values='BasePrice', names='Segment')")
    exec(f"{temp_fig}.update_layout(title='Overall Revenue Per Segment',title_font_size=24)")

    # Data Transfer
    fig_dict={}
    fig_dict["Total"]=[eval(temp_fig),segment_sale_all]
    segment_dict[title]=fig_dict




    main_fig_num=fig_num




    main_fig_num=fig_num




    # Segment_Sale17 contain reveue of each state for year 2017-18
    # Creating ya_Mix dataframe containg revenue per month for each year
    segment_sale_mix=pd.DataFrame()
    ind=0
    for y in start_years:
        temp='seg_'+str(y)
        temp=eval(temp).groupby('Segment').BasePrice.sum().sort_values(ascending = False).to_frame(name=f'BasePrice{short_years[ind]}').reset_index()
        ind=ind+1
        if segment_sale_mix.empty:
            segment_sale_mix=temp
        else:
            segment_sale_mix= pd.merge(segment_sale_mix,temp, on='Segment',how='outer').fillna(0)






    title="(Bar) Revenue Per Segment of Each Year"
    fig_dict={}
    fig_num=main_fig_num
    temp_fig='fig_'+str(fig_num)
    fig_num=fig_num+1;
    exec(f"{temp_fig}=go.Figure()")
    for y in short_years:
        temp='BasePrice'+str(y)
        exec(f"{temp_fig}.add_trace(go.Bar(x=segment_sale_mix['Segment'],y=segment_sale_mix[temp],name=temp))")
    exec(f"{temp_fig}.update_layout(title=title,title_font_size=24,xaxis=dict(tickangle=315))")

    # Data Transfer
    fig_dict["All Year"]=[eval(temp_fig),segment_sale_mix]
    segment_dict[title]=fig_dict


    # Pie plot for Every year
    title="(Pie) Revenue Per Segment of Each Year"
    fig_dict={}
    fig_num=main_fig_num
    size=len(start_years)
    ind=0
    for y in start_years:
        temp_fig='fig_'+str(fig_num)
        fig_num=fig_num+1;
        exec(f"{temp_fig}=go.Figure()")
        exec(f"{temp_fig} = px.pie(segment_sale_mix, values=f'BasePrice{short_years[ind]}', names='Segment')")
        exec(f"{temp_fig}.update_layout(title=f'Revenue Per Segment in {years[ind]}',title_font_size=24)")
        ind=ind+1;
        fig_dict[f"Year:{y}"]=[eval(temp_fig),segment_sale_mix]

    # Data Transfer
    segment_dict[title]=fig_dict




    main_fig_num=fig_num




    seg_all_quarter=df.groupby(['Segment','Quarter']).BasePrice.sum().sort_values(ascending = False).to_frame(name='PriceAll').reset_index()
    seg_all_q_mix=pd.DataFrame()
    for q in quarters:
        temp=pd.DataFrame()
        temp=seg_all_quarter.loc[seg_all_quarter['Quarter'] == int(q)][['Segment','PriceAll']]
        temp.rename(columns = {'PriceAll':f'Quarter {q}'}, inplace = True)
        if seg_all_q_mix.empty:
            seg_all_q_mix=temp
        else:
            seg_all_q_mix= pd.merge(seg_all_q_mix,temp, on='Segment',how='outer').fillna(0)





    title="(Bar) Revenue Per Segment Of Each Quarter"
    fig_num=main_fig_num
    temp_fig='fig_'+str(fig_num)
    fig_num=fig_num+1;
    exec(f"{temp_fig}=go.Figure()")
    for q in full_quarters:
        exec(f"{temp_fig}.add_trace(go.Bar(x=seg_all_q_mix['Segment'],y=seg_all_q_mix[q],name=q))")
    exec(f"{temp_fig}.update_layout(title=f'Overall Revenue Per Segment for each Quarter',title_font_size=24,xaxis=dict(tickangle=315))")

    # Data Transfer
    fig_dict={}
    fig_dict["Quarter"]=[eval(temp_fig),seg_all_q_mix]
    segment_dict[title]=fig_dict




    main_fig_num=fig_num




    ind=0
    for year in start_years:
        fetch_data='df_'+str(year)
        work_data='seg_'+str(year)+'_quarter'
        exec(f"{work_data}={fetch_data}.groupby(['Segment','Quarter']).BasePrice.sum().sort_values(ascending = False).to_frame(name=f'Price{short_years[ind]}').reset_index()")
        main_data='seg_'+str(year)+'_q_mix'
        exec(f"{main_data}=pd.DataFrame()")

        for q in quarters:
            temp=pd.DataFrame()
            temp=eval(work_data).loc[eval(work_data)['Quarter'] == int(q)][['Segment',f'Price{short_years[ind]}']]
            temp.rename(columns = {f'Price{short_years[ind]}':f'Quarter {q}'}, inplace = True)
            if eval(main_data).empty:
                exec(f"{main_data}=temp")
            else:
                exec(f"{main_data}= pd.merge({main_data},temp, on='Segment',how='outer').fillna(0)")
        for q in full_quarters:
            if q not in eval(main_data).columns:
                exec(f"{main_data}[q] = 0.0")
        exec(f"{main_data}['Year']='{years[ind]}'")
        ind=ind+1





    title="(Bar) Revenue Per Segment Of Each Quarter Per Year"
    fig_dict={}
    fig_num=main_fig_num
    i=0
    for y in start_years:
        temp_fig='fig_'+str(fig_num)
        fig_num=fig_num+1;
        exec(f"{temp_fig}=go.Figure()")
        temp='seg_'+str(y)+'_q_mix'
        for q in full_quarters:
            exec(f"{temp_fig}.add_trace(go.Bar(x=eval(temp)['Segment'],y=eval(temp)[q],name=q))")
        exec(f"{temp_fig}.update_layout(title='Revenue Per Quarter of each Segment in {years[i]}',title_font_size=24,xaxis=dict(tickangle=315))")
        fig_dict[f"Year:{y}"]=[eval(temp_fig),eval(temp)]
        i=i+1

    # Data Transfer
    segment_dict[title]=fig_dict




    main_fig_num=fig_num




    title="(Bar) Revenue Per Year Of Each Quarter For Each Segment"
    fig_dict={}
    fig_num=main_fig_num
    for segment in segments:

        temp = pd.DataFrame()
        for y in start_years:
            main_data='seg_'+str(y)+'_q_mix'
            if temp.empty:
                temp=eval(main_data).loc[eval(main_data)['Segment']==segment]
            else:
                temp=temp.append(eval(main_data).loc[eval(main_data)['Segment']==segment],ignore_index=True)
        if temp.empty==False:
            temp_fig='fig_'+str(fig_num)
            fig_num=fig_num+1;
            exec(f"{temp_fig}=go.Figure()")
            for q in full_quarters:
                exec(f"{temp_fig}.add_trace(go.Bar(x=temp['Year'],y=temp[q],name=q))")
            exec(f"{temp_fig}.update_layout(title=f'Revenue of {segment} per Quarter in Each Year',title_font_size=24,xaxis=dict(tickangle=0))")
            fig_dict[f"Segment:{segment}"]=[eval(temp_fig),temp]


    # Data Transfer
    segment_dict[title]=fig_dict




    main_fig_num=fig_num




    title="(Pie) Revenue Per Segment Of Each Quarter For Each Year"
    fig_dict={}
    fig_num=main_fig_num
    size=len(quarters)*len(start_years)
    ind=0
    ind2=0
    for y in start_years:
        main_data='seg_'+str(y)+'_q_mix'
        for q in quarters:

            if not (eval(main_data)[f'Quarter {q}'] == 0).all():
                temp_fig='fig_'+str(fig_num)
                fig_num=fig_num+1;
                exec(f"{temp_fig}=go.Figure()")
                exec(f"new_data={main_data}[['Segment','Quarter {q}']].copy()")
                exec(f"{temp_fig} = px.pie(new_data, values=f'Quarter {q}', names='Segment')")
                exec(f"{temp_fig}.update_layout(title='Revenue of Year : {years[ind]} , Quarter {q}',title_font_size=24)")
                fig_dict[f"Year:{y}, Quarter:{q}"]=[eval(temp_fig),new_data]
            ind2=ind2+1;
        ind=ind+1

    # Data Transfer
    segment_dict[title]=fig_dict




    main_fig_num=fig_num




    main_data_dict["Segment Analysis"]=segment_dict














# Function for doing all analysis for differnt columns
def col_analysis(val,col_val,x,rotate,main_fig_num):
    product_dict={}
    figures = {}
    fig_num=main_fig_num
#   Creating data copy in pl1_17 format
    pl=new_data.copy()
    pl.dropna(subset=[val], inplace=True)
    for y in start_years:
        temp='pl_'+str(y)
        temp2='new_data_'+str(y)
        exec(f"{temp}={temp2}.copy()")
        exec(f"{temp}.dropna(subset=[val], inplace=True)")
        
#   Finding all the unique values in Product Level  
    pl_values=pl[val].unique()
    
#   Plotting Overall Revenue per Product of Product Level
    global temp_fig
    title=f"(Bar) Revenue Per Value of {val}"
    temp_fig='fig_'+str(fig_num)
    exec(f"global {temp_fig};{temp_fig}=go.Figure()")
    pl_sale_all=pl.groupby(val).BasePrice.sum().sort_values(ascending = False).to_frame(name=f'BasePrice').reset_index()
    exec(f"{temp_fig}=px.bar(pl_sale_all,x=val,y='BasePrice')")
    exec(f"{temp_fig}.update_layout(title=title,title_font_size=24,xaxis=dict(tickangle=rotate))")
    figures[f"{temp_fig}_{fig_num}"] = eval(temp_fig)
    fig_num=fig_num+1;
    fig_dict={}
    fig_dict["Total"]=[eval(temp_fig),pl_sale_all]
    product_dict[title]=fig_dict
    
    
#     Pie Plot of Revenue per Product in Product Level
    title=f"(Pie) Revenue Per Value of {val}"
    temp_fig='fig_'+str(fig_num)
    exec(f"global {temp_fig}; {temp_fig}=go.Figure()")
    exec(f"{temp_fig}=go.Figure()")
    exec(f"{temp_fig} = px.pie(pl_sale_all, values='BasePrice', names=val)")
    exec(f"{temp_fig}.update_layout(title=title,title_font_size=24)")
    figures[f"{temp_fig}_{fig_num}"] = eval(temp_fig)
    fig_num=fig_num+1;
    fig_dict={}
    fig_dict["Total"]=[eval(temp_fig),pl_sale_all]
    product_dict[title]=fig_dict
    
#   Finding the revenue of each product in our product level for each year 
    pl_sale_mix=pd.DataFrame()
    ind=0
    for y in start_years:
        temp='pl_'+str(y)
        temp=eval(temp).groupby(val).BasePrice.sum().sort_values(ascending = False).to_frame(name=f'BasePrice{short_years[ind]}').reset_index()
        ind=ind+1
        if pl_sale_mix.empty:
            pl_sale_mix=temp
        else:
            pl_sale_mix= pd.merge(pl_sale_mix,temp, on=val,how='outer').fillna(0)
            
#   Plotting Revenue of each product in product level each year
    title=f"(Bar) Revenue Per Value in {val} of Each Year"
    temp_fig='fig_'+str(fig_num)
    exec(f"global {temp_fig}; {temp_fig}=go.Figure()")
    for y in short_years:
        temp='BasePrice'+str(y)
        exec(f"{temp_fig}.add_trace(go.Bar(x=pl_sale_mix[val],y=pl_sale_mix[temp],name=temp))")
    exec(f"{temp_fig}.update_layout(title='Revenue Per Product in {col_val} in Each Year',title_font_size=24,xaxis=dict(tickangle=rotate))")
    figures[f"{temp_fig}_{fig_num}"] = eval(temp_fig)
    fig_num=fig_num+1;
    
    # Data Transfer
    fig_dict={}
    fig_dict["All Year"]=[eval(temp_fig),pl_sale_mix]
    product_dict[title]=fig_dict

# Pie Chart of Revenue per year of each product in product level 
    title=f"(Pie) Revenue Per Value in {val} of Each Year"
    fig_dict={}
    size=len(start_years)
    ind=0
    for y in start_years:
        temp_fig='fig_'+str(fig_num)
        exec(f"global {temp_fig}; {temp_fig}=go.Figure()")
        exec(f"{temp_fig} = px.pie(pl_sale_mix, values=f'BasePrice{short_years[ind]}', names=val)")
        exec(f"{temp_fig}.update_layout(title='Revenue Per Product in {col_val} in {years[ind]}',title_font_size=24)")
        figures[f"{temp_fig}_{fig_num}"] = eval(temp_fig)
        fig_num=fig_num+1;
        ind=ind+1;
        fig_dict[f"Year:{y}"]=[eval(temp_fig),pl_sale_mix]
    product_dict[title]=fig_dict

# Making dataframe with product level and its revenue in each quarter
    pl_all_quarter=pl.groupby([val,'Quarter']).BasePrice.sum().sort_values(ascending = False).to_frame(name='PriceAll').reset_index()
    pl_all_q_mix=pd.DataFrame()
    for q in quarters:
        temp=pd.DataFrame()
        temp=pl_all_quarter.loc[pl_all_quarter['Quarter'] == int(q)][[val,'PriceAll']]
        temp.rename(columns = {'PriceAll':f'Quarter {q}'}, inplace = True)
        if pl_all_q_mix.empty:
            pl_all_q_mix=temp
        else:
            pl_all_q_mix= pd.merge(pl_all_q_mix,temp, on=val,how='outer').fillna(0)

#    Plotting revenue per product of product level in each quarter
    title=f"(Bar) Revenue Per Value in {val} of Each Quarter"
    temp_fig='fig_'+str(fig_num)
    exec(f"global {temp_fig}; {temp_fig}=go.Figure()")
    for q in full_quarters:
        exec(f"{temp_fig}.add_trace(go.Bar(x=pl_all_q_mix[val],y=pl_all_q_mix[q],name=q))")
    exec(f"{temp_fig}.update_layout(title=title,title_font_size=24,xaxis=dict(tickangle=rotate))")
    figures[f"{temp_fig}_{fig_num}"] = eval(temp_fig)
    fig_num=fig_num+1;
    # Data Transfer
    fig_dict={}
    fig_dict["Quarter"]=[eval(temp_fig),pl_all_q_mix]
    product_dict[title]=fig_dict

#   Finding Revenue of each product level value per quarter for each year seperately 
    ind=0
    title=f"(Bar) Revenue Per Value in {val} of Each Quarter Per Year"
    fig_dict={}
    for year in start_years:
        fetch_data='new_data_'+str(year)
        work_data='pl_'+str(year)+'_quarter'
        exec(f"{work_data}={fetch_data}.groupby([val,'Quarter']).BasePrice.sum().sort_values(ascending = False).to_frame(name=f'Price{short_years[ind]}').reset_index()")
        main_data='pl_'+str(year)+'_q_mix'
        exec(f"{main_data}=pd.DataFrame()")
        for q in quarters:
            temp=pd.DataFrame()
            temp=eval(work_data).loc[eval(work_data)['Quarter'] == int(q)][[val,f'Price{short_years[ind]}']]
            temp.rename(columns = {f'Price{short_years[ind]}':f'Quarter {q}'}, inplace = True)
            if eval(main_data).empty:
                exec(f"{main_data}=temp")
            else:
                exec(f"{main_data}= pd.merge({main_data},temp, on=val,how='outer').fillna(0)")
        for q in full_quarters:
            if q not in eval(main_data).columns:
                exec(f"{main_data}[q] = 0.0")
        exec(f"{main_data}['Year']='{years[ind]}'")
        
#   Plotting Revenue Per Quarter of each Product Level Value for each year seperately
        
        temp_fig='fig_'+str(fig_num)
        exec(f"global {temp_fig}; {temp_fig}=go.Figure()")
        for q in full_quarters:
            exec(f"{temp_fig}.add_trace(go.Bar(x=eval(main_data)[val],y=eval(main_data)[q],name=q))")
        exec(f"{temp_fig}.update_layout(title='Revenue Per Quarter of each Product Type in {years[ind]}',title_font_size=24,xaxis=dict(tickangle=rotate))")
        figures[f"{temp_fig}_{fig_num}"] = eval(temp_fig)
        fig_num=fig_num+1;
        ind=ind+1;
        globals()[main_data] = locals()[main_data]
        fig_dict[f"Year:{year}"]=[eval(temp_fig),eval(main_data)]
    # Data Transfer
    product_dict[title]=fig_dict
            
        
#   Plotting Quartey and yearly analysis of each product seperately
    title=f"(Bar) Revenue Per Year Of Each Quarter For Each value of {val}"
    fig_dict={}
    for product in pl_values:
        temp = pd.DataFrame()
        for y in start_years:
            main_data='pl_'+str(y)+'_q_mix'
            if temp.empty:
                temp=eval(main_data).loc[eval(main_data)[val]==product]
            else:
                temp=temp.append(eval(main_data).loc[eval(main_data)[val]==product],ignore_index=True)
        if temp.empty==False:
            temp_fig='fig_'+str(fig_num)
            exec(f"global {temp_fig}; {temp_fig}=go.Figure()")
            for q in full_quarters:
                exec(f"{temp_fig}.add_trace(go.Bar(x=temp['Year'],y=temp[q],name=q))")
            exec(f"{temp_fig}.update_layout(title='Revenue of {product} per Quarter in Each Year',title_font_size=24,xaxis=dict(tickangle=rotate))")
            figures[f"{temp_fig}_{fig_num}"] = eval(temp_fig)
            fig_num=fig_num+1;
            fig_dict[f"{col_val}:{product}"]=[eval(temp_fig),temp]
    product_dict[title]=fig_dict       
            
# Pie char of revenue of every quarter for every year
    title=f"(Pie) Revenue Per Value in {val} Of Each Quarter For Each Year"
    fig_dict={}
    size=len(quarters)*len(start_years)
    ind=0
    ind2=0
    for y in start_years:
        main_data='pl_'+str(y)+'_q_mix'
        for q in quarters:
            if not (eval(main_data)[f'Quarter {q}'] == 0).all():
                temp_fig='fig_'+str(fig_num)
                exec(f"global {temp_fig}; {temp_fig}=go.Figure()")
                exec(f"{temp_fig} = px.pie(eval(main_data), values=f'Quarter {q}', names=val)")
                exec(f"{temp_fig}.update_layout(title='Revenue of Year : {years[ind]} , Quarter {q}',title_font_size=24)")
                figures[f"{temp_fig}_{fig_num}"] = eval(temp_fig)
                fig_num=fig_num+1;
                fig_dict[f"Year:{y}, Quarter:{q}"]=[eval(temp_fig),eval(main_data)]
            ind2=ind2+1;
        ind=ind+1
    product_dict[title]=fig_dict
    main_data_dict[f"{col_val} Analysis"]=product_dict
    return fig_num,figures



prev_main_fig_num=main_fig_num
#Product Level 1 Analysis
if cdict['BasePrice'] and cdict['PL'] and cdict['BillDate']:


    # 1sr Aurgument = Database to work on
    # 2st Aurgument = Column Name to be analyzed
    # 3nd Aurgument = Complete Column Name in full form 
    # 4rd Aurgument = Number of Last few product for which we need more description
    # 5th Aurgument = Degree of Ratation of x axis value
    # 6th Aurgument is auto aurguement for refrencing figure number




    new_data=df.copy()
    # Creating multiple dataframe from our new dataframe of updated columns for each year
    for y in start_years:
        temp='new_data_'+str(y)
        x=int(y)+1
        exec(f"{temp}=new_data.loc[(new_data['BillDate'] >= '20{y}-04-01') & (new_data['BillDate'] <= '20{x}-03-31')]")




    fig_num,figures=col_analysis('PL1','Product Level 1',0,315,main_fig_num)




    for key, value in figures.items():
        temp='fig_'+str(prev_main_fig_num)
        exec(f"{temp}=figures[key]")
        prev_main_fig_num=prev_main_fig_num+1




    main_fig_num=fig_num









# If we want analysis of some other column like segment and state then we should follow the below template
if cdict['ExtraAnalysis']:
    # Extra Analysis Start
    # Creating a variable for containig image number

    prev_main_fig_num=main_fig_num

    # Copying df to data for doing some changes in our data

    new_data=df.copy()


    # Provide the name of column in temp for which you want to perform analysis
    temp='State' 
    val=new_data[temp].unique()
    # print(val)
    # We need to edit the data here according to our data as if there are 50 differnt value in column we are providing then the pie chart will not be represented as expected
    # Provide the name of different state for which you want to see the analysis

    new_data=new_data[new_data[temp].isin(['Kentucky','Idaho','Florida'])]

    val=new_data[temp].unique()

    # Creating multiple dataframe from our new dataframe of updated columns for each year
    for y in start_years:
        new_temp='new_data_'+str(y)
        x=int(y)+1
        exec(f"{new_temp}=new_data.loc[(new_data['BillDate'] >= '20{y}-04-01') & (new_data['BillDate'] <= '20{x}-03-31')]")

    # 1sr Aurgument = Database to work on
    # 2st Aurgument = Column Name to be analyzed (Name this column different everytime you use as it should detect as diffent key for our dictionary)
    # 3nd Aurgument = Complete Column Name in full form 
    # 4rd Aurgument = Number of Last few product for which we need more description
    # 5th Aurgument = Degree of Rotation of x axis value
    # 6th Aurgument is auto aurguement for refrencing figure number

    # Provide a detail name of column or the name of column to be shown in plots
    temp2 = 'States'
    fig_num,figures=col_analysis(temp,temp2,0,315,main_fig_num)

    for key, value in figures.items():
        temp='fig_'+str(prev_main_fig_num)
        exec(f"{temp}=figures[key]")
        prev_main_fig_num=prev_main_fig_num+1
    main_fig_num=fig_num
    # Extra Analysis End






# Basic RFM Analysis
if cdict['BasePrice'] and cdict['CustomerName'] and cdict['BillDate']:




    # Making Copy of Data to use while doing rfm analysis 
    # rfm contain all the data, rfm_17 contain data of year 2017-18 and so on
    rfm=df.copy() 
    for y in start_years:
        temp='rfm_'+str(y)
        temp2='df_'+str(y)
        exec(f"{temp}={temp2}.copy()")




    # RFM_Recency contain the Customer Name with the recency value


    # Recency Means days passed after his last purchase
    # Here we find the last purchse data of each customer
    rfm_recency = rfm.groupby(by='CustomerName',as_index=False)['BillDate'].max()
    rfm_recency.columns = ['CustomerName','LastPurchaseDate']

    # Getting the most recent data means the end date of our data
    recent_date = rfm_recency['LastPurchaseDate'].max()

    # Finding recency column in days by substracting recent date by customer last purchase date
    rfm_recency['Recency'] = rfm_recency['LastPurchaseDate'].apply(lambda x: (recent_date-x).days)
    rfm_recency=rfm_recency.sort_values(by = 'Recency')
    rfm_recency


    # Frequency Means number of time a customer has made its purchase
    rfm_frequency = rfm.drop_duplicates().groupby(by=['CustomerName'], as_index=False)['BillDate'].count()
    rfm_frequency.columns = ['CustomerName', 'Frequency']
    rfm_frequency=rfm_frequency.sort_values(by = 'Frequency',ascending=False)
    rfm_frequency


    # Monetary Mean the overall revenue generated by a customer in all the years
    rfm_monetary = rfm.groupby(by='CustomerName', as_index=False)['BasePrice'].sum()
    rfm_monetary.columns = ['CustomerName', 'Monetary']
    rfm_monetary=rfm_monetary.sort_values(by = 'Monetary',ascending=False)
    rfm_monetary


    # RFM_MIX contain all recency frequency and monetary value of a customer
    rfm_mix = rfm_recency.merge(rfm_frequency, on='CustomerName')
    rfm_mix = rfm_mix.merge(rfm_monetary, on='CustomerName')
    rfm_mix=rfm_mix.drop(columns='LastPurchaseDate')





    # The .rank function will give ranking to a customer according to its position among all the customer in a particular column
    rfm_mix['R_rank'] = rfm_mix['Recency'].rank(ascending=False)
    rfm_mix['F_rank'] = rfm_mix['Frequency'].rank(ascending=True)
    rfm_mix['M_rank'] = rfm_mix['Monetary'].rank(ascending=True)

    # Normalizing the rank into a value of 100 by dividing each rank by max possible rank and multiply by 100
    rfm_mix['R_rank_norm'] = (rfm_mix['R_rank']/rfm_mix['R_rank'].max())*100
    rfm_mix['F_rank_norm'] = (rfm_mix['F_rank']/rfm_mix['F_rank'].max())*100
    rfm_mix['M_rank_norm'] = (rfm_mix['M_rank']/rfm_mix['M_rank'].max())*100







    # Finding overall rank = 0.15*Recency + 0.28*Frequency + 0.57*Monetary
    # This value can be changed as required for considering differnt aspect of analysis
    rfm_mix['RFM_Score'] = 0.15*rfm_mix['R_rank_norm']+0.28 * rfm_mix['F_rank_norm']+0.57*rfm_mix['M_rank_norm']
    rfm_mix['RFM_Score'] *= 0.05
    rfm_mix = rfm_mix.round(2)

    # Removing Extra column and sorting the customer according to rfm score
    rfm_mix_sorted=rfm_mix
    rfm_mix_sorted = rfm_mix_sorted.sort_values(by='RFM_Score',ascending=False)
    rfm_mix_sorted=rfm_mix_sorted[['CustomerName', 'RFM_Score']]




    # We have RFM Score in Range 0-5 we seperate it in 5 segment with rfm range as:
    # 1) Top Customer > 4.5
    # 2) High Value Customer > 4
    # 3) Medium Value Customer > 3
    # 4)Low Value Customer > 1.6
    # 5) High Value Customer > 0
    # This value can also be altered as required
    rfm_mix["Customer_segment"] = np.where(rfm_mix['RFM_Score'] >4.5, "Top Customer",(np.where(rfm_mix['RFM_Score'] > 4,"High Value Customer",(np.where(rfm_mix['RFM_Score'] > 3,"Medium Value Customer",(np.where(rfm_mix['RFM_Score'] > 1.6,"Low Value Customer","Lost Customer")))))))




    title="(Pie) General RFM Analysis"
    fig_num=main_fig_num
    temp_fig='fig_'+str(fig_num)
    fig_num=fig_num+1;
    exec(f"{temp_fig}=go.Figure()")
    rfm_segment_counts = rfm_mix['Customer_segment'].value_counts()
    exec(f"{temp_fig} = px.pie(rfm_mix, values=rfm_segment_counts.values,names=rfm_segment_counts.index)")
    exec(f"{temp_fig}.update_layout(title=title,title_font_size=24)")
    for x,trace in enumerate(eval(temp_fig).data):
        trace.marker.colors = [color_map[l] for l in trace.labels]



    fig_dict={}
    fig_dict["Basic"]=[eval(temp_fig),rfm_mix[['CustomerName', 'RFM_Score', 'Customer_segment']]]
    rfm_dict[title]=fig_dict




    main_fig_num=fig_num














    # Quantile-based discretization Method of RFM Analysis




    # Copyting rfm_mix for doing quantitle analysis for rfm
    rfm_q=rfm_mix[['CustomerName','R_rank','F_rank','M_rank']].copy()




    # Here we cut the Recency rank into 5 equal quantitle and labelled them
    rfm_q['r'] = pd.qcut(rfm_q['R_rank'], q=5, labels=[5, 4, 3, 2, 1])




    # Displaying the Customer count in each quantitle and the min and max recency  and avg recency
    rfm_q.groupby('r').agg(
        count=('CustomerName', 'count'),
        min_recency=('R_rank', min),
        max_recency=('R_rank', max),
        avg_recency=('R_rank', 'mean')
    ).sort_values(by='avg_recency')




    # Doing the above analysis for Monetarty
    rfm_q['m'] = pd.qcut(rfm_q['M_rank'], q=5, labels=[1, 2, 3, 4, 5])
    rfm_q.groupby('m').agg(
        count=('CustomerName', 'count'),
        min_monetary=('M_rank', min),
        max_monetary=('M_rank', max),
        avg_monetary=('M_rank', 'mean')
    ).sort_values(by='avg_monetary')




    # Analysis for frequency
    rfm_q['f'] = pd.qcut(rfm_q['F_rank'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])
    rfm_q.groupby('f').agg(
        count=('CustomerName', 'count'),
        min_frequency=('F_rank', min),
        max_frequency=('F_rank', max),
        avg_frequency=('F_rank', 'mean')
    ).sort_values(by='avg_frequency')




    # Finding rfm score by adding all three value as a character
    rfm_q['rfm'] = rfm_q['r'].astype(str) +\
                   rfm_q['f'].astype(str) +\
                   rfm_q['m'].astype(str)




    # Fiding RFM Score by adding all three value as a integer
    rfm_q['RFM_Score'] = rfm_q['r'].astype(int) +\
                         rfm_q['f'].astype(int) +\
                         rfm_q['m'].astype(int)




    rfm_q.groupby('RFM_Score').agg(
        customers=('CustomerName', 'count'),
        mean_recency=('R_rank', 'mean'),
        mean_frequency=('F_rank', 'mean'),
        mean_monetary=('M_rank', 'mean'),
    ).sort_values(by='RFM_Score')




    # As the R,F,M value is in range 1,5 both inclusive the minimum rfm score value is 3 and maximum is 15
    # We seperate this rfm score in 5 segment
    # 1) Top Customer > 13
    # 2) High Value Customer > 11
    # 3) Medium Value Customer > 9
    # 4)Low Value Customer > 6
    # 5) High Value Customer > 0
    # This value can also be altered as required

    rfm_q["Customer_segment"] = np.where(rfm_q['RFM_Score']>=13, "Top Customer",(np.where(rfm_q['RFM_Score'] >= 11,"High Value Customer",(np.where(rfm_q['RFM_Score'] >=9,"Medium Value Customer",(np.where(rfm_q['RFM_Score'] >=6,"Low Value Customer",'Lost Customer')))))))




    title='(Pie) Qunatile RFM Analysis'
    fig_num=main_fig_num
    temp_fig='fig_'+str(fig_num)
    fig_num=fig_num+1;
    exec(f"{temp_fig}=go.Figure()")
    rfm_segment_counts = rfm_q['Customer_segment'].value_counts()
    exec(f"{temp_fig} = px.pie(rfm_q, values=rfm_segment_counts.values, names=rfm_segment_counts.index)")
    exec(f"{temp_fig}.update_layout(title=title,title_font_size=24)")
    for x,trace in enumerate(eval(temp_fig).data):
        trace.marker.colors = [color_map[l] for l in trace.labels]


    # For data Transfer to dictionary for Dashboard
    fig_dict={}
    fig_dict["Quantile"]=[eval(temp_fig),rfm_q[['CustomerName', 'RFM_Score', 'Customer_segment']]]
    rfm_dict[title]=fig_dict




    main_fig_num=fig_num




    # This is RFM Analysis using Quantile method for every year seperately
    title='(Pie) Quantitle RFM Analysis Of Each Year'
    fig_dict={}
    ind=0
    fig_num=main_fig_num
    for y in start_years:
        final_data='rfm_q_'+str(y)
        temp2='df_'+str(y)
        exec(f"rfm_y={temp2}.copy()")
        rfm_y_recency = rfm_y.groupby(by='CustomerName',as_index=False)['BillDate'].max()
        rfm_y_recency.columns = ['CustomerName','LastPurchaseDate']
        recent_date = rfm_y_recency['LastPurchaseDate'].max()
        rfm_y_recency['Recency'] = rfm_y_recency['LastPurchaseDate'].apply(lambda x: (recent_date-x).days)
        rfm_y_recency=rfm_y_recency.sort_values(by = 'Recency')
        rfm_y_frequency = rfm_y.drop_duplicates().groupby(by=['CustomerName'], as_index=False)['BillDate'].count()
        rfm_y_frequency.columns = ['CustomerName', 'Frequency']
        rfm_y_frequency=rfm_y_frequency.sort_values(by = 'Frequency',ascending=False)
        rfm_y_monetary = rfm_y.groupby(by='CustomerName', as_index=False)['BasePrice'].sum()
        rfm_y_monetary.columns = ['CustomerName', 'Monetary']
        rfm_y_monetary=rfm_y_monetary.sort_values(by = 'Monetary',ascending=False)
        rfm_y_mix = rfm_y_recency.merge(rfm_y_frequency, on='CustomerName')
        rfm_y_mix = rfm_y_mix.merge(rfm_y_monetary, on='CustomerName')
        rfm_y_mix = rfm_y_mix.drop(columns='LastPurchaseDate')

        rfm_y_mix['R_rank'] = rfm_y_mix['Recency'].rank(ascending=False)
        rfm_y_mix['F_rank'] = rfm_y_mix['Frequency'].rank(ascending=True)
        rfm_y_mix['M_rank'] = rfm_y_mix['Monetary'].rank(ascending=True)
        rfm_q_y=rfm_y_mix[['CustomerName','R_rank','F_rank','M_rank']].copy()
        rfm_q_y['r'] = pd.qcut(rfm_q_y['R_rank'], q=5, labels=[5, 4, 3, 2, 1])
        rfm_q_y['m'] = pd.qcut(rfm_q_y['M_rank'], q=5, labels=[1, 2, 3, 4, 5])
        rfm_q_y['f'] = pd.qcut(rfm_q_y['F_rank'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])
        rfm_q_y['rfm'] = rfm_q_y['r'].astype(str) +\
                         rfm_q_y['f'].astype(str) +\
                         rfm_q_y['m'].astype(str)
        rfm_q_y['RFM_Score'] = rfm_q_y['r'].astype(int) +\
                               rfm_q_y['f'].astype(int) +\
                               rfm_q_y['m'].astype(int)

        rfm_q_y["Customer_segment"] = np.where(rfm_q_y['RFM_Score']>=13, "Top Customer",(np.where(rfm_q_y['RFM_Score'] >= 11,"High Value Customer",(np.where(rfm_q_y['RFM_Score'] >=9,"Medium Value Customer",(np.where(rfm_q_y['RFM_Score'] >=6,"Low Value Customer",'Lost Customer')))))))
        rfm_q_y[['CustomerName', 'RFM_Score', 'Customer_segment']]
        rfm_segment_counts = rfm_q_y['Customer_segment'].value_counts()

        temp_fig='fig_'+str(fig_num)
        fig_num=fig_num+1;
        exec(f"{temp_fig}=go.Figure()")
        exec(f"{temp_fig} = px.pie(rfm_q_y, values=rfm_segment_counts.values, names=rfm_segment_counts.index)")
        exec(f"{temp_fig}.update_layout(title='Qunatile RFM Analysis of {years[ind]}',title_font_size=24)")
        for x,trace in enumerate(eval(temp_fig).data):
            trace.marker.colors = [color_map[l] for l in trace.labels]

        exec(f"{final_data}=rfm_q_y.copy()")
        fig_dict[f"Year: {years[ind]}"]=[eval(temp_fig),rfm_q_y]
        ind=ind+1
    rfm_dict[title]=fig_dict

    #     print(rfm_q_y.to_string())




    main_fig_num=fig_num




    # Combinig all years Customer Segment Data into one dataframe for comparing
    temp='rfm_q_'+str(start_years[0])
    rfm_q_mix=eval(temp)[["CustomerName","Customer_segment"]].copy()
    rfm_q_mix=rfm_q_mix.rename(columns={"Customer_segment":f"Customer_segment_{start_years[0]}"})
    for y in start_years[1:]:
        temp='rfm_q_'+str(y)
        rfm_q_mix = pd.merge(rfm_q_mix,eval(temp)[['CustomerName','Customer_segment']],how='outer', on = 'CustomerName')
        rfm_q_mix=rfm_q_mix.rename(columns={"Customer_segment":f"Customer_segment_{y}"})





    rfm_q_mix_merged = pd.merge(rfm_q_mix, rfm_q[['CustomerName','Customer_segment']], on='CustomerName',how='outer')
    rfm_q_mix_merged.rename(columns={'Customer_segment': 'Customer_segment_all'}, inplace=True)




    # Finding the Customer who made there first purchase in years 14-15 and similary for all other years
    title="(Pie) Customer Who Joined in a year and there segment in end of that year"
    fig_dict={}
    size=len(start_years)
    i=0
    fig_num=main_fig_num
    while i<size:
        temp='rfm_join_'+str(start_years[i])
        work_data=rfm_q_mix_merged.copy()
        j=0
        while j<=i:
            if j==i:
                work_data=work_data[work_data[f"Customer_segment_{start_years[j]}"].notnull()]
            else:
                work_data=work_data[work_data[f"Customer_segment_{start_years[j]}"].isnull()]
            j=j+1
        work_data=work_data[["CustomerName",f"Customer_segment_{start_years[i]}"]]
        exec(f"{temp}=work_data.copy()")
        rfm_segment_counts = work_data[f'Customer_segment_{start_years[i]}'].value_counts()
        temp_fig='fig_'+str(fig_num)
        fig_num=fig_num+1;
        exec(f"{temp_fig}=go.Figure()")
        exec(f"{temp_fig} = px.pie(eval(temp), values=rfm_segment_counts.values, names=rfm_segment_counts.index)")
        exec(f"{temp_fig}.update_layout(title='Customer Who Joined in {years[i]} and there segment in end of {years[i]}',title_font_size=24)")
        for x,trace in enumerate(eval(temp_fig).data):
            trace.marker.colors = [color_map[l] for l in trace.labels]

        fig_dict[f"Year: {years[i]}"]=[eval(temp_fig),eval(temp)]
        i=i+1
    rfm_dict[title]=fig_dict




    main_fig_num=fig_num




    # Finding the Customer who made there first purchase in years 15-16 and similary for all other years
    # Then plotting such customer with there segment in present year considering overall data
    title="(Pie) Customer Who Joined in a year and there current segment"
    fig_dict={}
    size=len(start_years)
    i=0
    fig_num=main_fig_num
    while i<size:
        temp='rfm_join_'+str(start_years[i])
        work_data=rfm_q_mix_merged.copy()
        j=0
        while j<=i:
            if j==i:
                work_data=work_data[work_data[f"Customer_segment_{start_years[j]}"].notnull()]
            else:
                work_data=work_data[work_data[f"Customer_segment_{start_years[j]}"].isnull()]
            j=j+1
    #     print(f"\n\n\nCustomer Who Joined in {years[i]} :\n")
        extra_data_transfer=work_data[["CustomerName",f"Customer_segment_{start_years[i]}","Customer_segment_all"]]
        work_data=work_data[["CustomerName",f"Customer_segment_all"]]
        exec(f"{temp}=work_data.copy()")
        rfm_segment_counts = work_data[f'Customer_segment_all'].value_counts()
        temp_fig='fig_'+str(fig_num)
        fig_num=fig_num+1;
        exec(f"{temp_fig}=go.Figure()")
        exec(f"{temp_fig} = px.pie(rfm_mix, values=rfm_segment_counts.values, names=rfm_segment_counts.index,color_discrete_map=color_map)")
        exec(f"{temp_fig}.update_layout(title='Customer who joined in {years[i]} and there current segment',title_font_size=24)")
        for x,trace in enumerate(eval(temp_fig).data):
            trace.marker.colors = [color_map[l] for l in trace.labels]

        fig_dict[f"Year: {years[i]}"]=[eval(temp_fig),extra_data_transfer]
        i=i+1
    rfm_dict[title]=fig_dict




    main_fig_num=fig_num









    # Getting all detail of a particular segment like Top Segment and then finding the trend of customer changing segment from Top to other segment in its next year
    # This can help to understand about how well we retain our customer over the year
    title="(Pie) Customer Who Changed There Segment"
    fig_dict={}
    size=len(start_years)
    i=1
    fig_num=main_fig_num

    while i<size:
        temp='rfm_join_'+str(start_years[i])
        work_data=rfm_q_mix.copy()
        rm=eval(temp).index
        work_data=work_data.drop(rm)
        for seg in Customer_Segment:
            temp2=work_data.copy()
            temp2['Customer_segment_'+start_years[int(i)]] = temp2['Customer_segment_'+start_years[int(i)]].fillna('NO Purchase')
            temp2=temp2[temp2['Customer_segment_'+start_years[int(i)-1]]==seg]
            rfm_segment_counts = temp2['Customer_segment_'+start_years[int(i)]].value_counts()
            temp_fig='fig_'+str(fig_num)
            fig_num=fig_num+1;
            exec(f"{temp_fig}=go.Figure()")
            exec(f"{temp_fig} = px.pie(temp2, values=rfm_segment_counts.values, names=rfm_segment_counts.index,color_discrete_map=color_map)")
            exec(f"{temp_fig}.update_layout(title='{seg} Customers of {years[int(i)-1]} who changed in {years[i]}',title_font_size=24)")
            for x,trace in enumerate(eval(temp_fig).data):
                trace.marker.colors = [color_map[l] for l in trace.labels]

            fig_dict[f"Segment:{seg}, Year:{years[int(i)-1]}"]=[eval(temp_fig),temp2]
        i=i+1
    rfm_dict[title]=fig_dict




    main_fig_num=fig_num




    main_data_dict["RFM Analysis"]=rfm_dict




    # This show us the trend in change in customer segment in one year for each segment seperately
    # The first bar of Top Segment Plot means the condition of segment of TOP customer of 14-15 in 15-16 
    title="Stacked Plot of Customer Segment Change in next Year"
    fig_dict={}
    fig_num=main_fig_num

    for seg in Customer_Seg:
        i=1;
        temp="rfm_nextyear_multilevel_"+str(seg)
        exec(f"{temp}=pd.DataFrame()")
        for k,v in main_data_dict["RFM Analysis"]["(Pie) Customer Who Changed There Segment"].items():
            if seg in k:
                temp2=v[1][['CustomerName','Customer_segment_'+start_years[int(i)]]]
                temp2.rename(columns = {f"Customer_segment_{start_years[int(i)]}":f"Customer_segment_{start_years[int(i-1)]}"}, inplace = True)
                i=i+1
                temp_col_name = temp2.iloc[:, 1]
                segment_counts = temp2.iloc[:, 1].groupby(temp_col_name).size()
                total_count = segment_counts.sum()
                segment_percents = segment_counts / total_count * 100
                new_df = pd.DataFrame({
                    'Segment': segment_percents.index,
                    temp2.columns[1]: segment_percents.values
                })
                if eval(temp).empty:
                    exec(f"{temp}=new_df")
                else:
                    exec(f"{temp}=pd.merge({temp}, new_df,on='Segment',how='outer')")

        temp_fig='fig_'+str(fig_num)
        fig_num=fig_num+1;
        x_values = eval(temp).columns[1:]
        y_values = eval(temp)['Segment'].unique()
        df_melt = pd.melt(eval(temp), id_vars=['Segment'], var_name='Year', value_name='Percent')

    #    Creating Label for X axix of out plot
        year_labels = [label.split("_")[-1] for label in x_values]
        new_year_labels = [f"{year_labels[i]}-{int(year_labels[i])+1} to {int(year_labels[i])+1}-{int(year_labels[i])+2}" for i in range(len(year_labels))]
        ticktext = new_year_labels

        exec(f"{temp_fig} = px.bar(df_melt, x='Year', y='Percent', color='Segment', barmode='stack',color_discrete_map=color_map)")
        eval(temp_fig).update_layout(
            title = f"Stacked Segment: {seg}",
            xaxis_title = 'Year', 
            yaxis_title = 'Percent',
            xaxis=dict(
                tickmode='array',
                tickvals=x_values,
                ticktext=ticktext,
            ),)
        fig_dict[f"Stacked Segment:{seg}, Next Year Segment"]=[eval(temp_fig),eval(temp)]
    rfm_dict[title]=fig_dict

    # Temp here tells that all "Top" cutomer of a year and there segment in its next year




    main_fig_num=fig_num









    # This show us the trend in change in customer segment in one year for each segment seperately
    # The first bar of Top Segment Plot means the condition of segment of TOP customer of 14-15 in today
    title="Stacked Plot of Customer Segment Change in current Year"
    fig_dict={}
    fig_num=main_fig_num
    size=len(start_years)-1
    for seg in Customer_Seg:
        i=0
        temp="rfm_finalyear_multilevel_"+str(seg)
        exec(f"{temp}=pd.DataFrame()")
        for k,v in main_data_dict["RFM Analysis"]["(Pie) Customer Who Changed There Segment"].items():
            if seg in k:
                temp2=v[1][['CustomerName','Customer_segment_'+start_years[int(size)]]]
                temp2.rename(columns = {f"Customer_segment_{start_years[int(size)]}":f"Customer_segment_{start_years[int(i)]}"}, inplace = True)
                i=i+1
                temp_col_name = temp2.iloc[:, 1]
                segment_counts = temp2.iloc[:, 1].groupby(temp_col_name).size()
                total_count = segment_counts.sum()
                segment_percents = segment_counts / total_count * 100
                new_df = pd.DataFrame({
                    'Segment': segment_percents.index,
                    temp2.columns[1]: segment_percents.values
                })
                if eval(temp).empty:
                    exec(f"{temp}=new_df")
                else:
                    exec(f"{temp}=pd.merge({temp}, new_df,on='Segment',how='outer')")
        temp_fig='fig_'+str(fig_num)
        fig_num=fig_num+1;
        x_values = eval(temp).columns[1:]
        y_values = eval(temp)['Segment'].unique()
        df_melt = pd.melt(eval(temp), id_vars=['Segment'], var_name='Year', value_name='Percent')

        year_labels = [label.split("_")[-1] for label in x_values]
        new_year_labels = [f"{year_labels[i]}-{int(year_labels[i])+1} to Current Date" for i in range(len(year_labels))]
        ticktext = new_year_labels

        exec(f"{temp_fig} = px.bar(df_melt, x='Year', y='Percent', color='Segment', barmode='stack',color_discrete_map=color_map)")
        eval(temp_fig).update_layout(
            title = f"Stacked Segment: {seg}",
            xaxis_title = 'Year', 
            yaxis_title = 'Percent',
            xaxis=dict(
                tickmode='array',
                tickvals=x_values,
                ticktext=ticktext,
            ),)
        fig_dict[f"Stacked Segment:{seg}, Current Segment"]=[eval(temp_fig),eval(temp)]
    rfm_dict[title]=fig_dict





    main_fig_num=fig_num




    main_data_dict["RFM Analysis"]=rfm_dict














# Customer Retention
if cdict['CustomerName'] and cdict['BillDate']:




    # Customer Churn :Customer churn is the proportion of customers that leave during a given time period
    # Customer Retention :Customer Retention is the ability of a company to retain its customers during a given time period
    # Cohort Analysis : Person that is your customer for 3 years behaves differently than a person that is a customer since 1 month.
    # A Cohort Analysis breaks the data up in related groups rather than looking at all the customers as one unit within a defined time-span.




    # This Plot Contain data for each year seperate so the customer can repeate over year as when in next year customer customer back he will be a new customer in data
    # Making copy of orignial data to work
    fig_dict={}
    title=f"Retention Analysis"
    ind=0
    fig_num=main_fig_num
    for y in start_years:
        temp='df_'+str(y)
        ret=eval(temp).copy()
        # We Do retention analysis on different months so to differentiate each day of
        # a month we just make the date of each month of each year as 1
        def get_month(x):
            return dt.datetime(x.year, x.month, 1)

        # ret['BillDate'] now contain the date as 1 for each BillDate
        ret['BillDate'] = ret['BillDate'].apply(get_month)

        # After this grouping contain all the billdate after the data is grouped using Name
        grouping = ret.groupby('CustomerName')['BillDate']
        # CohortDate will contain the min date of a cutomer from its group means it will be his first purchase date
        ret['CohortDate'] = grouping.transform('min')
    #     print(ret[['BillDate','Name','CohortDate']])
        # This bill_year will contain year of each bill date and bill month contain month of each billdate
        bill_year, bill_month = get_year_int(ret, 'BillDate')

        # This cohort_year will contain year of each cohortdate and cohortmonth contain month of each cohortdate
        cohort_year, cohort_month = get_year_int(ret, 'CohortDate')

        # Calculate difference in years
        years_diff = bill_year - cohort_year

        # Calculate difference in months
        months_diff = bill_month - cohort_month

        # Extract the difference in months from all previous values
        ret['CohortIndex'] = years_diff * 12 + months_diff
        # Groupby with two variable will check all different pair of both variable means it will consider each pair of the variable as one data item
        grouping = ret.groupby(['CohortDate', 'CohortIndex'])

        # Count the number of unique values per Customer
        cohort_data = grouping['CustomerName'].apply(pd.Series.nunique).reset_index()
        # Create a pivot
        cohort_counts = cohort_data.pivot(index='CohortDate', columns='CohortIndex', values='CustomerName')

        # Select the first column and store it to cohort_sizes
        cohort_sizes = cohort_counts.iloc[:,0]

        # Divide the cohort count by cohort sizes along the rows
    #     retention = cohort_counts.divide(cohort_sizes, axis=0)*100
        retention = cohort_counts
    #     Saving retention as dataframe 
        temp_name='ret_'+str(y)
        exec(f"{temp_name} = pd.DataFrame(retention)")


        # Create list of month names for visualisation
        month_list = retention.reset_index()['CohortDate']

        def get_month_name(x):
           return dt.datetime.strftime(x, '%b-%y')
    
        month_list = month_list.apply(get_month_name)



    #     We will not modify our dataframe for having a diffence in place where there is actually no customer vs place where data is not present/provided.
    #     We will all extra row column to complete the dataframe 
    #     0 represent that there are actually no cutomer in that section
    #     -1/Nan represent that data is not procided

        # Initialize inches plot figure
        exec(f"{temp_name} = {temp_name}.reset_index(drop=False)")
        exec(f"{temp_name}.fillna(0, inplace=True)")


        # Define the number of blocks to modify in each row
        n_blocks = min(len(eval(temp_name).columns), len(eval(temp_name)) - 1)

        # Loop over each row and modify the appropriate number of blocks
        for i in range(1, n_blocks + 1):
            eval(temp_name).iloc[i, -i:] = -1


        exec(f"{temp_name} = {temp_name}.replace(-1, np.nan)")

        all_cols = [i for i in range(0, 12)]
        existing_cols = eval(temp_name).columns.tolist()
        missing_cols = list(set(all_cols) - set(existing_cols))
        for col in missing_cols:
            eval(temp_name)[col] = np.nan    

        last_date = pd.to_datetime(eval(temp_name)['CohortDate']).max()
        last_month = int(datetime.strftime(last_date, "%m"))
        last_year = int(datetime.strftime(last_date, "%Y"))
        all_row=[]
        if last_month<=3 :
            temp_val=4
            while temp_val<=12:
                date_obj = datetime(last_year-1,temp_val,1)
                dt64 = np.datetime64(date_obj)
                dt64=pd.to_datetime(dt64)
                dt64 = dt64.strftime('%Y-%m-%d')
                all_row.append(dt64)
                temp_val=temp_val+1
            temp_val=1
            while temp_val<=3:
                date_obj = datetime(last_year,temp_val,1)
                dt64 = np.datetime64(date_obj)
                dt64=pd.to_datetime(dt64)
                dt64 = dt64.strftime('%Y-%m-%d')
                all_row.append(dt64)
                temp_val=temp_val+1


        else:
            temp_val=4
            while temp_val<=12:
                date_obj = datetime(last_year,temp_val,1)
                dt64 = np.datetime64(date_obj)
                dt64=pd.to_datetime(dt64)
                dt64 = dt64.strftime('%Y-%m-%d')
                all_row.append(dt64)
                temp_val=temp_val+1
            temp_val=1
            while temp_val<=3:
                date_obj = datetime(last_year+1,temp_val,1)
                dt64 = np.datetime64(date_obj)
                dt64=pd.to_datetime(dt64)
                dt64 = dt64.strftime('%Y-%m-%d')
                all_row.append(dt64)
                temp_val=temp_val+1


        all_row = np.array(all_row).astype('datetime64')
        for temp_row in all_row:
            if not (eval(temp_name)['CohortDate'].isin([str(temp_row)])).any():
                new_row = pd.DataFrame({"CohortDate": temp_row, **{col: np.nan for col in eval(temp_name).columns[1:]}}, index=[0])
                exec(f"{temp_name}=pd.concat([{temp_name},new_row], ignore_index=True)")

        exec(f"{temp_name} = {temp_name}.sort_values('CohortDate')")
        exec(f"{temp_name} = {temp_name}.reset_index(drop=True)")


        temp_fig='fig_'+str(fig_num)
        fig_num=fig_num+1;
        exec(f"{temp_fig}=go.Figure()")
        exec(f"{temp_fig} = px.imshow({temp_name}.set_index('CohortDate'), y={temp_name}['CohortDate'],width=800,height=800,color_continuous_scale=heatmap_color_scheme_low,text_auto=True)")
        exec(f"{temp_fig}.update_layout(margin=dict(t=200, b=100),title='{years[ind]} Retention Analysis (Considering Yearly Data)',title_font_size=24,xaxis_side='top')")

        fig_dict[f"Year: {years[ind]}"]=[eval(temp_fig),{temp_name}]
        ind=ind+1
    ret_dict[title]=fig_dict




    main_fig_num=fig_num




    title=f"Month-wise Retention Analysis"
    fig_dict={}
    i=0
    fig_num=main_fig_num
    for m in months:
        num=12
        temp='ret_'+str(m)
        exec(f"{temp}=pd.DataFrame()")

        for y in start_years:
            temp2='ret_'+str(y)
            exec(f"{temp2} = {temp2}.replace(np.nan,-1)")
            row = eval(temp2).iloc[i]
            row=row.iloc[1:]
            row=row.tolist()
            row = [value for value in row if not math.isnan(value)]
            row = [round(value, 1) for value in row]
    #         print(f"Row : {row}\n")
            if eval(temp).empty:
                new_months = list(range(0,num))
                exec(f"{temp}=pd.DataFrame(columns=new_months)")
                exec(f"{temp} = {temp}.append(pd.Series(row, index={temp}.columns), ignore_index=True)")
            else:
                exec(f"{temp} = {temp}.append(pd.Series(row, index={temp}.columns), ignore_index=True)")
        eval(temp).insert(0, 'Year', short_years, True)
        exec(f"{temp} = {temp}.replace(-1,np.nan)")
        temp_fig='fig_'+str(fig_num)
        fig_num=fig_num+1;
        exec(f"{temp_fig}=go.Figure()")
        exec(f"{temp_fig} = px.imshow(eval(temp).set_index('Year'), y=eval(temp)['Year'],color_continuous_scale=heatmap_color_scheme_high,text_auto=True)")
        exec(f"{temp_fig}.update_layout(margin=dict(t=200, b=100),title='{months[i]} Retention Analysis (Considering Yearly Data)',title_font_size=24,xaxis_side='top')")

        fig_dict[f"Month:{m}"]=[eval(temp_fig),eval(temp)]
        exec(f"{temp} = {temp}.replace(np.nan,-1)")
        i=i+1
    ret_dict[title]=fig_dict 




    main_fig_num=fig_num




    i=0
    ret_avg_all=pd.DataFrame()
    for m in months:
        temp='ret_'+str(m)
        temp2=eval(temp).copy()
        temp3='ret_avg_'+str(m)
        num_rows=temp2.shape[0]
        row_sum = temp2.iloc[:, 1:].sum(axis=0)/num_rows
        row_sum = pd.Series(['Average'], index=['Year']).append(row_sum)
        temp2 = temp2.append(row_sum, ignore_index=True)
        exec(f"{temp3}= temp2.copy()")
        exec(f"{temp3} = {temp3}.iloc[[-1]]")
        if ret_avg_all.empty:
            ret_avg_all=eval(temp3)
        else:
            ret_avg_all=pd.concat([ret_avg_all,eval(temp3)], axis=0)




    fig_num=main_fig_num
    ret_avg_all_temp=ret_avg_all.copy()
    ret_avg_all_temp = ret_avg_all_temp.reset_index(drop=True)
    ret_avg_all_temp = ret_avg_all_temp.drop('Year', axis=1)
    ret_avg_all_temp['Months']=pd.Series(months)
    last_col = ret_avg_all_temp.columns[-1]
    ret_avg_all_temp = ret_avg_all_temp[[last_col]+list(ret_avg_all_temp.columns[:-1])]
    ret_avg_all_temp= ret_avg_all_temp.replace(-1,np.nan)
    temp_fig='fig_'+str(fig_num)
    fig_num=fig_num+1;
    exec(f"{temp_fig}=go.Figure()")
    exec(f"{temp_fig} = px.imshow(ret_avg_all_temp.set_index('Months'), y=ret_avg_all_temp['Months'],width=800,height=800,color_continuous_scale=heatmap_color_scheme_high,text_auto=True)")
    exec(f"{temp_fig}.update_layout(margin=dict(l=0, r=0, t=200, b=100),title='Average Retention Analysis (Considering yearly data)',title_font_size=24,xaxis_side='top')")

    fig_dict={}
    fig_dict['Average']=[eval(temp_fig),ret_avg_all_temp]
    ret_dict["Average Retention Analysis"]=fig_dict




    main_fig_num=fig_num




    main_data_dict["Retention Analysis (Considering Yearly Data)"]=ret_dict
    ret_dict={}




    # In above retention analysis there is one issue that we have considered yearly data so for plotting row of march we just have data of march as year ends on march and we are not able to analysis this month properly so now we will consider complete data which will provide detail about every month
    # Also it consider all customer as new customer in next year




    # All 12 months descriptive analysis on retention
    # Doing this so that we can check analysis for each month as in above the last month do not have any analysis 




    # Making copy of orignial data to work
    ind=0
    fig_num=main_fig_num
    temp='df'
    ret=eval(temp).copy()

    # Getting this to have the last date for seperating missing data and data actually zero
    first_date = pd.to_datetime(eval(temp)['BillDate']).min()
    last_date = pd.to_datetime(eval(temp)['BillDate']).max()


    # We Do retention analysis on different months so to differentiate each day of
    # a month we just make the date of each month of each year as 1
    def get_month(x):
        return dt.datetime(x.year, x.month, 1)
    # print(ret)
        # ret['BillDate'] now contain the date as 1 for each BillDate
    ret['BillDate'] = ret['BillDate'].apply(get_month)

        # After this grouping contain all the billdate after the data is grouped using Name
    grouping = ret.groupby('CustomerName')['BillDate']
        # CohortDate will contain the min date of a cutomer from its group means it will be his first purchase date
    ret['CohortDate'] = grouping.transform('min')

        # This bill_year will contain year of each bill date and bill month contain month of each billdate
    bill_year, bill_month = get_year_int(ret, 'BillDate')

        # This cohort_year will contain year of each cohortdate and cohortmonth contain month of each cohortdate
    cohort_year, cohort_month = get_year_int(ret, 'CohortDate')

        # Calculate difference in years
    years_diff = bill_year - cohort_year

        # Calculate difference in months
    months_diff = bill_month - cohort_month

        # Extract the difference in months from all previous values
    ret['CohortIndex'] = years_diff * 12 + months_diff

        # Groupby with two variable will check all different pair of both variable means it will consider each pair of the variable as one data item
    grouping = ret.groupby(['CohortDate', 'CohortIndex'])

        # Count the number of unique values per Customer
    cohort_data = grouping['CustomerName'].apply(pd.Series.nunique).reset_index()

        # Create a pivot
    cohort_counts = cohort_data.pivot(index='CohortDate', columns='CohortIndex', values='CustomerName')

        # Select the first column and store it to cohort_sizes
    cohort_sizes = cohort_counts.iloc[:,0]

        # Divide the cohort count by cohort sizes along the rows
    retention_per = cohort_counts.divide(cohort_sizes, axis=0)*100
    retention_val = cohort_counts

    # Retention in Cutomer Numbers
    #Saving retention as dataframe 
    temp_name='ret_extra_months'
    exec(f"{temp_name} = pd.DataFrame(retention_val)")


    # Create list of month names for visualisation
    month_list = retention.reset_index()['CohortDate']

    def get_month_name(x):
        return dt.datetime.strftime(x, '%b-%y')
    
    month_list = month_list.apply(get_month_name)
    exec(f"{temp_name} = {temp_name}.reset_index(drop=False)")


    #     We will not modify our dataframe for having a diffence in place where there is actually no customer vs place where data is not present/provided.
    #     We will all extra row column to complete the dataframe 
    #     0 represent that there are actually no cutomer in that section
    #     -1/Nan represent that data is not procided


    first_month = int(datetime.strftime(first_date, "%m"))
    first_year = int(datetime.strftime(first_date, "%Y"))
    last_month = int(datetime.strftime(last_date, "%m"))
    last_year = int(datetime.strftime(last_date, "%Y"))
    last_missing_row=0
    if last_month<=3:
        last_missing_row=3-last_month
    else:
        last_missing_row=(12-last_month)+3


    all_cols = [i for i in range(0,(len(years)*12))]
    existing_cols = eval(temp_name).columns.tolist()
    missing_cols = list(set(all_cols) - set(existing_cols))
    for col in missing_cols:
        eval(temp_name)[col] = 0

    all_row=[]
    for sy in years:
        sy=sy.split('-')[0]
        temp_val=4
        while temp_val<=12:
            date_obj = datetime(int(sy),temp_val,1)
            dt64 = np.datetime64(date_obj)
            dt64=pd.to_datetime(dt64)
            dt64 = dt64.strftime('%Y-%m-%d')
            all_row.append(dt64)
            temp_val=temp_val+1
        temp_val=1
        while temp_val<=3:
            date_obj = datetime(int(sy)+1,temp_val,1)
            dt64 = np.datetime64(date_obj)
            dt64=pd.to_datetime(dt64)
            dt64 = dt64.strftime('%Y-%m-%d')
            all_row.append(dt64)
            temp_val=temp_val+1

    new_temp_name = eval(temp_name)
    all_row = np.array(all_row).astype('datetime64')
    for temp_row in all_row:
        if not (new_temp_name['CohortDate'].isin([str(temp_row)])).any():
    #         print(temp_row)
            temp_value = temp_row.astype(datetime)
            check_month = int(datetime.strftime(temp_value, "%m"))
            check_year = int(datetime.strftime(temp_value, "%Y"))
            if check_year<first_year or check_year>last_year or ((check_year==first_year)and(check_month<first_month)) or ((check_year==last_year)and(check_month>last_month)):
    #             print(f"check_y : {check_year}  , check_m :{check_month}")
                new_row = pd.DataFrame({"CohortDate": temp_value, **{col: -1 for col in eval(temp_name).columns[1:]}}, index=[0])
                exec(f"{temp_name}=pd.concat([{temp_name},new_row], ignore_index=True)")
            else:
                new_row = pd.DataFrame({"CohortDate": temp_value, **{col: 0 for col in eval(temp_name).columns[1:]}}, index=[0])
                exec(f"{temp_name}=pd.concat([{temp_name},new_row], ignore_index=True)")

    exec(f"{temp_name} = {temp_name}.sort_values('CohortDate')")
    exec(f"{temp_name} = {temp_name}.reset_index(drop=True)")

    # exec(f"{temp_name} = {temp_name}.reset_index(drop=False)")
    exec(f"{temp_name}.fillna(0, inplace=True)")

    # Define the number of blocks to modify in each row
    n_blocks = min(len(eval(temp_name).columns), len(eval(temp_name)) - 1)

    # Loop over each row and modify the appropriate number of blocks
    for i in range(0, ((n_blocks + 1)-last_missing_row)):
        eval(temp_name).iloc[i, -(i+last_missing_row):] = -1

    # print(eval(temp_name))
    exec(f"{temp_name} = {temp_name}.replace(-1, np.nan)")

    temp_fig='fig_'+str(fig_num)
    fig_num=fig_num+1;
    exec(f"{temp_fig}=go.Figure()")
    exec(f"{temp_fig} = px.imshow(eval(temp_name).set_index('CohortDate'),y=eval(temp_name)['CohortDate'],width=800,height=800,color_continuous_scale=heatmap_color_scheme_low,text_auto=True)")
    exec(f"{temp_fig}.update_layout(margin=dict(l=0, r=0, t=200, b=100),title='Overall Retention Analysis (Considering complete data)',title_font_size=24,xaxis_side='top')")
    fig_dict={}
    fig_dict["Overall"]=[eval(temp_fig),eval(temp_name)]
    ret_dict["Overall Retention Analysis (Considering complete data)"]=fig_dict




    main_fig_num=fig_num




    ret_12_months=ret_extra_months.iloc[:,:13]
    if ret_12_months['CohortDate'].dtype != 'datetime64[ns]':
        ret_12_months['CohortDate'] = pd.to_datetime(ret_12_months['CohortDate'])
    ret_12_months.insert(0, 'Months', get_year_int(ret_12_months,'CohortDate')[1], True)
    ret_12_months.insert(0, 'Year', get_year_int(ret_12_months,'CohortDate')[0], True)
    ret_12_months=ret_12_months.drop('CohortDate',axis=1)




    month_map = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
                 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
                 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

    def get_month_name(month_number):
        return month_number.map(month_map)





    fig_num=main_fig_num
    fig_dict={}
    ind=0
    for y in first_years:
        y=int(y)
        temp='ret_alldata_year_'+str(start_years[ind])
        exec(f"{temp}=ret_12_months[((ret_12_months['Year'] == y) & (ret_12_months['Months']>=4)) | ((ret_12_months['Year']==y+1) & (ret_12_months['Months']<=3))].copy()")
        exec(f"{temp}.insert(1, 'Months_Name', get_month_name({temp}['Months']), True)")
        exec(f"{temp}={temp}.drop('Year',axis=1)")
        exec(f"{temp}={temp}.drop('Months',axis=1)")
    #     print(temp.to_string())
        temp_fig='fig_'+str(fig_num)
        fig_num=fig_num+1;
        exec(f"{temp_fig}=go.Figure()")
        exec(f"{temp_fig} = px.imshow({temp}.set_index('Months_Name'),y={temp}['Months_Name'],width=800,height=800,color_continuous_scale=heatmap_color_scheme_low,text_auto=True)")
        exec(f"{temp_fig}.update_layout(margin=dict(l=0, r=0, t=200, b=100),title='Retention of {y}-{y+1} (Considering Complete Data)',title_font_size=24,xaxis_side='top')")
        fig_dict[f"Year :{years[ind]}"]=[eval(temp_fig),eval(temp)]
        ind=ind+1

    ret_dict[f"Retention of all years"]=fig_dict




    main_fig_num=fig_num




    title=f"Month-wise Retention Analysis"
    fig_dict={}
    i=0
    fig_num=main_fig_num
    for m in months:
        num=12
        temp='ret_all_'+str(m)
        exec(f"{temp}=pd.DataFrame()")

        for y in start_years[:-data_incomplete_year_count]:
            temp2='ret_alldata_year_'+str(y)
            exec(f"{temp2} = {temp2}.fillna(-1)")

            row = eval(temp2).iloc[i]
            row=row.iloc[1:]
            row=row.tolist()
            row = [value for value in row if not pd.isna(value)]
            row = [round(value, 1) for value in row]
            if eval(temp).empty:
                new_months = list(range(1,num+1))
                exec(f"{temp}=pd.DataFrame(columns=new_months)")
                exec(f"{temp} = {temp}.append(pd.Series(row, index={temp}.columns), ignore_index=True)")
            else:
                exec(f"{temp} = {temp}.append(pd.Series(row, index={temp}.columns), ignore_index=True)")
        eval(temp).insert(0, 'Year', short_years[:-data_incomplete_year_count], True)
        exec(f"{temp} = {temp}.replace(-1,np.nan)")
        temp_fig='fig_'+str(fig_num)
        fig_num=fig_num+1;
        exec(f"{temp_fig}=go.Figure()")
        exec(f"{temp_fig} = px.imshow(eval(temp).set_index('Year'), y=eval(temp)['Year'],color_continuous_scale=heatmap_color_scheme_low,text_auto=True)")
        exec(f"{temp_fig}.update_layout(margin=dict(t=200, b=100),title='{months[i]} Retention Analysis (Considering Complete Data)',title_font_size=24,xaxis_side='top')")
        fig_dict[f"Month:{m}"]=[eval(temp_fig),eval(temp)]
        i=i+1
    ret_dict[title]=fig_dict 




    main_fig_num=fig_num




    title=f"(Line) Retention Analysis"
    fig_dict={}
    i=0
    fig_num=main_fig_num
    for m in months:
        temp='ret_all_'+str(m)
        exec(f"{temp} = {temp}.replace(-1, pd.NaT)") #Replacing all -1 with NAN so that it does not get plot
        traces = []
        for i in range(len(eval(temp))):
            traces.append(go.Scatter(
                x=eval(temp).columns[1:], # Use the column names as x-axis values
                y=eval(temp).iloc[i, 1:], # Select the data values for the current row
                name=eval(temp)['Year'][i] # Use the Year column for the legend label
            ))

        # Define the plot layout
        layout = go.Layout(
            title=f"Retention Analysis of {m} (Considering Complete Data)",
            xaxis=dict(title='Months'),
            yaxis=dict(title='Customer Retained')
        )

        # Create the plot figure
        temp_fig='fig_'+str(fig_num)
        fig_num=fig_num+1;
        exec(f"{temp_fig}= go.Figure(data=traces, layout=layout)")
        fig_dict[f"Month:{m}"]=[eval(temp_fig),eval(temp)]
        i=i+1
    ret_dict[title]=fig_dict 




    main_fig_num=fig_num




    main_data_dict["Retention Analysis (Considering Complete Data)"]=ret_dict




# Cross Selling Recomendation
if cdict['ProductDetail'] and cdict['OrderID'] and cdict['Segment']:

    # Creating a datacopy for working
    csr=df.copy()




    # # Renaming Column for working easily
    # csr['OrderID']=df['Sales Order']
    # csr['ProductDetail']=df['Description']




    # Preprocessing the data
    missing = csr.isna().sum()
    csr=csr.dropna(subset=['ProductDetail'])
    csr=csr.dropna(subset=['OrderID'])
    # missing = csr.isna().sum()




    # csr_g contain copy of csr for doing genral cross selling analysis
    csr_g=csr.copy()




    # Adding a product bundle column which will contain all the product under same orderID
    csr=csr[csr['OrderID'].duplicated(keep=False)]
    csr_g['ProductBundle']=csr_g.groupby(['OrderID'])['ProductDetail'].transform(lambda x: ','.join(x))
    csr_g=csr_g[['OrderID','ProductBundle','Segment']].drop_duplicates()




    # Here we create a counter and count the number of purchase of each combination
    # of product and display the most common combination
    count = Counter()
    general_cross_sell={}
    for row in csr_g['ProductBundle']:
        row_list=row.split(',')
        count.update(Counter(combinations(row_list,2)))
    count=count.most_common(10)

    i=0

    general_cross_sell['General'] = pd.DataFrame([{'Product 1': t[0][0], 'Product 2': t[0][1], 'Count': t[1]} for t in count])
    cross_sell_dict['General']=general_cross_sell


    # Segment wise Cross Selling

    csr_seg=csr.copy()
    csr_seg=csr_seg.dropna(subset=['Segment'])
    csr_seg=csr_seg[csr_seg['OrderID'].duplicated(keep=False)]
    csr_seg['ProductBundle']=csr_seg.groupby(['OrderID','Segment'])['ProductDetail'].transform(lambda x: ','.join(x))
    csr_seg=csr_seg[['OrderID','ProductBundle','Segment']].drop_duplicates()
    new_segments=csr_seg['Segment'].unique()
    segment_cross_sell={}
    for seg in new_segments:
        count = Counter()
        csr_new=csr_seg[csr_seg['Segment']==seg].copy()
        for row in csr_new['ProductBundle']:
            row_list=row.split(',')
            count.update(Counter(combinations(row_list,2)))
        count=count.most_common(10)
        i=0
        segment_cross_sell[seg] = pd.DataFrame([{'Product 1': t[0][0], 'Product 2': t[0][1], 'Count': t[1]} for t in count])
    cross_sell_dict['Segment']=segment_cross_sell




# State wise Cross Selling
if cdict['ProductDetail'] and cdict['OrderID'] and cdict['ProductDetail']:




    csr_state=csr.copy()
    missing = csr_state.isna().sum()
    csr_state=csr_state.dropna(subset=['State'])
    csr_state=csr_state[csr_state['OrderID'].duplicated(keep=False)]
    csr_state['ProductBundle']=csr_state.groupby(['OrderID','State'])['ProductDetail'].transform(lambda x: ','.join(x))
    csr_state=csr_state[['OrderID','ProductBundle','State']].drop_duplicates()
    new_states=csr_state['State'].unique()
    state_cross_sell={}
    for st in new_states:
        count = Counter()
        csr_new=csr_state[csr_state['State']==st].copy()
        for row in csr_new['ProductBundle']:
            row_list=row.split(',')
            count.update(Counter(combinations(row_list,2)))
        count=count.most_common(10)
        i=0
        state_cross_sell[st] = pd.DataFrame([{'Product 1': t[0][0], 'Product 2': t[0][1], 'Count': t[1]} for t in count])
    cross_sell_dict['State']=state_cross_sell

    main_data_dict["Cross Selling"]=cross_sell_dict




def is_array(obj):
    return isinstance(obj, list)


external_stylesheets = ['/assets/style.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
server=app.server

# Create the layout
app.layout = html.Div([
    dcc.Dropdown(
        id='dropdown1',
        options=[
            {'label': k, 'value': k} for k in main_data_dict.keys()
        ],
        value=list(main_data_dict.keys())[0],
        className='dropdown1',
    ),
    dcc.Dropdown(id='dropdown2',className='dropdown2'),
    dcc.Dropdown(id='dropdown3',multi=True,className='dropdown3'),
    html.Button('DataFrames', id='toggle-button', n_clicks=0, className='button'),
    html.Div(id='output-container', className='output-container')
], className='container')

# Create the callback functions
@app.callback(
    dash.dependencies.Output('dropdown2', 'options'),
    [dash.dependencies.Input('dropdown1', 'value')]
)
def update_dropdown2_options(selected_key):
    # print(f"Key:{selected_key}, Subkey1:{type(main_data_dict[selected_key])}")
    sub_dict = main_data_dict[selected_key]
    return [{'label': k, 'value': k} for k in sub_dict.keys()]

@app.callback(
    dash.dependencies.Output('dropdown2', 'value'),
    [dash.dependencies.Input('dropdown2', 'options')]
)
def update_dropdown2_value(options):
    # print(f"OPTIONS is : {options}\n")
    return options[0]['value']

@app.callback(
    dash.dependencies.Output('dropdown3', 'options'),
    [dash.dependencies.Input('dropdown1', 'value'),
     dash.dependencies.Input('dropdown2', 'value')]
)
def update_dropdown3_options(selected_key, selected_subkey):
    # print(f"HKey:{selected_key}, HSubkey1:{selected_subkey}, HSubkey2:{type(main_data_dict[selected_key][selected_subkey])}")
    figure_dict = main_data_dict[selected_key][selected_subkey]
    return [{'label': k, 'value': k} for k in figure_dict.keys()]

@app.callback(
    
    dash.dependencies.Output('dropdown3', 'value'), 
    [dash.dependencies.Input('dropdown3', 'options')]
)
def update_dropdown3_value(options):
    # print(f"Value is : {options[0]['value']}")
    return options[0]['value']

@app.callback(
    dash.dependencies.Output('output-container', 'children'),
    [dash.dependencies.Input('dropdown1', 'value'),
     dash.dependencies.Input('dropdown2', 'value'),
     dash.dependencies.Input('dropdown3', 'value'),
     dash.dependencies.Input('toggle-button', 'n_clicks')]
)


def display_data(selected_key, selected_subkey, keys, n_clicks):
    if not keys:
        return None
    if isinstance(keys, str):
        keys = [keys]


    temp = main_data_dict[selected_key][selected_subkey]
    figure_dict=[temp[k] for k in keys]
    components = []
    i=1
    for fig in figure_dict:
        if not is_array(fig):
            components.append(html.Div([
                html.H3(f"Dataframe {i}:"),
                html.Div([
                    dcc.Markdown(f"```{fig}```")
                ])
            ]))
            i+=1
        else:
            if n_clicks % 2 == 1:
                for df in fig[1:]:
                    components.append(html.Div([
                        html.H3(f"Dataframe {i}:"),
                        html.Div([
                            dcc.Markdown(f"```{df}```")
                        ])
                    ]))
                    i+=1
            else:
                components.append(dcc.Graph(figure=fig[0]))
                # components=components
    return components


    

if __name__ == '__main__':
    app.run_server(debug=True)





