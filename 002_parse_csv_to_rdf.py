#!/usr/bin/env python3
#author: Harshvardhan J. Pandit

'''Take CSV and generate RDF from it'''

########################################
# How to read and understand this file #
# 1. Start from the end of the file
# 2. This script reads CSV files explicitly declared
# 3. It generates RDF terms using rdflib for Classes and Properties
# 4. It writes those terms to a file - one per each module
# 5. It combines all written files into dpv.ttl and dpv-gdpr.ttl

# CSV FILES are in IMPORT_CSV_PATH
# RDF FILES are written to EXPORT_TTL_PATH
########################################

IMPORT_CSV_PATH = './vocab_csv'
EXPORT_TTL_PATH = './vocab_rdf'

import csv
from collections import namedtuple

from rdflib import Graph, Namespace
from rdflib.namespace import XSD
from rdflib import RDF, RDFS, OWL
from rdflib.term import Literal, URIRef, BNode

import logging
# logging configuration for debugging to console
logging.basicConfig(
    level=logging.DEBUG, format='%(levelname)s - %(funcName)s :: %(lineno)d - %(message)s')
DEBUG = logging.debug
INFO = logging.info

DCT = Namespace('http://purl.org/dc/terms/')
DPV = Namespace('http://www.w3.org/ns/dpv#')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
ODRL = Namespace('http://www.w3.org/ns/odrl/2/')
OWL = Namespace('http://www.w3.org/2002/07/owl#')
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
SPL = Namespace('http://www.specialprivacy.eu/langs/usage-policy#')
SVD = Namespace('http://www.specialprivacy.eu/vocabs/data#')
SVDU = Namespace('http://www.specialprivacy.eu/vocabs/duration#')
SVL = Namespace('http://www.specialprivacy.eu/vocabs/locations#')
SVPR = Namespace('http://www.specialprivacy.eu/vocabs/processing#')
SVPU = Namespace('http://www.specialprivacy.eu/vocabs/purposes#')
SVR = Namespace('http://www.specialprivacy.eu/vocabs/recipients')
SW = Namespace('http://www.w3.org/2003/06/sw-vocab-status/ns#')

NAMESPACES = {
    'dct': DCT,
    'dpv': DPV,
    'foaf': FOAF,
    'odrl': ODRL,
    'owl': OWL,
    'skos': SKOS,
    'spl': SPL,
    'svd': SVD,
    'svdu': SVDU,
    'svl': SVL,
    'svpr': SVPR,
    'svpu': SVPU,
    'svr': SVR,
    'sw': SW,
}

DPV_Class = namedtuple('DPV_Class', [
    'term', 'rdfs_label', 'dct_description', 'rdfs_subclassof', 
    'rdfs_seealso', 'rdfs_comment', 'rdfs_isdefinedby', 
    'dct_created', 'sw_termstatus', 'dct_creator', 
    'dct_dateaccepted', 'resolution'])

DPV_Property = namedtuple('DPV_Property', [
    'term', 'rdfs_label', 'dct_description', 
    'rdfs_domain', 'rdfs_range', 'rdfs_subpropertyof',
    'rdfs_seealso', 'rdfs_comment', 'rdfs_isdefinedby', 
    'dct_created', 'sw_termstatus', 'dct_creator', 
    'dct_dateaccepted', 'resolution'])


def extract_terms_from_csv(filepath, Class):
    '''extracts data from file.csv and creates instances of Class
    returns list of Class instances'''
    # this is a hack to get parseable number of fields from CSV
    # it relies on the internal data structure of a namedtuple
    attributes = Class.__dict__
    attributes = len(attributes['_fields'])
    with open(filepath) as fd:
        csvreader = csv.reader(fd)
        next(csvreader)
        terms = []
        for row in csvreader:
            row = row[:attributes]
            terms.append(Class(*row))

    return terms


