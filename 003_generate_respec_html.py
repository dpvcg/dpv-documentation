#!/usr/bin/env python3
#author: Harshvardhan J. Pandit 

'''Generates ReSpec documentation for DPV using RDF and SPARQL'''

# The vocabularies are modular

IMPORT_TTL_PATH = './vocab_rdf'
EXPORT_HTML_PATH = './vocab_html'

from rdflib import Graph, Namespace
from rdflib import URIRef
from rdflib import RDF, RDFS
from rdflib.namespace import NamespaceManager
from rdflib.namespace import XSD
from rdflib.term import Literal, URIRef
from rdflib.plugins.sparql import prepareQuery

from rdform import DataGraph, RDFS_Resource

# UGLY UGLY globals
G = None


TEMPLATE_DATA = {}


def load_data(label, filepath):
    global G
    g = Graph()
    g.load(filepath, format='turtle')
    G = DataGraph()
    G.load(g)
    G.graph.ns = { k:v for k,v in G.graph.namespaces() }
    classes = G.get_instances_of('rdfs_Class')
    # for c in classes:
    #     print(c, c.__dict__['metadata'].keys())
    TEMPLATE_DATA[f'{label}_classes'] = classes
    TEMPLATE_DATA[f'{label}_properties'] = G.get_instances_of('rdf_Property')


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


# LOAD DATA
load_data('core', f'{IMPORT_TTL_PATH}/base.ttl')
load_data('personaldata', f'{IMPORT_TTL_PATH}/personal_data_categories.ttl')
load_data('purpose', f'{IMPORT_TTL_PATH}/purposes.ttl')
load_data('processing', f'{IMPORT_TTL_PATH}/processing.ttl')
load_data('technical_organisational_measures', f'{IMPORT_TTL_PATH}/technical_organisational_measures.ttl')
load_data('entities', f'{IMPORT_TTL_PATH}/entities.ttl')
load_data('consent', f'{IMPORT_TTL_PATH}/consent.ttl')


# generate HTML
from jinja2 import FileSystemLoader, Environment
JINAJ2_TEMPLATE_VARS = {
    'RDF_DESC_PROP': ('rdf_type', 'schema_name', 'schema_url'),
    
}
JINJA2_TESTS = {
    'RDFS_Resource': lambda x: type(x) is RDFS_Resource,
    'BNode': lambda x: x.startswith('u'),
}
JINJA2_FILTERS = {
    'fragment_this': fragment_this,
    'prefix_this': prefix_this,
}

template_loader = FileSystemLoader(searchpath='./jinja2_resources')
template_env = Environment(
    loader=template_loader, 
    autoescape=True, trim_blocks=True, lstrip_blocks=True)
template_env.tests.update(JINJA2_TESTS)
template_env.filters.update(JINJA2_FILTERS)
template = template_env.get_template('template_base.jinja2')
with open(f'{EXPORT_HTML_PATH}/index.html', 'w+') as fd:
    fd.write(template.render(
        **TEMPLATE_DATA, **JINAJ2_TEMPLATE_VARS))

print('--- END ---')