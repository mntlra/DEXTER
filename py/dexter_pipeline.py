# Testing Class
import csv
import time
import pandas as pd
import sys
import spacy

from expand_entities import expand_entity_mentions
from input_handling import preprocess_sentence
from exceptions import MatchNotFound, InvalidArgument, GeneNotFound, MistypedExpressionLevel, DiseaseNotFound
from relation_extraction import relation_extraction
from entity_detection import get_miRNA, get_annotations_list_pmids, retokenize_miRNA
from argument_filtering_extraction import check_components, extract_gene, normalize_expression_level, extract_disease, \
    get_comparison, check_entity


# Extracting input and output file from arguments
if len(sys.argv) < 3:
    print('Usage: path_to_input_file path_to_output_file')
    raise Exception
input_file = sys.argv[1]
print(f'Reading from {sys.argv[1]}')
output_file = sys.argv[2]

# Trigger lists to filter-out sentences
trigs = ["high", "low", "increase", "decrease", "express", "silence", "reduce", "elevate", "change", "regulate",
                 "overexpresse", "over-expresse", "over-expressed", "underexpresse", "under-expressed", "unchanged", "up-regulate", "upregulate", "down-regulate",
                 "downregulate", "elevated", "normalize", 'underexpresse', 'under-expressed', 'amplify',
         'find', 'note', 'detect', 'observe', 'discover', 'occurred', 'occur', 'appear', 'identify', 'show',
         'prove', 'know', 'report', 'suggest', 'document', 'demonstrate', 'tend', 'amplified/over-expressed',
         'coexpressed', 'coexpresse', 'downexpressed', 'downexpresse', 'lower-expressed', 'lower-expresse', 'validate']
pmids = []
check = {}
print('Getting all the annotations')
start_time = time.time()
df = pd.read_csv(input_file, index_col=False)
tot_docs = 0
i = 1
for index, row in df.iterrows():
    try:
        tmp = check[str(row['PMID'])]
    except KeyError:
        tot_docs += 1
        pmids.append(str(row['PMID']))
        check[str(row['PMID'])] = 1

annotations, general_annotations = get_annotations_list_pmids(pmids)

print("--- %s seconds ---" % (time.time() - start_time))
# Measuring time execution without considering loading of the abstract
start_time = time.time()
print("--- Spacy pipeline initialization ---")
# Initialize the pipeline
nlp_biore = spacy.load("en_core_sci_sm")
# Add entity expansion custom component
nlp_biore.add_pipe("expand_entity_mentions", name="Entity Expansion", after="ner")

print("--- Start parsing ---")

# output csv file
header = ['PMID', 'geneMen', 'geneID', 'DOID', 'DOID_Name', 'DiseaseMention', 'DiseaseDetectedFrom', 'ExpressionLevel', 'SentenceType',
          'Sample1', 'Sample2', 'Sentence']
rows = []

