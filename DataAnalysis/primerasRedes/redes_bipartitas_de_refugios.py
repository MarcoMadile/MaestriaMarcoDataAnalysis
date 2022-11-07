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
import mantel
import random
from html2image import Html2Image
from PIL import Image


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
        dfs[j]["date"] =  dfs[j]["date"].apply(fixing_dates)
        dates.append(np.unique(dfs[j]["date"]))
        dfs[j]["timeGMT"] = dfs[j]["timeGMT"].apply(change_int)
    dates=np.unique(np.concatenate(dates).ravel())
    return dfs,dates,t_names

#some files have dates like: "2022-01-21" and I want all dates in same format: "21/01/2022"
def fixing_dates(x):
    x=str(x)
    if "-" in x:
        aux=x.split("-")
        return aux[2]+"/"+aux[1]+"/"+aux[0]
    else:
        return x
        

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
        return x.strftime("%d/%m/%Y")
    else:
        aux= x.split("/")
        return aux[2]+"/"+aux[1]+"/"+aux[0]

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

#makes html map with the refugies   
def make_map_from_refuguies(df_ref,topo_map=False,radius_nodes=10,refus_labels=False,refus_labels_anchor = (0,0)):
    map_out=get_map(topo_map)
    # get refugies_label as sorted as it is in refugies
    refugies_label=df_ref["refugie_label"].unique()
    refugies_label.sort() 
    for i in range(len(refugies_label)):
        refugie=df_ref[df_ref["refugie_label"]==refugies_label[i]].iloc[0][["lat","lon"]]
        df_aux=df_ref[df_ref["refugie_label"]==refugies_label[i]]
        t_names=np.unique(df_aux["t_name"].values)
        folium.CircleMarker(location=[refugie[0],refugie[1]],radius=radius_nodes,color="orange",fill_color="orange",fill_opacity=0.3,popup="<b>Refugio</b><br>"+"nro"+str(refugies_label[i])+"  "+str(t_names)).add_to(map_out)
        # add not popup text to the map 
        if refus_labels:
            folium.Marker(location=[refugie[0],refugie[1]],icon=folium.features.DivIcon(icon_size=(150,36),icon_anchor=refus_labels_anchor,html='<div style="font-size: 10pt; color: white">%s</div>' % str(refugies_label[i]))).add_to(map_out)
    return map_out

def get_map(topo_map=False,coords=[-40.585390,-64.996220],zoom=15):
    map1 = folium.Map(location = coords,zoom_start=zoom)
    if topo_map:
        folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr= 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)').add_to(map1)
    else: 
        folium.TileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",attr="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community").add_to(map1)
    return map1 

def get_adjacency_matrix(df_ref):
    refugies_label=df_ref["refugie_label"].unique()
    refugies = [df_ref[df_ref["refugie_label"]==refugies_label[i]].iloc[0][["lat","lon"]] for i in range(len(refugies_label))]
    t_uniq_names=np.unique(df_ref["t_name"].values)
    adjacency_matrix=np.zeros((len(refugies),len(t_uniq_names)))
    for i in range(len(refugies)):
        refugie=refugies[i]
        df_aux=df_ref[df_ref["refugie_label"]==refugies_label[i]]
        #count the number of each tnames that are in that refugie. then add that number to the adjacency matrix
        for t_name in t_uniq_names:  
            adjacency_matrix[i,t_uniq_names.tolist().index(t_name)]=len(df_aux[df_aux["t_name"]==t_name])
    return adjacency_matrix,np.linspace(0,len(refugies)-1,num=len(refugies)),t_uniq_names

# makes bipartite network from nodes ref and nodes turltes
def get_bigraph(df_ref,plot=False,k=0.5,return_refugies=False,nodesize=200,scale=1,iters=50,weight="weight"):
    refugies_label=df_ref["refugie_label"].unique()
    refugies = [df_ref[df_ref["refugie_label"]==refugies_label[i]].iloc[0][["lat","lon"]] for i in range(len(refugies_label))]
    t_uniq_names=np.unique(df_ref["t_name"].values)
    B = nx.Graph()
    # Add nodes with the node attribute "bipartite"
    refuguies_nodes=refugies_label
    
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
        pos=nx.spring_layout(B,k,iterations=iters,scale=scale,weight=weight)
        edges = B.edges()
        weights = [B[u][v]['weight'] for u,v in edges]
        weights=np.array(weights)
        weights=5*weights/np.max(weights)+np.ones(len(weights))*0.1
        nx.draw_networkx_nodes(B, pos=pos, nodelist=t_uniq_names, node_color=colors_t_names,node_size=nodesize,label=t_uniq_names)
        nx.draw_networkx_edges(B, pos=pos, width=weights)
        nx.draw_networkx_nodes(B, pos=pos, nodelist=refuguies_nodes, node_color=colors_refugies,node_size=nodesize,label=refuguies_nodes)
        nx.draw_networkx_labels(B,pos,font_size=10,font_family='sans-serif')
        plt.show()
    if return_refugies:
        return B,refugies
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

