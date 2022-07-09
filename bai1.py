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
for chapter in range(1, 8):
    for section in range(1, 6):
        url = 'https://jtest.net/tu-vung-n4/chapter-{num1}/section-{num}'.format(
            num=section, num1=chapter)

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
        connection = sqlite3.connect("test_chap{num}.db".format(num=chapter))
        cursor = connection.cursor()

        cursor.execute(
            '''create table bai{num} (mp3_link text,Han_TU text,Tieng_Nhat text,Nghia_Viet text,vd_TN text,vd_TV text)'''.format(num=section))
        cursor.executemany(
            "insert into bai{num} (mp3_link,Han_TU,Tieng_Nhat,Nghia_Viet,vd_TN,vd_TV) VALUES (?,?,?,?,?,?)".format(num=section), res)
        # connection.commit()

        # Export data to csv file
        cursor.execute('select * from bai{num}'.format(num=section))
        with open("N4\\Chap{num1}\\bai{num}.csv".format(num=section, num1=chapter), 'w', newline='', encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([i[0] for i in cursor.description])
            csv_writer.writerows(cursor)

        connection.close()
