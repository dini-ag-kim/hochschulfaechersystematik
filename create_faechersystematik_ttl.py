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
        notation = level_dict_list[idx]['notation']
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
            narrower_dict[notation_broader_level].append(dict["notation"])
        else:
            narrower_dict[notation_broader_level]=[dict["notation"]]
    return narrower_dict

def add_narrower(dict_list_broader, dict_list_narrower, deprecated_broader_list):
    narrower = extract_narrower(dict_list_narrower)
    for item in deprecated_broader_list:
        for k,v in item.items():
            if k in narrower:
                narrower[k].append(v)
    for d in dict_list_broader:
        if d["notation"] in narrower:
            d.update(narrower=narrower[d["notation"]])


# extract translations of prefLabels
current_hfs_file = "https://github.com/dini-ag-kim/hochschulfaechersystematik/blob/master/hochschulfaechersystematik.ttl?raw=true"
lang_preflabel_list, deprecated_broader_list = extract_preflabel_translations(current_hfs_file)
hfs_deprecated_notations = extract_deprecated_notations(current_hfs_file)

# extract hfs data from destatis files
url_1st_level = "https://github.com/dini-ag-kim/destatis-schluesseltabellen/blob/main/studierende/Faechergruppe.csv?raw=true"
url_2nd_level = "https://github.com/dini-ag-kim/destatis-schluesseltabellen/raw/main/studierende/STB.csv?raw=true"
url_3rd_level = "https://github.com/dini-ag-kim/destatis-schluesseltabellen/blob/main/studierende/Studienfach.csv?raw=true"

df_1st_level = pd.read_csv(url_1st_level, encoding="ISO-8859-1", sep=';', quotechar='"', header=None, engine ='python', dtype=str, usecols=[0, 2], names=["notation", "label"])
df_2nd_level = pd.read_csv(url_2nd_level, encoding="ISO-8859-1", sep=';', quotechar='"', header=None, engine ='python', dtype=str, usecols=[0, 2, 3], names=["notation", "label", "broader"])
df_3rd_level = pd.read_csv(url_3rd_level, encoding="ISO-8859-1", sep=';', quotechar='"', header=None, engine ='python', dtype=str, usecols=[0, 2, 3], names=["notation", "label", "broader"])

# remove duplicate, unused notation 10 from top level
# remove unused notations 15 & 20
df_1st_level = df_1st_level[~df_1st_level["notation"].isin(["10", "15", "20"])]

# remove of "10" subordinate notations from 2nd and 3rd level
df_2nd_level = df_2nd_level[df_2nd_level.broader !="10"]
df_3rd_level = df_3rd_level[df_3rd_level.broader !="83"]

df_1st_level['notation'] = df_1st_level['notation'].str.lstrip("0")
df_2nd_level['broader'] = df_2nd_level['broader'].str.lstrip("0")

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
g.add((URIRef('scheme'), dct['publisher'], rdflib.term.URIRef('https://oerworldmap.org/resource/urn:uuid:fd06253e-fe67-4910-b923-51db9d27e59f')))
g.add((URIRef('scheme'), vann['preferredNamespaceUri'], Literal('https://w3id.org/kim/hochschulfaechersystematik/')))
g.add((URIRef('scheme'), vann['preferredNamespacePrefix'], Literal('hfs')))
g.add((URIRef('scheme'), schema['isBasedOn'], rdflib.term.URIRef('http://bartoc.org/node/18919')))


for idx, i in enumerate(dict_1st_level):
    top_level = dict_1st_level[idx]['notation']
    g.add((URIRef('n%s' % top_level), RDF['type'], skos['Concept']))
    g.add((URIRef('n%s' % top_level), skos['topConceptOf'], (URIRef('scheme'))))
    g.add((URIRef('n%s' % top_level), skos['prefLabel'], Literal(dict_1st_level[idx]['label'], lang='de')))
    for item in dict_1st_level[idx]['narrower']:
        g.add((URIRef('n%s' % top_level), skos['narrower'], (URIRef('n%s' % item))))
    if dict_1st_level[idx].get('label_en'):
        g.add((URIRef('n%s' % top_level), skos['prefLabel'], Literal(dict_1st_level[idx]['label_en'], lang='en')))
        g.add((URIRef('n%s' % top_level), skos['prefLabel'], Literal(dict_1st_level[idx]['label_uk'], lang='uk')))
        g.add((URIRef('n%s' % top_level), skos['notation'], Literal(top_level)))
    else:
        logging.warning("No translation for {notation}".format(notation=top_level))
    g.add((URIRef('scheme'), skos['hasTopConcept'], (URIRef('n%s' % top_level))))
    for idx_2, i_2 in enumerate(dict_2nd_level):
        if dict_2nd_level[idx_2]['broader'] == top_level:
            level_2_notation = dict_2nd_level[idx_2]['notation']
            g.add((URIRef('n%s' % level_2_notation), RDF['type'], skos['Concept']))
            g.add((URIRef('n%s' % level_2_notation), skos['prefLabel'], Literal(dict_2nd_level[idx_2]['label'], lang='de')))
            if dict_2nd_level[idx_2].get('label_en'):
                g.add((URIRef('n%s' % level_2_notation), skos['prefLabel'], Literal(dict_2nd_level[idx_2]['label_en'], lang='en')))
                g.add((URIRef('n%s' % level_2_notation), skos['prefLabel'], Literal(dict_2nd_level[idx_2]['label_uk'], lang='uk')))
            else:
                logging.warning("No translation for {notation}".format(notation=level_2_notation))
            g.add((URIRef('n%s' % level_2_notation), skos['broader'], (URIRef('n%s' % dict_2nd_level[idx_2]['broader']))))
            for item in dict_2nd_level[idx_2]['narrower']:
                g.add((URIRef('n%s' % level_2_notation), skos['narrower'], (URIRef('n%s' % item))))
            g.add((URIRef('n%s' % level_2_notation), skos['notation'], Literal(level_2_notation)))
            g.add((URIRef('n%s' % level_2_notation), skos['inScheme'], (URIRef('scheme'))))
            for idx_3, i_3 in enumerate(dict_3rd_level):
                if dict_3rd_level[idx_3]['broader'] == level_2_notation:
                    level_3_notation = dict_3rd_level[idx_3]['notation']
                    g.add((URIRef('n%s' % level_3_notation), RDF['type'], skos['Concept']))
                    g.add((URIRef('n%s' % level_3_notation), skos['prefLabel'],Literal(dict_3rd_level[idx_3]['label'], lang='de')))
                    if dict_3rd_level[idx_3].get('label_en'):
                        g.add((URIRef('n%s' % level_3_notation), skos['prefLabel'],Literal(dict_3rd_level[idx_3]['label_en'], lang='en')))
                        g.add((URIRef('n%s' % level_3_notation), skos['prefLabel'],Literal(dict_3rd_level[idx_3]['label_uk'], lang='uk')))
                    else:
                        logging.warning("No translation for {notation}".format(notation=level_3_notation))
                    g.add((URIRef('n%s' % level_3_notation), skos['notation'], Literal(level_3_notation)))
                    g.add((URIRef('n%s' % level_3_notation), skos['inScheme'], (URIRef('scheme'))))
                    g.add((URIRef('n%s' % level_3_notation), skos['broader'], (URIRef('n%s' % dict_3rd_level[idx_3]['broader']))))

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

g.serialize('hochschulfaechersystematik.ttl', format='turtle')