# from refugies data it calculates the mass center of refugies for each turtle and the spatial distribution ( similar to moment of inertia)
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

# from dataframe with ref and df with encounters, it finds min distance in time of nights spend in ref and min dist in time from that two dates to encounter. If no encounter was messaured between those two turtles it saves a nan.
def nearest_days_in_ref_to_encounters(file_encuentros,df_refugios):
    df_encounters = pd.read_csv(file_encuentros, sep=';',header=0)
    df_min_dist= pd.DataFrame(columns=["t_name1","t_name2","day1","day2","refu_label","min_dist_time","date_encounter","min_dist_encounter"])
    refus_labels = df_refugios["refugie_label"].unique()
    for refu in refus_labels:
        df_aux= df_refugios[df_refugios["refugie_label"]==refu]
        t_in_ref= df_aux["t_name"].unique()
        if len(t_in_ref)>1:
            # for each pair of turtles in df_aux find min distance in time and save it. Time is in date column of df_aux
            for i in range(len(t_in_ref)):
                for j in range(i+1,len(t_in_ref)):
                    t1= t_in_ref[i]
                    t2= t_in_ref[j]
                    df_t1= df_aux[df_aux["t_name"]==t1]
                    df_t2= df_aux[df_aux["t_name"]==t2]
                    # get min distance in time
                    min_dist= np.inf
                    for d1 in df_t1["date"]:
                        for d2 in df_t2["date"]:
                            day1= datetime.datetime.strptime(d1, '%d/%m/%Y')
                            day2= datetime.datetime.strptime(d2, '%d/%m/%Y')

                            dist= np.abs((day1-day2).days)
                            if dist<min_dist:
                                min_dist=dist
                                d1_to_save=d1
                                d2_to_save=d2
                    # get from df_encounters the part of the encounter between t1 and t2
                    df_enc_t1_t2= df_encounters[(df_encounters["name one"]==t1) & (df_encounters["name two"]==t2)]
                    df_enc_t2_t1 = df_encounters[(df_encounters["name one"]==t2) & (df_encounters["name two"]==t1)]
                    df_enc_ts = pd.concat([df_enc_t1_t2,df_enc_t2_t1])
                    if len(df_enc_ts)>0:
                        dates_enc = df_enc_ts["day"].unique()
                        min_dist_enc= np.inf
                        for d in dates_enc:
                            day3= datetime.datetime.strptime(d, '%d/%m/%Y')
                            dist= np.abs((day1-day3).days) + np.abs((day2-day3).days)
                            if dist<min_dist_enc:
                                min_dist_enc=dist
                                d_encounter_to_save=d
                    else: 
                        min_dist_enc= np.nan
                        d_encounter_to_save= np.nan
                    dict_to_save={"t_name1":t1,"t_name2":t2,"day1":d1_to_save,"day2":d2_to_save,"refu_label":refu,"min_dist_time":min_dist,"date_encounter":d_encounter_to_save,"min_dist_encounter":min_dist_enc}
                    pd_to_save= pd.DataFrame(dict_to_save,index=[0])
                    df_min_dist= pd.concat([df_min_dist,pd_to_save],ignore_index=True)
    return df_min_dist

# from two Graphs returns TP,FP,FN,TN as if one graph is predicting the edges of the other Graph
def comparing_two_networks(G_predictor,G_messaured):
    edges_predicted=[]
    for u,v in G_predictor.edges():
        edges_predicted.append((u,v))
    # get list of edges in G_encuentros
    edges_messaured=[]
    for u,v in G_messaured.edges():
        edges_messaured.append((u,v))
    # get list of edges not in G_encuentros
    edges_not_messaured=[]
    edges_from_prediction_in_messaured=[]
    for edge in edges_predicted:
        if edge not in edges_messaured:
            edges_not_messaured.append(edge)
        else:
            edges_from_prediction_in_messaured.append(edge)
    edges_in_messaured_not_in_prediction=[]
    for edge in edges_messaured:
        if edge not in edges_predicted:
            edges_in_messaured_not_in_prediction.append(edge)
    # true negative, edges that are not in  G_from_ref and not in G_encuentros
    true_negative=0
    for edge in edges_not_messaured:
        if edge not in edges_in_messaured_not_in_prediction:
            true_negative+=1
    TP = len(edges_from_prediction_in_messaured)
    FP = len(edges_not_messaured) 
    FN = len(edges_in_messaured_not_in_prediction)
    TN = true_negative
    return TP,FP,FN,TN

