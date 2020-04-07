import os
import re
import json
import pandas as pd

# globals and default paths
DEFAULT_CITY_PATH = os.path.join(os.path.dirname(__file__),r'../data/yeshuvim_20200301.csv')
DEFAULT_TYPE_JSON_PATH = os.path.join(os.path.dirname(__file__),r'type_regex.json')

def prepare_city_list():
    yeshuv_df = pd.read_csv(DEFAULT_CITY_PATH, encoding="cp1255", usecols=["שם_ישוב"], skiprows=1, dtype=str)
    yeshuv_df["שם_ישוב"] = yeshuv_df["שם_ישוב"].apply(lambda x: x.split("  ")[0].replace(")", "").replace("(", ""))

    union_set_1 = set(yeshuv_df["שם_ישוב"].tolist())
    union_set_2 = set(yeshuv_df["שם_ישוב"].str.replace("-", " ").tolist())
    union_set_3 = set(yeshuv_df["שם_ישוב"].str.replace("י", "יי").tolist())
    union_set_4 = set(yeshuv_df["שם_ישוב"].str.replace(" - ", " ").tolist())
    union_set_5 = set(yeshuv_df["שם_ישוב"].str.replace("יי", "י").tolist())
    union_set_6 = set(yeshuv_df["שם_ישוב"].str.split("-", " ").tolist())

    split_set = []
    for elem in yeshuv_df["שם_ישוב"].str.split("-").tolist():
        for name in elem:
            split_set.append(name)
    union_set_7 = set(split_set)
    temp = set(union_set_1.union(union_set_2).union(union_set_3).union(union_set_4).union(union_set_5).union(
        union_set_6).union(union_set_7))
    all_seperated_names = []
    for name in temp:
        try:
            candidate = name.rstrip().lstrip()
            all_seperated_names.append(candidate)
        except:
            pass
    all_seperated_names = set(all_seperated_names)
    return all_seperated_names


class InfoExtractor:
    def __init__(self, city_db_path=DEFAULT_CITY_PATH, type_json_path=DEFAULT_TYPE_JSON_PATH):
        self._column_list = []
        with open(type_json_path, "r") as fp:
            regex_dict = json.load(fp)
        self._regex_list = []
        self._type_list = []
        for key, value in regex_dict.items(): #key is type name, value is keywrods
            self._regex_list.append(r"(?=(" + '|'.join(value) + r"))")
            self._type_list.append(key)
        self._city_db_path = city_db_path
        self._city_list = prepare_city_list()
        pass

    def extract_type(self, text) -> dict:
        result_list = []
        for current_type, current_regex in zip(self._type_list, self._regex_list):
            if re.search(current_regex, text):
                result_list.append(current_type)
        if len(result_list) > 0:
            return result_list
        return None

    def extract_city(self, text) -> str:
        candidate_text = text[-15:]
        best_match = "   "
        for city in self._city_list:
            if city == candidate_text or (city in candidate_text and len(city) > len(best_match)):
                best_match = city
#        print("text: " + text + " candidate_text: " + str(candidate_text) + " , city: " + best_match)
        if best_match == '   ':  #failed extraction
            return None
        return best_match

    def extract_street(self, text) -> dict:
        raise NotImplementedError

    '''
    combines all of the modules functions to extract as much data as possible from text
    '''
    def extract_info(self, text) -> dict:
        result_dict = dict()
        result_dict["types"] = self.extract_type(text)
        result_dict["city"] = self.extract_city(text)
        return result_dict


if __name__ == "__main__":
    ie = InfoExtractor()
    example_text = r"בית ספר עירוני ה' אבנר חושן 57 מודיעין"
    print("example: " + example_text)
    print(ie.extract_info(text=example_text))
