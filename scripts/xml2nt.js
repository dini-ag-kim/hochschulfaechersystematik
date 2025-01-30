var xpath = require('xpath')
var dom = require('xmldom').DOMParser
var fs = require('fs')

var xml = fs.readFileSync('fachgebiete.xml', 'utf8')

var doc = new dom().parseFromString(xml)
var nodes = xpath.select('/valuespaces/valuespace[@property="ccm:taxonid"]/key', doc)
var topConcepts = []
var childConcepts = []

ID_PREFIX = 'n'
nodes.forEach(node => {
  const id = `${ID_PREFIX}${node.textContent}`
  const notation = node.textContent
  const label = node.getAttribute('cap')
  const parent = `${ID_PREFIX}${node.getAttribute('parent')}`
  parent !== ID_PREFIX
    ? childConcepts.push({id, parent, label, notation })
    : topConcepts.push({id, label, notation})
})

console.log(`
@base <http://w3id.org/class/hochschulfaechersystematik/> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix dct: <http://purl.org/dc/terms/> .

<scheme> a skos:ConceptScheme ;
  dct:title "Destatis-Systematik der Fächergruppen, Studienbereiche und Studienfächer"@de ;
  skos:hasTopConcept ${topConcepts.map(concept => '<' + concept.id + '>').join(', ')} .
`)

topConcepts.forEach(concept => console.log(`
<${concept.id}> a skos:Concept ;
  skos:prefLabel "${concept.label}"@de ;
  ${
    childConcepts.some(child => child.parent === concept.id) &&
    'skos:narrower ' + childConcepts.filter(child => child.parent === concept.id).map(child => '<' + child.id + '>').join(', ') + ';'
    || ''
  }
  skos:notation "${concept.notation}" ;
  skos:topConceptOf <scheme> .
`))

childConcepts.forEach(concept => console.log(`
<${concept.id}> a skos:Concept ;
  skos:prefLabel "${concept.label}"@de ;
  ${
    childConcepts.some(child => child.parent === concept.id) &&
    'skos:narrower ' + childConcepts.filter(child => child.parent === concept.id).map(child => '<' + child.id + '>').join(', ') + ';'
    || ''
  }
  skos:broader <${concept.parent}> ;
  skos:notation "${concept.notation}" ;
  skos:inScheme <scheme> .
`))
