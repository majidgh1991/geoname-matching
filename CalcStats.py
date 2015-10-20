import sys
import ast

garbage_count = 0

partial_city_count = 0
partial_state_count = 0
partial_country_count = 0

cmp_city_count = 0
cmp_state_count = 0
cmp_country_count = 0

typo_city_count = 0
typo_state_count = 0
typo_country_count = 0

missing_country = 0
missing_state = 0
missing_city = 0

multiple_city = 0

with open(sys.argv[1]) as input_file:
    for line in input_file:
        mylist = ast.literal_eval(str(line))
        flag_country = False
        flag_state = False
        flag_city = 0
        for set in mylist:
            if "city_cmp" in set:
                cmp_city_count += 1
                flag_city += 1
            elif "city_partial" in set:
                partial_city_count += 1
                flag_city += 1
            elif "city_typo" in set:
                typo_city_count += 1
                flag_city += 1
            elif "state_cmp" in set:
                cmp_state_count += 1
                flag_state = True
            elif "state_partial" in set:
                partial_state_count += 1
                flag_state = True
            elif "country_cmp" in set:
                cmp_country_count += 1
                flag_country = True
            elif "country_partial" in set:
                partial_country_count += 1
                flag_country = True
            else:
                garbage_count += 1

        if flag_country is False:
            missing_country += 1
        if flag_state is False:
            missing_state += 1
        if flag_city == 0:
            # print line
            missing_city += 1
        if flag_city > 1:
            multiple_city += 1
print missing_city
print multiple_city
print missing_country
print missing_state
