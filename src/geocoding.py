import sys,os
import pandas as pd
import numpy as np
import pickle
import json
from tqdm import tqdm
from pyproj import Proj
from sqlalchemy import create_engine


#region config :
location_col = 'place'
id = 'OBJECTID'
cache_table = 'research.geocoding_cache'
db = create_engine(r'postgresql://postgres:sergtsop@pg-covid-19.clqp7zznjkvp.eu-west-2.rds.amazonaws.com:5432/postgres')
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

#region depracted :
'''
cache_text = ''
cache_result = None

def geocode_api(gmaps,text):
    global cache_text,cache_result
    if type(text) is not str:
        result = None
    else:
        # do not call api on the same text
        result = gmaps.geocode(text) if text != cache_text else  cache_result
    # update cache
    cache_text = text
    cache_result = result
    return result


def add_geocoding_results(df,query_results_file):
    query_results = {}
    if os.path.exists(query_results_file):
        print(f'loading query results from file: {query_results_file}')
        with open(query_results_file,'rb') as fp:
            query_results = pickle.load(fp)
    else:
        print(f'query api for {df.shape[0]} records:')
        import googlemaps
        try:
            from apikey import mykey
        except:
            print(f'please add file src/apikey.py with one line:\n mykey=<valid api key> \n to your local repository')
            exit(10)

        gmaps = googlemaps.Client(key=mykey)
        for index,row in tqdm(df.sort_values(by=location_col).iterrows(),total=df.shape[0]):
            query_results[row[id]] = geocode_api(gmaps,row[location_col])

        print(f'save results to : {query_results_file}')
        with open(query_results_file, 'wb') as fp:
            pickle.dump(query_results, fp)

    print('add query results to input dataframe:')

    def valid(id):
        return query_results[id] is not None and len(query_results[id]) > 0

    def get_geo_x(id, query_results):
        return query_results[id][0]['geometry']['location']['lng'] if valid(id) else None

    def get_geo_y(id, query_results):
        return query_results[id][0]['geometry']['location']['lat'] if valid(id) > 0 else None

    def get_viewport(id, query_results,axis=0):
        if not valid(id):
            return None
        vp = query_results[id][0]['geometry']['viewport']
        northeast = geo2utm(vp['northeast']['lat'],vp['northeast']['lng'])
        southwest = geo2utm(vp['southwest']['lat'],vp['southwest']['lng'])
        return int(np.abs(northeast[0] - southwest[0])) if axis == 0 else int(np.abs(northeast[1] - southwest[1]))

    def get_partial_match(id,query_results):
        if not valid(id):
            return None
        return query_results[id][0]['partial_match'] if 'partial_match' in query_results[id][0] else False


    def get_partial_match(id,query_results):
        if not valid(id):
            return None
        return query_results[id][0]['partial_match'] if 'partial_match' in query_results[id][0] else False


    def get_location_type(id, query_results):
        return query_results[id][0]['geometry']['location_type'] if valid(id) else None

    def get_location_types(id, query_results):
        return ' '.join(query_results[id][0]['types']) if valid(id) else None

    df['gmapapi_x'] = df[id].apply(lambda t : get_geo_x(t,query_results))
    df['gmapapi_y'] = df[id].apply(lambda t : get_geo_y(t,query_results))
    df['gmapapi_location_type'] = df[id].apply(lambda t: get_location_type(t, query_results))
    df['gmapapi_viewport_x'] = df[id].apply(lambda t: get_viewport(t,query_results, axis=0))
    df['gmapapi_viewport_y'] = df[id].apply(lambda t: get_viewport(t,query_results, axis=1))
    df['gmapapi_count'] = df[id].apply(lambda t: len(query_results[t]) if valid(t) else None)
    df['gmapapi_partial_match'] = df[id].apply(lambda t : get_partial_match(t,query_results))
    df['gmapapi_location_types'] = df[id].apply(lambda t : get_location_types(t,query_results))

    return df
'''
#endregion depracted

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

