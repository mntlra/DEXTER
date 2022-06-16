import re

from spacy import Language
from spacy.tokens import Span

trigger_words = ['tissue', 'cell', 'patient', 'sample', 'tumor', 'cancer', 'carcinoma',
                 'cell line', 'cell-line', 'group', 'blood', 'sera', 'serum', 'fluid', 'subset', 'case', 'men', 'women',
                 'control', 'normal', 'health', 'healthy', 'NC', 'adjacent', 'peri-tumoral', 'peritumoral', 'tumoral',
                 'cancerous', 'non-tumor', 'non-tumoral', 'non-cancerous']

skip_words = ['gain', 'increased', 'increase', 'reduce', 'express', 'high', 'overexpressed', 'over-expressed',
              'positive', 'strong', 'elevated', 'upregulated', 'up-regulated', 'higher', 'loss', 'decreased', 'low',
              'underexpressed', 'under-expressed', 'down-regulated', 'downregulated', 'reduced', 'knockdown',
              'suppressed', 'decrease', 'negative', 'weak', 'lower']


@Language.component("expand_entity_mentions")
def expand_entity_mentions(doc):
    """
    Expand entity mentions relying on hand-crafted rules

    :param doc: (spacy.tokens.doc.Doc) text processed w/ spaCy models

    :return: a new set of entities for doc
    """

    # Entity expansion tokenwise based on trigger words
    spans = expand_entity_tokenwise(doc)
    # loop over restricted entities and expand entity mentions
    for ent in doc.ents:
        # Check for compound names external of the entity
        candidates = [doc[j] for j in range(ent.start, ent.end) if doc[j].dep_ in ["compound", "amod"] and
                      doc[j].head.i not in range(ent.start, ent.end) and doc[j].head.lemma_ not in skip_words]
        if candidates:
            for token in candidates:
                # Extend the entity
                spans = extend_compound(token, doc, spans, ent.start, ent.end)
        else:  # current entity does not present a compound name
            spans.append([ent.start, ent.end])

    # expression level extension
    extend_expression_level(doc, spans)
    # patients expansion
    extend_patients(doc, spans)

    if spans:  # doc contains valid entity mentions (update entities)
        # merge entities w/ overlapping spans
        merged_spans = merge_spans(spans)
        # skip words wrongly inserted in the expansion
        for span in merged_spans:
            if doc[span[0]].lemma_ in skip_words and \
                    [doc[i] for i in range(span[0], span[1]) if doc[i].lemma_ in ["expression", "level"]]:
                span[0] = span[0] + 1    # skip /trigger_word/ if before "level|expression...."
        doc.ents = [Span(doc, span[0], span[1], label='ENTITY') for span in merged_spans]

    return doc


def extend_compound(token, doc, spans, start, end):
    """
    Extend entity to contain the compound name

    :param  token:  (spacy.tokens) token with a dependency "compound" or "amod" outside the entity
    :param  doc: (spacy.tokens.doc.Doc) text processed w/ spaCy models
    :param  spans: (list(list)) list of span ranges [start, end]
    :param  start: (int) start index of the entity containing the input token
    :param  end: (int) end index of the entity containing the input token

    :return: list of expanded spans
    """

    # Check if token head is already contained in an entity
    c_entity = [e for e in doc.ents if token.head.i in range(e.start, e.end)]
    if c_entity:
        # merging the two entities
        start_ent = min(start, c_entity[0].start)
        end_ent = max(end, c_entity[0].end)
    else:
        # adding token to the input entity
        start_ent = min(start, token.head.i)
        end_ent = max(end, token.head.i+1)
    spans.append([start_ent, end_ent])
    return spans


