# DEXTER
This repository contains the source code of DEXTER, a system to automatically extract Gene-Disease Associations from biomedical abstracts. The work was original presented in the paper by Gupta et al. [*'DEXTER: Disease-Expression Relation Extraction from Text'*](https://pubmed.ncbi.nlm.nih.gov/29860481/). This repository contains a reproduced version of the system described in the above mentioned paper. 

**Contents**

* [System Requirements](#system-requirements)
* [Data format](#data-format)
* [Running DEXTER](#running-dexter)

## System Requirements

DEXTER is based on the [SpaCy library](https://spacy.io/) so make sure to [install](https://spacy.io/usage) it before running the code.

## Data Format

DEXTER takes as input a csv file with the following column names:
- PMID: PubMed ID of the abstract.
- Sentence: sentence to be parsed.

The output is a csv files with the following columns:
- PMID: PubMed ID of the abstract where the sentence is contained.
- geneMen: gene mentioned in the sentence.
- geneID: identifier of the gene mentioned in the sentence.
- DOID: DOID of the associated disease.
- DOID_Name: name of the associated disease.
- DiseaseMention: associated disease mention in the sentence
- DiseaseDetectedFrom: location of the disease (i.e, Sentence_ARG, Title, Sentence)
- ExpressionLevel: gene expression level (UP/DOWN)
- SentenceType: sentence type (TypeA/TypeB)
- Sample1: Compared Entity 1 extracted by the RE module
- Sample2: Compared Entity 2 extracted by the RE module (NA for TypeB sentences)
- Sentence: sentence text.

## Running DEXTER

To execute the code run:
```
python dexter_pipeline.py [path_to_input_file] [path_to_output_file]
```

If you wish to run the code on the original data, unzip the data folder and run:
```
python dexter_pipeline.py ../data/input/DEXTER_DATA.csv ../data/output/[filename].csv
```
