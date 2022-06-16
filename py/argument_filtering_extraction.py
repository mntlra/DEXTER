import json
import re
from pathlib import Path
import os
import spacy

from entity_detection import is_expression_type, is_disease_sample
from exceptions import InvalidArgument, GeneNotFound, MistypedExpressionLevel, DiseaseNotFound

# Dictionary for Expression Level Normalization
expression_level_norm = {'gain': 'UP', 'increased': 'UP', 'high': 'UP', 'overexpressed': 'UP',
                         'over-expressed': 'UP', 'positive': 'UP', 'strong': 'UP', 'elevated': 'UP',
                         'upregulated': 'UP', 'up-regulated': 'UP', 'higher': 'UP', 'loss': 'DOWN',
                         'decreased': 'DOWN', 'low': 'DOWN', 'underexpressed': 'DOWN', 'under-expressed': 'DOWN',
                         'down-regulated': 'DOWN', 'downregulated': 'DOWN', 'reduced': 'DOWN', 'knockdown': 'DOWN',
                         'suppressed': 'DOWN', 'negative': 'DOWN', 'weak': 'DOWN', 'lower': 'DOWN', 'highest': 'UP',
                         'up-regulates': 'UP', 'downregulation': 'DOWN', 'upregulation': 'UP', 'elevation': 'UP',
                         'amplified/over-expressed': 'UP', 'over-expression': 'UP', 'up-regulation': 'UP',
                         'down-regulation': 'DOWN', 'coexpressed': 'UP', 'coexpresse': 'UP', 'downexpressed': 'DOWN',
                         'downexpresse': 'DOWN', 'lower-expressed': 'DOWN', 'lower-expresse': 'DOWN'}
# Dictionary for Expression Level Normalization (adverbs)
advmod_norm = {'highly': 'UP', 'abundantly': 'UP', 'anomalously': 'UP', 'strongly': 'UP',
               'predominantly': 'UP', 'broadly': 'UP', 'widely': 'UP', 'scarcely': 'DOWN', 'lowly': 'DOWN',
               'positively': 'UP', 'negatively': 'DOWN', 'commonly': 'UP'}

# Triggers for flag 'Control'
control_trigs = ['control', 'normal', 'health', 'healthy', 'NC', 'adjacent', 'peri-tumoral', 'peritumoral', 'non tumor',
                 'non-tumor', 'non tumoral', 'non-tumoral', 'non cancerous', 'non-cancerous']

# Triggers for flag 'Control-Implicit'
control_implicit_trigs = ["increase", "decrease", "express", "silence", "reduce", "elevate", "change", "regulate",
                          "overexpresse", "over-expressed", "unchanged", "up-regulate", "upregulate", "down-regulate",
                          "downregulate", "elevated", "normalize"]

# Investigation triggers for disease inference
investigation_trigs = ['investigate', 'investigated', 'examine', 'examined', 'analyze', 'analyzed', 'evaluate',
                       'evaluated', 'studied', 'compared', 'demonstrated']

# Analyzed triggers for disease inference
analyzed_trigs = ['tested', 'explored', 'collected', 'analyzed', 'measured', 'enrolled', 'assessed']

# Generic Diseases
generic_diseases = ['tumor', 'cancer', 'disease', 'tumor metastases', 'infection', 'metastases', 'tumors', 'died',
                    'cancerous', 'carcinoma', 'cancerous', 'metastasis']

# Dictionary to map DOIDs to the Disease Name
doid_to_names_json = str(Path(os.path.abspath(os.getcwd())).absolute()) + "/data/input/" + 'doid_to_names.json'
with open(doid_to_names_json, 'r') as udf:
    doid_to_names = json.loads(udf.read())


