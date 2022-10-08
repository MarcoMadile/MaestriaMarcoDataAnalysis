import pandas as pd 
import glob
import numpy as np
import folium
import folium.plugins
import ipdb
from geopy import distance 
from scipy.stats import itemfreq
import networkx as nx
import matplotlib.pyplot as plt
import datetime
import os

#changing time tu int, so i can compare them with ints 
def change_int(x):
    return int(x)

#getting all files in folder 
def get_files_and_dates(folder):
    filenames=folder+"/*.csv"
    files=glob.glob(filenames)
    dfs=[]
    t_names=[]
    for a in files:
        dfs.append(pd.read_csv(a,sep=";",encoding='latin-1'))
        tort=a.replace(".csv","")
        tort=tort.replace(folder,"")
        tort=tort.replace("\\","")
        tort=tort.split("_", 1)[0]
        if tort[1]=="0":
            tort=tort[0]+tort[2:]
        t_names.append(str(tort))
    dates=[]
    for j in range(len(dfs)):
        dates.append(np.unique(dfs[j]["date"]))
        dfs[j]["timeGMT"]=dfs[j]["timeGMT"].apply(change_int)
    dates=np.unique(np.concatenate(dates).ravel())
    return dfs,dates,t_names


#getting all files in folder 
def get_files_and_dates_IGOTO(folder):
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
        df[j]["Date"]=df[j]["Date"].apply(fixing_dates_Igoto)
        df[j][" Time"]=df[j][" Time"].apply(fixing_time_Igoto)
        dates.append(np.unique(df[j]["Date"]))
        #set column names of df[j]
        df[j]=df[j].rename(columns={" Latitude" : "lat", " Longitude" : "lon",
        "Date":"date", " Time": "timeGMT"})  
    dates=np.unique(np.concatenate(dates).ravel())
    return df,dates,t_names


#some files have dates like: "21:01:2022" (type datetime) and I want all dates in same format: "2022/01/21" type str
def fixing_dates_Igoto(x):
    if isinstance(x, datetime.date):
        return x.strftime("%Y/%m/%d")
    else:
        return str(x)

#some times are in format "8:57" and need to be in format "8:57:00"
def fixing_time_Igoto(x):
    x=str(x)
    if len(x)>9:
        x=x.split(" ")[1]
    if  " " in x:
        x=x.replace(" ","")
    if x.count(":")==1:
        return x+":00"
    else:
        return x

#start a pandas data frame with column names = lon,lat,date,t_name,sex. If data is Igoto then i need sex dict to know the sex of Turtles
def save_refugies_data(dfs,dates,t_names,cutoff_time=2000,distance_refugies=10,data_is_Igoto=False,file_for_sex="D:\\facultad\\IB5toCuatri\\Tesis\\MaestriaMarco\\DataAnalysisDataAnalysis\\encuentros_csv\\encuentroscompleto_only_space.csv"):
    df_out=pd.DataFrame(columns=["lat","lon","date","t_name","sex","refugie_label"])
    refugies=[]
    
    sex_dict= get_sex_dict(file_for_sex)
    for date in dates:
        for j in range(len(dfs)):
            if data_is_Igoto:
                points=get_last_cordinate_from_day_IGOTO(dfs[j],date,cutoff_time)
            else:
                points=get_last_cordinate_from_day(dfs[j],date,cutoff_time)
            if points!=0:
                is_in_refugies,refugie = poin_in_refuguies(points,refugies,distance_refugies)
                if  is_in_refugies:
                    index_refugie=refugies.index(refugie)
                    if data_is_Igoto:
                        dict={"lat":str(refugie[0]),"lon":str(refugie[1]),"date":str(date),"t_name":str(t_names[j]),"sex":sex_dict[t_names[j]],"refugie_label":str(index_refugie)}
                    else:
                        dict={"lat":str(refugie[0]),"lon":str(refugie[1]),"date":str(date),"t_name":str(t_names[j]),"sex":sex_dict[t_names[j]],"refugie_label":str(index_refugie)}
                    df_line=pd.DataFrame(dict,dtype=str,index=[0])
                    df_out=pd.concat([df_out,df_line],ignore_index=True)
                else:
                    refugies.append(points)
                    index_refugie=refugies.index(points)
                    if  data_is_Igoto:
                        dict={"lat":str(points[0]),"lon":str(points[1]),"date":str(date),"t_name":str(t_names[j]),"sex":sex_dict[t_names[j]],"refugie_label":str(index_refugie)}
                    else: 
                        dict={"lat":str(points[0]),"lon":str(points[1]),"date":str(date),"t_name":str(t_names[j]),"sex":sex_dict[t_names[j]],"refugie_label":str(index_refugie)}
                    df_line=pd.DataFrame(dict,dtype=str,index=[0])
                    df_out=pd.concat([df_out,df_line],ignore_index=True)
           
    return df_out