def add_common_triples_for_all_terms(term, graph):
    '''Adds triples for any term to graph
    Common triples are those shared by Class and Property
    terms: data structure of term; is object with attributes
    graph: rdflib graph
    returns: None'''
    # rdfs:label
    graph.add((DPV[f'{term.term}'], RDFS.label, Literal(term.rdfs_label, lang='en')))
    # dct:description
    graph.add((DPV[f'{term.term}'], DCT.description, Literal(term.dct_description, lang='en')))
    # rdfs:seeAlso
    if term.rdfs_seealso:
        links = [l.strip() for l in term.rdfs_seealso.split(',')]
        for link in links:
            if link.startswith('http'):
                graph.add((DPV[f'{term.term}'], RDFS.seeAlso, URIRef(link)))
            else:
                graph.add((DPV[f'{term.term}'], RDFS.seeAlso, Literal(link, datatype=XSD.string)))
    # rdfs:comment
    if term.rdfs_comment:
        graph.add((DPV[f'{term.term}'], RDFS.comment, Literal(term.rdfs_comment, lang='en')))
    # rdfs:isDefinedBy
    if term.rdfs_isdefinedby:
        links = [l.strip() for l in term.rdfs_isdefinedby.split(',')]
        for link in links:
            if link.startswith('http'):
                graph.add((DPV[f'{term.term}'], RDFS.isDefinedBy, URIRef(link)))
            else:
                graph.add((DPV[f'{term.term}'], RDFS.isDefinedBy, Literal(link, datatype=XSD.string)))
    # dct:created
    graph.add((DPV[f'{term.term}'], DCT.created, Literal(term.dct_created, datatype=XSD.date)))
    # sw:term_status
    graph.add((DPV[f'{term.term}'], SW.term_status, Literal(term.sw_termstatus, lang='en')))
    # dct:creator
    if term.dct_creator:
        authors = [a.strip() for a in term.dct_creator.split(',')]
        for author in authors:
            graph.add((DPV[f'{term.term}'], DCT.creator, Literal(author, datatype=XSD.string)))
    # dct:date-accepted
    if term.dct_dateaccepted:
        graph.add((DPV[f'{term.term}'], DCT['date-accepted'], Literal(term.dct_dateaccepted, datatype=XSD.date)))
    # resolution
        # do nothing

    return None


def add_triples_for_classes(classes, graph):
    '''Adds triples for classes to graph
    classes: list of CSV data rows
    graph: rdflib graph
    returns: None'''

    for cls in classes:
        # only record accepted classes
        if cls.sw_termstatus != "accepted":
            continue
        # rdf:type
        graph.add((DPV[f'{cls.term}'], RDF.type, RDFS.Class))
        # rdfs:subClassOf
        if cls.rdfs_subclassof:
            parents = [p.strip() for p in cls.rdfs_subclassof.split(',')]
            for parent in parents:
                if parent.startswith('http'):
                    graph.add((DPV[f'{cls.term}'], RDFS.subClassOf, URIRef(parent)))
                else:
                    graph.add((DPV[f'{cls.term}'], RDFS.subClassOf, DPV[f'{parent}']))
        
        add_common_triples_for_all_terms(cls, graph)

    return None
        

def add_triples_for_properties(properties, graph):
    '''Adds triples for properties to graph
    properties: list of CSV data rows
    graph: rdflib graph
    returns: None'''

    for prop in properties:
        # only record accepted classes
        if prop.sw_termstatus != "accepted":
            continue
        # rdf:type
        graph.add((DPV[f'{prop.term}'], RDF.type, RDF.Property))
        # rdfs:domain
        if prop.rdfs_domain:
            graph.add((DPV[f'{prop.term}'], RDFS.domain, DPV[f'{prop.rdfs_domain}']))
        # rdfs:range
        if prop.rdfs_range:
            graph.add((DPV[f'{prop.term}'], RDFS.range, DPV[f'{prop.rdfs_range}']))
        # rdfs:subPropertyOf
        if prop.rdfs_subpropertyof:
            parents = [p.strip() for p in prop.rdfs_subpropertyof.split(',')]
            for parent in parents:
                if parent.startswith('http'):
                    graph.add((DPV[f'{prop.term}'], RDFS.subPropertyOf, URIRef(parent)))
                else:
                    graph.add((DPV[f'{prop.term}'], RDFS.subPropertyOf, DPV[f'{parent}']))
        add_common_triples_for_all_terms(prop, graph)


