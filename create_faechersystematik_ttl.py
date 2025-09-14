import pandas as pd
import rdflib.term
from rdflib import Graph, Literal, RDF, URIRef, Namespace, DCTERMS
import logging


def extract_preflabel_translations(current_ttl):
    pref_label_dict_list = []
    deprecated_broader_list = []
    g_old = Graph()
    g_old.parse(current_ttl, format="ttl")
    qres = g_old.query(
        """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

        SELECT DISTINCT ?label_en ?label_uk ?concept ?broader
           WHERE {
               ?concept a skos:Concept ;
                    skos:prefLabel ?label ;
                    skos:prefLabel ?label_en ; 
                    skos:prefLabel ?label_uk . 

                FILTER(lang(?label_en)="en") 
                FILTER(lang(?label_uk)="uk")
            OPTIONAL
            {?concept   owl:deprecated true ;
                    skos:broader ?broader .
            }
           }""")
    for row in qres:
        notation = row.concept.replace("https://w3id.org/kim/hochschulfaechersystematik/n", "")
        pref_label_dict = {notation: {"label_en": f"{row.label_en}", "label_uk": f"{row.label_uk}"}}
        pref_label_dict_list.append(pref_label_dict)
        if row.broader is not None:
            deprecated_broader = {f"{row.broader.replace("https://w3id.org/kim/hochschulfaechersystematik/n", "")}": notation}
            deprecated_broader_list.append(deprecated_broader)
    return pref_label_dict_list, deprecated_broader_list

def extract_deprecated_notations(current_ttl):
    g_old = Graph()
    g_old.parse(current_ttl, format="ttl")
    qres = g_old.query(
        """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX :  <https://w3id.org/kim/hochschulfaechersystematik/>

        SELECT *
           WHERE { 
                    ?concept   owl:deprecated true ; 
                    ?p ?o . 
           }""")

    return qres

def add_pref_labels_lang(level_dict_list, current_pref_labels_dict):
    for idx, i in enumerate(level_dict_list):
        notation = level_dict_list[idx]['uri']
        if notation in current_pref_labels_dict:
            for k,v in current_pref_labels_dict.items():
                pref_label_en = v.get("label_en")
                pref_label_uk = v.get("label_uk")
                level_dict_list[idx].update({"label_en": pref_label_en, "label_uk": pref_label_uk})
    return level_dict_list

def extract_narrower(dict_list):
    narrower_dict = {}
    for dict in dict_list:
        notation_broader_level = dict["broader"]
        if notation_broader_level in narrower_dict:
            narrower_dict[notation_broader_level].append(dict["uri"])
        else:
            narrower_dict[notation_broader_level]=[dict["uri"]]
    return narrower_dict

def add_narrower(dict_list_broader, dict_list_narrower, deprecated_broader_list):
    narrower = extract_narrower(dict_list_narrower)
    for item in deprecated_broader_list:
        for k,v in item.items():
            if k in narrower:
                narrower[k].append(v)
    for d in dict_list_broader:
        if d["uri"] in narrower:
            d.update(narrower=narrower[d["uri"]])

def copy_notation(dictionary):
    dictionary["uri"] = dictionary["notation"]

# extract translations of prefLabels
current_hfs_file = "https://github.com/dini-ag-kim/hochschulfaechersystematik/blob/master/hochschulfaechersystematik.ttl?raw=true"
lang_preflabel_list, deprecated_broader_list = extract_preflabel_translations(current_hfs_file)
hfs_deprecated_notations = extract_deprecated_notations(current_hfs_file)

# extract hfs data from destatis files
url_1st_level = "https://github.com/dini-ag-kim/destatis-schluesseltabellen/blob/main/studierende/Faechergruppe.csv?raw=true"
url_2nd_level = "https://raw.githubusercontent.com/dini-ag-kim/destatis-schluesseltabellen/refs/heads/main/studierende/Studienbereich.csv"
url_3rd_level = "https://github.com/dini-ag-kim/destatis-schluesseltabellen/blob/main/studierende/Studienfach.csv?raw=true"

df_1st_level = pd.read_csv(url_1st_level, encoding="utf-8", sep=';', quotechar='"', skiprows=1 , header=None, engine ='python', dtype=str, usecols=[0, 2], names=["notation", "label"])
df_2nd_level = pd.read_csv(url_2nd_level, encoding="utf-8", sep=';', quotechar='"', skiprows=1 , header=None, engine ='python', dtype=str, usecols=[0, 2, 5], names=["notation", "label", "broader"])
df_3rd_level = pd.read_csv(url_3rd_level, encoding="utf-8", sep=';', quotechar='"', skiprows=1, header=None, engine ='python', dtype=str, usecols=[0, 2, 5], names=["notation", "label", "broader"])

# remove duplicate notation 10 from top level
# remove unused notations
df_1st_level = df_1st_level[~df_1st_level["notation"].isin(["10", "15", "20", "90"])]

# remove subordinate notations from 2nd and 3rd level
df_2nd_level = df_2nd_level[df_2nd_level.broader !="10"]
df_2nd_level = df_2nd_level[df_2nd_level.broader !="90"]
df_3rd_level = df_3rd_level[df_3rd_level.broader !="83"]

df_1st_level['notation'] = df_1st_level['notation'].str.lstrip("0")
df_2nd_level['broader'] = df_2nd_level['broader'].str.lstrip("0")

# add new column "uri" based on "notation" to enable the URI to be assigned independently of the notations
copy_notation(df_1st_level)
copy_notation(df_2nd_level)
copy_notation(df_3rd_level)

# change uri "128" > "0128"
df_3rd_level["uri"] = df_3rd_level["uri"].replace("128", "0128")

dict_1st_level = df_1st_level.to_dict("records")
dict_2nd_level = df_2nd_level.to_dict("records")
dict_3rd_level = df_3rd_level.to_dict("records")

add_narrower(dict_1st_level, dict_2nd_level, deprecated_broader_list)
add_narrower(dict_2nd_level, dict_3rd_level, deprecated_broader_list)


# add translations from current hfs to dictionaries
for lang_preflabel_dict in lang_preflabel_list:
    dict_1st_level = add_pref_labels_lang(dict_1st_level, lang_preflabel_dict)
    dict_2nd_level = add_pref_labels_lang(dict_2nd_level, lang_preflabel_dict)
    dict_3rd_level = add_pref_labels_lang(dict_3rd_level, lang_preflabel_dict)

g = Graph()

# namespaces
base = 'https://w3id.org/kim/hochschulfaechersystematik/'
vann = Namespace('http://purl.org/vocab/vann/')
dct = Namespace('http://purl.org/dc/terms/')
owl = Namespace('http://www.w3.org/2002/07/owl#')
skos = Namespace('http://www.w3.org/2004/02/skos/core#')
schema = Namespace('https://schema.org/')
g.bind("schema", schema)
g = Graph(base=base)

#conceptScheme
g.add((URIRef('scheme'), RDF['type'], skos['ConceptScheme']))
g.add((URIRef('scheme'), dct['title'], Literal('Destatis-Systematik der Fächergruppen, Studienbereiche und Studienfächer', lang='de')))
g.add((URIRef('scheme'), dct['alternative'], Literal('Hochschulfächersystematik', lang='de')))
g.add((URIRef('scheme'), dct['description'], Literal('Diese SKOS-Klassifikation basiert auf der Destatis-[\"Systematik der Fächergruppen, Studienbereiche und Studienfächer\"](https://bartoc.org/en/node/18919).', lang='de')))
g.add((URIRef('scheme'), dct['issued'], Literal('2019-12-11')))
g.add((URIRef('scheme'), dct['license'], rdflib.term.URIRef('http://dcat-ap.de/def/licenses/other-closed')))
g.add((URIRef('scheme'), dct['publisher'], rdflib.term.URIRef('https://oerworldmap.org/resource/urn:uuid:fd06253e-fe67-4910-b923-51db9d27e59f')))
g.add((URIRef('scheme'), dct['source'], rdflib.term.URIRef('https://www.destatis.de/DE/Methoden/Klassifikationen/Bildung/studenten-pruefungsstatistik.html')))
g.add((URIRef('scheme'), vann['preferredNamespaceUri'], Literal('https://w3id.org/kim/hochschulfaechersystematik/')))
g.add((URIRef('scheme'), vann['preferredNamespacePrefix'], Literal('hfs')))
g.add((URIRef('scheme'), schema['isBasedOn'], rdflib.term.URIRef('http://bartoc.org/node/18919')))

for idx, i in enumerate(dict_1st_level):
    top_level = dict_1st_level[idx]['uri']
    g.add((URIRef('n%s' % top_level), RDF['type'], skos['Concept']))
    g.add((URIRef('n%s' % top_level), skos['topConceptOf'], (URIRef('scheme'))))
    g.add((URIRef('n%s' % top_level), skos['prefLabel'], Literal(dict_1st_level[idx]['label'], lang='de')))
    if dict_1st_level[idx].get('narrower'):
        for item in dict_1st_level[idx]['narrower']:
            g.add((URIRef('n%s' % top_level), skos['narrower'], (URIRef('n%s' % item))))
    if dict_1st_level[idx].get('label_en'):
        g.add((URIRef('n%s' % top_level), skos['prefLabel'], Literal(dict_1st_level[idx]['label_en'], lang='en')))
        g.add((URIRef('n%s' % top_level), skos['prefLabel'], Literal(dict_1st_level[idx]['label_uk'], lang='uk')))
        g.add((URIRef('n%s' % top_level), skos['notation'], Literal(dict_1st_level[idx]['notation'])))
    else:
        logging.warning("No translation for {notation}".format(notation=top_level))
    g.add((URIRef('scheme'), skos['hasTopConcept'], (URIRef('n%s' % top_level))))

for idx_2, i_2 in enumerate(dict_2nd_level):
    level_2_uri = dict_2nd_level[idx_2]['uri']
    g.add((URIRef('n%s' % level_2_uri), RDF['type'], skos['Concept']))
    g.add((URIRef('n%s' % level_2_uri), skos['prefLabel'], Literal(dict_2nd_level[idx_2]['label'], lang='de')))
    if dict_2nd_level[idx_2].get('label_en'):
        g.add((URIRef('n%s' % level_2_uri), skos['prefLabel'], Literal(dict_2nd_level[idx_2]['label_en'], lang='en')))
        g.add((URIRef('n%s' % level_2_uri), skos['prefLabel'], Literal(dict_2nd_level[idx_2]['label_uk'], lang='uk')))
    else:
        logging.warning("No translation for {notation}".format(notation=level_2_uri))
    g.add((URIRef('n%s' % level_2_uri), skos['broader'], (URIRef('n%s' % dict_2nd_level[idx_2]['broader']))))
    if dict_2nd_level[idx_2].get('narrower'):
        for item in dict_2nd_level[idx_2]['narrower']:
            g.add((URIRef('n%s' % level_2_uri), skos['narrower'], (URIRef('n%s' % item))))
    g.add((URIRef('n%s' % level_2_uri), skos['notation'], Literal(dict_2nd_level[idx_2]['notation'])))
    g.add((URIRef('n%s' % level_2_uri), skos['inScheme'], (URIRef('scheme'))))

for idx_3, i_3 in enumerate(dict_3rd_level):
    level_3_uri = dict_3rd_level[idx_3]['uri']
    g.add((URIRef('n%s' % level_3_uri), RDF['type'], skos['Concept']))
    g.add((URIRef('n%s' % level_3_uri), skos['prefLabel'], Literal(dict_3rd_level[idx_3]['label'], lang='de')))
    if dict_3rd_level[idx_3].get('label_en'):
        g.add((URIRef('n%s' % level_3_uri), skos['prefLabel'], Literal(dict_3rd_level[idx_3]['label_en'], lang='en')))
        g.add((URIRef('n%s' % level_3_uri), skos['prefLabel'], Literal(dict_3rd_level[idx_3]['label_uk'], lang='uk')))
    else:
        logging.warning("No translation for {notation}".format(notation=level_3_uri))
    g.add((URIRef('n%s' % level_3_uri), skos['notation'], Literal(dict_3rd_level[idx_3]['notation'])))
    g.add((URIRef('n%s' % level_3_uri), skos['inScheme'], (URIRef('scheme'))))
    g.add((URIRef('n%s' % level_3_uri), skos['broader'], (URIRef('n%s' % dict_3rd_level[idx_3]['broader']))))

g.add((URIRef('n0'), RDF['type'], skos['Concept']))
g.add((URIRef('n0'), skos['prefLabel'], Literal('Fachübergreifend', lang='de')))
g.add((URIRef('n0'), skos['prefLabel'], Literal('Interdisciplinary', lang='en')))
g.add((URIRef('n0'), skos['prefLabel'], Literal('Міждисциплінарний', lang='uk')))
g.add((URIRef('n0'), skos['topConceptOf'], (URIRef('scheme'))))
g.add((URIRef('n0'), skos['notation'], Literal('0')))
g.add((URIRef('scheme'), skos['hasTopConcept'], (URIRef('n0'))))
g.bind("dct", DCTERMS)

# add deprecated notations
for row in hfs_deprecated_notations:
    g.add((URIRef(row.concept), row.p, row.o))

g.serialize('hochschulfaechersystematik.ttl', format='turtle', encoding='utf-8')