#get the last coordinate from a day, supposed to be the place where the turtle sleeps
def  get_last_cordinate_from_day(df,day,cutoff_time):
    df_aux=df[df["date"]==day]
    if len(df_aux)>=1:
        if df_aux["timeGMT"].iloc[-1]>=cutoff_time:
            return (df_aux["lat"].iloc[-1],df_aux["lon"].iloc[-1])
    return 0

#get the last coordinate from a day, supposed to be the place where the turtle sleeps for IGOTO
def  get_last_cordinate_from_day_IGOTO(df,day,cutoff_time):
    df_aux=df[df["date"]==day]
    if len(df_aux)>=1:
        #define hour of cutoff time as 20:00:00
        hour= 100*int(df_aux.iloc[-1]["timeGMT"].split(":")[0])
        if hour>=cutoff_time:
            return (df_aux["lat"].iloc[-1],df_aux["lon"].iloc[-1])
    return 0

#check if the point is considered a new refugie or not        
def poin_in_refuguies(points,refugies,distance_refugies):
    for refuguie in refugies:
        if distance.distance(points,refuguie).m<=distance_refugies:
            return True,refuguie
    return False,0

def get_sex_dict(file_for_sex):
    df_sexs = pd.read_csv(file_for_sex,sep=";")
    t1= (df_sexs["name one"].values).tolist()
    t2= (df_sexs["name two"].values).tolist()
    sex1 = (df_sexs["sex one"].values).tolist()
    sex2 = (df_sexs["sex two"].values).tolist()
    dict_sexs = dict(zip(t1+t2, sex1+sex2))# make dict from uniques values of t1+t2 to sex1 and sex2 
    dict_sexs["T6"]="hembra"
    dict_sexs["T184"]="hembra"
    dict_sexs["T54"]= "macho"
    dict_sexs["T128"]="macho"
    return dict_sexs
    
def make_map_from_refuguies(df_ref,topo_map=False):
    map_out=get_map(topo_map)
    #get unique values of (lat,lon) from df_ref, for each one, save a refuguie name and a list of tnames that are in that refugie
    refugies=np.unique(df_ref[["lat","lon"]].values.astype("<U22"),axis=0)
    for i in range(len(refugies)):
        refugie=refugies[i]
        df_aux=df_ref[(df_ref["lat"]==refugie[0]) & (df_ref["lon"]==refugie[1])]
        t_names=np.unique(df_aux["t_name"].values)
        folium.CircleMarker(location=[refugie[0],refugie[1]],radius=10,color="red",fill_color="red",fill_opacity=0.3,popup="<b>Refugio</b><br>"+"nro"+str(i)+"  "+str(t_names)).add_to(map_out)
    
    return map_out

def get_map(topo_map):
    coords=[-40.585390,-64.996220]
    map1 = folium.Map(location = coords,zoom_start=15)
    if topo_map:
        folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr= 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)').add_to(map1)
    else: 
        folium.TileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",attr="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community").add_to(map1)
    return map1 

def get_adjacency_matrix(df_ref):
    refugies=np.unique(df_ref[["lat","lon"]].values.astype("<U22"),axis=0)
    t_uniq_names=np.unique(df_ref["t_name"].values)
    adjacency_matrix=np.zeros((len(refugies),len(t_uniq_names)))
    for i in range(len(refugies)):
        refugie=refugies[i]
        df_aux=df_ref[(df_ref["lat"]==refugie[0]) & (df_ref["lon"]==refugie[1])]
        #count the number of each tnames that are in that refugie. then add that number to the adjacency matrix
        for t_name in t_uniq_names:  
            adjacency_matrix[i,t_uniq_names.tolist().index(t_name)]=len(df_aux[df_aux["t_name"]==t_name])
    return adjacency_matrix,np.linspace(0,len(refugies)-1,num=len(refugies)),t_uniq_names