for index, row in df.iterrows():
    pmid = str(row['PMID'])
    input_doc = preprocess_sentence(str(row['Sentence']))
    doc = nlp_biore(input_doc)
    print('sentence:', doc.text)
    retokenize_miRNA(doc)
    # filter out sentences that do not contain type-A or type-B triggers
    if [t for t in doc if t.lemma_ in trigs]:

        correct_matches = []
        potential_failures = []
        print("Relation Extraction Module for sentence:", doc.text)
        print("PMID:", pmid)
        try:
            # Relation Extraction Module
            cmp_list, sent_type, rules = relation_extraction(doc, nlp_biore)
            # Gene and Disease mentions
            try:
                genes = annotations[pmid]['genes']
                diseases = annotations[pmid]['diseases']
                diseases_title = annotations[pmid]['diseases_title']
                title = annotations[pmid]['title']
                abstract = nlp_biore(annotations[pmid]['abstract'])
            except KeyError:
                genes = {}
                diseases = {}
                diseases_title = {}
                title = None
                abstract = None
            print('Abstract title:', title)
            print("sent_type:", sent_type)
            for components in cmp_list:
                print(components)
                cmp_type = sent_type
                # microRNA mentions
                micro_rnas = get_miRNA(doc)
                # --- Argument Filtering ---
                try:
                    res_check = check_components(components, genes, diseases, micro_rnas, general_annotations)
                    if res_check:
                        if sent_type == 'TypeA' and components['compared_entity_1'].text == components['compared_entity_2'].text:
                            if not correct_matches:
                                cmp_type = 'TypeB'
                            else:
                                continue
                        elif sent_type == 'TypeA':
                            try:
                                tmp = check_entity(components['compared_entity_2'], diseases, general_annotations)
                            except InvalidArgument:
                                if not correct_matches:
                                    cmp_type = 'TypeB'
                                else:
                                    continue
                        print("Extracting gene")
                        # --- Gene/miRNA Extraction ---
                        try:
                            gene_mentions = extract_gene(doc, components['compared_aspect'], genes, micro_rnas, general_annotations)
                            print("gene mentions:", gene_mentions)
                        except GeneNotFound:
                            print('Failed to extract gene/miRNA from Compared Aspect or Expressed Aspect')
                            continue
                        # --- Expression Level Normalization ---
                        try:
                            norm_level = normalize_expression_level(doc, components)
                            print("normalized level:", norm_level)
                        except MistypedExpressionLevel:
                            print('Failed to Normalize the scale indicator')
                            continue
                        # --- Disease Extraction ---
                        try:
                            doid, doid_name, mention, disease_location = extract_disease(components, cmp_type, diseases, diseases_title, general_annotations, title, abstract)
                            print("extracted disease:", doid_name, 'id:', doid, 'location:', disease_location)
                        except DiseaseNotFound:
                            print('Failed to extract the disease')
                            continue
                        # --- Comparison Flag ---
                        flag = get_comparison(components, cmp_type)
                        print("Flag comparison:", flag)
                        print("Components extracted correctly")
                        # Extracting gene_id
                        for gene in gene_mentions:
                            if gene[1] == 'gene':
                                try:
                                    ncbi_id = genes[gene[0]]
                                except KeyError:
                                    # Check general_annotations
                                    try:
                                        ncbi_id = general_annotations[gene[0]]
                                    except KeyError:
                                        ncbi_id = 'NA'
                            else:
                                ncbi_id = 'NA'
                            # --- Saving the results ---
                            if cmp_type == 'TypeA':
                                potential_row = [pmid, gene[0], ncbi_id, doid, doid_name, mention,
                                                     disease_location, norm_level, cmp_type,
                                                     components['compared_entity_1'].text,
                                                     components['compared_entity_2'].text,
                                                     doc.text]
                            elif cmp_type == 'TypeB':
                                potential_row = [pmid, gene[0], ncbi_id, doid, doid_name, mention,
                                                     disease_location, norm_level, cmp_type,
                                                     components['compared_entity_1'].text, None,
                                                     doc.text]
                            # Check for duplicates
                            info = [pmid, gene, norm_level, cmp_type, doc.text]
                            if info not in correct_matches:
                                correct_matches.append(info)
                                rows.append(potential_row)
                except InvalidArgument:
                    print('Arguments found by RE module do not meet the type constraints')
                    continue
        except MatchNotFound:
            print('RE module failed to retrieve the components')
            continue

print('--- Saving the results ---')
tot_matched = 0
pmids_matched = {}
# writing to csv file
with open(output_file, 'w') as csvfile:
    # creating a csv writer object
    csvwriter = csv.writer(csvfile)
    # writing the fields
    csvwriter.writerow(header)
    for r in rows:
        if r[0] not in pmids_matched.keys():
            tot_matched += 1
            pmids_matched[r[0]] = {}
            pmids_matched[r[0]]['sentences'] = [r[9]]
            pmids_matched[r[0]]['rows'] = [r]
            # writing the data rows
            csvwriter.writerow(r)
        elif r not in pmids_matched[r[0]]['rows']:
            if r[9] not in pmids_matched[r[0]]['sentences']:
                pmids_matched[r[0]]['sentences'].append(r[9])
            tot_matched += 1
            pmids_matched[r[0]]['rows'].append(r)
            # writing the data rows
            csvwriter.writerow(r)

print("--- %s seconds ---" % (time.time() - start_time))
print('tot docs to parse: ', tot_docs)
print('Documents correctly parsed: ', len(pmids_matched.keys()))
