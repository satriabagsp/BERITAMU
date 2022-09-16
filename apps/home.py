import streamlit as st
import pandas as pd

def app():

    st.title("BERITA-MU.COM")

    st.write("""
    ## Scraping berita sesuai kemauanmu..

    Silakan unduh template file keyword pada tombol di bawah untuk membuat daftar kata kunci berita yang diinginkan. Silakan cek daftar kata kunci yang telah di-scraping pada menu 'EKSPOR HASIL SCRAPING'.
    """)

    df_temp = pd.DataFrame([['batubara'],['minyak']], columns=['keyword'])
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(df_temp)
    st.download_button(
        label="Unduh Template",
        data=csv,
        file_name=f'keyword.csv',
        mime='text/csv',
    )