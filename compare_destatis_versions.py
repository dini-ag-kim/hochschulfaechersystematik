from rdflib import Graph
import csv

current_classification = "https://raw.githubusercontent.com/dini-ag-kim/hochschulfaechersystematik/master/hochschulfaechersystematik.ttl"
new_classification = "hochschulfaechersystematik.ttl" # path of the newly created version

data_old = Graph().parse(current_classification, format="ttl")
data_new = Graph().parse(new_classification, format="ttl")

query = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    
    SELECT ?notation ?prefLabel
    WHERE {
        ?s skos:notation ?notation.
        ?s skos:prefLabel ?prefLabel . 
        FILTER langmatches(lang(?prefLabel) , 'de')
    }
"""

new_notation_output = open("new_notations.csv", "w")
changed_label_output = open("changed_labels.csv", "w")
deprecated_notation_output = open("deprecated_notations.csv", "w")

old_dict = {}
for r in data_old.query(query):
    old_dict.update({str(r['notation']): str(r['prefLabel'])})

for r in data_new.query(query):
    new_notation = str(r['notation'])
    new_preflabel = str(r['prefLabel'])
    if new_notation in old_dict.keys():
        if new_preflabel != old_dict[new_notation]:
            changed_label_output.write(new_notation + ";" + new_preflabel + ";Old label: " + old_dict[new_notation] + "\n" )
        del old_dict[new_notation]
    else:
        new_notation_output.write(new_notation + ";" + new_preflabel + "\n")

for k, v in old_dict.items():
    csv.writer(deprecated_notation_output, delimiter=";").writerow([k,v])