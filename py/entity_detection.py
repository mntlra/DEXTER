import json
import os
import re
from pathlib import Path
import requests
import spacy
from spacy.tokens import Span
from exceptions import PubMedIDNotFound

# Triggers to detect if a phrase is of type 'Expression'
expression_trigs = ['over-expression', 'under-expression', 'expression', 'up-regulation', 'down-regulation',
                    'overexpression', 'underexpression', 'upregulation', 'downregulation', 'level', 'levels',
                    'knockdown', 'elevation', 'production', 'silencing', 'loss', 'gain', 'depletion', 'absence',
                    'abundance', 'concentration', 'expressions', 'mRNA', 'plasma', 'protein', 'proteins', 'gene',
                    'genes', 'antigen', 'suppressor', 'receptor']

# Triggers to detect if a phrase is of type 'Disease-Disease Sample'
disease_sample_trigs = ['tissue', 'cell', 'patient', 'sample', 'tumor', 'cancer', 'carcinoma', 'cell line', 'cell-line',
                        'group', 'blood', 'sera', 'serum', 'fluid', 'subset', 'case', 'men', 'women', 'man', 'woman',
                        'control', 'normal', 'parenchyma', 'healthy', 'levels', 'stage', 'stages', 'individual',
                        'individuals', 'disease', 'culture', 'cultivate', 'metastatic', 'malignant', 'conditions',
                        'condition', 'human', 'humans', 'cell-type', 'thymocyte', 'meningioma']

# Regular Expression to retrieve miRNA mentions
mi_regex = '(([a-z]{3,4}-)?(mi|Mi|MI)(RNA|R|r)s?(((([0-9]|[a-z])+)-[^ ,.]*)|((([0-9]|[a-z])+)|(-[^ ,.]*))))' + '|' + '([M,m]icro[-]?RNA(s?)-([0-9]|[a-z])+)'

# Dictionary for mapping MESH IDs to DOIDs
mesh_to_doid_json = str(Path(os.path.abspath(os.getcwd())).absolute()) + "/data/input/" + 'mesh_to_doid.json'
with open(mesh_to_doid_json, 'r') as udf:
    mesh_to_doid = json.loads(udf.read())


def get_annotations(pmid):
    """
    Retrieves gene and disease mentions in the abstract and disease mentions in the title from PubTator.

    :param pmid: (String) PubMed ID of the abstract

    :return: list of genes and diseases mentioned in the abstract and the disease mentions in the title
    :return: title as a string if show_title=True
    """
    abstract_text, title_text = None, None
    genes, diseases, diseases_title = {}, {}, {}
    response = requests.get(
        "https://www.ncbi.nlm.nih.gov/research/pubtator-api/publications/export/biocjson?pmids=" + pmid)
    if response.status_code == 404:
        return abstract_text, genes, diseases, diseases_title, title_text
    for passage in response.json()["passages"]:
        # Retrieving abstract text and annotations
        if passage['infons']['type'] == 'abstract':
            # Retrieving abstract text
            abstract_text = passage['text']
            # Retrieving annotations
            for annotation in passage['annotations']:
                # Retrieving gene annotations
                if annotation['infons']['type'] == 'Gene':
                    try:
                        genes[annotation['text']] = annotation['infons'][
                            'identifier']
                    except KeyError:
                        # Check if it is a gene without ncbi gene ID or if it is a miRNA
                        if re.search(mi_regex, annotation['text']):
                            # if microRNA
                            genes[annotation['text']] = 'micro-RNA'
                        else:
                            genes[annotation['text']] = 'ncbi gene_id not found'
                # Retrieving disease annotations
                elif annotation['infons']['type'] == 'Disease':
                    try:
                        if annotation['infons']['identifier'] is None:
                            continue
                        try:
                            # Map MESH IDs to DOIDs
                            diseases[annotation['text']] = mesh_to_doid[annotation['infons']['identifier']]
                        except KeyError:
                            continue
                    except KeyError:
                        continue
        # Retrieving title text and disease annotations
        elif passage['infons']['type'] == 'title':
            # Retrieving title text
            title_text = passage['text']
            # Retrieve disease annotations
            for annotation in passage['annotations']:
                if annotation['infons']['type'] == 'Disease':
                    try:
                        if annotation['infons']['identifier'] is None:
                            continue
                        try:
                            # Map MESH IDs to DOIDs
                            diseases_title[annotation['text']] = mesh_to_doid[
                                annotation['infons']['identifier']]
                        except KeyError:
                            continue
                    except KeyError:
                        continue

    return abstract_text, genes, diseases, diseases_title, title_text