def check_components(components, genes, diseases, micro_rnas, general_annotations, verbose=False):
    """
    Check if the arguments found by the RE module meet the type constraints.

    :param components: (dict) dictionary of arguments found by the RE module.
    :param genes: (dict) dictionary of gene mentions detected using PubTator.
    :param diseases: (dict) dictionary of disease mentions detected using PubTator.
    :param micro_rnas: (list(String)) list of microRNA mentions detected using regex.
    :param general_annotations: (dict) dictionary of overall annotations.
    :param verbose: (Boolean) if True display diagnostic prints

    :return: return True if components are okay, else raise an exception.
    """

    # CA of type 'expression' or contains a gene/miRNA mention
    # CE1 of type 'disease/disease-sample' or contains a disease mention
    if check_aspect(components['compared_aspect'], genes, micro_rnas, general_annotations, verbose) \
            and check_entity(components['compared_entity_1'], diseases, general_annotations):
        return True


def check_aspect(component, genes, micro_rnas, general_annotations, verbose):
    """
    Check if Compared Aspect is of type expression or contains gene/microRNA mentions.

    :param component: (spacy.tokens.span.Span) Compared Aspect extracted bhy the RE module.
    :param genes: (dict) dictionary of gene mentions detected using PubTator.
    :param micro_rnas: (list(String)) list of microRNA mentions detected using regex.
    :param general_annotations: (dict) dictionary of overall annotations.
    :param verbose: (Boolean) if True display diagnostic prints

    :return: True if CA meet the type constraint otherwise raise an Exception
    """
    # Normalize compared_aspect special characters such as '-' and if start of sentence lower-case first letter
    compared_aspect = component.text.encode().replace(b"\xe2\x80\x91", b"-").decode()
    if verbose:
        print('Compared Aspect', compared_aspect)
    # Check compared_aspect of type 'expression or gene/microRNA itself
    if genes and [g for g in genes.keys() if g in compared_aspect]:
        if verbose:
            print("compared aspect is the gene itself")
        return True
    if micro_rnas and [m for m in micro_rnas if m in compared_aspect]:
        if verbose:
            print("compared aspect is the microRNA itself")
        return True
    if is_expression_type(component):
        if verbose:
            print("Compared aspect is of type expression")
        return True
    if general_annotations['genes'] and [g for g in general_annotations['genes'].keys() if g in compared_aspect]:
        if verbose:
            print('Gene mention in general_annotations')
        return True
    # look for 'CD[0-9]+' genes
    if re.search("CD[0-9]+", compared_aspect):
        if verbose:
            print('CD* gene mention')
        return True
    # lower-case normalization
    if verbose:
        print('Try lower-case normalization')
    if genes:
        tmp = [g for g in genes.keys() if g.lower() in compared_aspect.lower()]
        if tmp:
            if verbose:
                print(f'gene lower-case normalization: {tmp}')
            return True
    # if gene is not yet found, look for general_annotations
    if general_annotations['genes']:
        tmp = [m for m in general_annotations['genes'].keys() if m.lower() in compared_aspect.lower()]
        if verbose:
            print('Searching general_annotations')
            print('mentions:', tmp)
        if tmp:
            if verbose:
                print(f'gene lower-case normalization in general_annotations: {tmp}')
            return True
    if verbose:
        print("Compared aspect does not meet type constraint")
    raise InvalidArgument


def check_entity(component, diseases, general_annotations, verbose=False):
    """
    Check if Compared Entity 1/Compared Entity 2 is of type disease/disease-sample or contains disease mentions.

    :param component: (spacy.tokens.doc.Doc) Compared Entity extracted by the RE module.
    :param diseases: (dict) dictionary of disease mentions detected using PubTator.
    :param general_annotations: (dict) dictionary of overall annotations.
    :param verbose: (Boolean) if True display diagnostic prints

    :return: True if CE1/CE2 meet the type constraint otherwise raise an Exception
    """

    if verbose:
        print(f"Checking compared entity/expression location: {component.text}")
    if [k for k in diseases.keys() if k in component.text.lower()]:
        if verbose:
            print("Compared entity is a disease")
        return True
    # Check compared_entities of type disease/disease-sample
    if is_disease_sample(component):
        if verbose:
            print("Compared entity is of type disease sample")
        return True
    if general_annotations['diseases'] and [g for g in general_annotations['diseases'].keys() if g in component.text]:
        if verbose:
            print('Compared entity contains a disease in general_annotations')
        return True
    raise InvalidArgument


