from dataclasses import replace
from matplotlib.pyplot import draw
import pandas as pd 
import glob
import numpy as np
from geopy import distance 
import folium
import ipdb
from datetime import datetime
from datetime import timedelta


#fixing time because some files have time=8 when i want time= 0008 (so then i have it in same format)
def fixing_time(x):
    x=str(x)
    if len(x)==4:
        return x
    elif len(x)==2:
        return "00"+x
    else:
        return "0"+x

#some files have dates like: "2022-01-21" and I want all dates in same format: "21/01/2022"
def fixing_dates(x):
    x=str(x)
    if "-" in x:
        aux=x.split("-")
        return aux[2]+"/"+aux[1]+"/"+aux[0]
    else:
        return x

#returns all cordinates
def get_all_coordinates(df):
    points=zip(df.loc[:]["lat"],df.loc[:]["lon"])
    points=np.array(list(points))
    return points

#getting all files in folder 
def get_files_and_dates(folder):
    filenames=folder+"/*.csv"
    files=glob.glob(filenames)
    df=[]
    tnames=[]
    for a in files:
        df.append(pd.read_csv(a,sep=";",encoding='latin-1'))
        tort=a.replace(".csv","")
        tort=tort.replace(folder,"")
        tort=tort.replace("\\","")
        tort=tort.split("_", 1)[0]
        if tort[1]=="0":
            tort=tort[0]+tort[2:]
        tnames.append(str(tort))
    dates=[]
    for j in range(len(df)):
        df[j]["timeGMT"]=df[j]["timeGMT"].apply(fixing_time)
        df[j]["date"]=df[j]["date"].apply(fixing_dates)
        dates.append(np.unique(df[j]["date"]))
    dates=np.unique(np.concatenate(dates).ravel())
    return df,dates,tnames

#if tortugues were close in same day, it prints then in map and saves one map for each day
def check_encounters(df,dates,mindist):
    colors=["red","green","yellow","grey","pink","aqua","purple","white","black","brown","lime","beige"]
    for day in dates: 
        map1=get_map()
        for i in range(len(df)):
            for j in range(i+1,len(df)):
                draw_near_points(df[i],df[j],colors[i],colors[j],map1,mindist,day)
        name=str(day)+"_nearpoints"+".html"
        name=name.replace("/","_")
        print("guarde el día ",day)
        map1.save(name)

def get_map():
    coords=[-40.585390,-64.996220]
    map1 = folium.Map(location = coords,zoom_start=15)
    folium.TileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",attr="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community").add_to(map1)
    return map1 

#draws near points only in space for same date, each color same tortugue
def draw_near_points(df1,df2,color1,color2,map1,mindist,day):
    points1=get_cordinates_from_day(df1,day)
    points2=get_cordinates_from_day(df2,day)
    if ((len(points1)>0) and (len(points2)>0)):
        for point1 in points1:
            distances=np.array([(distance.distance(x,point1).m) for x in points2]).astype(int)
            indexes=np.where(distances<mindist)#where the distance is smaller from min distance
            for k in indexes[0]:
                
                dt=get_delta_time(df1,df2,day,point1,points2[k])
                dx=distances[k]
                x2=points2[k]
                folium.PolyLine([x2,point1],color=color1,weight=2.5, opacity=0.5,popup="dt = "+str(dt)+" and dr ="+str(dx)).add_to(map1)

                folium.CircleMarker([x2[0],x2[1]],radius=3,stroke=False,fill=True,fill_color=color2,fill_opacity=1).add_to(map1)

                folium.CircleMarker([point1[0],point1[1]],radius=3,stroke=False,fill=True,fill_color=color1,fill_opacity=1).add_to(map1)
    

def get_cordinates_from_day(df,day):
    points=zip(df.loc[df['date']==day]["lat"],df.loc[df['date']==day]["lon"])
    points=np.array(list(points))
    return points

#gets difference in time from points from a day in dataframes
def get_delta_time(df1,df2,day,point1,point2):
    t1=pd.to_datetime(df1.loc[df1["date"]==day].loc[df1["lat"]==point1[0]]["timeGMT"],format="%H%M")
    t2=pd.to_datetime(df2.loc[df2["date"]==day].loc[df2["lat"]==point2[0]]["timeGMT"],format="%H%M")
    t1=t1.to_numpy()
    t2=t2.to_numpy()
    dt=((t1[0]-t2[0]).astype('timedelta64[s]')).astype("int")
    return np.abs(dt/60),t1[0]

#if tortugues were close in time and space on same day, it prints then in map and saves one map for each day, it also saves in a csv file some relevant data from that pair of points
def check_spacetime_encounters(df,dates,mindistspace,mindisttime,tnames,path=""):
    columnnames=["day","time distance","space distance","sex one", "sex two","time" ,"name one", "name two"]
    dfout=pd.DataFrame(columns=columnnames,dtype=str)
    for day in dates: 
        for i in range(len(df)):
            for j in range(i+1,len(df)):
                dfout=draw_near_spacetime_points(df[i],df[j],mindisttime,day,mindistspace,dfout,tnames[i],tnames[j])
    dfout.to_csv(path+"encuentroscompleto_tiempo_largo.csv",index=False,sep=";")

