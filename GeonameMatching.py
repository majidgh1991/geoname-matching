import sys
import re
import json

matching = {}
with open("../geonameData/tfidf_output_geonames_weapons.json") as input_file:
    for line in input_file:
        data = json.loads(line)
        queryStr = data["query_string"]["name"]
        for candidate in data["query_string"]["candidates"]:
            candidateStr = candidate["name"]