def extract_gene(sentence, component, genes, micro_rnas, general_annotations, verbose=False):
    """
    Extract gene/miRNA mention in the sentence by matching against precomputed PubTator mentions or
    microRNa detected in previous module.

    :param sentence: (spacy.tokens.doc.Doc) input sentence
    :param component: (spacy.tokens.span.Span) Compared Aspect extracted by the RE module.
    :param genes: (dict) dictionary of gene mentions detected using PubTator.
    :param micro_rnas: (list(String)) list of microRNA mentions detected using regex.
    :param general_annotations: (dict) dictionary of overall annotations.
    :param verbose: (Boolean) if True display diagnostic prints

    :return: String corresponding to the gene/miRNA mentioned in the sentence and 'gene' or 'micro-RNA' type
    otherwise raise an Exception.
    """
    # Normalize compared_aspect special characters such as '-' to avoid mismatch
    compared_aspect = component.text.encode().replace(b"\xe2\x80\x91", b"-").decode()
    # Check if previous word is a gene/miRNA mention, if CA is of expression_type
    if is_expression_type(component):
        if isinstance(component, spacy.tokens.token.Token):
            prev_token = sentence[component.i-1].text
        else:
            prev_token = sentence[component.start-1].text
    else:
        prev_token = ''
    if verbose:
        print(f'prev_token: {prev_token}')
    # Check if there are gene mentions or microRNA mentions available
    if genes or micro_rnas:
        # Gene mentions in compared aspect
        tmp = [g for g in genes.keys() if g in compared_aspect]
        if tmp:
            # Discard gene mentions that are substring of other mentions
            gene = [t for t in tmp if not any(t in b for b in tmp if b != t)]
            results = []
            for g in gene:
                # Check if it is a miRNA
                if genes[g] == 'micro-RNA':
                    if verbose:
                        print('MicroRNA extracted from gene mentions')
                    results.append([g, 'micro-RNA'])
                else:
                    if verbose:
                        print('Gene extracted from gene mentions')
                    results.append([g, 'gene'])
            return results
        # Check if previous token is a gene/miRNA mention
        elif prev_token in genes.keys():
            if verbose:
                print('Previous token is a gene')
            if genes[prev_token] == 'micro-RNA':
                return [[prev_token, 'micro-RNA']]
            else:
                return [[prev_token, 'gene']]
        # Check microRNA mentions
        elif micro_rnas:
            mi_rna = [m for m in micro_rnas if m in compared_aspect]
            if mi_rna:
                if verbose:
                    print('MicroRNA extracted from mentions')
                results = []
                for m in mi_rna:
                    results.append([m, 'micro-RNA'])
                return results
            # Check if previous token is a gene/miRNA mention
            elif prev_token in micro_rnas:
                if verbose:
                    print('Previous token is a miRNA:', prev_token)
                return [[prev_token, 'micro-RNA']]
    # if gene is not yet found, look for general_annotations
    if general_annotations['genes']:
        tmp = [m for m in general_annotations['genes'].keys() if m in compared_aspect]
        if verbose:
            print('Searching general_annotations')
        if tmp:
            # Check it is not a mismatch, i.e. we match some characters inside a token
            if isinstance(component, spacy.tokens.token.Token):
                tokens = [component]
            else:
                tokens = [t for t in component]
            mentions = []
            for match in tmp:
                toks = match.split()
                # matches that are subtokens
                out_of_ca = [t for t in toks if not (any(t == tok.text.strip(', ') for tok in tokens) or any(t in tok.text.split('/') for tok in tokens))]
                if not out_of_ca:
                    mentions.append(match)
            if mentions:
                if verbose:
                    print('Found gene mentions in general_annotations')
                results = []
                for m in mentions:
                    if not results and m != 'to':
                        if general_annotations['genes'][m] == 'micro-RNA':
                            results.append([m, 'micro-RNA'])
                        else:
                            results.append([m, 'gene'])
                if results:
                    if verbose:
                        print('Returning gene mentions in general_annotations')
                    return results
        # Check if previous token is a gene/miRNA mention
        if prev_token in general_annotations['genes'].keys():
            if verbose:
                print('Previous token is in general_annotations')
            if general_annotations['genes'][prev_token] == 'micro-RNA':
                return [[prev_token, 'micro-RNA']]
            else:
                return [[prev_token, 'gene']]
    # look for 'CD[0-9]+' genes
    if re.search("CD[0-9]+", compared_aspect):
        if verbose:
            print('gene found by regex CD[0-9]+')
        return [[re.search("CD[0-9]+", compared_aspect).group(), 'gene']]

    if isinstance(component, spacy.tokens.token.Token):
        tokens = [component]
    else:
        tokens = [t for t in component]
    # lower-case normalization
    if verbose:
        print('Trying lower-case normalization')
    if genes:
        tmp = [g for g in genes.keys() if g.lower() in compared_aspect.lower()]
        if tmp:
            # Discard gene mentions that are substring of other mentions
            gene = [t for t in tmp if not any(t in b for b in tmp if b != t)]
            results = []
            for g in gene:
                # Check if it is a miRNA
                if genes[g] == 'micro-RNA':
                    if verbose:
                        print('MicroRNA extracted from gene mentions')
                    results.append([g, 'micro-RNA'])
                else:
                    if verbose:
                        print('Gene extracted from gene mentions')
                    results.append([g, 'gene'])
                # Check it is not a mismatch, i.e. we match some characters inside a token
                mentions = []
                if verbose:
                    print('Check results are not mismatches')
                for match in results:
                    toks = match[0].split()
                    # matches that are subtokens
                    out_of_ca = [t for t in toks if not (any(t.lower() == tok.text.strip(', ').lower() for tok in tokens) or any(t in tok.text.split('/') for tok in tokens))]
                    if not out_of_ca:
                        mentions.append(match)
                if mentions:
                    results = []
                    for m in mentions:
                        if not results and m != 'to':
                            results.append(m)
                    if verbose:
                        print('Returning gene mentions in annotations')
                    return results
    # if gene is not yet found, look for general_annotations
    if general_annotations['genes']:
        tmp = [m for m in general_annotations['genes'].keys() if m.lower() in compared_aspect.lower()]
        if verbose:
            print('Searching lower-case general_annotations')
        if tmp:
            # Check it is not a mismatch, i.e. we match some characters inside a token
            mentions = []
            for match in tmp:
                toks = match.split()
                # matches that are subtokens
                out_of_ca = [t for t in toks if not any(t.lower() == tok.text.strip(', ').lower() for tok in tokens)]
                if not out_of_ca:
                    mentions.append(match)
            if mentions:
                if verbose:
                    print('Found gene mentions in general_annotations')
                results = []
                for m in mentions:
                    if not results and m != 'to':
                        if general_annotations['genes'][m] == 'micro-RNA':
                            results.append([m, 'micro-RNA'])
                        else:
                            results.append([m, 'gene'])
                return results
    if genes:
        if verbose:
            print('Try special characters normalization')
        # Substitute special characters such as beta/alpha
        new_ca = ''
        if b"\xce\xb2" in component.text.encode():
            new_ca = component.text.encode().replace(b"\xce\xb2", b"beta").decode()
        if b"\xce\xb1" in component.text.encode():
            if new_ca:
                new_ca = new_ca.encode().replace(b"\xce\xb1", b"alpha").decode()
            else:
                new_ca = component.text.encode().replace(b"\xce\xb1", b"alpha").decode()
        if new_ca:
            if genes:
                tmp = [g for g in genes.keys() if g in new_ca]
                if tmp:
                    # Discard gene mentions that are substring of other mentions
                    gene = [t for t in tmp if not any(t in b for b in tmp if b != t)]
                    results = []
                    for g in gene:
                        # Check if it is a miRNA
                        if genes[g] == 'micro-RNA':
                            if verbose:
                                print('MicroRNA extracted from gene mentions')
                            results.append([g, 'micro-RNA'])
                        else:
                            if verbose:
                                print('Gene extracted from gene mentions')
                            results.append([g, 'gene'])
                    return results
            if general_annotations['genes']:
                tmp = [m for m in general_annotations['genes'].keys() if m in new_ca]
                if verbose:
                    print('Searching general_annotations')
                if tmp:
                    # Discard gene mentions that are substring of other mentions
                    gene = [t for t in tmp if not any(t in b for b in tmp if b != t)]
                    results = []
                    for g in gene:
                        # Check if it is a miRNA
                        if general_annotations['genes'][g] == 'micro-RNA':
                            if verbose:
                                print('MicroRNA extracted from general_annotations')
                            results.append([g, 'micro-RNA'])
                        else:
                            if verbose:
                                print('MicroRNA extracted from general_annotations')
                            results.append([g, 'gene'])
                    return results
    raise GeneNotFound