#makes drawing in maps and saves data in df 
def draw_near_spacetime_points(df1,df2,mindisttime,day,mindistspace,dfout,tname1,tname2):
    points1=get_cordinates_from_day(df1,day)
    points2=get_cordinates_from_day(df2,day)
    if ((len(points1)>0) and (len(points2)>0)):
        for point1 in points1:
            distances=np.array([(distance.distance(x,point1).m) for x in points2]).astype(int)
            indexes=np.where(distances<mindistspace)#where the distance is smaller from min distance
            for k in indexes[0]:                
                dt,t=get_delta_time(df1,df2,day,point1,points2[k])
                if dt<mindisttime:
                    dx=distances[k]
                    x2=points2[k]
                    g1=df1["sexo"][3]
                    g2=df2["sexo"][3]
                    dict={"day":str(day),"time distance":str(dt),"space distance":str(dx),"sex one":str(g1),"sex two":str(g2),"time":str(t),"name one":str(tname1),"name two":str(tname2)}
                    dfaux=pd.DataFrame(dict,dtype=str,index=[0])
                    dfout=pd.concat([dfout,dfaux],ignore_index=True)
    return dfout
                
        
def check_spacetime_encounters_neardays(df,dates,mindistspace,mindistdays,tnames,path=""):
    columnnames=["day","daydif","space distance","sex one", "sex two","name one", "name two"]
    dfout=pd.DataFrame(columns=columnnames,dtype=str)
    for day in dates: 
        for i in range(len(df)):
            for j in range(i+1,len(df)):
                dfout=check_near_spacedays_points(df[i],df[j],mindistdays,day,mindistspace,dfout,tnames[i],tnames[j])
    dfout.to_csv(path+"encuentroscompleto_neardays2.csv",index=False,sep=";")
            
                

def check_near_spacedays_points(df1,df2,mindistdays,day,mindistspace,dfout,tname1,tname2):
    points1=get_cordinates_from_day(df1,day)
    dayDatetime=datetime.strptime(day,"%d/%m/%Y")
    daystocheck=[day]
    for h in range(1,mindistdays+1):
        auxday=dayDatetime+timedelta(days=h)
        daystocheck.append(auxday.strftime("%d/%m/%Y"))
        auxday=dayDatetime-timedelta(days=h)
        daystocheck.append(auxday.strftime("%d/%m/%Y"))
    for day1 in daystocheck:
        points2=get_cordinates_from_day(df2,day1)
        if ((len(points1)>0) and (len(points2)>0)):
            for point1 in points1:
                distances=np.array([(distance.distance(x,point1).m) for x in points2]).astype(int)
                indexes=np.where(distances<mindistspace)#where the distance is smaller from min distance
                for k in indexes[0]:                
                    dx=distances[k]
                    x2=points2[k]
                    g1=df1["sexo"][3]
                    g2=df2["sexo"][3]
                    dict={"day":str(day),"daydif":str(day1),"space distance":str(dx),"sex one":str(g1),"sex two":str(g2),"name one":str(tname1),"name two":str(tname2)}
                    dfaux=pd.DataFrame(dict,dtype=str,index=[0])
                    dfout=pd.concat([dfout,dfaux],ignore_index=True)
    return dfout
    

def check_space_encounters_any_day(df,mindistspace,tnames,path=""):
    columnnames=["day","daydif","space distance","sex one", "sex two","name one", "name two"]
    dfout=pd.DataFrame(columns=columnnames,dtype=str)
    for i in range(len(df)):
            for j in range(i+1,len(df)):
                if not tnames[i]==tnames[j]:
                    dfout=check_near_space_points(df[i],df[j],mindistspace,dfout,tnames[i],tnames[j])
    dfout.to_csv(path+"encuentroscompleto_only_space.csv",index=False,sep=";")

def check_near_space_points(df1,df2,mindistspace,dfout,tname1,tname2):
    points1=get_all_coordinates(df1)
    points2=get_all_coordinates(df2)
    dates1=list(df1["date"])
    dates2=list(df2["date"])
    g1=df1["sexo"][3]
    g2=df2["sexo"][3]
    if ((len(points1)>0) and (len(points2)>0)):
        for h in range(len(points1)):
            point1=points1[h]
            distances=np.array([(distance.distance(x,point1).m) for x in points2]).astype(int)
            indexes=np.where(distances<mindistspace)#where the distance is smaller from min distance
            for k in indexes[0]:                
                    dx=distances[k]
                    x2=points2[k]
                    dict={"day":str(dates1[h]),"daydif":str(dates2[k]),"space distance":str(dx),"sex one":str(g1),"sex two":str(g2),"name one":str(tname1),"name two":str(tname2)}
                    dfaux=pd.DataFrame(dict,dtype=str,index=[0])
                    dfout=pd.concat([dfout,dfaux],ignore_index=True)
    print("done "+tname1+"-"+tname2)
    return dfout
                
folder="todaslascampanas" #folder where the files are
df,dates,tnames=get_files_and_dates(folder)

mindistspace=20 #minimun distance in space to filter points that were close
mindisttime=20  #minimun distance in time to filter points that were close
mindistdays=2 #minimun distance in days to filter points that were close
path_csv="MaestriaMarco\DataAnalysis\encuentros_csv\\" #path to save the csv files
#check_encounters(df,dates,mindistspace)
#check_spacetime_encounters_neardays(df,dates,mindistspace,mindistdays,tnames,path_csv)
#check_spacetime_encounters(df,dates,mindistspace,mindisttime,tnames,path=path_csv)
check_space_encounters_any_day(df,mindistspace,tnames,path=path_csv)