def get_bigraph(df_ref,plot=False,k=0.5):
    refugies=np.unique(df_ref[["lat","lon"]].values.astype("<U22"),axis=0)
    refugies=np.unique(df_ref[["lat","lon"]].values.astype("<U22"),axis=0)
    t_uniq_names=np.unique(df_ref["t_name"].values)
    B = nx.Graph()
    # Add nodes with the node attribute "bipartite"
    refuguies_nodes=np.linspace(0,len(refugies)-1,num=len(refugies),dtype=int)
    B.add_nodes_from(t_uniq_names.tolist(), bipartite=1)
    B.add_nodes_from(refuguies_nodes.tolist(), bipartite=0)
    # Add edges with the edge attribute "weight"
    for i in range(len(refugies)):
        refugie=refugies[i]
        df_aux=df_ref[(df_ref["lat"]==refugie[0]) & (df_ref["lon"]==refugie[1])]
        for t_name in t_uniq_names:  
            if len(df_aux[df_aux["t_name"]==t_name])>0:
                B.add_edge(t_name,refuguies_nodes[i],weight=len(df_aux[df_aux["t_name"]==t_name]))
    if plot:
        colors_refugies=["sandybrown"]*len(refugies)
        colors_t_names=get_colors_turtles(df_ref,t_uniq_names)
        pos=nx.spring_layout(B,k)
        edges = B.edges()
        weights = [B[u][v]['weight'] for u,v in edges]
        weights=np.array(weights)
        weights=5*weights/np.max(weights)+np.ones(len(weights))*0.1
        nx.draw_networkx_nodes(B, pos=pos, nodelist=t_uniq_names, node_color=colors_t_names,node_size=200,label=t_uniq_names)
        nx.draw_networkx_edges(B, pos=pos, width=weights)
        nx.draw_networkx_nodes(B, pos=pos, nodelist=refuguies_nodes, node_color=colors_refugies,node_size=200,label=refuguies_nodes)
        nx.draw_networkx_labels(B,pos,font_size=10,font_family='sans-serif')
        plt.show()
    return B

def get_colors_turtles(df_ref,t_uniq_names):
    t_colors=[]
    for turtle in t_uniq_names:
        sex=df_ref[df_ref["t_name"]==turtle]["sex"].iloc[0]
        if sex=="macho":
            t_colors.append("lightblue")
        elif sex=="hembra":
            t_colors.append("pink")
        else:
            t_colors.append("silver")
    return t_colors


def get_mass_center_and_spatialD(df_ref):
    u_tnames= np.unique(df_ref["t_name"].values)
    df_space_dist=pd.DataFrame(columns=["t_name","mass_center_lat","mass_center_lon","spatialD","sex"])
    for t_name in u_tnames:
        df_aux=df_ref[df_ref["t_name"]==t_name]
        lat=df_aux["lat"].values.astype(float)
        lon=df_aux["lon"].values.astype(float)
        mass_center_lat=np.mean(lat)
        mass_center_lon=np.mean(lon)
        # mean of distance to mass_center using distance.distance function in meters
        spatialD=np.mean([distance.distance((mass_center_lat,mass_center_lon),(lat[i],lon[i])).m for i in range(len(lat))])
        t_sex= df_aux["sex"].iloc[0]
        df_aux = pd.DataFrame({"t_name":t_name,"mass_center_lat":mass_center_lat,"mass_center_lon":mass_center_lon,"spatialD":spatialD,
        "sex":t_sex},index=[0])
        df_space_dist=pd.concat([df_space_dist,df_aux],ignore_index=True)
    return df_space_dist

"""folder_to_Igoto="D:\\facultad\\IB5toCuatri\\Tesis\\MaestriaMarco\\DataAnalysis\\DatosIgoto2022Todos"
dfsI,datesI,t_namesI=get_files_and_dates_IGOTO(folder_to_Igoto)
file_to_sex= "D:\\facultad\\IB5toCuatri\\Tesis\\MaestriaMarco\\DataAnalysis\\encuentros_csv\\encuentroscompleto_only_space.csv"
df_refugiosI=save_refugies_data(dfsI,datesI,t_namesI,cutoff_time=2000,distance_refugies=0,data_is_Igoto=True,file_for_sex=file_to_sex)"""

#dfs,dates,t_names=get_files_and_dates_IGOTO("D:\\facultad\\IB5toCuatri\\Tesis\\MaestriaMarco\\DataAnalysis\\DatosIgoto2022Todos")
#df_coincidencia=save_refugies_data(dfs,dates,t_names,distance_refugies=200)
#map1=make_map_from_refuguies(df_coincidencia)