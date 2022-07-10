from asyncio.windows_events import NULL
from encodings import utf_8
from operator import attrgetter
from os import curdir
from urllib import response
from bs4 import BeautifulSoup
import requests
import pandas as pd
import sqlite3
import csv


def get_chapter_number(url):
    response = requests.get(url)
    tmp = BeautifulSoup(response.content, 'html.parser')
    chapter_len = tmp.find_all('div', attrs={'class': 'col-sm-6'})
    return len(chapter_len)


def get_section_number(url, chap_num):
    response = requests.get(url)
    tmp = BeautifulSoup(response.content, 'html.parser')
    filter1 = tmp.find_all('div', attrs={'class': 'col-sm-6'})
    section_len = filter1[chap_num-1].find_all('p')
    return(len(section_len) - 1)


# print(get_chapter_number('https://jtest.net/tu-vung-n4'))
# print(get_section_number('https://jtest.net/tu-vung-n3', 6))
for type in range(1, 6):
    url_tmp = 'https://jtest.net/tu-vung-n{n}'.format(n=type)
    chapter_max = get_chapter_number(url_tmp)
    section_max = get_section_number(url_tmp)
    for chapter in range(1, chapter_max):
        section_max = get_section_number(url_tmp, chapter)
        for section in range(1, section_max):
            url = 'https://jtest.net/tu-vung-n4/chapter-{num1}/section-{num2}'.format(
                num1=chapter, num2=section)

            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            # Lấy từng thẻ dịch - start index = 1
            filter_each = soup.find_all(
                'tr'
            )
            # print(filter_each[1])
            # print(filter_each[36])
            res = list()
            index = 1
            for i in range(1, len(filter_each)):
                # Lấy link .mp3
                get_mp3 = filter_each[i].find(
                    'button', attrs={'type': 'button', 'class':
                                     'btn btn-link playWordSound'})
                if get_mp3 is None:
                    tmp = ('',)
                else:
                    tmp = (str(get_mp3['value']),)

                # print(str(get_mp3['value']))
                # Lấy từ vựng : Hán tự, Tiếng Nhật, nghĩa Việt
                Han_tu = filter_each[i].find('small',
                                             {'class': 'text-danger'})

                tmp += (str(Han_tu.get_text()),)
                # print(str(Han_tu.get_text()))
                Tieng_nhat = filter_each[i].find_all('small', {})

                if len(Tieng_nhat) == 1:
                    tmp += ("",)
                else:
                    tmp += (Tieng_nhat[1].get_text().replace('\n', ''),)
                Nghia_Viet = filter_each[i].find('span')
                tmp += (Nghia_Viet.get_text(),)
                # print(Nghia_Viet.get_text())
                # Lấy ví dụ
                vd_TiengNhat = filter_each[i].find(
                    'p'
                )

                vd_TiengViet = filter_each[i].find_all('span')
                tmp += (str(vd_TiengNhat.contents), vd_TiengViet[1].text,)
                # list lưu tuple
                res.append(tmp)

            # database sqplite
            connection = sqlite3.connect(
                "test_chap{num1}.db".format(num1=chapter))
            cursor = connection.cursor()

            cursor.execute(
                '''create table bai{num2} (mp3_link text,Han_TU text,Tieng_Nhat text,Nghia_Viet text,vd_TN text,vd_TV text)'''.format(num2=section))
            cursor.executemany(
                "insert into bai{num2} (mp3_link,Han_TU,Tieng_Nhat,Nghia_Viet,vd_TN,vd_TV) VALUES (?,?,?,?,?,?)".format(num2=section), res)
            # connection.commit()

            # Export data to csv file
            cursor.execute('select * from bai{num2}'.format(num2=section))
            with open("N4\\Chap{num1}\\bai{num2}.csv".format(num1=chapter, num2=section), 'w', newline='', encoding="utf-8") as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([i[0] for i in cursor.description])
                csv_writer.writerows(cursor)

            connection.close()