#plots a graph in a map 
def plot_conections_in_map(G_refugies,refugies_loc):
    map_with_conections = get_map()
    for u,v in G_refugies.edges():
        #add circle marker in refugies_loc[int(u)] and refugies_loc[int(v)] and connect them with line. 
        folium.CircleMarker(location=list(refugies_loc[int(u)].astype(float)),radius=3,color='orange',fill=True,fill_color='orange',fill_opacity=0.81).add_to(map_with_conections)
        folium.CircleMarker(location=list(refugies_loc[int(v)].astype(float)),radius=3,color='orange',fill=True,fill_color='orange',fill_opacity=0.81).add_to(map_with_conections)
        folium.PolyLine(locations=[refugies_loc[int(u)].astype(float),refugies_loc[int(v)].astype(float)],color='lightblue',weight=0.71).add_to(map_with_conections)
    return map_with_conections

# get adjacency matrix of a graph and distances between nodes in meters 
def matrix_distance_and_adjancency(G_refugies,refugies_loc):
    Adj_matrix = nx.adjacency_matrix(G_refugies).todense()
    Adj_matrix = np.array(Adj_matrix)
    #calculate distance matrix for each pair of nodes in refugies_loc
    dist_matrix = np.zeros((len(refugies_loc),len(refugies_loc)))
    for i in range(len(refugies_loc)):
        for j in range(len(refugies_loc)):
            dist_matrix[i,j] = distance.distance(refugies_loc[i],refugies_loc[j]).m
    return Adj_matrix,dist_matrix

#it like double_edge swap of nx but for bigraphs
def swap_conections_in_bigraph(B,swaps,max_trys):
    B_double_edge_swap = B.copy()
    for swap in range(swaps):
        for trys in range(max_trys):
            edge1 = random.choice(list(B_double_edge_swap.edges()))
            edge2 = random.choice(list(B_double_edge_swap.edges()))
            # check if connection exists in B from edge1[0] to edge2[1] and from edge2[0] to edge1[1]
            if ((edge1[0],edge2[1]) not in B_double_edge_swap.edges()) and ((edge2[0],edge1[1]) not in B_double_edge_swap.edges()):
                B_double_edge_swap.remove_edge(edge1[0],edge1[1])
                B_double_edge_swap.remove_edge(edge2[0],edge2[1])
                B_double_edge_swap.add_edge(edge1[0],edge2[1])
                B_double_edge_swap.add_edge(edge2[0],edge1[1])
                break
    return B_double_edge_swap 


#make map highlighting the path the turtles took from one day in refugie to another
def turtle_ref_path_map(t_name,df_of_refugies,node_r_norm=7,oppacity_lines= 0.71):
    map_turtle_path = get_map()
    df_ref_turtle = df_of_refugies[df_of_refugies["t_name"]==t_name]
    df_ref_turtle = df_ref_turtle.reset_index(drop=True)
    df_ref_turtle["date"] = pd.to_datetime(df_ref_turtle["date"],format="%d/%m/%Y")
    df_ref_turtle = df_ref_turtle.sort_values(by="date")
    df_ref_turtle = df_ref_turtle.reset_index(drop=True)
    df_ref_turtle["date"] = df_ref_turtle["date"].dt.strftime("%d/%m/%Y")

    unique_ref = np.unique(df_ref_turtle[["lat","lon"]].values.astype("<U22"),axis=0)
    for j in range(1,len(df_ref_turtle)):
        df_j=df_ref_turtle.iloc[j]
        df_j_1=df_ref_turtle.iloc[j-1]
        # make line from df_j_1 to df_j
        folium.PolyLine(locations=[[float(df_j_1["lat"]),float(df_j_1["lon"])],[float(df_j["lat"]),float(df_j["lon"])]],color="lightblue",weight=oppacity_lines).add_to(map_turtle_path)
    for i in range(len(unique_ref)):
        ref = unique_ref[i]
        nights_on_ref = len(df_ref_turtle[(df_ref_turtle["lat"]==ref[0]) & (df_ref_turtle["lon"]==ref[1])])
        map_turtle_path.add_child(folium.CircleMarker(location=[ref[0],ref[1]],popup="Nights on refugie: "+str(nights_on_ref),radius = nights_on_ref/node_r_norm,color="orange",fill=True,fill_color="orange",fill_opacity=0.81))
    
    return map_turtle_path

