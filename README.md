# Documentation generator for DPV vocabularies

Downloads the CSV data for DPV and other vocabularies (such as DPV-GDPR), converts it to RDF serialisations, and generates HTML documentation using the W3C ReSpec template.

Requires: `python3` and modules `rdflib`, `rdflib-jsonld`, `jinja2`

The Data Privacy Vocabulary (DPV) is available at https://www.w3.org/ns/dpv and its repository is at https://github.com/dpvcg/dpv. 

> NOTE: This repository only holds the scripts required to generate the documentation. This is NOT the repository for the vocabulary itself. This is to keep the vocabulary and documentation in separate repositories.

## Quick Summary

There are 3 scripts to executre for each of the three tasks.

`./001_download_vocab_in_csv.py` will download the CSV data from a Google Sheets document and store it in the `vocab_csv` path specified. The outcome will be a CSV file for each sheet.

`./002_parse_csv_to_rdf.py` will create RDF serialisations for DPV using data from CSV. It will create different serialisation files for each 'module' and also for DPV combined.

`./003_generate_respec_html.py` will generate HTML documentation for DPV from RDF.


## How everything works

### Downloading CSV data

This uses the Google Sheet export link to download the sheet data in CSV form. Needs specifying the document ID in `DPV_DOCUMENT_ID` variable and listing the sheet name(s) in `DPV_SHEETS`. The default save path for CSV is `vocab_csv`.

### Converting to RDF

This uses `rdflib` to generate the RDF data from CSV. It uses `DPV_CSV_FILES` to retrieve classes and properties from the CSV and render them in RDF serialisations. Namespaces are manually represented in the top of the document and are automatically handled in text as URI references. Serialisations to be produced are registered in `RDF_SERIALIZATIONS` variable.

The variables for CSV inputs and RDF outputs are:

* `IMPORT_CSV_PATH` defines where the CSV files are stored, with default value `./vocab_csv`
* `EXPORT_DPV_PATH` defines where the DPV rdf files are stored, with default value `./vocab_dpv`
* `EXPORT_DPV_MODULE_PATH` defines where the DPV module files are stored, with default value `./vocab_dpv/modules`
* `EXPORT_DPV_GDPR_PATH`  defines where the DPV-GDPR files are stored, with default value `./vocab_dpv_gdpr`

There are three main classes responsible for generation of metadata:

* `add_common_triples_for_all_terms` will add common metadata for each term, such as label, description, author, and so on
* `add_triples_for_classes` will add metadata for classes such as subclass
* `add_triples_for_properties` will add metadata for properties such as domain, range, sub-property

### Generating HTML documentation

This uses `jinja2` to render the HTML file from a template. The data is loaded using a module called `rdform` which is meant to provide ORM features and convenience features over RDF data. 

The variables for RDF inputs and HTML outputs are:

* `IMPORT_DPV_MODULES_PATH` defines where the RDF for DPV modules are loaded from, with default value `./vocab_dpv/modules`
* `IMPORT_DPV_GDPR_PATH` defines where the RDF for DPV-GDPR module is loaded from,  with default value `./vocab_dpv_gdpr`
* `EXPORT_HTML_PATH` defines where the output HTML is stored, with default value `./docs`

The general flow of steps in the script is along the following lines:

1. Load RDF instances from a module file with the `load_data` function. 
2. This creates a RDF graph using `rdflib` and extracts classes and properties from it in separate variables as `{module}_classes` and `{module}_properties`
3. Create HTML using a `jinja2` template, which is located in `jinja2_resources`. The tempalte for dpv is `template_dpv.jinja2`.
4. The template uses a macro to repeat the same table and metadata records for each module and term. The macro is defined in `macro_term_table.jinja2`. The template file itself contains the other information such as headlines and paragraphs.

## FAQ

1. Fixing an error in the vocabulary terms i.e. term label, property, annotation --> Make the changes in the Google Sheet, and run scripts to download CSV, parse RDF, and generate HTML
2. Fixing an error in serialisation e.g. rdf:Property is defined as rdfs:Propety --> Make the changes in the `002` script for generating RDF, and generate HTML
3. Changing content in HTML documentation e.g. change motivation paragraph --> Make the changes in the relevant `template` and generate HTML