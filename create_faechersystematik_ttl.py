import pandas as pd
import rdflib.term
from rdflib import Graph, Literal, RDF, URIRef, Namespace

url_1st_level = "https://github.com/dini-ag-kim/destatis-schluesseltabellen/blob/main/studierende/Faechergruppe.csv?raw=true"
url_2nd_level = "https://github.com/dini-ag-kim/destatis-schluesseltabellen/raw/main/studierende/STB.csv?raw=true"
url_3rd_level = "https://github.com/dini-ag-kim/destatis-schluesseltabellen/blob/main/studierende/Studienfach.csv?raw=true"

df_1st_level = pd.read_csv(url_1st_level, encoding="ISO-8859-1", sep=';', quotechar='"', header=None, engine ='python', dtype=str, usecols=[0, 2], names=["notation", "label"])
df_2nd_level = pd.read_csv(url_2nd_level, encoding="ISO-8859-1", sep=';', quotechar='"', header=None, engine ='python', dtype=str, usecols=[0, 2, 3], names=["notation", "label", "broader"])
df_3rd_level = pd.read_csv(url_3rd_level, encoding="ISO-8859-1", sep=';', quotechar='"', header=None, engine ='python', dtype=str, usecols=[0, 2, 3], names=["notation", "label", "broader"])

dict_1st_level = df_1st_level.to_dict("records")
dict_2nd_level = df_2nd_level.to_dict("records")
dict_3rd_level = df_3rd_level.to_dict("records")

g = Graph()

vann = Namespace('http://purl.org/vocab/vann/')
dct = Namespace('http://purl.org/dc/terms/')
owl = Namespace('http://www.w3.org/2002/07/owl#')
skos = Namespace('http://www.w3.org/2004/02/skos/core#')
schema = Namespace('https://schema.org/')
g.bind("schema", schema)

#conceptScheme
g.add((URIRef('scheme'), RDF['type'], skos['ConceptScheme']))
g.add((URIRef('scheme'), dct['title'], Literal('Destatis-Systematik der Fächergruppen, Studienbereiche und Studienfächer', lang='de')))
g.add((URIRef('scheme'), dct['alternative'], Literal('Hochschulfächersystematik', lang='de')))
g.add((URIRef('scheme'), dct['description'], Literal('Diese SKOS-Klassifikation basiert auf der Destatis-[\"Systematik der Fächergruppen, Studienbereiche und Studienfächer\"](https://bartoc.org/en/node/18919).', lang='de')))
g.add((URIRef('scheme'), dct['issued'], Literal('2019-12-11')))
g.add((URIRef('scheme'), dct['publisher'], rdflib.term.URIRef('https://oerworldmap.org/resource/urn:uuid:fd06253e-fe67-4910-b923-51db9d27e59f')))
g.add((URIRef('scheme'), vann['preferredNamespaceUri'], rdflib.term.URIRef('https://w3id.org/kim/hochschulfaechersystematik/')))
g.add((URIRef('scheme'), schema['isBasedOn'], rdflib.term.URIRef('http://bartoc.org/node/18919')))


for idx, i in enumerate(dict_1st_level):
    top_level = dict_1st_level[idx]['notation'].lstrip("0")
    g.add((URIRef('n%s' % top_level), RDF['type'], skos['Concept']))
    g.add((URIRef('n%s' % top_level), skos['topConceptOf'], (URIRef('scheme'))))
    g.add((URIRef('n%s' % top_level), skos['prefLabel'], Literal(dict_1st_level[idx]['label'], lang='de')))
    g.add((URIRef('n%s' % top_level), skos['notation'], Literal(top_level)))
    for idx_2, i_2 in enumerate(dict_2nd_level):
        if dict_2nd_level[idx_2]['broader'].lstrip("0") == top_level:
            level_2_notation = dict_2nd_level[idx_2]['notation']
            g.add((URIRef('n%s' % level_2_notation), RDF['type'], skos['Concept']))
            g.add((URIRef('n%s' % level_2_notation), skos['prefLabel'], Literal(dict_2nd_level[idx_2]['label'], lang='de')))
            g.add((URIRef('n%s' % level_2_notation), skos['broader'], (URIRef('n%s' % dict_2nd_level[idx_2]['broader'].lstrip('0')))))
            g.add((URIRef('n%s' % level_2_notation), skos['notation'], Literal(level_2_notation)))
            g.add((URIRef('n%s' % level_2_notation), skos['inScheme'], (URIRef('scheme'))))
            for idx_3, i_3 in enumerate(dict_3rd_level):
                if dict_3rd_level[idx_3]['broader'] == level_2_notation:
                    level_3_notation = dict_3rd_level[idx_3]['notation']
                    g.add((URIRef('n%s' % level_3_notation), RDF['type'], skos['Concept']))
                    g.add((URIRef('n%s' % level_3_notation), skos['prefLabel'],Literal(dict_3rd_level[idx_3]['label'], lang='de')))
                    g.add((URIRef('n%s' % level_3_notation), skos['notation'], Literal(level_3_notation)))
                    g.add((URIRef('n%s' % level_3_notation), skos['inScheme'], (URIRef('scheme'))))
                    g.add((URIRef('n%s' % level_3_notation), skos['broader'], (URIRef('n%s' % dict_3rd_level[idx_3]['broader'].lstrip('0')))))

g.add((URIRef('n0'), RDF['type'], skos['Concept']))
g.add((URIRef('n0'), skos['prefLabel'], Literal('Fachübergreifend', lang='de')))
g.add((URIRef('n0'), skos['notation'], Literal('0')))
g.add((URIRef('n0'), skos['topConceptOf'], (URIRef('scheme'))))

g.serialize('hochschulfaechersystematik.ttl', format='turtle')

