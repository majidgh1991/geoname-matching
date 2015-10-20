import json
import operator
import munkres
import jaro
import math
import re
import sys

class Levenshtein:
    def measure(self, seq1, seq2):
        oneago = None
        thisrow = range(1, len(seq2) + 1) + [0]
        for x in range(len(seq1)):
            twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
            for y in range(len(seq2)):
                delcost = oneago[y] + 1
                addcost = thisrow[y - 1] + 1
                subcost = oneago[y - 1] + (seq1[x] != seq2[y])
                thisrow[y] = min(delcost, addcost, subcost)
        max_len = max({len(seq1), len(seq2)})
        min_len = min({len(seq1), len(seq2)})
        return float(max_len - thisrow[len(seq2) - 1]) / float(min_len)

class EntityTransformation:
    threshold = 1.0
    stateToAbbr = {}
    stateAbbrs = set()
    allCities = set()
    reportFile = None

    def __init__(self):
        self.threshold = 1.0   # complete match for now
        self.stateToAbbr = eval(open("state_abbr.txt").read())
        self.allCities = set(line.strip() for line in open("all_cities.txt"))
        for key, val in self.stateToAbbr.iteritems():
            self.stateAbbrs.add(val)
        self.allCities = set(line.strip() for line in open("all_cities.txt"))
        self.reportFile = open("training_report.txt", "w")

    def stringDistSmith(self, strG, strR): # uses smith-waterman method
        if (len(strG) < 1 or len(strR) < 1):
            return [0.0, -1, -1, 1000, 10000]
        # print strG + " / " + strR
        row = len(strR)
        col = len(strG)
        strR = "^" + strR
        strG = "^" + strG

        matrix = []
        path = []
        for i in range(row + 1):
            matrix.append([0] * (col + 1))
            path.append(["N"] * (col + 1))
        # print_matrix(matrix)
        indelValue = -1
        matchValue = 2
        for i in range(1, row + 1):
            for j in range(1, col + 1):
                # penalty map
                from_left = matrix[i][j - 1] + indelValue
                from_top = matrix[i - 1][j] + indelValue
                if strR[i] == strG[j]:
                    from_diag = matrix[i - 1][j - 1] + matchValue
                else:
                    from_diag = matrix[i - 1][j - 1] + indelValue

                matrix[i][j] = max(from_left, from_top, from_diag)
                if matrix[i][j] == from_diag:
                    path[i][j] = "LT"
                elif matrix[i][j] == from_top:
                    path[i][j] = "T"
                else:
                    path[i][j] = "L"
                # if matrix[i][j] < 0:
                #     matrix[i][j] = 0
        max_sim = 0
        max_index = 0
        for i in range(1, row + 1):
            if (max_sim < matrix[i][col]):
                max_sim = matrix[i][col]
                max_index = i

        # find the path
        i = max_index
        j = col
        # for i in range(len(path)):
        #     print path[i]
        count_mismatch = 0
        count_gap = 0
        while j > 0:
            # print path[i][j]
            if path[i][j] == "T":
                i -= 1
                count_gap += 1
            elif path[i][j] == "L":
                j -= 1
                count_gap += 1
            elif path[i][j] == "LT":
                i -= 1
                j -= 1
                if matrix[i][j] < matrix[i-1][j-1]:
                    count_mismatch += 1
            else:
                count_mismatch = 1000
                count_gap = 1000
                break
        start_index = i
        # for i in range(len(matrix)):
        #     print matrix[i]
        return [float(max_sim) / float(len(strG) - 1) / 2.0,
                start_index, max_index,
                count_gap, count_mismatch]

    def findAndRemove(self, tofind, string, degree=0): # degree is how strict you want to be
        [score, sindex, lindex, gap, mismatch] = self.stringDistSmith(tofind, string)
        report = ""
        newstr = string
        if(score >= 1):
            report = "COMPLETE"
            newstr = string[:sindex] + string[lindex+1:]
        elif degree == 0 and mismatch < 2 and gap < 1:
            report = "TYPO"
            newstr = string[:sindex] + string[lindex+1:]
        else:
            report = "MISSING"
        newstr.strip()
        newstr = re.sub("\\s+", " ", newstr)
        return [report, newstr]

    def printPossibleTransformations(self, queryStr, refStr):
        countryReport = ""
        stateReport = ""
        cityReport = ""
        queryStr = queryStr.replace(",", " ")
        queryStr = re.sub("\\s+", " ", queryStr)
        refArgs = refStr.split(",")
        while len(refArgs) < 3:
            refArgs.append("")
        # print refArgs
        [cityReport, queryStr] = self.findAndRemove(refArgs[0], queryStr)
        print "\t\t" + queryStr
        [countryReport, queryStr] = self.findAndRemove(refArgs[2], queryStr)
        print "\t\t" + queryStr
        [stateReport, queryStr] = self.findAndRemove(refArgs[1], queryStr)
        if stateReport == "MISSING":
            # also look for state abbreviation
            if refArgs[1] in self.stateToAbbr:
                if self.stateToAbbr[refArgs[1]] in queryStr:
                    queryStr = queryStr.replace(self.stateToAbbr[refArgs[1]], "")
                    stateReport = "ABBR"
        print "\t\t" + queryStr
        matchingReport = countryReport + "_COUNTRY" ", " + \
                stateReport + "_STATE" + ", " + \
                cityReport + "_CITY"

        print "\t\t" + matchingReport

        remainingTags = []
        queryStr = re.sub("\\s+", " ", queryStr)
        # for city in self.allCities:
        #     [report, queryStr] = self.findAndRemove(city, queryStr, 1)
        #     if report == "COMPLETE":
        #         remainingTags.append("CITY")
        #         print city + " cmp"
        #     if queryStr == "":
        #         break
        # for state, abbr in self.stateToAbbr.iteritems():
        #     [report, queryStr] = self.findAndRemove(state, queryStr)
        #     if report == "COMPLETE":
        #         remainingTags.append("STATE")
        #     elif report == "TYPO":
        #         remainingTags.append("STATE_TYPO")
        #     if queryStr == "":
        #         break

        remainingWords = re.split("\\s+", queryStr)
        for word in remainingWords:
            if word == "":
                continue
            elif word.strip() in self.stateAbbrs:
                remainingTags.append("STATE_ABBR")
            elif word.strip() in self.stateToAbbr:
                remainingTags.append("STATE")
            elif word.strip() in self.allCities:
                remainingTags.append("CITY")
            else:
                remainingTags.append("GARBAGE")
        print("\t\t" + queryStr + " " + str(remainingTags))
        self.reportFile.write("matched: " + matchingReport + "\n")
        self.reportFile.write("remained: " + str(remainingTags) + "\n")

    def scoreTransformation(self, queryStr, refStr, fprob, rprob):
        queryStr = queryStr.replace(",", " ")
        queryStr = re.sub("\\s+", " ", queryStr)
        refArgs = refStr.split(",")
        resultScore = 1
        while len(refArgs) < 3:
            refArgs.append("")
        # print refArgs
        [score, index, gap] = self.stringDistSmith(refArgs[0], queryStr) # city
        if(score >= 1):
            resultScore *= (fprob[0][0])
            queryStr = queryStr.replace(queryStr[index - len(refArgs[0]):index], "")
        elif gap < 2:
            # print("typo city " + str(gap))
            resultScore *= (fprob[0][1])
            queryStr = queryStr.replace(queryStr[index - len(refArgs[0]):index], "")
        else:
            # print("missing city " + str(gap))
            resultScore *= (fprob[0][2])
        # print "\t\t" + queryStr
        [score, index, gap] = self.stringDistSmith(refArgs[2], queryStr) # country
        if(score >= 1):
            resultScore *= (fprob[2][0])
            queryStr = queryStr.replace(queryStr[index - len(refArgs[2]):index], "")
        elif gap < 2:
            resultScore *= (fprob[2][1])
            queryStr = queryStr.replace(queryStr[index - len(refArgs[2]):index], "")
        else:
            resultScore *= (fprob[2][2])
        # print "\t\t" + queryStr
        [score, index, gap] = self.stringDistSmith(refArgs[1], queryStr) # state
        if(score >= 1):
            resultScore *= (fprob[1][0])
            queryStr = queryStr.replace(queryStr[index - len(refArgs[1]):index], "")
        elif gap < 2:
            resultScore *= (fprob[1][1])
            queryStr = queryStr.replace(queryStr[index - len(refArgs[1]):index], "")
        else:
            resultScore *= (fprob[1][2])

            # also look for state abbreviation
            if refArgs[1] in self.stateToAbbr:
                if self.stateToAbbr[refArgs[1]] in queryStr:
                    queryStr = queryStr.replace(self.stateToAbbr[refArgs[1]], "")
                    resultScore *= (fprob[1][3])
        # print(resultScore)

        remainingWords = re.split("\\s+", queryStr)

        numbers = {"country_abbr": 0,
                       "country": 0,
                       "state_abbr": 0,
                       "state": 0,
                       "city_abbr": 0,
                       "city": 0,
                       "garbage": 0}
        for word in remainingWords:
            if word == "":
                continue
            if word.strip() in self.allCities:
                numbers["city"] += 1
                # resultScore *= (rprob[4])
                # remainingTags.append("CITY")
            elif word.strip() in self.stateAbbrs:
                numbers["state_abbr"] += 1
                # resultScore *= (rprob[1])
                # remainingTags.append("STATE_ABBR")
            elif word.strip() in self.stateToAbbr:
                numbers["state"] += 1
                # resultScore *= (rprob[2])
                # remainingTags.append("STATE")
            else:
                numbers["garbage"] += 1
                # resultScore *= (rprob[5])
                # remainingTags.append("GARBAGE")

        for key, value in numbers.iteritems():
            if value == 0:
                resultScore *= rprob[key][0]
            elif value == 1:
                resultScore *= rprob[key][1]
            else:
                resultScore *= rprob[key][2]
        return resultScore

