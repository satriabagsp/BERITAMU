import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from apps import detik
from apps import cnbc

def app():

    st.title("SCRAPING BERITA")

    keyword_path = st.file_uploader('Upload File "keyword.csv" yang telah berisi kata kunci yang diinginkan.', type=(["csv"]))

    # if cekKeyword:
    if keyword_path is not None:
        path_in = keyword_path
        df_keyword = pd.read_csv(path_in)
        list_keyword = df_keyword['keyword'].to_list()
        st.write(f'Kata kunci yang akan diambil:')
        st.write(list_keyword)
    else:
        st.write('Silakan pilih file "keyword.csv" terlebih dahulu..')
        path_in = None

    # Set Date
    start_date = st.date_input("Tanggal Awal:", date.today())
    tommorow_date = start_date + timedelta(days=1)
    end_date = st.date_input("Tanggal Akhir:", tommorow_date)
    date_list = pd.date_range(start=start_date,end=end_date).to_list()

    # Tombol scrape data
    scrapData = st.button("Scrap Berita")
    if scrapData:
        st.info(f'Scrap Data Berita {list_keyword} periode {start_date.strftime("%d/%m/%Y")} - {end_date.strftime("%d/%m/%Y")} sedang berjalan di background, silakan tunggu..')
        with st.spinner('Wait for it...'):
            # t1 = threading.Thread(target = detik.multi_scrap_detik, args=(list_keyword, start_date, end_date,))
            # t1.start()
            # print('run Detik')
            # t2 = threading.Thread(target = cnbc.multi_scrap_cnbc, args=(list_keyword, date_list,))
            # t2.start()
            # print('run CNBC')
            
            print('run Detik')
            for keyword in list_keyword:
                detik.multi_scrap_detik(keyword, start_date, end_date)
                cnbc.multi_scrap_cnbc(keyword, date_list)