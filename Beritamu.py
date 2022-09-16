import streamlit as st
from datetime import date, datetime, timedelta
import pandas as pd
from st_on_hover_tabs import on_hover_tabs
import mysql.connector as mysql
from streamlit_option_menu import option_menu
from apps import home, ekspor, scrap  # import your app modules here

st.set_page_config(layout="wide")

apps = [
    {"title": "Beranda", "icon": "house", "func": home.app},
    {"title": "Ekspor Hasil Scraping", "icon": "map", "func": ekspor.app},
    {"title": "Scraping Berita Baru", "icon": "cloud-upload", "func": scrap.app},
]

titles = [app["title"] for app in apps]
titles_lower = [title.lower() for title in titles]
icons = [app["icon"] for app in apps]

with st.sidebar:
        selected = option_menu(
            "BERITA-MU",
            options=titles,
            icons=icons,
            menu_icon="cast",
            default_index=0,
        )

        st.sidebar.title("About")
        st.sidebar.info(
            """
            Aplikasi ini dapat digunakan untuk mengumpulkan data berita berdasarkan kata kunci yang di-input oleh pengguna. Sumber data berita pada aplikasi ini:
            -  [Detik](https://www.detik.com)
            -  [CNBC Indonesia](https://www.cnbcindonesia.com)
            
            
            Hubungi admin melalui:
                [GitHub](https://github.com/) | [Twitter](https://twitter.com/) | [YouTube](https://www.youtube.com/c/) | [LinkedIn](https://www.linkedin.com/in/).
        """
        )

for app in apps:
    if app["title"] == selected:
        app["func"]()
        break