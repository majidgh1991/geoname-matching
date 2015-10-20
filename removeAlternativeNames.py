geonames = {}
outFile = open("../geonameData/us_populated_places_states_cleaned.csv", "w")
with open("../geonameData/us_populated_places_states_altnames_cleaned.csv") as input_file:
    for line in input_file:
        args = line.split("\t")
        uri = args[0].strip()
        name = args[1].strip()
        if uri not in geonames:
            geonames.update({uri: name})
    for key, val in geonames.iteritems():
        outFile.write(key + "\t" + val + "\n")
