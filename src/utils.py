import googlemaps
from time import sleep
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
from pathlib import Path
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import json
from datetime import datetime
from shapely.geometry import Point
import geopandas as gpd


def gmap_query(query: str, gmaps):
    # gmaps = googlemaps.Client(key='AIzaSyBK9irAZ_Jtzt9ZKRDoAmWfe72_uny4Md0')
    res = list()
    iter_num = 0
    args = {
        'location': '31.518200,34.955511',  # center of Israel
        'radius': '250km'  # cover whole country
    }
    while True:
        iter_num += 1
        curr_res = gmaps.places(query, **args)
        sleep(2)  # otherwise api raises exception
        if 'next_page_token' not in curr_res:
            res.extend(curr_res['results'])
            break
        else:
            args['page_token'] = curr_res['next_page_token']
        res.extend(curr_res['results'])
    return res


def scrap_infected_places() -> pd.DataFrame:
    chrome_driver_path = os.path.abspath('../chromedriver_win32/chromedriver.exe')
    options = webdriver.ChromeOptions()
    home_path = str(Path.home())
    prefs = {"download.default_directory": home_path}
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options)
    url = 'https://www.arcgis.com/apps/webappviewer/index.html?id=20ded58639ff4d47a2e2e36af464c36e&locale=he'
    driver.get(url)
    WebDriverWait(driver, 100).until(ec.visibility_of_element_located((By.XPATH, "//button")))
    driver.find_elements_by_xpath("//button")[0].click()  # click initial message
    WebDriverWait(driver, 100).until(ec.element_to_be_clickable((By.XPATH, "//div[@class='close-btn']")))
    driver.find_elements_by_xpath("//div[@class='close-btn']")[0].click()  # click search sidebar
    driver.find_elements_by_xpath(
        "//div[@class='jimu-corner-all jimu-widget-zoomslider jimu-widget-zoomsliderRtl jimu-widget vertical']")[
        0].click()  # zoom out
    driver.find_elements_by_xpath("//div[@class='jimu-widget-attributetable-switch close']")[
        0].click()  # open attribute table
    WebDriverWait(driver, 100).until(ec.presence_of_element_located((By.ID, "dgrid_0")))
    driver.find_elements_by_xpath("//span[@class='dijitReset dijitInline dijitArrowButtonInner']")[
        0].click()  # open dropdown
    driver.find_elements_by_id("dijit_MenuItem_4_text")[0].click()  # click export to csv
    WebDriverWait(driver, 100).until(ec.element_to_be_clickable(
        (By.ID, 'jimu_dijit_Message_0')))
    driver.find_elements_by_id('jimu_dijit_Message_0')[0].click()
    if 'מיקומי חשיפה לקורונה.csv' in os.listdir(home_path):
        os.remove(home_path + '/' + 'מיקומי חשיפה לקורונה.csv')
    driver.find_elements_by_xpath(
        "//div[@class='jimu-btn jimu-popup-action-btn jimu-float-trailing jimu-trailing-margin1  ']")[
        0].click()  # click ok for download
    while 'מיקומי חשיפה לקורונה.csv' not in os.listdir(home_path):
        sleep(0.1)
    driver.close()
    df = pd.read_csv(home_path + '/' + 'מיקומי חשיפה לקורונה.csv')
    os.remove(home_path + '/' + 'מיקומי חשיפה לקורונה.csv')
    return df


def get_date_info(timestamp: datetime) -> dict:
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    date_hour = str(timestamp).split(' ')
    return {'date': date_hour[0], 'hour': date_hour[1], 'weekday': day_names[timestamp.weekday()]}


def get_activities_data(path: str) -> pd.DataFrame:
    activities = list()
    with open(path, 'r') as f:
        res = json.loads(f.read())
    for e in res['locations']:
        curr_dict = {}
        curr_dict['timestamp'] = datetime.fromtimestamp(float(e['timestampMs']) // 1000)
        curr_dict.update(get_date_info(curr_dict['timestamp']))
        curr_dict['latitude'] = e['latitudeE7']
        curr_dict['longitude'] = e['longitudeE7']
        if curr_dict['latitude'] > 900000000:
            curr_dict['latitude'] -= 4294967296
        if curr_dict['longitude'] > 1800000000:
            curr_dict['longitude'] -= 4294967296
        curr_dict['latitude'] /= 1e7
        curr_dict['longitude'] /= 1e7
        curr_dict['accuracy'] = e['accuracy']
        curr_dict['activity'] = None
        curr_dict['confidence'] = None
        activities.append(curr_dict)
        if 'activity' in e:
            for ref_e in e['activity']:
                curr_dict['timestamp'] = datetime.fromtimestamp(float(ref_e['timestampMs']) // 1000)
                curr_dict.update(get_date_info(curr_dict['timestamp']))
                curr_dict['confidence'] = max([a['confidence'] for a in ref_e['activity']])
                curr_dict['activity'] = \
                    [ac['type'] for ac in ref_e['activity'] if ac['confidence'] == curr_dict['confidence']][0]
                activities.append(curr_dict)
    df = pd.DataFrame(activities).drop_duplicates().reset_index(drop=True)
    df['geometry'] = df.apply(lambda x: Point((float(x['longitude']), float(x['latitude']))), axis=1)
    return df


def df_to_shape_file(df: pd.DataFrame, output_path='.'):
    df = gpd.GeoDataFrame(df, geometry='geometry')
    df['timestamp'] = df['timestamp'].astype(str)
    df.to_file(f'{output_path}/MyGeometries.shp', driver='ESRI Shapefile')


if __name__ == '__main__':
    # # example of gmap_query usage
    # gmaps = googlemaps.Client(key='AIzaSyA-kM5w49HNyBSVqUkPdI5s60PbI4xcoO0')
    # query = 'בית הכנסת'
    # res = gmap_query(query, gmaps)
    # example of scrap_infected_places usage
    df = scrap_infected_places()
    pass
