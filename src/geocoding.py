import sys,os
import pandas as pd
import numpy as np
import pickle
from pyproj import Proj
myProj = Proj("+proj=utm +zone=36K, +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")

#region consts
query_results_file = r'../data/gapi_results.pkl'
location_col = 'מקום'
id = 'OBJECTID'
# endregion consts

def geo2utm(lat,lon):
    return myProj(lon,lat)

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
        for index,row in df.iterrows():
            query_results[row[id]] = gmaps.geocode(row[location_col])
        print(f'save results to : {query_results_file}')
        with open(query_results_file, 'wb') as fp:
            pickle.dump(query_results, fp)

    print('add query results to input dataframe:')


    def get_geo_x(id, query_results):
        return query_results[id][0]['geometry']['location']['lng'] if len(query_results[id]) > 0 else None

    def get_geo_y(id, query_results):
        return query_results[id][0]['geometry']['location']['lat'] if len(query_results[id]) > 0 else None

    def get_viewport(id, query_results,axis=0):
        if len(query_results[id]) < 1:
            return None
        vp = query_results[id][0]['geometry']['viewport']
        northeast = geo2utm(vp['northeast']['lat'],vp['northeast']['lng'])
        southwest = geo2utm(vp['southwest']['lat'],vp['southwest']['lng'])
        return int(np.abs(northeast[0] - southwest[0])) if axis == 0 else int(np.abs(northeast[1] - southwest[1]))

    def get_partial_match(id,query_results):
        if  len(query_results[id]) < 1:
            return None
        return query_results[id][0]['partial_match'] if 'partial_match' in query_results[id][0] else False


    def get_partial_match(id,query_results):
        if  len(query_results[id]) < 1:
            return None
        return query_results[id][0]['partial_match'] if 'partial_match' in query_results[id][0] else False


    def get_location_type(id, query_results):
        return query_results[id][0]['geometry']['location_type'] if len(query_results[id]) > 0 else None



    df['gmapapi_x'] = df[id].apply(lambda t : get_geo_x(t,query_results))
    df['gmapapi_y'] = df[id].apply(lambda t : get_geo_y(t,query_results))
    df['gmapapi_location_type'] = df[id].apply(lambda t: get_location_type(t, query_results))
    df['gmapapi_viewport_x'] = df[id].apply(lambda t: get_viewport(t,query_results, axis=0))
    df['gmapapi_viewport_y'] = df[id].apply(lambda t: get_viewport(t,query_results, axis=1))
    df['gmapapi_count'] = df[id].apply(lambda t: len(query_results[t]))
    df['gmapapi_partial_match'] = df[id].apply(lambda t : get_partial_match(t,query_results))

    new_file_name = file_name.replace('.csv', '_results.csv')
    print(f'save input dataframe with query results to: {new_file_name}')
    df.to_csv(new_file_name)

