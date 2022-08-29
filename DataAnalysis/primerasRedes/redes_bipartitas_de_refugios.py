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


#start a pandas data frame with column names = lon,lat,date,t_name,sex
def save_refugies_data(dfs,dates,t_names,cutoff_time=2000,distance_refugies=10):
    df_out=pd.DataFrame(columns=["lat","lon","date","t_name","sex"])
    refugies=[]
    for date in dates:
        for j in range(len(dfs)):
            points=get_last_cordinate_from_day(dfs[j],date,cutoff_time)
            if points!=0:
                is_in_refugies,refugie = poin_in_refuguies(points,refugies,distance_refugies)
                if  is_in_refugies:
                    dict={"lat":str(refugie[0]),"lon":str(refugie[1]),"date":str(date),"t_name":str(t_names[j]),"sex":str(dfs[j]["sexo"][3])}
                    df_line=pd.DataFrame(dict,dtype=str,index=[0])
                    df_out=pd.concat([df_out,df_line],ignore_index=True) 
                else:
                    refugies.append(points)
                    dict={"lat":str(points[0]),"lon":str(points[1]),"date":str(date),"t_name":str(t_names[j]),"sex":str(dfs[j]["sexo"][3])}
                    df_line=pd.DataFrame(dict,dtype=str,index=[0])
                    df_out=pd.concat([df_out,df_line],ignore_index=True)
                   
    return df_out

#get the last coordinate from a day, supposed to be the place where the turtle sleeps
def get_last_cordinate_from_day(df,day,cutoff_time):
    df_aux=df_aux=df[df["date"]==day]
    if len(df_aux)>=1:
        if df_aux["timeGMT"].iloc[-1]>=cutoff_time:
            return (df["lat"].iloc[-1],df["lon"].iloc[-1])
    return 0

#check if the point is considered a new refugie or not        
def poin_in_refuguies(points,refugies,distance_refugies):
    for refuguie in refugies:
        if distance.distance(points,refuguie).m<=distance_refugies:
            return True,refuguie
    return False,0

    
def make_map_from_refuguies(df_ref):
    map_out=get_map()
    #get unique values of (lat,lon) from df_ref, for each one, save a refuguie name and a list of tnames that are in that refugie
    refugies=np.unique(df_ref[["lat","lon"]].values.astype("<U22"),axis=0)
    for i in range(len(refugies)):
        refugie=refugies[i]
        df_aux=df_ref[(df_ref["lat"]==refugie[0]) & (df_ref["lon"]==refugie[1])]
        t_names=np.unique(df_aux["t_name"].values)
        folium.CircleMarker(location=[refugie[0],refugie[1]],radius=10,color="red",fill_color="red",fill_opacity=0.3,popup="<b>Refugio</b><br>"+"nro"+str(i)+"  "+str(t_names)).add_to(map_out)
    
    return map_out

def get_map():
    coords=[-40.585390,-64.996220]
    map1 = folium.Map(location = coords,zoom_start=15)
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

def get_bigraph(df_ref,plot=False):
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
        pos=nx.spring_layout(B,k=0.5,iterations=100)
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



#dfs,dates,t_names=get_files_and_dates("D:\\facultad\\IB5toCuatri\\Tesis\\MaestriaMarco\\DataAnalysis\\todaslascampanas")
#df_coincidencia=save_refugies_data(dfs,dates,t_names,distance_refugies=200)
#map1=make_map_from_refuguies(df_coincidencia)