def createTrainingData():
    with open("../geonameData/groundTruth_matched.lower.tsv") as matchFile:
        for line in matchFile:
            if line == "":
                continue
            args = line.split("\t")
            matching.update({args[0]: args[1]})

    referenceNames = {}

    with open("../geonameData/us_populated_places_states_cleaned.csv") as input_file:
        for line in input_file:
            args = line.split("\t")
            uri = args[0].strip()
            name = args[1].strip()
            referenceNames.update({uri: name})

    with open("../geonameData/tfidf_output_geonames_weapons_groundTruth.json") as input_file:
        for line in input_file:
            jsonObj = json.loads(line)
            query_string = jsonObj["query_string"]["name"]
            query_string = query_string.replace(",", " ")
            query_string = re.sub("\\s+", " ", query_string)
            print query_string
            # print "\t" + matching[jsonObj["query_string"]["uri"].strip()].strip()
            # for candidate in jsonObj["query_string"]["candidates"]:
                # if jsonObj["query_string"]["uri"].strip() in matching:
                #     if not matching[jsonObj["query_string"]["uri"].strip()].strip() in candidate["uri"].strip():
                #         # print "\t" + matching[jsonObj["query_string"]["uri"].strip()]
                #         continue
                # else:
                #     print(jsonObj["query_string"]["uri"])
                #     sys.exit(-1)
                # ref_string = candidate["name"]
                # if(ref_string != ""):
                #     print "\t" + ref_string + ": "

            if not jsonObj["query_string"]["uri"].strip() in matching:
                print(jsonObj["query_string"]["uri"])
                sys.exit(-1)
            ref_string = referenceNames.get(matching[jsonObj["query_string"]["uri"].strip()].strip())
            if ref_string == None:
                print(matching[jsonObj["query_string"]["uri"].strip()])
                continue
            print "\t" + str(ref_string) + ": "
            et.printPossibleTransformations(str(query_string), str(ref_string))