def normalize_expression_level(sentence, components, verbose=False):
    """
    Normalize scale indicator/level indicator to high or low by matching them against a list of triggers.

    :param sentence: (spacy.tokens.doc.Doc) input sentence.
    :param components: (dict) dictionary of arguments found by the RE module.
    :param verbose: (Boolean) if True display diagnostic prints.

    :return: scale indicator/level indicator normalized to 'UP'/'DOWN' otherwise raise an Exception.
    """
    if verbose:
        print(components['scale_indicator'].text.lower())
    try:
        return expression_level_norm[components['scale_indicator'].text.lower()]
    except KeyError:
        # Check if there is an adverb that depends on SI (i.e., highly...)
        advs = [t for t in sentence if t.dep_ == 'advmod' and t.head == components['scale_indicator']]
        if advs:
            if verbose:
                print('Checking adverbs that depend on SI')
            for adv in advs:
                try:
                    return advmod_norm[adv.text.lower()]
                except KeyError:
                    continue
        # if any expression level is connected to the SI (one-hop or two-hops)
        if [t for t in sentence if (t.head == components['scale_indicator'] or t.head.head == components['scale_indicator']) and t.text in expression_level_norm.keys()]:
            levels = [t for t in sentence if (t.head == components['scale_indicator'] or t.head.head == components['scale_indicator']) and t.text in expression_level_norm.keys()]
            if verbose:
                print('Checking any expression level is connected to the SI (one-hop or two-hops)')
            for expr_level in levels:
                try:
                    return expression_level_norm[expr_level.text.lower()]
                except KeyError:
                    continue
        # Check if next token is an expression level trigger
        if sentence[components['scale_indicator'].i+1].text.lower() in expression_level_norm.keys():
            if verbose:
                print('next token is in expression level keys')
            return expression_level_norm[sentence[components['scale_indicator'].i+1].text.lower()]
        # Check if token may not match due to special characters (i.e., '/')
        if '/' in sentence[components['scale_indicator'].i+1].text:
            trig = sentence[components['scale_indicator'].i + 1].text.split('/')[0].lower()
            if trig in expression_level_norm.keys():
                if verbose:
                    print('Expression Level needed splitting')
                return expression_level_norm[trig]
        # if SI is 'expressed' without additional information normalize to 'UP'
        if components['scale_indicator'].text == 'expressed':
            return 'UP'
        # if there is an expr_level trigger whose head is a component
        if [t for t in sentence if t.text.lower() in expression_level_norm.keys() and any(t.head.text in components[c].text for c in components.keys())]:
            if verbose:
                print('found a trigger connected to any component')
            return expression_level_norm[[t.text.lower() for t in sentence if t.text.lower() in expression_level_norm.keys() and any(t.head.text in components[c].text for c in components.keys())][0]]
        # no other action, raise Exception
        raise MistypedExpressionLevel


