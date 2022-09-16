import streamlit as st
import pandas as pd
import mysql.connector as mysql

def app():

    st.title("EKSPOR DATA BERITA")

    # Tabel hasil scraping yang ada di DB
    st.write(" Kata kunci yang sudah diambil:")
    mydb_conn = mysql.connect(host = "localhost", user = "root", passwd = "", database = "berita")
    df_berita = pd.read_sql('SELECT `katakunci` as "Kata Kunci", COUNT(`katakunci`) as "Jumlah Berita" FROM hasil_scrap GROUP BY `katakunci`;', con=mydb_conn)
    mydb_conn.close()
    
    st.table(df_berita)

    # Pilih kata kunci yang akan diambil
    katakunci = df_berita['Kata Kunci'].tolist()
    options = st.multiselect('Pilih kata kunci yang akan diekspor', katakunci)
    options_str = str(options).replace('[','(').replace(']',')')
    ambilData = st.button("Lihat Berita")

    if ambilData:
        mydb_all = mysql.connect(host = "localhost", user = "root", passwd = "", database = "berita")
        df_filter = pd.read_sql(f'SELECT * FROM hasil_scrap WHERE katakunci IN {options_str};', con=mydb_all)
        mydb_all.close()

        st.dataframe(df_filter)

        def convert_df(df):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_csv(index=False, sep=';').encode('utf-8')

        csv = convert_df(df_filter)
        st.download_button(
            label="Unduh Berita",
            data=csv,
            file_name=f'data berita.csv',
            mime='text/csv',
        )