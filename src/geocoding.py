import sys,os
import pandas as pd
import googlemaps

gmaps = googlemaps.Client(key='AIzaSyBK9irAZ_Jtzt9ZKRDoAmWfe72_uny4Md0')

def geocoding(text):
    print(f'geocoding {text}')
    res = gmaps.geocode(text)
    if len(res) < 1 :
        return None
    geo = res[0]['geometry']['location']
    print(f'geo={geo}')
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

    df = pd.read_csv(file_name)
    print(df.head())

    location_col = 'מקום'
    df['geo'] = df[location_col].apply(lambda t : geocoding(t))
    print()


def print_geo_coding(res):
    print(f'{res["formatted_address"]} {res["geometry"]["location"]}')


