import pandas as pd 
import glob
import numpy as np
from geopy import distance 
import ipdb
import datetime
from datetime import timedelta



#getting all files in folder 
def get_files_and_dates(folder):
    filenames=folder+"/*.xlsx"
    files=glob.glob(filenames)
    df=[]
    t_names=[]
    for a in files:
        df.append(pd.read_excel(a))
        tort=a.replace(".xls","")
        tort=tort.replace(folder,"")
        tort=tort.replace("\\","")
        tort=tort.replace("x","")
        if tort[1]=="0":
            tort=tort[0]+tort[2:]
        t_names.append(str(tort))
    dates=[]
    for j in range(len(df)):
        df[j].dropna(subset=['Date'], inplace=True)
        df[j]["Date"]=df[j]["Date"].apply(fixing_dates)
        df[j][" Time"]=df[j][" Time"].apply(fixing_time)
        dates.append(np.unique(df[j]["Date"]))    
    dates=np.unique(np.concatenate(dates).ravel())
    return df,dates,t_names


#some files have dates like: "21:01:2022" (type datetime) and I want all dates in same format: "2022/01/21" type str
def fixing_dates(x):
    if isinstance(x, datetime.date):
        return x.strftime("%Y/%m/%d")
    else:
        return str(x)

#some times are in format "8:57" and need to be in format "8:57:00" and also remove seconds
def fixing_time(x):
    x=str(x)
    if len(x)>9:
        x=x.split(" ")[1]
    if  " " in x:
        x=x.replace(" ","")
    if x.count(":")==1:
        return x+":00"
    else:
        return x.split(":")[0]+":"+x.split(":")[1]+":00"

#make maps from points in df, each map has one point for each turtle and one map for each 15 minutes of medition.
def make_maps(dfs,dates,t_names,path=""):
    df_for_loop=unify_df(dfs,t_names)
    

#make unique df with datetime object in column time and turtle name in column name
def unify_df(dfs,t_names):
    unifyed_df=pd.DataFrame(columns=["Time","Latitude","Longitude","Turtle"])
    for h in range(len(dfs)):
        df_aux=pd.DataFrame(columns=["Time","Latitude","Longitude","Turtle"])
        time_series=pd.to_datetime(dfs[h]["Date"] + dfs[h][" Time"],format="%Y/%m/%d%H:%M:%S")
        df_aux["Time"]=time_series
        df_aux["Latitude"]=dfs[h][" Latitude"]
        df_aux["Longitude"]=dfs[h][" Longitude"]
        df_aux["Turtle"]=t_names[h]
        df_aux=interpol_trayectories(df_aux)
        ipdb.set_trace()
        unifyed_df=pd.concat([unifyed_df,df_aux],ignore_index=True)
    unifyed_df=unifyed_df.sort_values(by=["Time"],ignore_index=True)
    return unifyed_df

def interpol_trayectories(df):
    df.index=df["Time"]
    df_aux=df.loc[~df.index.duplicated(), :]
    df_aux=df_aux.asfreq(freq="60s")
    k = 20
    #reset index whitout adding column 
    df_aux["Time"]=df_aux.index
    df_aux.reset_index(inplace=True,drop=True)
    nan_places = df_aux.Longitude.isnull()
    #check if there are at least k nan consecutive values and if so delete them.
    for i in range(len(nan_places)):
        j=1
        while nan_places[i:i+j].sum()==j and i+j<len(nan_places):
            j+=1
        if j>=k:
            df_aux=df_aux.drop(df_aux.index[i:i+j-1])
    
    return df_aux
    
                

                
        

    




folder="DataAnalysis\DatosIgoto2022Todos" 
dfs,dates,t_names=get_files_and_dates(folder)
make_maps(dfs,dates,t_names)