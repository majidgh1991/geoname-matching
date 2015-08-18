import json
import munkres
import jaro
import re
import sys

class SmithWaterman:
	def measure(self, strG, strR):
		if(len(strG) < 1 or len(strR) < 1):
			return 0.0

		row = len(strR)
		col = len(strG)
		strR = "^"+strR
		strG = "^"+strG

		matrix = []
		path = []
		for i in range(row+1):
			matrix.append([0]*(col+1))
			path.append(["N"]*(col+1))
	# print_matrix(matrix)
		indelValue = -1
		matchValue = 2
		for i in range(1,row+1):
			for j in range(1,col+1):
				# penalty map
				from_left = matrix[i][j-1] + indelValue
				from_top = matrix[i-1][j] + indelValue
				if strR[i] == strG[j]:
					from_diag = matrix[i-1][j-1] + matchValue
				else:
					from_diag = matrix[i-1][j-1] + indelValue

				matrix[i][j] = max(from_left, from_top, from_diag)
				if matrix[i][j] < 0:
					matrix[i][j] = 0
		max_sim = 0
		for i in range(1, row+1):
			if(max_sim < matrix[i][col]):
				max_sim = matrix[i][col]
		#print(len(strG))
		return float(max_sim)/float(len(strG) - 1)/2.0
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
            max_len = max({len(seq1),len(seq2)})
            min_len = min({len(seq1),len(seq2)})
            return float(max_len - thisrow[len(seq2) - 1])/float(min_len)

class StringMatcher:
    threshold = .5
    method = "smith"

    def __init__(self, method, thr):
        self.threshold = thr
        self.method = method
        #self.setup_config(config_path)

    def sim_metric(self, test_word, keyword):
        if self.method == "smith":
            sw = SmithWaterman()
            return sw.measure(test_word, keyword)
        elif self.method == "jaro":
            return jaro.metric_jaro_winkler(test_word, keyword)
        else:
            return self.levenshtein_sim(keyword, test_word)

    def sim_measure(self, test_words, ref_words):
        outer_arr = []
        for in_word in test_words:
            inner_arr = []
            for ref_word in ref_words:
                sim = self.sim_metric(in_word, ref_word)
                if sim < self.threshold:
                    sim = 0.0
                inner_arr.append(1.0 - sim)
            outer_arr.append(inner_arr)
            if len(outer_arr) == 0:
                return 0.0
        m = munkres.Munkres()
        indexes = m.compute(outer_arr)
        values = []
        for row, column in indexes:
            values.append(1.0 - outer_arr[row][column]) #go back to similarity
        return sum(values)/(len(test_words)+len(ref_words)-len(values)+values.count(0.0))

class HybridJaccard:
    jaccardThr = 0.3
    jaccardMethod = "smith"
    inputPath = ""
    inputTokenizer = ","
    outputFilter = "count"
    numCand = 1
    scoreThr = 0.3
    
    def __init__(self, config_path = "config.json"):
        with open(config_path) as data_file:
            data = json.load(data_file)

        self.jaccardThr = float(data["method_config"]["parameters"]["threshold"])
        self.jaccardMethod = data["method_config"]["partial_method"]
        self.inputPath = data["input_config"]["path"]
        self.inputTokenizer = data["input_config"]["tokenizer"]
        self.outputFilter = data["output_config"]["filter"]
        self.numCand = int(data["output_config"]["num_candidates"])
        self.scoreThr = float(data["output_config"]["score_threshold"])
        
    def generateJson(self, key, matches, candidates_name):
        jsonObj = {"uri": str(key), candidates_name:[]}
        for match in matches:
            # print "Match:", type(match), ", ", match
            candidate = {}
            if type(match) is list or type(match) is dict or type(match) is tuple:
                candidate["uri"] = str(match[0])
                candidate["score"] = match[1]
            else:
                candidate["uri"] = str(match)
            jsonObj[candidates_name].append(candidate)
        return jsonObj

    def generateCandidates(self):
        sm = StringMatcher(self.jaccardMethod, self.jaccardThr)
        candidate_fields = []
        outputFile = open(sys.argv[2],"w")
        decoder = json.JSONDecoder()
        with open(sys.argv[1]) as inputFile:
            for jsonObj in inputFile:
                data = json.loads(jsonObj)
                queryString = data["name"]
                queryFields = queryString.split(self.inputTokenizer)
                candidates = []
                for i in range(len(data["candidates"])):
                    if isinstance(data["candidates"][i]["name"], list):
                        for candValue in data["candidates"][i]["name"]:
                            candidateFields = re.split(self.inputTokenizer, candValue)
                            print candidateFields
                            score = sm.sim_measure(candidateFields, queryFields)
                            candidates.append([data["candidates"][i]["uri"].encode('ascii', 'ignore'), score])
                            del candidateFields[:]
                    else:
                        candidateFields = re.split(self.inputTokenizer, data["candidates"][i]["name"])
                        print candidateFields
                        score = sm.sim_measure(candidateFields, queryFields)
                        candidates.append([data["candidates"][i]["uri"].encode('ascii', 'ignore'), score])
                        del candidateFields[:]
                candidates.sort(key=lambda tup: tup[1])

                if self.outputFilter == "count":
                    candidates = candidates[:self.numCand]
                else:
                    candidates = [t for t in candidates if t[1] > self.scoreThr]
                print >>outputFile, str(json.dumps(self.generateJson(data["uri"],
                                                     candidates, "matches")))
                del candidates[:]
                #print str(data["query_location"]["uri"]) + "\t" + temp_id + "\t" + str(max_score)
                #print temp_name + " " + str(max_score)
                #print "--------------------------------"
                #except:
                    

hj = HybridJaccard("config.json")
hj.generateCandidates()