def extract_disease(components, sent_type, diseases, diseases_title, general_annotations, title, abstract, verbose=False):
    """
    Disease Extraction. First check Compared Entities, else infer from context.

    :param components: (dict) dictionary of arguments found by the RE module.
    :param sent_type: (String)  string indicating if sentence is of Type A or Type B.
    :param diseases: (dict) dictionary of disease mentions detected using PubTator.
    :param diseases_title: (dict) dictionary of disease mentions detected in the title using PubTator.
    :param general_annotations: (dict) dictionary of overall annotations.
    :param title: (String) title text of the abstract.
    :param abstract: (spacy.tokens.doc.Doc) abstract processed w/ spaCy models
    :param verbose: (Boolean) if True display diagnostic prints

    :return: DOID of the disease, Disease Name, Mention, Disease Location otherwise raise an Exception.
    """
    mentions = []
    generic_mention = None
    diseases_CE1 = [k for k in diseases.keys() if k in components['compared_entity_1'].text]
    # Checking disease mentions in CE1
    if diseases_CE1:
        # Check it is not a mismatch, i.e. we match some characters inside a token
        if isinstance(components['compared_entity_1'], spacy.tokens.token.Token):
            tokens = [components['compared_entity_1']]
        else:
            tokens = [t for t in components['compared_entity_1']]
        for match in diseases_CE1:
            doid = diseases[match]
            disease_name = doid_to_names[doid]
            # Check it is not a generic disease
            if disease_name.lower() not in generic_diseases:
                toks = match.split()
                # Checking match is not a subtoken
                out_of_ca = [t for t in toks if not any(t == tok.text.strip(', ') for tok in tokens)]
                if not out_of_ca:
                    if verbose:
                        print('Disease extracted from CE1')
                    mentions.append([doid, disease_name, match, 'Sentence_ARG'])
            else:
                if verbose:
                    print('Storing a generic_disease')
                generic_mention = [doid, disease_name, match, 'Sentence_ARG']
    gen_diseases_CE1 = [k for k in general_annotations['diseases'].keys() if k in components['compared_entity_1'].text]
    if not mentions and gen_diseases_CE1:
        # Check it is not a mismatch, i.e. we match some characters inside a token
        if isinstance(components['compared_entity_1'], spacy.tokens.token.Token):
            tokens = [components['compared_entity_1']]
        else:
            tokens = [t for t in components['compared_entity_1']]
        for match in gen_diseases_CE1:
            doid = general_annotations['diseases'][match]
            disease_name = doid_to_names[doid]
            # Check it is not a generic disease
            if disease_name.lower() not in generic_diseases:
                toks = match.split()
                # Check match is not a subtoken
                out_of_ca = [t for t in toks if not any(t == tok.text.strip(', ') for tok in tokens)]
                if not out_of_ca:
                    if verbose:
                        print('Disease extracted from CE1 - general_annotations')
                    mentions.append([doid, disease_name, match, 'Sentence_ARG'])
            elif generic_mention is None:
                if verbose:
                    print('Storing a generic_disease')
                generic_mention = [doid, disease_name, match, 'Sentence_ARG']
    if sent_type == 'TypeA':
        if verbose:
            print(f' sent_type {sent_type} => checking for disease mentions in CE2')
        diseases_CE2 = [k for k in diseases.keys() if k in components['compared_entity_2'].text]
        if not mentions and diseases_CE2:
            # Check it is not a mismatch, i.e. we match some characters inside a token
            if isinstance(components['compared_entity_2'], spacy.tokens.token.Token):
                tokens = [components['compared_entity_2']]
            else:
                tokens = [t for t in components['compared_entity_2']]
            for match in diseases_CE2:
                doid = diseases[match]
                disease_name = doid_to_names[doid]
                # Check it is not a generic disease
                if disease_name.lower() not in generic_diseases:
                    toks = match.split()
                    # Check match is not a subetoken
                    out_of_ca = [t for t in toks if not any(t == tok.text.strip(', ') for tok in tokens)]
                    if not out_of_ca:
                        if verbose:
                            print('Disease extracted from CE2')
                        mentions.append([doid, disease_name, match, 'Sentence_ARG'])
                elif generic_mention is None:
                    if verbose:
                        print('Storing a generic_disease')
                    generic_mention = [doid, disease_name, match, 'Sentence_ARG']
        gen_diseases_CE2 = [k for k in general_annotations['diseases'].keys() if k in components['compared_entity_2'].text]
        if not mentions and gen_diseases_CE2:
            # Check it is not a mismatch, i.e. we match some characters inside a token
            if isinstance(components['compared_entity_2'], spacy.tokens.token.Token):
                tokens = [components['compared_entity_2']]
            else:
                tokens = [t for t in components['compared_entity_2']]
            for match in gen_diseases_CE2:
                doid = general_annotations['diseases'][match]
                disease_name = doid_to_names[doid]
                # Check it is not a generic disease
                if disease_name.lower() not in generic_diseases:
                    toks = match.split()
                    # Check match is not a subtoken
                    out_of_ca = [t for t in toks if not any(t == tok.text.strip(', ') for tok in tokens)]
                    if not out_of_ca:
                        if verbose:
                            print('Disease extracted from CE2 - general_annotations')
                        mentions.append([doid, disease_name, match, 'Sentence_ARG'])
                elif generic_mention is None:
                    if verbose:
                        print('Storing a generic_disease')
                    generic_mention = [doid, disease_name, match, 'Sentence_ARG']
    if mentions:
        return mentions[0]
    if verbose:
        print("Disease must be inferred from context")
        print('Checking Abstract title')
    # Infer from title
    if len(diseases_title.keys()) > 0:
        for d in diseases_title.keys():
            doid = diseases_title[d]
            disease_name = doid_to_names[doid]
            if disease_name.lower() not in generic_diseases:
                if verbose:
                    print('Disease extracted from title')
                return doid, disease_name, d, 'Title'
            elif generic_mention is None:
                if verbose:
                    print('Storing a generic_disease')
                generic_mention = [doid, disease_name, d, 'Title']
    if title is not None:
        gen_diseases_title = [d for d in general_annotations['diseases'].keys() if d in title]
        # Check for disease mentions in the title from general_annotations
        if gen_diseases_title:
            for d in gen_diseases_title:
                doid = general_annotations['diseases'][d]
                disease_name = doid_to_names[doid]
                if disease_name.lower() not in generic_diseases:
                    if verbose:
                        print('Disease extracted from title - general_annotations')
                    return doid, disease_name, d, 'Title'
                elif generic_mention is None:
                    if verbose:
                        print('Storing a generic_disease')
                    generic_mention = [doid, disease_name, d, 'Title']
    if abstract is not None:
        # Infer from context
        if verbose:
            print("Disease inferred from context")
        return infer_disease_from_context(abstract, diseases, general_annotations, generic_mention, verbose)
    else:
        if generic_mention is not None:
            if verbose:
                print('Returning a generic disease')
            return generic_mention
        else:
            raise DiseaseNotFound


