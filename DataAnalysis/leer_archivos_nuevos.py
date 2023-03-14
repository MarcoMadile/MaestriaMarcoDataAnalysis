import pandas as pd 
import glob
import pickle
import ipdb



# from folder returns list of csv with unified format
def get_N_files(folder_Ns,sex_dict_pickle= "sex_dict_tortoises.pickle"):
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

#from new igos return list with same unified format 
def get_V_files(folder_Vs,sex_dict_pickle="sex_dict_tortoises.pickle"): 
    







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
    dict_sexs["T76"]="hembra"
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
ipdb.set_trace()