#makes htmls to make gif of turtles path through refugies 
def make_html_temporal_maps(t_name,df_of_refugies,node_r_norm=3,oppacity_lines=0.51,line_size=3,frames_per_day=5,zoom_in_map=17,add_ref_label=False):
    df_ref_turtle = df_of_refugies[df_of_refugies["t_name"]==t_name]
    # reset index of df_ref_turtle
    df_ref_turtle = df_ref_turtle.reset_index(drop=True)
    df_ref_turtle["date"] = pd.to_datetime(df_ref_turtle["date"],format="%d/%m/%Y")
    df_ref_turtle = df_ref_turtle.sort_values(by="date")
    df_ref_turtle = df_ref_turtle.reset_index(drop=True)
    df_ref_turtle["date"] = df_ref_turtle["date"].dt.strftime("%d/%m/%Y")
    # get most used refugie as df_ref_turtle["refugie_label"] most repeted
    refugie_label_most_used = df_ref_turtle["refugie_label"].value_counts().index[0]
    # get center location as lat lon of refugie label most used
    center_lat = df_ref_turtle[df_ref_turtle["refugie_label"]==refugie_label_most_used]["lat"].values[0]
    center_lon = df_ref_turtle[df_ref_turtle["refugie_label"]==refugie_label_most_used]["lon"].values[0]
    frames_per_day = 5
    for j in range(1,len(df_ref_turtle)):
        df_j=df_ref_turtle.iloc[j]
        df_j_1=df_ref_turtle.iloc[j-1]
        # make line from df_j_1 to df_j
        # filter df_ref_turtle where iloc is less than j
        df_ref_turtle_j = df_ref_turtle[df_ref_turtle.index<j]
        refugies_label_to_j=df_ref_turtle_j["refugie_label"].unique()
        unique_ref_to_j = [df_ref_turtle_j[df_ref_turtle_j["refugie_label"]==refugies_label_to_j[i]].iloc[0][["lat","lon"]] for i in range(len(refugies_label_to_j))]
        
        for h in range(frames_per_day):
            map_turtle_path = get_map(topo_map=False,coords=[center_lat,center_lon],zoom=zoom_in_map)
            for k in range(1,len(df_ref_turtle_j)):
                df_k = df_ref_turtle_j.iloc[k]
                # get refugie label of df_k
                df_k_1 = df_ref_turtle_j.iloc[k-1]
                #make lines from lat lon of df_k_1 to lat lon of df_k
                # get lat lon of df_k_1
                lat_k_1 = float(df_k_1["lat"])
                lon_k_1 = float(df_k_1["lon"])
                # get lat lon of df_k
                lat_k = float(df_k["lat"])
                lon_k = float(df_k["lon"])
                # plot line from lat_k_1,lon_k_1 to lat_k,lon_k
                folium.PolyLine(locations=[[lat_k_1,lon_k_1],[lat_k,lon_k]],color="lightblue",weight=line_size,opacity=oppacity_lines).add_to(map_turtle_path)

            # make line from df_j_1 to (df_j-df_j_1)*frames_per_day/(i+1)+df_j_1
            for i in range(len(unique_ref_to_j)):
                ref_lat=unique_ref_to_j[i]["lat"]
                ref_lon = unique_ref_to_j[i]["lon"]
                nights_on_ref = len(df_ref_turtle_j[(df_ref_turtle_j["lat"]==ref_lat) & (df_ref_turtle_j["lon"]==ref_lon)])
                map_turtle_path.add_child(folium.CircleMarker(location=[float(ref_lat),float(ref_lon)],radius = nights_on_ref/node_r_norm,color="orange",fill=True,fill_color="orange",fill_opacity=0.81))
            
            lat = (float(df_j["lat"])-float(df_j_1["lat"]))*(h)/(frames_per_day-1)+float(df_j_1["lat"])
            lon = (float(df_j["lon"])-float(df_j_1["lon"]))*(h)/(frames_per_day-1)+float(df_j_1["lon"])
            folium.PolyLine(locations=[[float(df_j_1["lat"]),float(df_j_1["lon"])],[lat,lon]],color="lightblue",weight=oppacity_lines).add_to(map_turtle_path)
            date = df_j["date"]
            # Add year label to the map
            title_html = '''
                            <h3 align="left" style="font-size:22px"><b>{}</b></h3>
                            '''.format("Day:" + str(date)+"               Turtle:"+t_name)   
            map_turtle_path.get_root().html.add_child(folium.Element(title_html))
            refus_labels_anchor = (7,10)
            if add_ref_label:
                for k in range(len(unique_ref_to_j)):
                    folium.Marker(location=[float(unique_ref_to_j[k]["lat"]),float(unique_ref_to_j[k]["lon"])],icon=folium.features.DivIcon(icon_size=(150,36),icon_anchor=refus_labels_anchor,html='<div style="font-size: 10pt; color: white">%s</div>' % str(refugies_label_to_j[k]))).add_to(map_turtle_path)
                
            if j<10:
                map_turtle_path.save("D:\\facultad\\IB5toCuatri\\Tesis\\MaestriaMarco\\DataAnalysis\\primerasRedes\\gif_construccion_mapas\\"+t_name+"\\mapa_"+t_name+"_refugies_0"+str(j)+"_"+str(h)+".html")
            else: 
                map_turtle_path.save("D:\\facultad\\IB5toCuatri\\Tesis\\MaestriaMarco\\DataAnalysis\\primerasRedes\\gif_construccion_mapas\\"+t_name+"\\mapa_"+t_name+"_refugies_"+str(j)+"_"+str(h)+".html")
    return

