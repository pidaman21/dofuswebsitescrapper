import requests
import re
import json
import time
import mariadb
import sys
from bs4 import BeautifulSoup

def has_numbers(inputString):
    return any(char.isdigit() for char in str(inputString))

def element_exists(table, val_check_element):
    query_check_element = "SELECT id from "+ table +" WHERE name = ?"
    mycursor.execute(query_check_element, (val_check_element.strip(),))
    element = mycursor.fetchone()

    if element != None:
        return False
    else:
        return True

try:
    conn = mariadb.connect(
        user="root",
        password="abcde",
        host="localhost",
        port=3306,
        database="dofus"

    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

mycursor = conn.cursor()

def create_gear_json(res_url):
    last_insert_set_id = ''
    for url in res_url:
        res = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        })
        if res.status_code != 404:
            soup = BeautifulSoup(res.text, 'html.parser')
            res_title = soup.find('h1',class_="ak-return-link")
            res_anzahl = soup.find_all('div',class_="ak-front")
            res_item = soup.find_all('div',class_="ak-container ak-content-list ak-displaymode-image-col")
            res_img = soup.find_all('span',class_="ak-linker")
            res_set = soup.find_all('a',string=re.compile("Set"))
            res_gear_img = soup.find('div',class_="ak-encyclo-detail-illu")
            res_stats = soup.find('div', class_="ak-container ak-content-list ak-displaymode-col")

            item = []
            anzahl = []
            img = []
            set = ''
            for i in res_item:

                for span in i.find_all('span'):
                    if span.text !='' and 'equipment' not in i.a['href'] and 'monsters' not in i.a['href'] and 'weapon' not in i.a['href'] and 'pets' not in i.a['href'] and 'ceremonial-item' not in i.a['href']:
                        if len(item) < 8:
                            item.append(span.text)

            for a in res_anzahl:
                if a.text != '':
                    anzahl.append(a.text)

            for f in res_img:
                if f.text == '':
                    if len(img) < 8:
                        img.append(str(f).split('"')[5])

            for set in res_set:
                if set.text != "Sets":
                    set = set.text
                else:
                    set = ''

            if res_title == None:
                print(url)
                print(soup)

            item_name = res_title.text.strip()
            item_set_name = set
            item_pic_url = res_gear_img.img['src']

            query_check_item_exists = 'SELECT name FROM item'
            mycursor.execute(query_check_item_exists)
            res_all_items = mycursor.fetchall()

            query_check_ressource_exists = 'SELECT name FROM ressources'
            mycursor.execute(query_check_ressource_exists)
            res_all_ressources = mycursor.fetchall()

            query_check_set_exists = 'SELECT name FROM sets'
            mycursor.execute(query_check_set_exists)
            res_all_sets = mycursor.fetchall()

            if element_exists("sets",item_set_name):

                if item_set_name != '':
                    query_insert_set = 'INSERT INTO sets (name) VALUES(?)'
                    val_set = (item_set_name,)
                    mycursor.execute(query_insert_set, val_set)
                    last_insert_set_id = mycursor.lastrowid
            else:

                if item_set_name != '':
                    query_select_set_id = 'SELECT id FROM sets WHERE name = ?'
                    select_set_id_val = (item_set_name,)
                    mycursor.execute(query_select_set_id,select_set_id_val)
                    for id in mycursor:
                        last_insert_set_id = id[0]

            if element_exists('item',item_name):
                if last_insert_set_id == '':
                    last_insert_set_id = None
                query_insert_item = 'INSERT INTO item (name, pic_url,set_id) VALUES(?,?,?)'
                val_item = (item_name,item_pic_url,last_insert_set_id,)
                mycursor.execute(query_insert_item, val_item)
                last_insert_item_id = mycursor.lastrowid
            else:
                if item_name != '':
                    query_select_item_id = 'SELECT id FROM item WHERE name = ?'
                    select_item_id_val = (item_name,)
                    mycursor.execute(query_select_item_id,select_item_id_val)
                    for id in mycursor:
                        last_insert_item_id = id[0]

            if 'seal' not in item_name.lower() and 'dial' not in item_name.lower():
                insert_value = ""
                insert_column = ""
                try:
                    if len(res_stats.find_all('div',class_="ak-title")) > 0:
                        for stats in res_stats.find_all('div',class_="ak-title"):
                            res_split_stat = stats.text.strip().lower().split(" ")
                            if has_numbers( res_split_stat[0]):
                                if 'title:' not in res_split_stat[0].lower():
                                    if len(res_split_stat) > 2:
                                        if has_numbers(res_split_stat[0]) and has_numbers(res_split_stat[2]):
                                            if len(res_split_stat) == 5:
                                                insert_value = insert_value + "'" + res_split_stat[0] + " " + res_split_stat[1] + " " + res_split_stat[2]  + "',"
                                                if "%" in res_split_stat[2]:
                                                    insert_column = insert_column +"stats."+res_split_stat[3]+"_"+res_split_stat[4]+"_per,"
                                                else:
                                                    insert_column = insert_column +"stats."+res_split_stat[3]+"_"+res_split_stat[4]+","
                                            else:
                                                insert_value = insert_value + "'" + res_split_stat[0] + " " + res_split_stat[1] + " " + res_split_stat[2]  + "',"
                                                insert_column = insert_column +"stats."+res_split_stat[3]+","
                                        else:
                                            insert_value = insert_value + "'" + res_split_stat[0]+"',"
                                            if "%" in res_split_stat[0]:
                                                insert_column = insert_column +"stats."+res_split_stat[1]+"_"+res_split_stat[2]+"_per,"
                                            else:
                                                insert_column = insert_column +"stats."+res_split_stat[1]+"_"+res_split_stat[2]+","
                                    else:
                                        insert_value = insert_value + "'" + res_split_stat[0]+"',"
                                        insert_column = insert_column +"stats."+res_split_stat[1]+","
                except:
                    print("no stats")

                query_insert_stats = "INSERT INTO stats(item_id,"+insert_column[:-1]+") VALUES("+str(last_insert_item_id)+","+insert_value[:-1]+")"
                try:
                    mycursor.execute(query_insert_stats)
                except mariadb.Error as e:
                    print(f"duplicate entry: {e}")


            count = 0
            for count in range(0, len(item)):
                if item_name not in item:
                    if element_exists('ressources',item[count]):
                        ressources_title= item[count]
                        query_insert_ressources = 'INSERT INTO ressources (name, pic_url) VALUES(?,?)'
                        val_ressources = (ressources_title,img[count])
                        mycursor.execute(query_insert_ressources,val_ressources)
                        last_insert_res_id = mycursor.lastrowid
                        if count is not None:
                            query_insert_item2res = 'INSERT INTO item2res (item_id, res_id, count) VALUES(?,?,?)'
                            if len(item) < 0:
                                print("foobar2")
                                print(anzahl[count].strip())

                                val_item2res = (last_insert_item_id,last_insert_res_id,re.sub("[^0-9]", '',anzahl[count].strip()))
                        
                                mycursor.execute(query_insert_item2res,val_item2res)
                    else:
                        ressources_title= item[count]
                        query_select_res_id = 'SELECT id FROM ressources WHERE name = ?'
                        select_res_id_val = (ressources_title,)
                        mycursor.execute(query_select_res_id,select_res_id_val)
                        id = mycursor.fetchone()
                        for id in mycursor:
                            last_insert_res_id = id[0]
                            if count != None:
                                query_insert_item2res = 'INSERT INTO item2res (item_id, res_id, count) VALUES(?,?,?)'
                                val_item2res = (last_insert_item_id,last_insert_res_id,re.sub("[^0-9]", '',anzahl[count].strip()))
                                mycursor.execute(query_insert_item2res,val_item2res)
        conn.commit()