# #############################################################################

# DPV #

DPV_CSV_FILES = {
    'base': {
        'classes': f'{IMPORT_CSV_PATH}/BaseOntology.csv',
        'properties': f'{IMPORT_CSV_PATH}/BaseOntology_properties.csv',
        },
    'personal_data_categories': {
        'classes': f'{IMPORT_CSV_PATH}/PersonalDataCategory.csv',
        },
    'purposes': {
        'classes': f'{IMPORT_CSV_PATH}/Purpose.csv',
        },
    'processing': {
        'classes': f'{IMPORT_CSV_PATH}/Processing.csv'
        },
    'technical_organisational_measures': {
        'classes': f'{IMPORT_CSV_PATH}/TechnicalOrganisationalMeasure.csv',
        'properties': f'{IMPORT_CSV_PATH}/TechnicalOrganisationalMeasure_properties.csv',
        },
    'entities': {
        'classes': f'{IMPORT_CSV_PATH}/Entities.csv',
        },
    'consent': {
        'classes': f'{IMPORT_CSV_PATH}/Consent.csv',
        'properties': f'{IMPORT_CSV_PATH}/Consent_properties.csv',
        },
    }

# this graph will get written to dpv.ttl
DPV_GRAPH = Graph()

for name, module in DPV_CSV_FILES.items():
    graph = Graph()
    for prefix, namespace in NAMESPACES.items():
        graph.namespace_manager.bind(prefix, namespace)
    if 'classes' in module:
        classes = extract_terms_from_csv(module['classes'], DPV_Class)
        DEBUG(f'there are {len(classes)} classes in {name}')
        add_triples_for_classes(classes, graph)
    if 'properties' in module:
        properties = extract_terms_from_csv(module['properties'], DPV_Property)
        DEBUG(f'there are {len(properties)} properties in {name}')
        add_triples_for_properties(properties, graph)
    graph.serialize(f'{EXPORT_TTL_PATH}/{name}.ttl', format='turtle')
    INFO(f'wrote {EXPORT_TTL_PATH}/{name}.ttl')
    DPV_GRAPH += graph

# TODO: Also add information about the ontology itself
# this could be a simple file import
for prefix, namespace in NAMESPACES.items():
        DPV_GRAPH.namespace_manager.bind(prefix, namespace)
DPV_GRAPH.serialize(f'{EXPORT_TTL_PATH}/dpv.ttl', format='turtle')

# DPV-GDPR #
# dpv-gdpr is the exact same as dpv in terms of requirements and structure
# except that the namespace is different
# so instead of rewriting the entire code again for dpv-gdpr,
# here I become lazy and instead change the DPV namespace to DPV-GDPR

NAMESPACES['dpv'] = Namespace('https://www.w3.org/ns/dpv#')
NAMESPACES['dpv-gdpr'] = Namespace('http://www.w3.org/ns/dpv-gdpr#')
DPV = NAMESPACES['dpv-gdpr']

label = 'dpv-gdpr'
classes = f'{IMPORT_CSV_PATH}/LegalBasis.csv'

graph = Graph()
for prefix, namespace in NAMESPACES.items():
    graph.namespace_manager.bind(prefix, namespace)
classes = extract_terms_from_csv(classes, DPV_Class)
add_triples_for_classes(classes, graph)
graph.serialize(f'{EXPORT_TTL_PATH}/{label}.ttl', format='turtle')

# #############################################################################