# takes screenshots of htmls and saves pngs
def make_pngs_from_htmls(folder,remove_htmls=False):
    #get all files in folder 
    filenames=folder+"/*.html"
    files=glob.glob(filenames)
    hti = Html2Image(custom_flags=['--virtual-time-budget=10000'],output_path= folder)
    for file in files:
        #get name of file
        f_name=file.replace(".html","")
        f_name=f_name.replace(folder,"")
        f_name=f_name.replace("\\","")
        hti.screenshot(html_file=file,save_as= f_name+".png")
        if remove_htmls:
            os.remove(file)
    return

# from folder with pngs makes gif
def make_gif(folder="",duration_frame=100,remove_pngs=False,low_quality=True,quantity=0,save_name="gif_refugie_path",crop_images=False,crop_box=(0,0,1000,800)):
    #get all files in folder
    filenames=folder+"/*.png"
    files=glob.glob(filenames)
    #make gif
    frames = []
    if not quantity==0:
        files=files[:quantity]
    for i in files:
        new_frame = Image.open(i)
        if low_quality:
            new_size = (int(new_frame.width/4),int( new_frame.height/4))
            new_frame = new_frame.resize(new_size) 
        if crop_images:
            new_frame=new_frame.crop(crop_box)
        frames.append(new_frame)
        # Save into a GIF file that loops forever
        if remove_pngs:
            os.remove(i)
    if low_quality: 
        frames[0].save(save_name+'.gif', format='GIF',
                append_images=frames[1:],
                save_all=True,
                duration=duration_frame, loop=0)
    else:  
        frames[0].save(save_name+'_HD.gif', format='GIF',
                append_images=frames[1:],
                save_all=True,
                duration=duration_frame, loop=0)
    return



"""folder_to_Igoto="D:\\facultad\\IB5toCuatri\\Tesis\\MaestriaMarco\\DataAnalysis\\DatosIgoto2022Todos"
dfsI,datesI,t_namesI=get_files_and_dates_IGOTO(folder_to_Igoto)
file_to_sex= "D:\\facultad\\IB5toCuatri\\Tesis\\MaestriaMarco\\DataAnalysis\\encuentros_csv\\encuentroscompleto_only_space.csv"
df_refugiosI=save_refugies_data(dfsI,datesI,t_namesI,cutoff_time=2000,distance_refugies=0,data_is_Igoto=True,file_for_sex=file_to_sex)"""

#dfs,dates,t_names=get_files_and_dates_IGOTO("D:\\facultad\\IB5toCuatri\\Tesis\\MaestriaMarco\\DataAnalysis\\DatosIgoto2022Todos")
#df_coincidencia=save_refugies_data(dfs,dates,t_names,distance_refugies=200)
#map1=make_map_from_refuguies(df_coincidencia)