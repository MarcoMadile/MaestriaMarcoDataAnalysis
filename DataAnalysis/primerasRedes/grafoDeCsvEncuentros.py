from turtle import width
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import networkx as nx
import ipdb

#From encuentros (csv file) make a parejas (csv) that saves each couple and it returns couples 
def parejas_from_encuentros(csvName,csvNameOut="",saveCSv=False):
    df=pd.read_csv(csvName,sep=";")
    dates=np.unique(df["day"])
    parejas=[]
    for date in dates:
        #get all points for a date
        dfaux=df[df["day"]==date]
        t1=dfaux["name one"].values
        t2=dfaux["name two"].values
        paux=[]
        for i in range(len(t1)):
            paux.append(t1[i]+"_"+t2[i])
        
        parejas.append(np.unique(paux))
    #make a dataframe using dates as collums names and each array of parejas as rows. Fill each column with the strings of the parejas.
    dfparejas=pd.DataFrame(columns=dates,dtype=str)
    for i in range(len(dates)):
        dfparejas.iloc[:,i]=pd.Series(parejas[i])
    #sort columns names in dataframe. This should be according to the order of dates. Fist it should be getting the dates from column names and then sort them. The column names are strings so i need to convert them to date object to sort it.
    idx = pd.to_datetime(dfparejas.columns, errors='coerce', format='%d-%m-%y').argsort()
    dfparejas=dfparejas.iloc[:, idx]
    if saveCSv:
        dfparejas.to_csv(csvNameOut,sep=";")
    return parejas

#from parejas list, return names of turtles and grade in two different arrays 
def count_grades(parejas):
    parejasflat=[]
    for i in range(len(parejas)):
        for j in range(len(parejas[i])):
            parejasflat.append(parejas[i][j])
    parejasflat=np.unique(parejasflat)
    #separe parejasflat into two arrays, for each element of parejas flat separe where there is "_"
    parejasflat1=[]
    parejasflat2=[]
    for i in range(len(parejasflat)):
        parejasflat1.append(parejasflat[i].split("_")[0])
        parejasflat2.append(parejasflat[i].split("_")[1])
    #get uniques names 
    names=np.unique(parejasflat1+parejasflat2)
    conectionsForName=np.zeros(len(names))
    for i in range(len(names)):
        parejas_name=[]
        for j in range(len(parejasflat1)):
            if parejasflat1[j]==names[i]:
                if not parejasflat2[j] in parejas_name:
                    conectionsForName[i]+=1
                    parejas_name.append(parejasflat2[j])
        for j in range(len(parejasflat2)):
            if parejasflat2[j]==names[i]:
                if not parejasflat1[j]in parejas_name:
                    conectionsForName[i]+=1
                    parejas_name.append(parejasflat1[j])
    return names,conectionsForName

#from names and conectionsForname makes a histogram 
def plot_grades(names,conectionsForName):
    plt.bar(names,conectionsForName)
    plt.show()

#from encuentros csv it makes agraph of the connections between turtles adding weights to the edges depending on the number of meetings
def plot_weighted_graph(encuentrosCsv):
    df=pd.read_csv(encuentrosCsv,sep=";")
    t1=(df["name one"].values).tolist() 
    t2=(df["name two"].values).tolist()
    names=np.unique(t1+t2)
    sex_dict = get_sex_dict(encuentrosCsv,return_colors=True)

    G=nx.Graph()
    G.add_nodes_from(names)
    for i in range(len(t1)):
        if G.has_edge(t1[i],t2[i]):
            G[t1[i]][t2[i]]['weight']+=0.05
        else:
            G.add_edge(t1[i],t2[i],weight=0.1)
    edges = G.edges()
    weights = [G[u][v]['weight'] for u,v in edges]
    weights=np.array(weights)
    weights=20*weights/np.max(weights)+np.ones(len(weights))*0.1
    nx.draw(G, with_labels=True,width=weights,node_color=sex_dict.values())
    plt.show()    
    return G

def get_sex_dict(encuentros_csv,return_colors=False):
    df = pd.read_csv(encuentros_csv,sep=";")
    t1= (df["name one"].values).tolist()
    t2= (df["name two"].values).tolist()
    sex1 = (df["sex one"].values).tolist()
    sex2 = (df["sex two"].values).tolist()
    if return_colors:
        for i in range(len(sex1)):
            if sex1[i]== "macho":
                sex1[i]="blue"
            elif sex1[i]== "hembra":
                sex1[i]= "pink"
            else: 
                sex1[i]= "grey"

            if sex2[i]== "macho":
                sex2[i]="blue"
            elif sex2[i]== "hembra":
                sex2[i]= "pink"
            else: 
                sex2[i]= "grey"      
            
    dict_sexs = dict(zip(t1+t2, sex1+sex2))
    return dict_sexs
    # make dict from uniques values of t1+t2 to sex1 and sex2 
