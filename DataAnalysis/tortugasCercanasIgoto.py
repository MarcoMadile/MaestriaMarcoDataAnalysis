import pandas as pd 
import glob
import numpy as np
from geopy import distance 
import ipdb
import datetime





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

#some times are in format "8:57" and need to be in format "8:57:00"
def fixing_time(x):
    
    x=str(x)
    if len(x)>9:
        x=x.split(" ")[1]
    if  " " in x:
        x=x.replace(" ","")
    if x.count(":")==1:
        return x+":00"
    else:
        return x

#if tortugues were close in time and space on same day, it prints then in map and saves one map for each day, it also saves in a csv file some relevant data from that pair of points
def save_spacetime_encounters(df,dates,min_dist_space,min_dist_time,t_names,file_out="encuentros_Igoto_20min.csv"):
    colum_names=["day","time distance","space distance","time" ,"name one", "name two"]
    df_out=pd.DataFrame(columns=colum_names,dtype=str)
    for day in dates: 
        for i in range(len(df)):
            for j in range(i+1,len(df)):
                dfout=find_near_spacetime_points(df[i],df[j],min_dist_time,day,min_dist_space,df_out,t_names[i],t_names[j])
    dfout.to_csv(file_out,index=False,sep=";")

#finds all points that are close in time and space on a day
def find_near_spacetime_points(df1,df2,min_dist_time,day,min_dist_space,df_out,t_name1,t_name2):
    points1=get_cordinates_from_day(df1,day)
    points2=get_cordinates_from_day(df2,day)
    if ((len(points1)>0) and (len(points2)>0)):
        for point1 in points1:
            distances=np.array([(distance.distance(x,point1).m) for x in points2]).astype(int)
            indexes=np.where(distances<min_dist_space)#where the distance is smaller from min distance
            for k in indexes[0]:               
                dt,t=get_delta_time(df1,df2,day,point1,points2[k])
                if dt<min_dist_time:
                    dx=distances[k]
                    dict={"day":str(day),"time distance":str(dt),"space distance":str(dx),"time":str(t),"name one":str(t_name1),"name two":str(t_name2)}
                    df_aux=pd.DataFrame(dict,dtype=str,index=[0])
                    df_out=pd.concat([df_out,df_aux],ignore_index=True)
    return df_out

def get_cordinates_from_day(df,day):
    points=zip(df.loc[df['Date']==day][" Latitude"],df.loc[df['Date']==day][" Longitude"])
    points=np.array(list(points))
    return points

#gets difference in time from points from a day in dataframes
def get_delta_time(df1,df2,day,point1,point2):
    t1=pd.to_datetime(df1.loc[df1["Date"]==day].loc[(df1[" Latitude"]==point1[0]) & (df1[" Longitude"]==point1[1])][" Time"],format="%H:%M:%S")
    t2=pd.to_datetime(df2.loc[df2["Date"]==day].loc[(df2[" Latitude"]==point2[0]) & (df2[" Longitude"]==point2[1])][" Time"],format="%H:%M:%S")
    t1=t1.to_numpy()
    t2=t2.to_numpy()
    dt=((t1[0]-t2[0]).astype('timedelta64[s]')).astype("int")
    return np.abs(dt/60),t1[0]




folder="DataAnalysis\DatosIgoto2022Todos" #folder where the files are
df,dates,t_names=get_files_and_dates(folder)

min_dist_space=20 #minimun distance in space to filter points that were close
min_dist_time=20  #minimun distance in time to filter points that were close
min_dist_days=2 #minimun distance in days to filter points that were close

save_spacetime_encounters(df,dates,min_dist_space,min_dist_time,t_names)