def infer_disease_from_context(doc, diseases, general_annotations, generic_mention, verbose):
    """
    Infer the disease mentioned by checking for investigation or analyzed sentences.

    :param doc: (spacy.tokens.doc.Doc) text processed w/ spaCy models.
    :param diseases: (dict) dictionary of disease mentions detected using PubTator.
    :param general_annotations: (dict) dictionary of overall annotations.
    :param generic_mention: (list) list of DOID of the disease, Disease Name, Mention, Disease Location
    of a generic disease extracted before.
    :param verbose: (Boolean) if True display diagnostic prints.

    :return: DOID of the disease, Disease Name, Mention, Disease Location otherwise raise an Exception.
    """
    count = 0
    for sentence in doc.sents:
        count += 1
        # Check disease mentions in the first sentence
        if count == 1:
            disease = [d for d in diseases.keys() if d in sentence.text]
            gen_disease = [d for d in general_annotations['diseases'].keys() if d in sentence.text]
            if disease:
                for d in disease:
                    doid = diseases[d]
                    disease_name = doid_to_names[doid]
                    if disease_name.lower() not in generic_diseases:
                        if verbose:
                            print('Disease extracted from the First Sentence')
                        return doid, disease_name, d, 'First_Sentence'
                    elif generic_mention is None:
                        if verbose:
                            print('Storing a generic_disease')
                        generic_mention = [doid, disease_name, d, 'First_Sentence']
            if gen_disease:
                for d in gen_disease:
                    doid = general_annotations['diseases'][d]
                    disease_name = doid_to_names[doid]
                    if disease_name.lower() not in generic_diseases:
                        if verbose:
                            print('Disease extracted from the First Sentence - general_annotations')
                        return doid, disease_name, d, 'First_Sentence'
                    elif generic_mention is None:
                        if verbose:
                            print('Storing a generic_disease')
                        generic_mention = [doid, disease_name, d, 'First_Sentence']
        else:
            # Check for investigation triggers
            if [t for t in sentence if t.text in investigation_trigs]:
                # Check if subjects of the triggers is in the list
                if [t for t in sentence if t.dep_ == 'nsubj' and t.text.lower() in ['we', 'authors', 'purpose', 'aim', 'objective', 'results']]:
                    disease = [k for k in diseases.keys() if k in sentence.text]
                    gen_disease = [k for k in general_annotations['diseases'].keys() if k in sentence.text]
                    # Check disease mention in the sentence
                    if disease:
                        for d in disease:
                            doid = diseases[d]
                            disease_name = doid_to_names[doid]
                            # Check it is not a generic disease
                            if disease_name.lower() not in generic_diseases:
                                if verbose:
                                    print('Disease inferred from context')
                                return doid, disease_name, d, 'Sentence'
                            elif generic_mention is None:
                                if verbose:
                                    print('Storing a generic_disease')
                                generic_mention = [doid, disease_name, d, 'Sentence']
                    # Check disease mention in the sentence in general_annotations
                    elif gen_disease:
                        for d in gen_disease:
                            doid = general_annotations['diseases'][d]
                            disease_name = doid_to_names[doid]
                            # Check it is not a generic disease
                            if disease_name.lower() not in generic_diseases:
                                if verbose:
                                    print('Disease inferred from context')
                                return doid, disease_name, d, 'Sentence'
                            elif generic_mention is None:
                                if verbose:
                                    print('Storing a generic_disease')
                                generic_mention = [doid, disease_name, d, 'Sentence']
            # Check for analyzed triggers
            if [t for t in sentence if t.text in analyzed_trigs]:
                disease = [k for k in diseases.keys() if k in sentence.text]
                gen_disease = [k for k in general_annotations['diseases'].keys() if k in sentence.text]
                # Check disease mention in the sentence
                if disease:
                    for d in disease:
                        doid = diseases[d]
                        disease_name = doid_to_names[doid]
                        # Check it is not a generic disease
                        if disease_name.lower() not in generic_diseases:
                            if verbose:
                                print('Disease inferred from context')
                            return doid, disease_name, d, 'Sentence'
                        elif generic_mention is None:
                            if verbose:
                                print('Storing a generic_disease')
                            generic_mention = [doid, disease_name, d, 'Sentence']
                # Check disease mention in the sentence in general_annotations
                elif gen_disease:
                    for d in gen_disease:
                        doid = general_annotations['diseases'][d]
                        disease_name = doid_to_names[doid]
                        # Check it is not a generic disease
                        if disease_name.lower() not in generic_diseases:
                            if verbose:
                                print('Disease inferred from context')
                            return general_annotations['diseases'][d], disease_name, d, 'Sentence'
                        elif generic_mention is None:
                            if verbose:
                                print('Storing a generic_disease')
                            generic_mention = [doid, disease_name, d, 'Sentence']
    if generic_mention is not None:
        if verbose:
            print('Returning a generic disease')
        return generic_mention
    else:
        raise DiseaseNotFound


def get_comparison(components, sent_type):
    """
    Set a flag for comparison to Control or implicit Control by matching compared entities/expression location
    with a list of control triggers.

    :param components: (dict) dictionary of arguments found by the RE module.
    :param sent_type: (String) string indicating if sentence is of Type A or Type B.

    :return: flag set accordingly.
    """
    if sent_type == 'TypeA':
        if not isinstance(components['compared_entity_1'], spacy.tokens.token.Token):
            # Check Compared Entity 1 contains a control trigger
            control_1 = [t for t in components['compared_entity_1'] if t.lemma_ in control_trigs]
            if control_1:
                return 'Control'
            else:
                if not isinstance(components['compared_entity_2'], spacy.tokens.token.Token):
                    # Check Compared Entity 2 contains a control trigger
                    control_2 = [t for t in components['compared_entity_2'] if t.lemma_ in control_trigs]
                    if control_2:
                        return 'Control'
        return 'Not-Control'
    elif sent_type == 'TypeB':
        # Check Scale Indicator
        if components['scale_indicator'].lemma_ in control_implicit_trigs \
                or components['scale_indicator'].text.lower() in ['higher', 'lower']:
            return 'Control_Implicit'
        else:
            return 'none'
