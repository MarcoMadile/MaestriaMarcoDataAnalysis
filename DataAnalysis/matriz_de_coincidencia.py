import pandas as pd 
import glob
import numpy as np
import ipdb



#some files have dates like: "2022-01-21" and I want all dates in same format: "21/01/2022"
def fixing_dates(x):
    x=str(x)
    if "-" in x:
        aux=x.split("-")
        return aux[2]+"/"+aux[1]+"/"+aux[0]
    else:
        return x



#getting all files in folder 
def get_files_and_dates(folder):
    filenames=folder+"/*.csv"
    files=glob.glob(filenames)
    df=[]
    t_names=[]
    for a in files:
        df.append(pd.read_csv(a,sep=";",encoding='latin-1'))
        tort=a.replace(".csv","")
        tort=tort.replace(folder,"")
        tort=tort.replace("\\","")
        tort=tort.split("_", 1)[0]
        if tort[1]=="0":
            tort=tort[0]+tort[2:]
        t_names.append(str(tort))
    dates=[]
    for j in range(len(df)):
        df[j]["date"]=df[j]["date"].apply(fixing_dates)
        dates.append(np.unique(df[j]["date"]))

    dates=list(np.unique(np.concatenate(dates).ravel()))
    return df,dates,t_names

def matriz_de_coincidencia(df,dates,t_names):
    df_out=pd.DataFrame(columns=["turtles"]+dates)
    unique_turtles=np.unique(t_names)
    df_out["turtles"]=unique_turtles
    for i in range(len(dates)):
        for j in range(len(t_names)):
            if  (df_out.loc[df_out["turtles"]==t_names[j],dates[i]].isnull().iloc[0]):
                df_out.loc[df_out["turtles"]==t_names[j],dates[i]]=len(df[j][df[j]["date"]==dates[i]])
            else:
                df_out.loc[df_out["turtles"]==t_names[j],dates[i]]=df_out.loc[df_out["turtles"]==t_names[j],dates[i]]+len(df[j][df[j]["date"]==dates[i]])
    return df_out

#Get csv with coincidences
folder="D:\\facultad\\IB5toCuatri\\Tesis\\MaestriaMarco\\DataAnalysis\\todaslascampanas"
df,dates,t_names=get_files_and_dates(folder)
df_coincidencia=matriz_de_coincidencia(df,dates,t_names)
df_igotos=df_coincidencia[df_coincidencia["turtles"].isin(["T10","T12","T6","T30","T54","T79"])]
df_igotos.index=range(len(df_igotos))
df_igotos=df_igotos.replace(0,np.nan).dropna(axis=1,thresh=2)
df_igotos=df_igotos.replace(np.nan,0)
df_igotos.to_csv("tortugas_igoto_coincidencias.csv",sep=";")