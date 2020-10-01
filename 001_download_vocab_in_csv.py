#!/usr/bin/env python3
#author: Harshvardhan J. Pandit

'''Downloads the DPV spreadsheets in CSV form'''

# Google Export link
GOOGLE_EXPORT_LINK = (
    'https://docs.google.com/spreadsheets/d/'
    '%s/gviz/tq?tqx=out:csv&sheet=%s')

# The document *must* be publicly viewable (minimum permissions)
# The document ID is found within the URL
DPV_DOCUMENT_ID = '1bChnl0JcVNPFLkYAq59531-q2xZuhk9CQIKKWyRoSB4'
# The sheet names are assumed to be valid IRIs
# If they are not, escape them for IRI/HTML representation
DPV_SHEETS = (
    'BaseOntology',
    'BaseOntology_properties',
    'TechnicalOrganisationalMeasure',
    'TechnicalOrganisationalMeasure_properties',
    'PersonalDataCategory',
    'Processing',
    'Purpose',
    'Purpose_properties',
    'Entities',
    'LegalBasis',
    'Consent',
    'Consent_properties',
    )

from urllib import request


def download_csv(document_id, sheet_name, save_path='./vocab_csv'):
    '''Download the sheet and save to given path'''
    url = GOOGLE_EXPORT_LINK % (document_id, sheet_name)
    print(f'Downloading {sheet_name}...', end='')
    request.urlretrieve(url, f'{save_path}/{sheet_name}.csv')
    print('DONE')


if __name__ == '__main__':
    for sheet in DPV_SHEETS:
        download_csv(DPV_DOCUMENT_ID, sheet)
