import requests
import pandas as pd
from datetime import date
from bs4 import BeautifulSoup
import math
from fake_useragent import UserAgent
from lxml import etree
from sentimen_indo import sentiment
import mysql.connector as mysql
import threading
import urllib3
import time
from concurrent.futures import ThreadPoolExecutor
urllib3.disable_warnings()

# Multithread Things
maxthreads = 8
smphr = threading.Semaphore(value=maxthreads)
threads = list()

ua = UserAgent()

def get_berita(url_berita, kata_kunci):
    url_berita = str(url_berita)
    payload={}
    headers = {
        'User-Agent': str(ua.random)
    }
    response_berita = requests.request("GET", url_berita, headers=headers, data=payload, verify=False)
    html_response_berita = response_berita.text
    html_bs4_berita = BeautifulSoup(html_response_berita, "html.parser")

    # URL berita
    url_berita = url_berita

    # Sumber berita
    sumber_berita = 'CNBC'

    # Kata Kunci
    kata_kunci = str(kata_kunci)

    # Mengambil informasi tanggal berita dari HTML pada tag div dengan class=date -> cari di struktur HTML
    tanggal = html_bs4_berita.find('div', class_='date').text

    # Olah tanggal
    tanggal = tanggal + ':00'

    #Ubah bulan
    tanggal = tanggal.replace(' January ', '-01-')
    tanggal = tanggal.replace(' February ', '-02-')
    tanggal = tanggal.replace(' March ', '-03-')
    tanggal = tanggal.replace(' April ', '-04-')
    tanggal = tanggal.replace(' May ', '-05-')
    tanggal = tanggal.replace(' June ', '-06-')
    tanggal = tanggal.replace(' July ', '-07-')
    tanggal = tanggal.replace(' Agustus ', '-08-')
    tanggal = tanggal.replace(' September ', '-09-')
    tanggal = tanggal.replace(' October ', '-10-')
    tanggal = tanggal.replace(' November ', '-11-')
    tanggal = tanggal.replace(' Desember ', '-12-')


    # Ubah format tanggal
    kalender = tanggal.split(' ')[0]
    kalender = kalender.split('-')
    kalender_fix = kalender[2] + '-' + kalender[1] + '-' + kalender[0]

    # Mengambil informasi judul berita dari HTML pada tag H1 -> cari di struktur HTML
    judul = html_bs4_berita.find('h1').text

    # Mengambil informasi isi berita dari HTML
    isi = html_bs4_berita.find('div', class_='detail_text')
    ## Memecah isi berita menjadi per paragraf
    list_paragraf = isi.find_all('p')
    ## Mengambil text dari setiap paragraf
    list_paragraf_clean = [paragraf.text for paragraf in list_paragraf]
    ## Menggabungkan list menjadi satu
    isi_clean = ' '.join(list_paragraf_clean)
    ## Membersihkan isi berita dari elemen tidak penting
    isi_clean = isi_clean.replace('\r\n', '')
    isi_clean = isi_clean.replace('ADVERTISEMENT SCROLL TO RESUME CONTENT', '')


    # Sentiment
    sentimen_judul = sentiment(judul)
    sentimen_berita = sentiment(isi_clean)


    # Add to DB
    isi_baris = [url_berita, sumber_berita, kata_kunci, kalender_fix, judul, isi_clean, sentimen_judul, sentimen_berita]
    
    mydb = mysql.connect(host = "localhost", user = "root", passwd = "", database = "berita")
    mycursor = mydb.cursor()

    sql = "INSERT IGNORE hasil_scrap VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "

    mycursor.execute(sql, isi_baris)
    mydb.commit()
    mydb.close()

def scrap_cnbc(keyword, date):
    print(f'{keyword} - {date}')
    # Main def
    keyword_set = keyword.replace(' ', '+')
    for page in range(4):
        # Set URL pencarian
        url_pencarian = f'https://www.cnbcindonesia.com/search?query={keyword_set}&p={page+1}&kanal=news&tipe=artikel&date={date.strftime("%Y/%m/%d")}'

        # Request url pencarian
        # Request Halaman
        payload={}
        headers = {
            'User-Agent': str(ua.random)
        }
        response = requests.request("GET", url_pencarian, headers=headers, data=payload, verify=False)
        html_response = response.text

        # Memanggil variabel berisi struktur HTML dari halaman CNBC yang telah direquest sebelumnya.
        html_bs4 = etree.HTML(str(html_response)) 

        # Get URL berita
        berita_urls = html_bs4.xpath('//article/a/@href')
        for berita_url in berita_urls:
            get_berita(berita_url, keyword)
                
# Multithreading
def multi_scrap_cnbc(keyword, date_list):
    with ThreadPoolExecutor(max_workers=8) as executor:
        for date in date_list:
            executor.submit(scrap_cnbc, keyword, date)

    # threads = [threading.Thread(name=f"CNBC {keyword} - {date}", target=scrap_cnbc, args=(keyword, date)) for date in date_list]
    # for thread in threads:
    #     thread.start()
    # for thread in threads:
    #     thread.join()

# # DF Keyword
# df_keyword = pd.read_csv('keyword.csv')
# list_keyword = df_keyword['keyword'].to_list()

# # Tanggal
# start_date = date(2022,7,1)
# end_date = date(2022,7,15)
# date_list = pd.date_range(start=start_date,end=end_date).to_list()

# multi_scrap_cnbc(list_keyword, date_list)