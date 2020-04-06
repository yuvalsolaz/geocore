import pandas as pd
import re
import inspect
import numpy as np
from src.geocoding import geo2utm, id
import math

df = pd.read_csv("../data/EPI_CoronaExposure_XRM_NEW_31_3_1807_TableToExcel_results.csv", index_col=0)
df_valid = df.loc[df['valid'] == 1]
print(df_valid.shape)

def get_two_pts_dist(row):
    if pd.isna(row['gmapapi_x']):
        return None
    gold_utm = geo2utm(row['POINT_X'],row['POINT_Y'])
    gmaps_utm = geo2utm(row['gmapapi_x'],row['gmapapi_y'])

    dist = np.subtract(gold_utm, gmaps_utm) ** 2
    dist = np.sum(dist)
    dist = np.sqrt(dist)

    return dist

df_valid['distance_m'] = df.apply(lambda t : get_two_pts_dist(t), axis=1)
dist_thresh = 30
mistakes_cnt = df_valid[df_valid['distance_m'] > dist_thresh].sum()
print('too far percentage (more than %f meters): %f'.format(dist_thresh, mistakes_cnt))
i =9

