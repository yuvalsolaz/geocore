import sys,os
import pandas as pd
import pickle
import googlemaps

try:
    from apikey import mykey
except:
    print(f'please add file src/apikey.py with one line:\n mykey=<valid api key> \n to your local repository')
    exit(10)

gmaps = googlemaps.Client(key=mykey)

#region consts
query_results_file = r'../data/gapi_results.pkl'
location_col = 'מקום'
id = 'OBJECTID'
# endregion consts

def get_geo(id,query_results):
    res = query_results[id] #gmaps.geocode(text)
    if len(res) < 1 :
        return None
    geo = res[0]['geometry']['location']
    return (geo['lat'],geo['lng'])


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
        for index,row in df.iterrows():
            query_results[row[id]] = gmaps.geocode(row[location_col])
        print(f'save results to : {query_results_file}')
        with open(query_results_file, 'wb') as fp:
            pickle.dump(query_results, fp)

    print('add query results to input dataframe:')
    df['gmapapi'] = df[id].apply(lambda t : get_geo(t,query_results))

    new_file_name = file_name.replace('.csv', '_results.csv')
    print(f'save input dataframe with query results to: {new_file_name}')
    df.to_csv(new_file_name)

