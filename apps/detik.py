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
urllib3.disable_warnings()
import time
from concurrent.futures import ThreadPoolExecutor

ua = UserAgent()

def get_berita(url_berita, kata_kunci):
    url_berita = str(url_berita)
    payload={}
    headers = {
        'User-Agent': str(ua.random)
    }
    response_berita = requests.request("GET", url_berita, headers=headers, data=payload, verify=False)
    html_response_berita = response_berita.text
    html_bs4_berita = etree.HTML(str(html_response_berita)) 

    # URL berita
    url_berita = url_berita

    # Sumber berita
    sumber_berita = 'Detik'

    # Kata Kunci
    kata_kunci = str(kata_kunci)

    ## Tanggal berita
    try:
        tanggal = html_bs4_berita.xpath('//div[@class="detail__date"]/text()')[0]
    except:
        tanggal = html_bs4_berita.xpath('//div[@class="date"]/text()')[0]

    # Olah tanggal
    tanggal_olah = tanggal.split(', ')
    tanggal_olah = tanggal_olah[1]
    tanggal_olah = tanggal_olah.replace(' WIB', ':00')
    tanggal_olah = tanggal_olah.replace(' Jan ', '-01-')
    tanggal_olah = tanggal_olah.replace(' Feb ', '-02-')
    tanggal_olah = tanggal_olah.replace(' Mar ', '-03-')
    tanggal_olah = tanggal_olah.replace(' Apr ', '-04-')
    tanggal_olah = tanggal_olah.replace(' Mei ', '-05-')
    tanggal_olah = tanggal_olah.replace(' Jun ', '-06-')
    tanggal_olah = tanggal_olah.replace(' Jul ', '-07-')
    tanggal_olah = tanggal_olah.replace(' Agu ', '-08-')
    tanggal_olah = tanggal_olah.replace(' Sep ', '-09-')
    tanggal_olah = tanggal_olah.replace(' Okt ', '-10-')
    tanggal_olah = tanggal_olah.replace(' Nov ', '-11-')
    tanggal_olah = tanggal_olah.replace(' Des ', '-12-')
    date_olah = tanggal_olah.split(' ')
    date_berita = date_olah[0]
    date_berita = date_berita.split('-')
    date_1 = date_berita[2]
    date_2 = date_berita[1]
    date_3 = date_berita[0]
    tanggal_fix = f'{date_1}-{date_2}-{date_3}'

    # Judul berita
    judul_berita = html_bs4_berita.xpath('//h1[@class="detail__title"]/text()')[0]
    judul_berita = " ".join(judul_berita.split())

    # Konten berita
    try:
        tpt = html_bs4_berita.xpath('//div[@class="detail__body-text itp_bodycontent"]/strong/text()')[0]
        kontens = kontens = html_bs4_berita.xpath('//div[@class="detail__body-text itp_bodycontent"]/p/text()')
    except:
        tpt = html_bs4_berita.xpath('//div[@class="detail__body-text itp_bodycontent"]/strong/text()')[0]
        kontens = kontens = html_bs4_berita.xpath('//div[@class="detail__body-text itp_bodycontent"]/div/text()')

    tpt = tpt + '-'
    full = []
    tpt_bersih = tpt.strip()
    full.append(tpt_bersih)
    for kontenn in kontens:
        kontenn_bersih = kontenn.strip()
        full.append(kontenn_bersih)
    konten = ' '.join(full)

    # Sentiment
    sentimen_judul = sentiment(judul_berita)
    sentimen_berita = sentiment(konten)


    # Add to DB
    isi_baris = [url_berita, sumber_berita, kata_kunci, tanggal_fix, judul_berita, konten, sentimen_judul, sentimen_berita]
    mydb = mysql.connect(host = "localhost", user = "root", passwd = "", database = "berita")
    mycursor = mydb.cursor()

    sql = "INSERT IGNORE hasil_scrap VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "

    mycursor.execute(sql, isi_baris)
    mydb.commit()
    mydb.close()


def scrap_detik(keyword, start_date, end_date, halaman):    
    print(f'{keyword} - {halaman}')
    # Request Halaman
    keyword_set = keyword.replace(' ', '+')
    url_halaman = f'https://www.detik.com/search/searchall?query={keyword_set}&siteid=3&sortby=time&sorttime=0&fromdatex={start_date.strftime("%d/%m/%Y")}&todatex={end_date.strftime("%d/%m/%Y")}&page={str(halaman)}'
    payload={}
    headers = {
        'User-Agent': str(ua.random)
    }
    response_halaman = requests.request("GET", url_halaman, headers=headers, data=payload, verify=False)
    html_response_halaman = response_halaman.text
    html_bs4_halaman = etree.HTML(str(html_response_halaman)) 
    urls_berita = html_bs4_halaman.xpath('//article/a/@href')

    for url_berita in urls_berita:
        try:
            get_berita(url_berita, keyword)
        except:
            pass

# Multithreading
def multi_scrap_detik(keyword, start_date, end_date):
    keyword_set = keyword.replace(' ', '+')
    url = f'https://www.detik.com/search/searchall?query={keyword_set}&siteid=3&sortby=time&sorttime=0&fromdatex={start_date.strftime("%d/%m/%Y")}&todatex={end_date.strftime("%d/%m/%Y")}'

    # Request Halaman
    payload={}
    headers = {
        'User-Agent': str(ua.random)
    }
    response = requests.request("GET", url, headers=headers, data=payload, verify=False)
    html_response = response.text

    # Memanggil variabel berisi struktur HTML dari halaman CNBC yang telah direquest sebelumnya.
    html_bs4 = BeautifulSoup(html_response, "html.parser")

    # Mengambil informasi jumlah berita
    jumlah_berita = html_bs4.find('span', class_='fl text').text
    jumlah_berita = jumlah_berita.split(', ')[1]
    jumlah_berita = jumlah_berita.split(' ')[0]

    # Mengambil informasi jumlah halaman
    jumlah_halaman = math.ceil(int(jumlah_berita) / 9)

    with ThreadPoolExecutor(max_workers=10) as executor:
        for halaman in range(1,jumlah_halaman+1):
            executor.submit(scrap_detik, keyword, start_date, end_date, halaman)
    
            
            

# DF Keyword
# df_keyword = pd.read_csv('keyword.csv')
# list_keyword = df_keyword['keyword'].to_list()

# # Tanggal
# start_date = date(2022,7,1)
# end_date = date(2022,7,2)

# multi_scrap_detik(list_keyword, start_date, end_date)