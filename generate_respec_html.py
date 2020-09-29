#!/usr/bin/env python3
#author: Harshvardhan J. Pandit 

'''Generates ReSpec documentation for DPV using RDF and SPARQL'''

# The vocabularies are modular

from rdflib import Graph, Namespace
from rdflib import URIRef
from rdflib import RDF, RDFS
from rdflib.namespace import NamespaceManager
from rdflib.namespace import XSD
from rdflib.term import Literal, URIRef
from rdflib.plugins.sparql import prepareQuery

from rdform import DataGraph, RDFS_Resource

g = Graph()
g.load('core.ttl', format='turtle')

G = DataGraph()
G.load(g)
G.graph.ns = { k:v for k,v in G.graph.namespaces() }

SPARQL_QUERY_CLASS = '''
    SELECT ?iri ?title
    WHERE {
        ?iri a rdfs:Class .
        ?iri rdfs:label ?title .
    }
    '''
SPARQL_QUERY_PROPERTIES = '''
    SELECT ?iri ?title
    WHERE {
        ?iri a rdf:Property .
        ?iri rdfs:label ?title .
    }
    '''

def prefix_this(item):
    # DEBUG(f'item: {item} type: {type(item)}')
    if type(item) is RDFS_Resource:
        item = item.iri
    elif type(item) is URIRef:
        item = str(item)
    if type(item) is str and item.startswith('http'):
        iri = URIRef(item).n3(G.graph.namespace_manager)
    else:
        iri = item
    if iri.count('_') > 0:
        iri = iri.split('_', 1)[1]
    # DEBUG(f'prefixed {item} to: {iri}')
    return iri

def fragment_this(item):
    if '#' not in item:
        return item
    return item.split('#')[-1]


# results = G.graph.query(SPARQL_QUERY)
# for iri, title, _ in results:
#     print(prefix_this(iri))


# generate HTML
from jinja2 import FileSystemLoader, Environment
JINAJ2_TEMPLATE_VARS = {
    'RDF_DESC_PROP': ('rdf_type', 'schema_name', 'schema_url'),
    'prefix_this': prefix_this,
}
JINJA2_TESTS = {
    'RDFS_Resource': lambda x: type(x) is RDFS_Resource,
    'BNode': lambda x: x.startswith('u'),
}
JINJA2_FILTERS = {
    'fragment_this': fragment_this,
}

classes = G.get_instances_of('rdfs_Class')
properties = G.get_instances_of('rdf_Property')

template_loader = FileSystemLoader(searchpath='.')
template_env = Environment(
    loader=template_loader, 
    autoescape=True, trim_blocks=True, lstrip_blocks=True)
template_env.tests.update(JINJA2_TESTS)
template_env.filters.update(JINJA2_FILTERS)
template = template_env.get_template('template_base.jinja2')
with open('index.html', 'w+') as fd:
    fd.write(template.render(
        classes=classes, properties=properties, **JINAJ2_TEMPLATE_VARS))

print('--- END ---')