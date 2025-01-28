import re
from rdflib import Graph

def format_list_items(unformatted_list):
    formatted_list = [i + "\n\n" for i in unformatted_list]
    return formatted_list


with open("hochschulfaechersystematik.ttl", "r") as rdf_file:
    base = 'https://w3id.org/kim/hochschulfaechersystematik/'
    g = Graph(base=base)
    g.parse(rdf_file, format="ttl")
    g.serialize('hochschulfaechersystematik.ttl', format='turtle')


with open("hochschulfaechersystematik.ttl", "r") as f:
    data = f.read()
    sort_block = re.findall(r'^[<:]n.*? \.$', data, flags=re.MULTILINE | re.DOTALL)
    prefix_matches = re.findall(r'^@.+\.$\n', data, flags=re.MULTILINE)
    other_matches = re.findall(r'^(?!<n|:n| |@|\n).*? \.$', data, flags=re.MULTILINE | re.DOTALL)
    list_sort = sorted(sort_block, key=lambda x: (len(x.split(' ')[0]), x))
    prefix_matches.insert(len(prefix_matches), "\n")
    result = prefix_matches + format_list_items(other_matches) + format_list_items(list_sort)

    with open("hochschulfaechersystematik.ttl", "w") as outfile:
        outfile.write("".join(result))