def get_annotations_list_pmids(pmids):
    """
    Retrieves gene and disease mentions in the abstract and disease mentions in the title from PubTator given a
    list of pmids.

    :param pmids: List(String) List of PubMed IDs

    :return: dictionary containing the gene and disease annotations for each pmid.
             {'pmid': {'genes': {'mention': 'ncbi gene id'}, 'diseases': {'mention': 'doid'}, 'diseases_title':{'mention': 'doid'}}}
    :return: dictionary of all annotations for the list of ids.
            {'genes': {'mention': 'ncbi gene id'}, 'diseases': {'mention': 'doid'}}
    """
    # Storing pmids in list of maximum 1000 elements to request annotations
    list_pmids = [[]]
    count = 0
    i = 0
    check = {}
    for pm_id in pmids:
        if pm_id not in check.keys():
            count += 1
            list_pmids[i].append(str(pm_id))
            check[str(pm_id)] = 1
        if count > 0 and count % 1000 == 0:
            i += 1
            list_pmids.append([])
    # dict of PubTator annotations based on pmid
    # ({'id': {'abstract':,'genes':{'text': id},'diseases':{'text': id},'diseases_title':{'text':i d}}})
    annotations = {}
    # dict of all annotations retrieved by PubTator for the list of pmids
    # ({'genes':{'id':text},'diseases':{'id':text}})
    general_annotations = {'genes': {}, 'diseases': {}}
    count = 0
    for list_ids in list_pmids:
        count += 1
        payload = {"pmids": list_ids}
        print("*** Parsing", str(count), 'list ***')
        response = requests.post(
            "https://www.ncbi.nlm.nih.gov/research/pubtator-api/publications/export/biocjson", json=payload)
        for r in response.iter_lines():
            res = json.loads(r.decode('utf-8'))
            # Initialization of each dictionary-key value
            annotations[res['id']] = {'abstract': {}, 'genes': {}, 'diseases': {}, 'diseases_title': {}}
            for passage in res["passages"]:
                # Retrieving abstract text and annotations
                if passage['infons']['type'] == 'abstract':
                    # Retrieving abstract text
                    annotations[res['id']]['abstract'] = passage['text']
                    # Retrieving annotations
                    for annotation in passage['annotations']:
                        # Retrieving gene annotations
                        if annotation['infons']['type'] == 'Gene':
                            try:
                                annotations[res['id']]['genes'][annotation['text']] = annotation['infons'][
                                    'identifier']
                            except KeyError:
                                # Check if it is a gene without ncbi gene ID or if it is a miRNA
                                if re.search(mi_regex, annotation['text']):
                                    # if microRNA
                                    annotations[res['id']]['genes'][annotation['text']] = 'micro-RNA'
                                else:
                                    annotations[res['id']]['genes'][annotation['text']] = 'ncbi gene_id not found'
                        # Retrieving disease annotations
                        elif annotation['infons']['type'] == 'Disease':
                            try:
                                if annotation['infons']['identifier'] is None:
                                    continue
                                try:
                                    # Map MESH IDs to DOIDs
                                    annotations[res['id']]['diseases'][annotation['text']] = mesh_to_doid[annotation['infons']['identifier']]
                                except KeyError:
                                    continue
                            except KeyError:
                                continue
                # Retrieving title text and disease annotations
                elif passage['infons']['type'] == 'title':
                    # Retrieving title text
                    annotations[res['id']]['title'] = passage['text']
                    # Retrieve disease annotations
                    for annotation in passage['annotations']:
                        if annotation['infons']['type'] == 'Disease':
                            try:
                                if annotation['infons']['identifier'] is None:
                                    continue
                                try:
                                    # Map MESH IDs to DOIDs
                                    annotations[res['id']]['diseases'][annotation['text']] = mesh_to_doid[
                                        annotation['infons']['identifier']]
                                except KeyError:
                                    continue
                            except KeyError:
                                continue
            # Store mentions in general_annotations if not already present
            general_annotations = populate_dict(annotations[res['id']], general_annotations)
    return annotations, general_annotations


