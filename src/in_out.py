#!/usr/bin/env python
# coding: utf-8
import pandas as pd
import os
import glob
import src.info as info

def read_allData(path_list,cols=None):
    """path_list ile belirtilen tüm dosyaları okur ve tek DataFrame'de birleştirir.
       ürün adı ve tarih bilgisini de ekler.

    Parameters
    ----------
    path_list (list) : Okunacak dosyalara ait path listesi
    cols (list) : Dosyalardan hangi sütunların okunacağı belirtilir. Default=None

    Returns
    -------
    all_data(pd.DataFrame)
    """

    master_data=pd.concat((pd.read_excel(file,usecols=cols).\
                       assign(name=info.get_productName(file),date=info.get_productDate(file)
                             ) for file in path_list),sort=False).reset_index(drop=True)
    return master_data


def get_path(folder_name):
    """Belirtilen klasördeki excel dosyalarına ait yolun bir listesini döndürür.
    Parameters
    ----------
    folder_name (str) : 
    Returns
    -------
    path_list (list)
    """

    files = [f for f in glob.glob(folder_name + "**/*.xlsx", recursive=True)]
    return files


# def write_excel(path,df,file_name,prod_name):
#     directory_path = path+'\\'+prod_name + '\\'
#     if not os.path.exists(directory_path):
#         os.mkdir(directory_path)
#         if not os.path.exists(directory_path+'detail\\'):
#             os.mkdir(directory_path+'detail\\')
#     writer = pd.ExcelWriter(directory_path+ file_name+'.xlsx', engine='xlsxwriter')
#     df.to_excel(writer, sheet_name='Sheet1')
#     writer.save()


# def write(name,full):
#     """Excel'e yazar
#     Parameters:
#         name (str): """
    
#     path = 'C:\\Users\\ugur.eren\\Python Codes\\cefis2\\out\\'
#     hour_series = pd.date_range('2018-01-01-18', periods=23, freq='H')
#     hour_series = hour_series.time
#     for i in range(23):
#         fn = hour_series[i].strftime("%H-%M-%S")        
#         write_excel(path=path,df=full.loc[hour_series[i]].dropna(),file_name=fn,prod_name=name)
#         write_excel(path=path,df=full.loc[hour_series[i]].describe(),file_name=fn+'_detail', prod_name=name+'\\detail')     