def expand_entity_tokenwise(doc):
    """
    Expand entity mentions tokenwise

    :param  doc: (spacy.tokens.doc.Doc) text processed w/ spaCy models

    :return: list of expanded spans
    """

    spans = list()
    # Trigger entities that could be expanded
    triggers = [t for t in doc if t.lemma_ in trigger_words]
    for token in triggers:
        # Check if token is inside an entity
        ent = [e for e in doc.ents if token.i in range(e.start, e.end)]
        if ent:
            start = ent[0].start
            end = ent[0].end
        else:
            # Consider input token as an entity
            start = token.i
            end = token.i+1
        # Check if any children of the token (not in the same entity) have a dependency "compound" or "amod"
        candidates = [child for child in token.children if child.dep_ in ["compound", "amod"] and
                      child.i not in range(start, end) and child.lemma_ not in skip_words and child.pos_ != 'SPACE']
        if candidates:
            # Expand the entity
            spans = extend_compound_tokenwise(candidates, spans, start, end)
        else:
            # Check if token has a dependency "compound" or "amod" whose head is not in the same entity
            if token.dep_ in ['compound', 'amod'] and token.head.i not in range(start, end) and token.head.lemma_ not in skip_words:
                ent_adj = [e for e in doc.ents if token.head.i in range(e.start, e.end)]
                if ent_adj:
                    start_ent = ent_adj[0].start
                    end_ent = ent_adj[0].end
                else:
                    start_ent = token.head.i
                    end_ent = token.head.i+1
                spans = extend_compound_tokenwise([token], spans, start_ent, end_ent)
            else:
                # Current entity does not present a compound name
                spans.append([start, end])
    return spans


def extend_compound_tokenwise(candidates, spans, start, end):
    """
    Extend entity to contain the compound name

    :param candidates: (list(spacy.tokens)) list of tokens that extend the input token
    :param spans: (list(list)) list of span ranges [start, end]
    :param start: (int) start index of the entity inside the token
    :param end: (int) end index of the entity inside the token

    :return: list of expanded spans
    """

    # Sort candidate tokens with ascending id
    candidates.sort(key=lambda t: t.i)
    start_ent = min(candidates[0].i, start)
    end_ent = max(candidates[len(candidates)-1].i+1, end)
    spans.append([start_ent, end_ent])
    return spans


def extend_expression_level(doc, spans):
    """
    Merge "expression|level|expression level [of] entity" or "entity level" in a single entity

    :param doc: (spacy.tokens.doc.Doc) text processed w/ spaCy models
    :param spans: (list(list)) list of span ranges [start, end]

    :return: list of expanded spans
    """
    for t in doc:
        if t.lemma_ in ['expression', 'level']:
            e = [ent for ent in doc.ents if t.i in range(ent.start, ent.end)]
            if e:
                # check if after the entity with expression|level there is "of + entity|token"
                if t.i == e[0].end-1 and doc[e[0].end].text == 'of':
                    tmp = doc[e[0].end].head
                    t_e = [ent for ent in doc.ents if tmp.i in range(ent.start, ent.end)]
                    if t_e:
                        spans.append([e[0].start, t_e[0].end])
                    else:
                        spans.append([e[0].start, tmp.i+1])
                else:
                    # check if we have entity + level|expression
                    prev_ent = [ent for ent in doc.ents if ent.end == e[0].start]
                    if prev_ent:
                        spans.append([prev_ent[0].start, e[0].end])
            else:
                # create an entity with "expression|level + of + next_token"
                if doc[t.i+1].text == 'of':
                    tmp = doc[t.i+2]
                    t_e = [e for e in doc.ents if tmp.i in range(e.start, e.end)]
                    if t_e:
                        spans.append([t.i, t_e[0].end])
                else:
                    # check if we have entity + level|expression
                    prev_ent = [ent for ent in doc.ents if ent.end == t.i and ent.text not in skip_words]
                    if prev_ent:
                        spans.append([prev_ent[0].start, t.i+1])


def extend_patients(doc, spans):
    """
    Merge 'patients with [entity]' in a single entity

    :param doc: (spacy.tokens.doc.Doc) text processed w/ spaCy models
    :param spans: (list(list)) list of span ranges [start, end]

    :return: list of expanded spans
    """
    for t in doc:
        if t.lemma_ == 'patient':
            if doc[t.i+1] .text == 'with':
                tmp = doc[t.i + 2]
                t_e = [e for e in doc.ents if tmp.i in range(e.start, e.end)]
                if t_e:
                    ent = [e for e in doc.ents if t.i in range(e.start, e.end)]
                    if ent:
                        spans.append([ent[0].start, t_e[0].end])
                    else:
                        spans.append([t.i, t_e[0].end])


def merge_spans(spans):
    """
    Merge spans w/ overlapping ranges

    :param    spans: (list(list)) list of span ranges [start, end]

    :return: a list of merged span ranges [start, end]
    """

    spans.sort(key=lambda span: span[0])
    # Avoid copying by reference
    merged_spans = [[spans[0][0], spans[0][1]]]
    for current in spans:
        previous = merged_spans[-1]
        if current[0] < previous[1]:
            previous[1] = max(previous[1], current[1])
        else:
            merged_spans.append(current)
    return merged_spans