def scoreCandidates(fvector, rprob):

    with open("../geonameData/tfidf_output_geonames_weapons_groundTruth.json") as input_file:
        for line in input_file:
            matching = {}
            data = json.loads(line)
            queryStr = data["query_string"]["name"]
            print(queryStr)
            for candidate in data["query_string"]["candidates"]:
                candidateStr = candidate["name"]
                matching.update({str(candidateStr): et.scoreTransformation(str(queryStr), str(candidateStr), fvector, rprob)})
            for key, val in sorted(matching.items(), key=operator.itemgetter(1), reverse=True):
                print("\t" + str(key) + ":  " + str(val))

et = EntityTransformation()
# et.printPossibleTransformations("west cost, los angelis area, california"
#                                 , "los angeles,california,united states")
lv = Levenshtein()
matching = {}

featuresVector = [[0.8872180451127819, 0.09022556390977443, 0.022556390977443608, 0.0],
                  [0.9924812030075187, 0.007518796992481203, 0.0, 0.0],
                  [0.15037593984962405, 0.007518796992481203, 0.8421052631578947, 0.0]]

remainingProbablities = {'country_abbr': [1.0, 0.0, 0.0],
                         'city': [0.3684210526315789, 0.48120300751879697, 0.15037593984962405],
                         'state': [1.0, 0.0, 0.0],
                         'state_abbr': [0.9172932330827067, 0.07518796992481203, 0.007518796992481203],
                         'garbage': [0.6616541353383458, 0.18045112781954886, 0.15789473684210525],
                         'city_abbr': [1.0, 0.0, 0.0],
                         'country': [1.0, 0.0, 0.0]}

createTrainingData()
# scoreCandidates(featuresVector, remainingProbablities)
# print et.stringDistSmith("st. louis", "st. louis st. louis missouri")
