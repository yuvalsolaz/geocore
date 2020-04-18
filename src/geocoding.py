import sys,os
import pandas as pd
import numpy as np
import json
from tqdm import tqdm
from pyproj import Proj
from sqlalchemy import create_engine


#region config :
location_col = 'place'
cache_table = 'research.geocoding_cache'
connection_str = r'postgresql://postgres:sergtsop@pg-covid-19.clqp7zznjkvp.eu-west-2.rds.amazonaws.com:5432/postgres'
db = create_engine(connection_str)
# endregion config


#region utils:
geo2utmProj = Proj("+proj=utm +zone=36K, +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
utm2GeoProj = Proj("+proj=utm +zone=36K, +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs",reversed=True)

def geo2utm(lat,lon):
    return geo2utmProj(lon,lat)

def utm2geo(lat,lon):
    return utm2GeoProj(lon,lat)
#endregion


'''
# databsed cached api:
if input text exists in database return results from database 
else  call api , save results in database and return results  
'''

def create_gmap_engine():
    import googlemaps
    gmaps = None
    try:
        from apikey import mykey
        gmaps = googlemaps.Client(key=mykey)
    except:
        print(f'please add file src/apikey.py with one line:\nmykey=<valid api key> \nto your local repository')
    return gmaps


def get_geocoding(gmaps,text):

    if type(text) is not str:
        print(f'text field type mismatch {type(text)} is not str')
        return None

    # replace all (') chars  with (") to prevent sql errors:
    text = text.replace('\'','')

    query_sql = f'''
    select results from {cache_table} where text='{text}'
    '''
    query_results = None
    try:
        query_results = db.execute(query_sql)
    except Exception as ex:
        print(f'Databse query Error: {ex}')

    if query_results is not None and query_results.rowcount > 0:
        return json.loads(query_results.next()._row[0])

    if gmaps is None:
        raise('Error invalid google maps api client')

    geocode_results = gmaps.geocode(text)
    # update cache :
    print(f'update cache {cache_table} with results')
    try:
        # replace all (') chars  with (") to prevent sql errors:
        geocode_results_json = json.dumps(geocode_results).replace('\'', '')
        insetr_sql = f'''
        insert into {cache_table} (text, results) values ('{text}', '{geocode_results_json}')
        '''
        db.execute(insetr_sql)
    except Exception as ex:
        print(f'Databse insert Error: {ex}')

    return geocode_results


def apply_geocoding(df):

    gmaps = create_gmap_engine()
    res_df = pd.DataFrame()
    for index, row in tqdm(df.iterrows(),total=df.shape[0]):
        geocoding_results = get_geocoding(gmaps, row[location_col])
        if geocoding_results is None or len(geocoding_results) < 1:
            res_df = res_df.append(row)
            continue
        vp = geocoding_results[0]['geometry']['viewport']
        northeast = geo2utm(vp['northeast']['lat'], vp['northeast']['lng'])
        southwest = geo2utm(vp['southwest']['lat'], vp['southwest']['lng'])
        row['gmapapi_x'] = geocoding_results[0]['geometry']['location']['lng']
        row['gmapapi_y'] = geocoding_results[0]['geometry']['location']['lat']
        row['gmapapi_location_type'] = geocoding_results[0]['geometry']['location_type']
        row['gmapapi_viewport_x'] = int(np.abs(northeast[0] - southwest[0]))
        row['gmapapi_viewport_y'] = int(np.abs(northeast[1] - southwest[1]))
        row['gmapapi_count'] = len(geocoding_results)
        row['gmapapi_partial_match'] = geocoding_results[0]['partial_match'] if 'partial_match' in geocoding_results[0] else False
        row['gmapapi_location_types'] = ' '.join(geocoding_results[0]['types'])
        res_df = res_df.append(row)

    return res_df



if __name__ == '__main__':

    if len(sys.argv) < 2:
        print (f'usage: python {sys.argv[0]} <text file>')
        exit(1)

    # load geo texts from csv file :
    file_name = sys.argv[1]
    if not os.path.exists(file_name):
        print (f'Error: file {file_name} not exists')
        exit(2)

    print(f'load input file {file_name}:')
    df = pd.read_csv(file_name)
    print(df.head())

    df = apply_geocoding(df)

    new_file_name = file_name.replace('.csv', '_results.csv')
    print(f'save input dataframe with query results to: {new_file_name}')
    df.to_csv(new_file_name)