def populate_dict(pmid_annotation, general_annotations):
    """
    Populate general_annotations with mentions retrieved for the specific pmid, if not already present.

    :param pmid_annotations: dictionary of mentions retrieved by PubTator for a specific pmid
    :param general_annotations: dictionary of general mentions
    
    :return general_annotations: dictionary of general mentions updated accordingly
    """
    # Store gene mentions in general_annotations if not already present
    for gene in pmid_annotation['genes'].keys():
        try:
            # Check if gene mention already present
            tmp = general_annotations['genes'][gene]
        except KeyError:
            # If not insert it, if any annotation is present
            try:
                general_annotations['genes'][gene] = pmid_annotation['genes'][gene]
            except KeyError:
                continue
    # Store disease mentions in abstract in general_annotations if not already present
    for disease in pmid_annotation['diseases'].keys():
        try:
            # Check if disease mention already present
            tmp = general_annotations['diseases'][disease]
        except KeyError:
            # If not insert it, if any annotation is present
            try:
                general_annotations['diseases'][disease] = pmid_annotation['diseases'][disease]
            except KeyError:
                continue
    # Store disease mentions in title in general_annotations if not already present
    for disease in pmid_annotation['diseases_title'].keys():
        try:
            # Check if disease mention already present
            tmp = general_annotations['diseases_title'][disease]
        except KeyError:
            # If not insert it, if any annotation is present
            try:
                general_annotations['diseases_title'][disease] = pmid_annotation['diseases_title'][disease]
            except KeyError:
                continue
    return general_annotations


def retokenize_miRNA(sentence):
    """
    Retokenize miRNA mentions in a single token if they are split in different tokens by Spacy Tokenizer.

    :param sentence: (spacy.tokens.doc.Doc) input sentence doc.
    :return: sentence retokenized.
    """

    miRNAs = get_miRNA(sentence)
    # if there is a miRNA mention in the sentence
    if len(miRNAs) > 0:
        for m in miRNAs:
            # Normalize miRNA mentions special characters such as '-' to avoid mismatch
            tok = [t for t in sentence if t.text.encode().replace(b"\xe2\x80\x91", b"-").decode() in m and not t.text == m]
            # if miRNA mention split in different tokens
            if len(tok) > 1:
                # order tokens based on their id
                tok.sort(key=lambda t: t.i)
                for i in range(0, len([t for t in tok if t.text[0] == m[0]])):
                    # merge only consecutives tokens
                    start = 0
                    end = 0
                    for j in range(0, len(tok)):
                        # first token is the start of the miRNA mention
                        if start == 0 and (not tok[j].text == m) and tok[j].text[0] == m[0]:
                            start = tok[j].i
                            end = tok[j].i + 1
                        # token is consecutive of the prev one
                        elif tok[j].i == end:
                            end = tok[j].i + 1
                        # retokenize the mention and start again
                        else:
                            break
                    # Retokenize miRNA mentions
                    if start != 0 and end != 0:
                        with sentence.retokenize() as retokenizer:
                            # retokenize miRNA mention
                            retokenizer.merge(sentence[start:end])
    return None


def get_miRNA(sentence):
    """
    Retrieve miRNA mentions by using a regex.

    :param sentence: (spacy.tokens.doc.Doc) input sentence doc.
    :return: list of microRNA mentions detected using regex.
    """
    miRNAs = []
    # Normalize miRNA mentions special characters such as '-' to avoid mismatch
    matches = re.finditer(mi_regex, sentence.text.encode().replace(b"\xe2\x80\x91", b"-").decode(), re.MULTILINE)
    tmp = []
    for match in matches:
        tmp.append(match.group())
    for t in tmp:
        if t not in ['miR', 'miRNA', 'MIR']:
            miRNAs.append(t)
    return miRNAs


def is_expression_type(span):
    """
    Check a Noun-Phrase is of type 'expression' by checking a list of expression triggers.

    :param span: (spacy.tokens.span.Span) Noun-Phrase to check
    :return: True or False.
    """
    if isinstance(span, spacy.tokens.token.Token):
        # Check if token is an expression trigger
        if span.text in expression_trigs:
            return True
        else:
            return False
    # Check if span contains an expression trigger
    elif [t for t in span if t.text in expression_trigs]:
        return True
    # Look for gene mentions 'CD[0-9]+'
    elif re.search("CD[0-9]+", span.text):
        return True
    else:
        return False


def is_disease_sample(span):
    """
    Check a Noun-Phrase is of type 'disease-sample' by checking a list of disease-sample triggers.

    :param span: (spacy.tokens.span.Span) Noun-Phrase to check
    :return: True or False.
    """
    if isinstance(span, spacy.tokens.token.Token):
        # Check if token is a disease/disease-sample trigger
        if span.lemma_ in disease_sample_trigs:
            return True
        else:
            return False
    # Check if span contains a disease/disease-sample trigger
    elif [t for t in span if t.lemma_ in disease_sample_trigs]:
        return True
    else:
        return False
