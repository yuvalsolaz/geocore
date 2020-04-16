import os
import sys
import pandas as pd
from geocoding import add_cahced_geocoding_results
from info_extactor import InfoExtractor

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print (f'usage: python {sys.argv[0]} <input csv file>')
        exit(1)

    # load input csv :
    file_name = sys.argv[1]
    if not os.path.exists(file_name):
        print (f'Error: file {file_name} not exists')
        exit(2)

    print(f'load input file {file_name}:')
    df = pd.read_csv(file_name)
    print(df.head())

    print(f'add geocoding results from google api:')
    df = add_cahced_geocoding_results(df)

    print(f'add regex results from info extractor :')
    ie = InfoExtractor()
    def get_type(text):
        if type(text) is not str:
            return None
        res =  ie.extract_type(text)
        return res[0] if res is not None else None

    def get_city(text):
        if type(text) is not str:
            return None
        return  ie.extract_city(text)

    df['extractor_place_type'] = df['place'].apply(lambda t: get_type(t))
    df['extractor_city'] = df['place'].apply(lambda t: get_city(t))

    new_file_name = file_name.replace('.csv', '_results.csv')
    print(f'save input dataframe with query results to: {new_file_name}')
    df.to_csv(new_file_name)