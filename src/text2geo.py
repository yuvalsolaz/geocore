import src.utils as utils
from src.geocoding import get_gmaps, geocode_api, get_gmap_query_score
import src.constants as constants


def text2geo(text):

    # todo - erez
    preprocessed_text = utils.preprocess_text_query(text) # for example, normalizing syng word etc.

    query_result = geocode_api(get_gmaps(), preprocessed_text)


    gmap_score = get_gmap_query_score(query_result)

    # todo - score from our database search

    # todo - other geo api's score

    # todo - ensemble

    final_geo
    if score > constants.GMAP_QUERY_SCORE_THRESH:

