import pandas as pd 
import glob
import numpy as np
import ipdb
import datetime
from datetime import timedelta
import folium
from html2image import Html2Image
import os
from PIL import Image

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
    return df,t_names


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
def get_df_days_colors(dfs,t_names):
    df_for_loop=unify_df(dfs,t_names)
    colors={"T6":"purple","T12":"white","T10":"black","T30":"orange","T54":"blue","T79":"pink"}
    #GET ONLY date (day month and year) FROM DATETIME OBJECT IN TIME COLUMN 
    days = df_for_loop["Time"].dt.date
    return df_for_loop,days, colors


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
        #df_aux=interpol_trayectories(df_aux)
        #ipdb.set_trace()
        unifyed_df=pd.concat([unifyed_df,df_aux],ignore_index=True)
    unifyed_df=unifyed_df.sort_values(by=["Time"],ignore_index=True)
    return unifyed_df

def save_maps(undf,days,colors,hour_start=" 08:00:00",end_hour=" 20:00:00",freq_points="15min"):
    coords=[-40.585390,-64.996220]
    for i in range(len(days)):
        df_day=undf[undf["Time"].dt.date==days[i]]
        df_day=df_day.reset_index(drop=True)
        df_day.index=df_day["Time"]
        df_day=df_day.loc[~df_day.index.duplicated(), :]
        turtles=list(colors.keys())
        df_turtles=[]
        for j in range(len(turtles)):
            df_turtles.append(df_day[df_day["Turtle"]==turtles[j]])
        for j in range(len(df_turtles)):
            df_turtles[j]=df_turtles[j].asfreq("1min",method="pad")
        start_time=pd.to_datetime(str(days[i])+hour_start)
        end_time=pd.to_datetime(str(days[i])+end_hour)
        time=pd.date_range(start_time,end_time,freq=freq_points)
        for j in range(len(time)):
            m_ij = folium.Map(location = coords,zoom_start=16)
            folium.TileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",attr="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community").add_to(m_ij)

            # Add year label to the map
            title_html = '''
                            <h3 align="left" style="font-size:22px"><b>{}</b></h3>
                            '''.format("Day and Hour:" + str(time[j]))   
            m_ij.get_root().html.add_child(folium.Element(title_html))
            for k in range(len(df_turtles)):
                if time[j] in df_turtles[k].index:
                    folium.CircleMarker(location=[df_turtles[k].loc[time[j]]["Latitude"],df_turtles[k].loc[time[j]]["Longitude"]],color=colors[turtles[k]],fill_color=colors[turtles[k]],fill_opacity=0.3).add_to(m_ij)
            m_ij.save(time[j].strftime("%m_%d_%Y_%H_%M")+".html")

    return

#makes pngs from html files so they can be used to make gif
def make_pngs(folder="",remove_htmls=True):

    #get all files in folder 
    filenames=folder+"/*.html"
    files=glob.glob(filenames)
    hti = Html2Image(custom_flags=['--virtual-time-budget=10000'])
    for file in files:
        #get name of file
        f_name=file.replace(".html","")
        f_name=f_name.replace(folder,"")
        f_name=f_name.replace("\\","")
        hti.screenshot(html_file=file,save_as= f_name+".png")
        if remove_htmls:
            os.remove(file)
    return

def make_gif(folder="",duration_frame=100,remove_pngs=True):
    #get all files in folder
    filenames=folder+"/*.png"
    files=glob.glob(filenames)
    #make gif
    frames = []
    for i in files:
        new_frame = Image.open(i)
<<<<<<< HEAD
        new_size = (int(new_frame.width/4),int( new_frame.height/4))
        new_frame = new_frame.resize(new_size) 
=======
>>>>>>> 9ad47dcda3cb04abc265d1ca3db81b0a3ab9b59b
        frames.append(new_frame)
        # Save into a GIF file that loops forever
        if remove_pngs:
            os.remove(i)
    
    frames[0].save('gif_trayectorias_IGOTo.gif', format='GIF',
            append_images=frames[1:],
            save_all=True,
            duration=duration_frame, loop=0)
    

    return




#def interpol_trayectories(df):
    df.index=df["Time"]
    df_aux=df.loc[~df.index.duplicated(), :]
    #if datetime distance is less than 20 minutes, interpolate time and lat and long. Time is interpolates so that there is a gap of 1 minute between each row.
    # using groupby functions separarte between rows where the time distance is greather than 20 minutes. Then apply interpolate function to each group.
    df_aux["Time_diff"]=df_aux["Time"].diff()
    where_greater_than_20=df_aux["Time_diff"]>timedelta(minutes=20)
    

                


        

    




