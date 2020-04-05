# geocore script:
1. takes address data (as free text) from input csv file
2. for each address string call google maps geocode api 
3. save dictionary with all results as a pickle file in : ./data/gapi_results.pkl
4. creates new csv file: ./data/test_results.csv with coordinates and some additional data 
5. if the api results file ( ./data/gapi_results.pkl) exists the script will not call the api 

