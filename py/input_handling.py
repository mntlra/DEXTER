import re

import requests


def load_from_pubtator(pmid):
    """
    Retrieves title and abstract text from PubTator.

    :param pmid: (String) PubMed ID of the abstract
    :return: string containing title text and abstract text.
    """
    response = requests.get(
        "https://www.ncbi.nlm.nih.gov/research/pubtator-api/publications/export/biocjson?pmids=" + pmid)
    title, abstract = None, None
    for passage in response.json()["passages"]:
        # Extracting title text
        if passage['infons']['type'] == 'title':
            title = passage['text']
        # Extracting abstract text
        elif passage['infons']['type'] == 'abstract':
            abstract = passage['text']

    if title is not None and abstract is not None:
        return title, abstract
    else:
        print("Could not find requested information")
        raise Exception


def preprocess_sentence(sentence):
    """
    Preprocess input sentence by removing undesired tokens and symbols.
    :param: sentence (String): input sentence.
    :return: preprocessed string sentence.
    """
    # Remove quote marks if present
    if sentence.startswith('"') and sentence.endswith('"'):
        norm_sentence = sentence[1:-1]
    else:
        norm_sentence = sentence[0:]
    # Remove number and minus at the start of the string (if present) (i.e., 3-)
    combined_pat = r'|'.join((r'^\s*[0-9]+-', r'^\s*[0-9]+'))
    norm_sentence = re.sub(combined_pat, '', norm_sentence)
    # Remove start of sentence 'RESULTS: ...'
    regex = r'|'.join((r'^(S|RESULTS|CONCLUSION|CONCLUSIONS|PURPOSE|OBJECTIVE|OBJECTIVES|BACKGROUND|MEASUREMENT|ABSTRACT)(.*(AND|/).*)?:',
                       r'^(RESULTS|CONCLUSION|CONCLUSIONS|PURPOSE|OBJECTIVE|OBJECTIVES|BACKGROUND|MEASUREMENT)'))
    processed_sentence = re.sub(regex, "", norm_sentence).strip()
    # Remove numbers between square brackets or ([0-9]) at the beginning of the sentence
    regex_num = r'|'.join((r'\s\[[^\[]*\]', r'^\([0-9]+\)\s'))
    input_doc = re.sub(regex_num, "", processed_sentence)

    return input_doc
