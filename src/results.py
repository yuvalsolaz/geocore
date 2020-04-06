import pandas as pd
import re
import inspect
import numpy as np
from src.geocoding import geo2utm, id
import math
import matplotlib.pyplot as plt

dist_thresh = 30
dist_max_value = 500

def get_two_pts_dist(row, first_x_field, first_y_field, second_x_field, second_y_field):
    if pd.isna(row[first_x_field]) or pd.isna(row[second_x_field]):
        return 3000
    gold_utm = geo2utm(row[first_y_field],row[first_x_field])
    gmaps_utm = geo2utm(row[second_y_field],row[second_x_field])

    dist = np.subtract(gold_utm, gmaps_utm) ** 2
    dist = np.sum(dist)
    dist = np.sqrt(dist)

    return dist

def compare_xy(df,first_x_field, first_y_field, second_x_field, second_y_field, hist_title, dist_thresh = 10):

    df['distance_m'] = df.apply(lambda t: get_two_pts_dist(t, first_x_field, first_y_field, second_x_field, second_y_field), axis=1)
    mistakes_cnt = np.sum(df['distance_m'] > dist_thresh)

    print(df['distance_m'].describe())
    print('too far percentage (more than {} meters): {}'.format(str(dist_thresh), str(mistakes_cnt / df.shape[0])))

    dist_list = df['distance_m'].tolist()
    dist_list = [x if x < dist_max_value else dist_max_value for x in dist_list]

    fig1 = plt.gcf()
    plt.hist(dist_list, bins=50, range=(0, dist_max_value))  # `density=False` would make counts
    plt.ylabel('count')
    plt.xlabel('distance [m]');
    plt.title(hist_title + '. less than {:.1f} meters percentage: {:.2f}'.format(dist_thresh,1 - mistakes_cnt / df.shape[0]) );
    fig1.savefig('figures/' + hist_title + '.png')
    plt.show()


is_gold_vs_gmaps_5000 = True
is_gold_vs_gmaps_1500 = True
is_gmaps_vs_arcgis = False
is_gold_vs_arcgis_1500 = True

if is_gold_vs_gmaps_5000:
    csv_path = "../data/EPI_CoronaExposure_XRM_NEW_31_3_1807_TableToExcel_results.csv"
    df = pd.read_csv(csv_path, index_col=0)
    df = df.loc[df['valid'] == 1]
    print(df.shape)

    first_x_field = 'POINT_X'
    first_y_field = 'POINT_Y'
    second_x_field = 'gmapapi_x'
    second_y_field = 'gmapapi_y'
    hist_title = 'Gold Vs Gmaps - 5000 samples'
    compare_xy(df, first_x_field, first_y_field, second_x_field, second_y_field, hist_title, dist_thresh)

if is_gold_vs_gmaps_1500:
    csv_path = "../data/test_results.csv"
    df = pd.read_csv(csv_path, index_col=0)
    print('df shape: ' + str(df.shape))

    first_x_field = 'x'
    first_y_field = 'y'
    second_x_field = 'gmapapi_x'
    second_y_field = 'gmapapi_y'
    hist_title = 'Gold Vs Gmaps - 1500 samples'
    compare_xy(df, first_x_field, first_y_field, second_x_field, second_y_field, hist_title, dist_thresh)

if is_gold_vs_arcgis_1500:
    csv_path = "../data/test_results.csv"
    df = pd.read_csv(csv_path, index_col=0)
    print('df shape: ' + str(df.shape))

    first_x_field = '(\'ArcGIS\',)_x'
    first_y_field = '(\'ArcGIS\',)_y'
    second_x_field = 'x'
    second_y_field = 'y'
    hist_title = 'Gold Vs ArcGIS - 1500 samples'
    compare_xy(df, first_x_field, first_y_field, second_x_field, second_y_field, hist_title, dist_thresh)




