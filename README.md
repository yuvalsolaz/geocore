#pipeline script:
1. takes address data (as free text) from input csv file with text column name "place" 
2. for each address string call google maps geocode api 
3. save cache with all api results in postgres database table: research.geocoding_cache
4. creates new csv file: ./data/test_results.csv with coordinates and some additional data
5. if the api results exists in the database cache table the script will not call the api


#Usage:
python src/pipeline.py <input csv>

#Runing example :
python src/pipeline.py ./data/test.csv

#Installation:
1. sudo apt install libpq-dev (ubuntu only for pg_config installation)
2. pip install -r requirements.txt
