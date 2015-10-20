import sys
import re

# features list (not all are supported yet!):
# CITY_CMP, CITY_TYPO, CITY_MISSING, CITY_ABBR
# STATE_CMP, STATE_TYPO, STATE_MISSING, STATE_ABBR
# COUNTRY_CMP, COUNTRY_TYPO, COUNTRY_MISSING, COUNTRY_ABBR

featuresCount = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
remainingCount = {"country_abbr": [0, 0, 0],
                   "country": [0, 0, 0],
                   "state_abbr": [0, 0, 0],
                   "state": [0, 0, 0],
                   "city_abbr": [0, 0, 0],
                   "city": [0, 0, 0],
                   "garbage": [0, 0, 0]}  # garbage, city, city_abr, state, state_abr, country, country_abbr


count = 0
with open("training_report.txt") as training_report:
    for line in training_report:
        if "matched" in line:
            count += 1
            line = line.replace("matched: ", "")
            tokens = line.split(", ")
            for token in tokens:
                if "COMPLETE_CITY" in token:
                    featuresCount[0][0] += 1
                elif "TYPO_CITY" in token:
                    featuresCount[0][1] += 1
                elif "MISSING_CITY" in token:
                    featuresCount[0][2] += 1
                elif "ABBR_CITY" in token:
                    featuresCount[0][3] += 1
                elif "COMPLETE_STATE" in token:
                    featuresCount[1][0] += 1
                elif "TYPO_STATE" in token:
                    featuresCount[1][1] += 1
                elif "MISSING_STATE" in token:
                    featuresCount[1][2] += 1
                elif "ABBR_STATE" in token:
                    featuresCount[1][3] += 1
                elif "COMPLETE_COUNTRY" in token:
                    featuresCount[2][0] += 1
                elif "TYPO_COUNTRY" in token:
                    featuresCount[2][1] += 1
                elif "MISSING_COUNTRY" in token:
                    featuresCount[2][2] += 1
                elif "ABBR_COUNTRY" in token:
                    featuresCount[2][3] += 1
        elif "remained" in line:
            numbers = {"country_abbr": 0,
                       "country": 0,
                       "state_abbr": 0,
                       "state": 0,
                       "city_abbr": 0,
                       "city": 0,
                       "garbage": 0}
            # print(numbers)
            line = line.replace("remained: [", "")
            tokens = line.split(", ")
            for token in tokens:
                if "COUNTRY" in token:
                    numbers["country"] += 1
                elif "STATE_ABBR" in token:
                    numbers["state_abbr"] += 1
                elif "STATE" in token:
                    numbers["state"] += 1
                elif "CITY_ABBR" in token:
                    print "here"
                    numbers["city_abbr"] += 1
                elif "CITY" in token:
                    numbers["city"] += 1
                elif "GARBAGE" in token:
                    numbers["garbage"] += 1
            for key, value in numbers.iteritems():
                if value == 0:
                    remainingCount[key][0] += 1
                elif value == 1:
                    remainingCount[key][1] += 1
                else:
                    remainingCount[key][2] += 1

normalizedRemainingCount = {}
for key, value in remainingCount.iteritems():
    normalizedRemainingCount.update({key: [float(x)/float(count) for x in value]})

print(str(featuresCount))
print(str([[float(y)/float(count) for y in x] for x in featuresCount]))
print(str(remainingCount))
print(str(normalizedRemainingCount))
print count
