import pandas as pd 
import glob
import pickle
import ipdb
import datetime
from datetime import timedelta
import numpy as np


# from folder returns list of csv with unified format
def get_N_files(folder_Ns="DataAnalysis/Datos_CampanaSaoFeb/Ns",sex_dict_pickle= "sex_dict_tortoises.pickle"):
    files = glob.glob(folder_Ns + "/*.csv")
    dfs_list = []
    for f in files:
        df = pd.read_csv(f,sep=",")
        df_ = pd.DataFrame()
        df_["lat"] = df["Latitude"]
        df_["lon"] = df["Longitude"]
        df_["dateTime"] =  pd.to_datetime(df["dateTime"].apply(lambda x: x[:19]))
        t_name = f.split("/")[-1].split("_")[0]
        df_["t_name"] = t_name
        with open(sex_dict_pickle,"rb") as f:
            sex_dict = pickle.load(f)       
        df_["sex"] = sex_dict[t_name]
        dfs_list.append(df_)
    return dfs_list

#from 6 old igos2022 return data
def get_igo_old_files(igo_folder = "DataAnalysis/DatosIgoto2022Todos",sex_dict_pickle= "sex_dict_tortoises.pickle"):
    filenames=igo_folder+"/*.xlsx"
    files=glob.glob(filenames)
    df=[]
    t_names=[]
    for a in files:
        df.append(pd.read_excel(a))
        tort=a.replace(".xls","")
        tort=tort.replace(igo_folder,"")
        tort=tort.replace("","")
        tort=tort.replace("x","")
        if tort[1]=="0":
            tort=tort[0]+tort[2:]
        t_names.append(str(tort))
    for j in range(len(df)):
        df[j].dropna(subset=['Date'], inplace=True)
        df[j]["Date"]=df[j]["Date"].apply(fixing_dates_igos)
        df[j][" Time"]=df[j][" Time"].apply(fixing_time_igos)
    dfs_list_new_f = []
    with open(sex_dict_pickle,"rb") as f:
            sex_dict = pickle.load(f)       
    for i in range(len(df)):
        df_nf = pd.DataFrame()
        df_nf["lat"] = df[i][" Latitude"]
        df_nf["lon"] = df[i][" Longitude"]
        df_nf["dateTime"] =  pd.to_datetime(df[i]["Date"]+" "+df[i][" Time"])
        df_nf["t_name"] = t_names[i]
        df_nf["sex"] = sex_dict[t_names[i]] 
        dfs_list_new_f.append(df_nf)
    return dfs_list_new_f


#some files have dates like: "21:01:2022" (type datetime) and I want all dates in same format: "2022/01/21" type str
def fixing_dates_igos(x):
    if isinstance(x, datetime.date):
        return x.strftime("%Y/%m/%d")
    else:
        return str(x)

#some times are in format "8:57" and need to be in format "8:57:00"
def fixing_time_igos(x):
    x=str(x)
    if len(x)>9:
        x=x.split(" ")[1]
    if  " " in x:
        x=x.replace(" ","")
    if x.count(":")==1:
        return x+":00"
    else:
        return x





def save_sex_dict(file_for_sex="DataAnalysis/encuentros_csv/encuentroscompleto_only_space.csv",save_into_pickle=False,filename="sex_dict_tortoises.pickle",return_dict=True):
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
    dict_sexs["T206"]="hembra"
    dict_sexs["T8"]="hembra"
    dict_sexs["T76"]="macho"
    dict_sexs["T185"]="hembra"
    dict_sexs["T238"]="hembra"
    dict_sexs["T42"]="hembra"
    if save_into_pickle:
        with open(filename, 'wb') as f:
            pickle.dump(dict_sexs, f)
    if return_dict:
        return dict_sexs


folder_N = "DataAnalysis/Datos_CampanaSaoFeb/Ns"
dfs_list = get_N_files(folder_N)
dfs_v_list = get_igo_old_files()
ipdb.set_trace()