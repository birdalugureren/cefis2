import time
from multiprocessing import Pool
import pandas as pd
import src.auxiliary_functions as aux
import src.condition as con
from datetime import time, datetime,date
import src.info as info
import src.in_out as io
import numpy as np
from src.density import Density, draw
import itertools

#sabitler
cols= ["Time","BID price","ASK price"]
columns=['time','bid_price','ask_price']

#değişkenler
time_stamp = None
values={'a_PNLTICK':10,
'a_TICKSIZE':0.0001,
'b_PNLTICK':6.25,
'b_TICKSIZE':0.0001}

#yardımcı fonksiyonlar
def spread_al(df):
    spread_dict = {}
    for date in non_duplicate_dates:
        for pair in paired_products:
            mp_1 = df[pd.Timestamp(date)][pair[0]]
            mp_2 = df[pd.Timestamp(date)][pair[1]]
            spread_dict[(date,pair[0]+"_"+pair[1])] = aux.find_spread(mp_1,mp_2,values)
    new_df = pd.DataFrame(spread_dict)
    new_df['time'] = df.time
    return new_df

def change_al(df):
    change_dict = {}
    for date in non_duplicate_dates:
        for pair in pairs:
            sub_df = df[date][pair]            
            change_dict[(date,pair)] = aux.find_change(sub_df)
    new_df = pd.DataFrame(change_dict)
    new_df['time'] = df.time
    return new_df


def read (path):
    df = pd.read_excel(path,usecols=cols)
    df.columns = columns
    return df

def _get_duramp(df):
    lengt = df.shape[1]
    df_list = []
    for i in range(lengt):
        df_list.append(aux.find_duramp(df.iloc[:,i]))
    return pd.concat(df_list).dropna()

def get_duramp(df):
    new_df = duzenle(df)
    product = {}
    for pair in pairs:
        product[pair] = _get_duramp(new_df[pair])
    return product

def duzenle(df):
    new_df = df.set_index('time')
    new_df = new_df.T.reset_index(level=0,drop=True).T
    return new_df

if __name__ == '__main__':
    path_list = io.get_path('C:\\Users\\ugur.eren\\Python Codes\\cefis2\\data\\')
    product_names = [info.get_productName(path) for path in path_list]
    date_list = [info.get_productDate(path) for path in path_list]
    cols= ["Time","BID price","ASK price"]
   
    #veri okunuyor
    pool = Pool(processes=4)
    okunan_veriler = pool.map(read,path_list)
    
    time_stamp = okunan_veriler[0].time

    #mid_price
    list_of_mid_price = pool.map(aux.get_mid_price,okunan_veriler)
    arrays = [date_list,product_names]
    df_mp = pd.DataFrame(data=list_of_mid_price, index = arrays)

    df_mp_t = df_mp.T
    df_mp_t['time'] = time_stamp
    list_of_hourly_mp = aux.split_df(df_mp_t,23)

    #ürün eşleştirme
    non_duplicate_dates = list(dict.fromkeys(date_list)) #tekrar eden tarihler kaldırıldı.
    non_duplicate_names = list(dict.fromkeys(product_names)) #tekrar eden ürünler kaldırıldı.
    paired_products = list(itertools.combinations(non_duplicate_names, 2)) #2'li kombinasyon kullanılarak ürünler eşleştiriliyor.

    #spread hesaplanıyor
    spread = [spread_al(df) for df in list_of_hourly_mp]

    #change hesaplanıyor
    pairs = [pair[0]+'_'+pair[1] for pair in paired_products]
    change_list = [change_al(df) for df in spread]

    #Duration ve Amplitude Hesaplanıyor
    duramp = [get_duramp(change) for change in change_list]

    #Medyanı baz alarak verileri yeniden düzenliyoruz
    hour_series = pd.date_range('2018-01-01-18', periods=23, freq='H').time
    edited_data = {}
    unconditional = {}

    for pair in pairs:
        con_list = []
        uncon_list = []
        for i in range(23):
            current = duramp[i][pair]
            con_df = con.single_scan(current,condition='median')
            con_list.append(con_df)
            uncon_list.append(current)
        edited_data[pair] = pd.concat(con_list,keys=hour_series)
        unconditional[pair] = pd.concat(uncon_list,keys= hour_series)

    #Dosyaya yazılıyor
    for pair in pairs:
        print("dosyaya yazılıyor: ",pair)
        df = edited_data[pair].reset_index()
        uncon_df = unconditional[pair].reset_index()
        df.columns=['time_period','time','duration','amplitude']
        uncon_df.columns=['time_period','time','duration','amplitude']
        df.to_csv(pair+".csv")
        uncon_df.to_csv(pair+"_unconditional.csv",index = False)
