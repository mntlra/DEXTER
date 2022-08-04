from spacy.matcher import DependencyMatcher
from exceptions import MatchNotFound

# Triggers for sentence form
# Compare words triggers
cmp_triggers = ["than", "versus", "vs.", "compared", "comparison"]
# Triggers for pattern rule selection
cmp1_triggers = ["high", "low", "higher", "lower"]
cmp2_triggers = ["increase", "decrease", "express", "silence", "reduce", "elevate", "change", "regulate",
                 "overexpresse", "over-expresse", "over-expressed", "underexpresse", "under-expressed", "unchanged", "up-regulate", "upregulate", "down-regulate",
                 "downregulate", "elevated", "normalize", 'underexpresse', 'under-expressed', 'amplify', 'amplified/over-expressed',
                 'coexpressed', 'coexpresse', 'downexpressed', 'downexpresse', 'lower-expressed', 'lower-expresse']
cmp12B_triggers = ["high", "low", "higher", "lower", "increase", "decrease", "express", "silence", "reduce", "elevate",
                   "change", "regulate", "overexpresse", "over-expresse", "over-expressed", "underexpresse", "under-expressed",
                   "unchanged", "up-regulate", "upregulate", "down-regulate", "downregulate", "elevated", "normalize",
                   'underexpresse', 'under-expressed', 'amplify', 'expressed', 'express', 'expressed',
                   'amplified/over-expressed', 'coexpressed', 'coexpresse', 'downexpressed', 'downexpresse',
                   'lower-expressed', 'lower-expresse', 'frequently']
cmp3_triggers = ['find', 'note', 'detect', 'observe', 'discover', 'occurred', 'occur', 'appear', 'show', 'identify',
                 'significant', 'reveal', 'demonstrate', 'appear', 'identify', 'show', 'prove', 'know', 'report',
                 'suggest', 'document', 'tend', 'determine', 'examine', 'confirm', 'validate', 'indicate']

# Component to extract
component_keys = ["scale_indicator", "compared_aspect", "compared_entity_1", "compared_entity_2", "n0"]

# ---
# TYPE A PATTERNS
# ---
# Sentence-form based patterns (starter rules)
# n0: both CE1 and CE2 depends on the scale_indicator
# n1: CE1 depends on the scale_indicator, CE2 depends on the compared_aspect
cmp1_n0 = [
    # Cond_1: {word:/(higher|lower|high|low)/}=N0
    # scale indicator: high|higher|low|lower
    {
        "RIGHT_ID": "n0",
        "RIGHT_ATTRS": {"LEMMA": {"IN": ["high", "low"]}}
    },
    # Cond_2: {}=N0>nsubj {}=N1
    # scale_indicator -> subject (CA)
    {
        "LEFT_ID": "n0",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_aspect",
        "RIGHT_ATTRS": {"DEP": "nsubj"},
    },
    # Cond_3: {}=N0>/nmod:in/ {}=N2
    # scale_indicator -[nmod]-> compared_entity_1
    {
        "LEFT_ID": "n0",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_1",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nmod", "advcl", 'conj']}, "ORTH": {"NOT_IN": ["compared", "comparison", "Compared", "Comparison"]}},
    },
    # Cond_3 part_b: case:in
    # compared_entity_1 -[case]-> in
    {
        "LEFT_ID": "compared_entity_1",
        "REL_OP": ">>",
        "RIGHT_ID": "case_in_1",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": {"IN": ["in", "In"]}},
    },
]
cmp1_n1 = [
    # Cond_1: {word:/(higher|lower|high|low)/}=N0
    # scale indicator: high|higher|low|lower
    {
        "RIGHT_ID": "n0",
        "RIGHT_ATTRS": {"LEMMA": {"IN": ["high", "low"]}}
    },
    # Cond_2: {}=N0>nsubj {}=N1
    # scale_indicator -> subject (CA)
    {
        "LEFT_ID": "n0",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_aspect",
        "RIGHT_ATTRS": {"DEP": "nsubj"},
    },
    # Cond_3: {}=N1>/nmod:in/ {}=N2
    # compared_aspect -[nmod]-> compared_entity_1
    {
        "LEFT_ID": "compared_aspect",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_1",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nmod", "advcl"]}, "ORTH": {"NOT_IN": ["compared", "comparison", "Compared", "Comparison"]}},
    },
    # Cond_3 part_b: case:in
    # compared_entity_1 -[case]-> in
    {
        "LEFT_ID": "compared_entity_1",
        "REL_OP": ">>",
        "RIGHT_ID": "case_in_1",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": {"IN": ["in", "of"]}},
    },
]
cmp2_n0 = [
    # Cond_1: {lemma:/.*(increase|decrease|express|silence|reduce|elevate|change|regulate)/}=N0
    # scale indicator: increase|decrease|...
    {
        "RIGHT_ID": "n0",
        "RIGHT_ATTRS": {"LEMMA": {"IN": cmp2_triggers}}
    },
    # Cond_2: {}=N0>nsubjpass|nsubj {}=N1
    # scale_indicator -> subject (CA)
    {
        "LEFT_ID": "n0",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_aspect",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nsubjpass", "nsubj", "dobj"]}},
    },
    # Cond_3: {}=N0>/nmod:in/ {}=N2
    # scale_indicator -[nmod|advcl|dobj]-> compared_entity_1
    {
        "LEFT_ID": "n0",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_1",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nmod", "advcl", "dobj"]}, "ORTH": {"NOT_IN": ["compared", "comparison", "Compared", "Comparison"]}},
    },
    # Cond_3 part_b: case:in
    # compared_entity_1 -[case]-> in
    {
        "LEFT_ID": "compared_entity_1",
        "REL_OP": ">>",
        "RIGHT_ID": "case_in_1",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": {"IN": ["in", "In"]}},
    }
]
cmp2_n1 = [
    # Cond_1: {lemma:/.*(increase|decrease|express|silence|reduce|elevate|change|regulate)/}=N0
    # scale indicator: increase|decrease|...
    {
        "RIGHT_ID": "n0",
        "RIGHT_ATTRS": {"LEMMA": {"IN": cmp2_triggers}}
    },
    # Cond_2: {}=N0>nsubjpass {}=N1
    # scale_indicator -> subject (CA)
    {
        "LEFT_ID": "n0",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_aspect",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nsubjpass", "nsubj", "dobj"]}},
    },
    # Cond_3: {}=N1>/nmod:in/ {}=N2
    # compared_aspect -[nmod|advcl|dobj]-> compared_entity_1
    {
        "LEFT_ID": "compared_aspect",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_1",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nmod", "advcl", "dobj"]}, "ORTH": {"NOT_IN": ["compared", "comparison", "Compared", "Comparison"]}},
    },
    # Cond_3 part_b: case:in
    # compared_entity_1 -[case]-> in
    {
        "LEFT_ID": "compared_entity_1",
        "REL_OP": ">>",
        "RIGHT_ID": "case_in_1",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": {"IN": ["in", "In"]}},
    }
]
# SI is amod dep on compared_aspect
cmp3_n0_amod = [
    # Cond_1: {lemma:/.*(find|note|detect|observe|discover|occurred|occur)/}=N0
    # n0: found|noted|observed|...
    {
        "RIGHT_ID": "n0",
        "RIGHT_ATTRS": {"LEMMA": {"IN": cmp3_triggers}}
    },
    # Cond_2: {}=N0</(nsubjpass|dobj)/{}=N1
    # n0 -[nsubjpass|dobj]-> compared_aspect
    {
        "LEFT_ID": "n0",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_aspect",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nsubjpass", "dobj", "nsubj"]}}
    },
    # Cond_3: {}=N0 >/nmod:in/ {}=N2
    # n0 -[nmod]-> compared_entity_1
    {
        "LEFT_ID": "n0",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_1",
        "RIGHT_ATTRS": {"DEP": "nmod", "ORTH": {"NOT_IN": ["compared", "comparison", "Compared", "Comparison"]}},
    },
    # Cond_3 part_b: case:in
    # compared_entity_1 -[case]-> in
    {
        "LEFT_ID": "compared_entity_1",
        "REL_OP": ">>",
        "RIGHT_ID": "case_in_1",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": {"IN": ["in", "In"]}},
    },
    # Cond_5|6 {}=N1 >amod{tag:/(JJ|JJR|VBN)/}=N4
    # compared_aspect > scale_indicator
    {
        "LEFT_ID": "compared_aspect",
        "REL_OP": ">>",
        "RIGHT_ID": "scale_indicator",
        "RIGHT_ATTRS": {"DEP": "amod", "TAG": {"IN": ["JJ", "JJR", "VBN", "VBD"]}},
    }
]
# SI is xcomp dep on compared_aspect, all the rest depends on cmp3 trig
cmp3_n0_xcomp_n0 = [
    # Cond_1: {lemma:/.*(find|note|detect|observe|discover|occurred|occur)/}=N0
    # n0: found|noted|observed|...
    {
        "RIGHT_ID": "n0",
        "RIGHT_ATTRS": {"LEMMA": {"IN": cmp3_triggers}}
    },
    # Cond_2: {}=N0</(nsubjpass|dobj)/{}=N1
    # n0 -[nsubjpass|dobj]-> compared_aspect
    {
        "LEFT_ID": "n0",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_aspect",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nsubjpass", "dobj", "nsubj"]}}
    },
    # Cond_5|6 {}=N1 >amod{tag:/(JJ|JJR|VBN)/}=N4
    # compared_aspect > scale_indicator
    {
        "LEFT_ID": "n0",
        "REL_OP": ">>",
        "RIGHT_ID": "scale_indicator",
        "RIGHT_ATTRS": {"DEP": {"IN": ["xcomp", "acl"]}, "TAG": {"IN": ["JJ", "JJR", "VBN", "VBD"]}},
    },
    # Cond_3: {}=N0 >/nmod:in/ {}=N2
    # n0 -[nmod]-> compared_entity_1
    {
        "LEFT_ID": "scale_indicator",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_1",
        "RIGHT_ATTRS": {"DEP": "nmod", "ORTH": {"NOT_IN": ["compared", "comparison", "Compared", "Comparison"]}},
    },
    # Cond_3 part_b: case:in
    # compared_entity_1 -[case]-> in
    {
        "LEFT_ID": "compared_entity_1",
        "REL_OP": ">>",
        "RIGHT_ID": "case_in_1",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": {"IN": ["in", "In"]}},
    }
]
# SI is xcomp dep on cmp3 trig, all the rest depends on SI
cmp3_n0_xcomp_SI = [
    # Cond_1: {lemma:/.*(find|note|detect|observe|discover|occurred|occur)/}=N0
    # n0: found|noted|observed|...
    {
        "RIGHT_ID": "n1",
        "RIGHT_ATTRS": {"LEMMA": {"IN": cmp3_triggers}}
    },
    # Cond_2: {}=N0</(nsubjpass|dobj)/{}=N1
    # n0 -[nsubjpass|dobj]-> compared_aspect
    {
        "LEFT_ID": "n1",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_aspect",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nsubjpass", "dobj", "nsubj"]}}
    },
    # Cond_5|6 {}=N1 >amod{tag:/(JJ|JJR|VBN)/}=N4
    # compared_aspect > scale_indicator
    {
        "LEFT_ID": "n1",
        "REL_OP": ">>",
        "RIGHT_ID": "n0",
        "RIGHT_ATTRS": {"DEP": {"IN": ["ccomp", "xcomp", "acl"]}, "TAG": {"IN": ["JJ", "JJR", "VBN", "VBD"]}},
    },
    # Cond_3: {}=N0 >/nmod:in/ {}=N2
    # n0 -[nmod]-> compared_entity_1
    {
        "LEFT_ID": "n0",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_1",
        "RIGHT_ATTRS": {"DEP": "nmod", "ORTH": {"NOT_IN": ["compared", "comparison", "Compared", "Comparison"]}},
    },
    # Cond_3 part_b: case:in
    # compared_entity_1 -[case]-> in
    {
        "LEFT_ID": "compared_entity_1",
        "REL_OP": ">>",
        "RIGHT_ID": "case_in_1",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": {"IN": ["in", "In"]}},
    }
]
cmp3_n1 = [
    # Cond_1: {lemma:/.*(find|note|detect|observe|discover|occurred|occur)/}=N0
    # found_in: found|noted|observed|...
    {
        "RIGHT_ID": "n0",
        "RIGHT_ATTRS": {"LEMMA": {"IN": cmp3_triggers}}
    },
    # Cond_2: {}=N0</(nsubjpass|dobj)/{}=N1
    # found_in -[nsubjpass|dobj]-> compared_aspect
    {
        "LEFT_ID": "n0",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_aspect",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nsubjpass", "dobj", "nsubj"]}}
    },
    # Cond_3: {}=N0 >/nmod:in/ {}=N2
    # compared_aspect -[nmod]-> compared_entity_1
    {
        "LEFT_ID": "compared_aspect",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_1",
        "RIGHT_ATTRS": {"DEP": "nmod", "ORTH": {"NOT_IN": ["compared", "comparison", "Compared", "Comparison"]}},
    },
    # Cond_3 part_b: case:in
    # compared_entity_1 -[case]-> in
    {
        "LEFT_ID": "compared_entity_1",
        "REL_OP": ">>",
        "RIGHT_ID": "case_in_1",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": {"IN": ["in", "In"]}},
    },
    # Cond_5|6 {}=N1 >amod{tag:/(JJ|JJR|VBN)/}=N4
    # compared_aspect > scale_indicator
    {
        "LEFT_ID": "compared_aspect",
        "REL_OP": ">>",
        "RIGHT_ID": "scale_indicator",
        "RIGHT_ATTRS": {"DEP": "amod", "TAG": {"IN": ["JJ", "JJR", "VBN", "VBD"]}},
    }
]

# ---
# Comparison-word based patterns (cmp_rules)
# than + in
# CE2 depends on SI
than_1_SI = [
    # Cond_4: {}=N2 !>/case/ {word:than}
    # not compared_entity_1 -[case]-> than
    {
        "LEFT_ID": "case_in_1",
        "REL_OP": ";",
        "RIGHT_ID": "case_than_1",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": "than", "OP": "!"},
    },
    # Cond_5: {}=N0>/nmod:in/({}=N3 > /case/{word:than})
    # scale_indicator -[nmod|advcl]-> compared_entity_2
    {
        "LEFT_ID": "n0",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_2",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nmod", "advcl", "dep"]}},
    },
    # Cond_5b: case:in
    # compared_entity_2 -[case]-> in
    {
        "LEFT_ID": "compared_entity_2",
        "REL_OP": ">",
        "RIGHT_ID": "case_in_2",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": {"IN": ["in", "In"]}},
    },
    # Cond_5c: case:than
    # compared_entity_2 -[case]-> than
    {
        "LEFT_ID": "compared_entity_2",
        "REL_OP": ">",
        "RIGHT_ID": "case_than_2",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": "than"},
    }
]
# CE2 depends on CE1
than_1_CE1 = [
    # Cond_4: {}=N2 !>/case/ {word:than}
    # not compared_entity_1 -[case]-> than
    {
        "LEFT_ID": "case_in_1",
        "REL_OP": ";",
        "RIGHT_ID": "case_than_1",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": "than", "OP": "!"},
    },
    # Cond_5: {}=N0>/nmod:in/({}=N3 > /case/{word:than})
    # scale_indicator -[nmod|advcl]-> compared_entity_2
    {
        "LEFT_ID": "compared_entity_1",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_2",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nmod", "advcl", "dep"]}},
    },
    # Cond_5b: case:in
    # compared_entity_2 -[case]-> in
    {
        "LEFT_ID": "compared_entity_2",
        "REL_OP": ">",
        "RIGHT_ID": "case_in_2",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": {"IN": ["in", "In"]}},
    },
    # Cond_5c: case:than
    # compared_entity_2 -[case]-> than
    {
        "LEFT_ID": "compared_entity_2",
        "REL_OP": ">",
        "RIGHT_ID": "case_than_2",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": "than"},
    }
]
# versus + in
# CE2 depends on SI
vs_1_SI = [
    # Cond_4: {}=N2 !>/cc/ {word:(versus|vs.)}
    # not case_in_1 ; versus_1
    {
        "LEFT_ID": "case_in_1",
        "REL_OP": ";",
        "RIGHT_ID": "versus_1",
        "RIGHT_ATTRS": {"ORTH": {"IN": ["versus", "vs."]}, "OP": "!"},
    },
    # Cond_5: {}=N0>/nmod:in/({}=N3 > /case/{word:(versus|vs.)})
    # scale_indicator -[nmod|advcl]-> compared_entity_2
    {
        "LEFT_ID": "n0",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_2",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nmod", "advcl", "dep"]}},
    },
    # Cond_5b: case:in
    # compared_entity_2 -[case]-> in
    {
        "LEFT_ID": "compared_entity_2",
        "REL_OP": ">",
        "RIGHT_ID": "case_in_2",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": {"IN": ["in", "In"]}},
    },
    # Cond_5c: cc:{word:(versus|vs.)}
    # case_in_2 ; versus_2
    {
        "LEFT_ID": "case_in_2",
        "REL_OP": ";",
        "RIGHT_ID": "versus_2",
        "RIGHT_ATTRS": {"ORTH": {"IN": ["versus", "vs."]}},
    }
]
# CE2 depends on CE1
vs_1_CE1 = [
    # Cond_4: {}=N2 !>/cc/ {word:(versus|vs.)}
    # not case_in_1 ; versus_1
    {
        "LEFT_ID": "case_in_1",
        "REL_OP": ";",
        "RIGHT_ID": "versus_1",
        "RIGHT_ATTRS": {"ORTH": {"IN": ["versus", "vs."]}, "OP": "!"},
    },
    # Cond_5: {}=N0>/nmod:in/({}=N3 > /case/{word:(versus|vs.)})
    # scale_indicator -[nmod|advcl]-> compared_entity_2
    {
        "LEFT_ID": "compared_entity_1",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_2",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nmod", "advcl", "dep"]}},
    },
    # Cond_5b: case:in
    # compared_entity_2 -[case]-> in
    {
        "LEFT_ID": "compared_entity_2",
        "REL_OP": ">",
        "RIGHT_ID": "case_in_2",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": {"IN": ["in", "In"]}},
    },
    # Cond_5c: cc:{word:(versus|vs.)}
    # case_in_2 ; versus_2
    {
        "LEFT_ID": "case_in_2",
        "REL_OP": ";",
        "RIGHT_ID": "versus_2",
        "RIGHT_ATTRS": {"ORTH": {"IN": ["versus", "vs."]}},
    }
]
# than|versus without "in"
# CE2 depends on SI
than_2_SI = [
    # Cond_4: {}=N0>/nmod:in/({}=N3 > /case/{word:(than|versus|vs.)})
    # scale_indicator -[nmod]-> compared_entity_2
    {
        "LEFT_ID": "n0",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_2",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nmod", "dep"]}},
    },
    # Cond_5b: case:than|versus|vs.
    # compared_entity_2 -[case]-> (than|versus|vs.)
    {
        "LEFT_ID": "compared_entity_2",
        "REL_OP": ">",
        "RIGHT_ID": "case_cmp_2",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": {"IN": ["than", "versus", "vs."]}},
    },
]
# CE2 depends on CE1
than_2_CE1 = [
    # Cond_4: {}=N0>/nmod:in/({}=N3 > /case/{word:(than|versus|vs.)})
    # scale_indicator -[nmod]-> compared_entity_2
    {
        "LEFT_ID": "compared_entity_1",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_2",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nmod", "dep"]}},
    },
    # Cond_5b: case:than|versus|vs.
    # compared_entity_2 -[case]-> (than|versus|vs.)
    {
        "LEFT_ID": "compared_entity_2",
        "REL_OP": ">",
        "RIGHT_ID": "case_cmp_2",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": {"IN": ["than", "versus", "vs."]}},
    },
]
# versus with dep "cc"
# CE2 depends on SI
vs_2 = [
    # Cond_4: {}=N0>/nmod:in/({}=N3 > /case/{word:(versus|vs.)})
    # compared_entity_1 -[conj]-> compared_entity_2
    {
        "LEFT_ID": "compared_entity_1",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_2",
        "RIGHT_ATTRS": {"DEP": "conj"},
    },
    # Cond_5b: case:than|versus|vs.
    # compared_entity_1 -[cc]-> versus|vs.
    {
        "LEFT_ID": "compared_entity_1",
        "REL_OP": ">",
        "RIGHT_ID": "case_cmp_2",
        "RIGHT_ATTRS": {"DEP": "cc", "ORTH": {"IN": ["versus", "vs."]}},
    },
]
# compare_1: both CEs depends on SI
compare_1_SI = [
    # Cond_4: {}=N0 </(advcl|nmod):(compared_to|compared_with)/ {}=N3
    # scale_indicator -[advcl|nmod]-> compared_entity_2
    {
        "LEFT_ID": "n0",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_2",
        "RIGHT_ATTRS": {"DEP": {"IN": ["advcl", "nmod"]}},
    },
    # Cond_4b: case:compared|comparison
    {
        "LEFT_ID": "compared_entity_2",
        "REL_OP": ">>",
        "RIGHT_ID": "case_compared",
        "RIGHT_ATTRS": {"DEP": {"IN": ["case", "dep"]}, "ORTH": {"IN": ["compared", "comparison","Compared", "Comparison"]}},
    },
]
# compare_1_CE1: CE2 depens on CE1
compare_1_CE1 = [
    # Cond_4: {}=N0 </(advcl|nmod):(compared_to|compared_with)/ {}=N3
    # scale_indicator -[advcl|nmod]-> compared_entity_2
    {
        "LEFT_ID": "compared_entity_1",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_2",
        "RIGHT_ATTRS": {"DEP": {"IN": ["advcl", "nmod"]}},
    },
    # Cond_4b: case:compared|comparison
    {
        "LEFT_ID": "compared_entity_2",
        "REL_OP": ">>",
        "RIGHT_ID": "case_compared",
        "RIGHT_ATTRS": {"DEP": {"IN": ["case", "dep"]}, "ORTH": {"IN": ["compared", "comparison", "Compared", "Comparison"]}},
    },
]
# compare_2: SI->compared|comparison->CE2
compare_2 = [
    # Cond_4: {}=N0 /xcomp/ {word:compared}
    # scale_indicator -[xcomp|advcl|nmod|dep|prep]-> case_compared
    {
        "LEFT_ID": "n0",
        "REL_OP": ">>",
        "RIGHT_ID": "case_compared",
        "RIGHT_ATTRS": {"DEP": {"IN": ["xcomp", "advcl", "nmod", "dep", "prep"]},
                        "ORTH": {"IN": ["compared", "comparison", "Compared", "Comparison"]}},
    },
    # Cond_4b: case_compared -[nmod]-> compared_entity_2
    {
        "LEFT_ID": "case_compared",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_2",
        "RIGHT_ATTRS": {"DEP": "nmod"},
    },
]
# compared_3 : CE1->compared->CE2
compare_3 = [
    # Cond_4: {}=N2 </(advcl|nmod):(compared_to|compared_with)/ {}=N3
    # compared_entity_1 -[advcl|nmod]-> case_compared
    {
        "LEFT_ID": "compared_entity_1",
        "REL_OP": ">>",
        "RIGHT_ID": "case_compared",
        "RIGHT_ATTRS": {"DEP": {"IN": ["advcl", "nmod", "dep", "acl"]},
                        "ORTH": {"IN": ["compared", "comparison", "Compared", "Comparison"]}},
    },
    # Cond_4b: case_compared -[nmod]|advcl-> compared_entity_2
    {
        "LEFT_ID": "case_compared",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_2",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nmod", "advcl"]}},
    },

]

# ---
# TYPE B PATTERNS
# ---
# Sentence-form based patterns for retrieving EA (starter rules)
# EA is the subject/acl of the sentence and depends on level indicator
subj_exp = [
    # Cond_1: {lemma:/cmp2_triggers + cmp1_triggers/}=N0
    # level indicator: cmp2_triggers
    {
        "RIGHT_ID": "scale_indicator",
        "RIGHT_ATTRS": {"LEMMA": {"IN": cmp12B_triggers}}
    },
    # Cond_2: {}=N0>nsubjpass {}=N1
    # level_indicator (LI) -[nsubjpass]-> expressed_aspect (EA)
    {
        "LEFT_ID": "scale_indicator",
        "REL_OP": ">",
        "RIGHT_ID": "compared_aspect",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nsubjpass", "nsubj", "dep", "dobj", "acl"]}},
    }
]
# EA is linked to level indicator by a path subj-conj
conj_exp = [
    # Cond_1: {lemma:/cmp2_triggers + cmp1_triggers/}=N0
    # level indicator: cmp2_triggers
    {
        "RIGHT_ID": "conj_clause",
        "RIGHT_ATTRS": {}
    },
    # Cond_0a: {}=N0< conj {}=N3
    # level_indicator (LI) -[conj]-> conjunction
    {
        "LEFT_ID": "conj_clause",
        "REL_OP": ">>",
        "RIGHT_ID": "scale_indicator",
        "RIGHT_ATTRS": {"LEMMA": {"IN": cmp12B_triggers}, "DEP": {"IN": ["conj", "acl", "dep"]}}
    },
    # Cond_0b: {}=N3> nsubj|nsubjpass {}=N4
    # conjunction -[nsubj|nsubjpass]-> expressed_aspect
    {
        "LEFT_ID": "conj_clause",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_aspect",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nsubjpass", "nsubj", "dobj"]}},
    },
]
# EA is appos depending on head of level indicator
appos_exp = [
    # Cond_1: {lemma:/cmp2_triggers + cmp1_triggers/}=N0
    # level indicator: cmp2_triggers
    {
        "RIGHT_ID": "compared_aspect",
        "RIGHT_ATTRS": {}
    },
    # Cond_0b: {}=N3> nsubj|nsubjpass {}=N4
    # conjunction -[nsubj|nsubjpass]-> expressed_aspect
    {
        "LEFT_ID": "compared_aspect",
        "REL_OP": ">",
        "RIGHT_ID": "conj_clause",
        "RIGHT_ATTRS": {"DEP": "appos"},
    },
    # Cond_0a: {}=N0< conj {}=N3
    # level_indicator (LI) -[conj]-> conjunction
    {
        "LEFT_ID": "conj_clause",
        "REL_OP": ">",
        "RIGHT_ID": "scale_indicator",
        "RIGHT_ATTRS": {"LEMMA": {"IN": cmp12B_triggers}, "DEP": {"IN": ["conj", "acl"]}}
    }
]
# EA is the subject/dobj/acl of the sentence and depends on n0
subj_fnd = [
    # Cond_1: {lemma:/cmp3_triggers/}=N0
    # n0: cmp3_triggers
    {
        "RIGHT_ID": "n0",
        "RIGHT_ATTRS": {"LEMMA": {"IN": cmp3_triggers}}
    },
    # Cond_2: {}=N0>nsubjpass|nsubj {}=N1
    # n0 -[nsubjpass|nsubj]-> expressed_aspect (EA)
    {
        "LEFT_ID": "n0",
        "REL_OP": ">",
        "RIGHT_ID": "compared_aspect",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nsubj", "nsubjpass", "dep", "acl", "dobj"]}},
    }
]
# EA is linked to n0 by a path subj-conj
conj_fnd = [
    # Cond_1: {lemma:/cmp2_triggers + cmp1_triggers/}=N0
    # level indicator: cmp2_triggers
    {
        "RIGHT_ID": "conj_clause",
        "RIGHT_ATTRS": {}
    },
    # Cond_0: {}=N0< conj {}=N3
    # level_indicator (LI) -[conj]-> conjunction
    {
        "LEFT_ID": "conj_clause",
        "REL_OP": ">",
        "RIGHT_ID": "n0",
        "RIGHT_ATTRS": {"LEMMA": {"IN": cmp3_triggers}, "DEP": "conj"}
    },
    # Cond_0b: {}=N3> nsubj|nsubjpass {}=N4
    # conjunction -[nsubj|nsubjpass]-> expressed_aspect
    {
        "LEFT_ID": "conj_clause",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_aspect",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nsubjpass", "nsubj"]}},
    },
]

# ---
# Patterns to retrieve express_location (cmp_rules)
# express_location depends on level_indicator
expressionIn_1 = [
    # Cond_3: {}=N0>/nmod:in/ {}=N2
    # level_indicator -[nmod]-> expression_location (EL)
    {
        "LEFT_ID": "scale_indicator",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_1",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nmod", "dobj"]}},
    },
    # Cond_3 part_b: case:in
    # expression_location -[case]-> in
    {
        "LEFT_ID": "compared_entity_1",
        "REL_OP": ">>",
        "RIGHT_ID": "case_in",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": {"IN": ["in", "In"]}},
    }
]
# express_location depends on expressed_aspect
expressionIn_2 = [
    # Cond_3: {}=N1>/nmod:in/ {}=N2
    # expressed_aspect -[nmod]-> expression_location (EL)
    {
        "LEFT_ID": "compared_aspect",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_1",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nmod", "dobj"]}},
    },
    # Cond_3 part_b: case:in
    # expression_location -[case]-> in
    {
        "LEFT_ID": "compared_entity_1",
        "REL_OP": ">>",
        "RIGHT_ID": "case_in",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": {"IN": ["in", "In"]}},
    }
]
# express_location depends on n0, LI dep 'amod' on n0
foundIn_1 = [
    # Cond_3: {}=N0>/nmod:in/ {}=N2
    # n0 -[nmod]-> expression_location (EL)
    {
        "LEFT_ID": "n0",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_1",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nmod", "dobj"]}},
    },
    # Cond_3 part_b: case:in
    # expression_location -[case]-> in
    {
        "LEFT_ID": "compared_entity_1",
        "REL_OP": ">>",
        "RIGHT_ID": "case_in",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": {"IN": ["in", "In"]}},
    },
    # Cond_4: {}=N1 >amod {tag:/(JJ|JJR|VBN)/}=N3
    # expressed_aspect -[amod]-> level_indicator
    {
        "LEFT_ID": "compared_aspect",
        "REL_OP": ">",
        "RIGHT_ID": "scale_indicator",
        "RIGHT_ATTRS": {"DEP": "amod", "TAG": {"IN": ['JJ', 'JJR', 'VBN', 'VBD']}},
    }
]
# express_location depends on expressed_aspect, LI dep 'amod' on n0
foundIn_2 = [
    # Cond_3: {}=N1>/nmod:in/ {}=N2
    # expressed_aspect -[nmod]-> expression_location (EL)
    {
        "LEFT_ID": "compared_aspect",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_1",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nmod", "dobj"]}},
    },
    # Cond_3 part_b: case:in
    # expression_location -[case]-> in
    {
        "LEFT_ID": "compared_entity_1",
        "REL_OP": ">>",
        "RIGHT_ID": "case_in",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": {"IN": ["in", "In"]}},
    },
    # Cond_4: {}=N1 >amod {tag:/(JJ|JJR|VBN)/}=N3
    # expressed_aspect -[amod]-> level_indicator
    {
        "LEFT_ID": "compared_aspect",
        "REL_OP": ">",
        "RIGHT_ID": "scale_indicator",
        "RIGHT_ATTRS": {"DEP": "amod", "TAG": {"IN": ['JJ', 'JJR', 'VBN', 'VBD']}},
    }
]
# level_indicator is xcomp, expression_location depends on level_indicator
EXPfoundIn_xcomp_1 = [
    # Cond_4: {}=N0>/xcomp|conj/ {}=N3
    # n0 -[xcomp|conj]-> level_indicator (LI)
    {
        "LEFT_ID": "n0",
        "REL_OP": ">",
        "RIGHT_ID": "scale_indicator",
        "RIGHT_ATTRS": {"DEP": {"IN": ["xcomp", "ccomp", "advcl"]}, "TAG": {"IN": ['JJ', 'JJR', 'VBN', 'VBD']}},
    },
    # Cond_3: {}=N1>/nmod:in/ {}=N2
    # expressed_aspect -[nmod]-> expression_location (EL)
    {
        "LEFT_ID": "scale_indicator",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_1",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nmod", "dobj"]}},
    },
    # Cond_3 part_b: case:in
    # expression_location -[case]-> in
    {
        "LEFT_ID": "compared_entity_1",
        "REL_OP": ">>",
        "RIGHT_ID": "case_in",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": {"IN": ["in", "In"]}},
    },
]
# level_indicator is xcomp, expression_location depends on n0
EXPfoundIn_xcomp_2 = [
    # Cond_4: {}=N0>/xcomp|conj/ {}=N3
    # n0 -[xcomp|conj]-> level_indicator (LI)
    {
        "LEFT_ID": "n0",
        "REL_OP": ">",
        "RIGHT_ID": "scale_indicator",
        "RIGHT_ATTRS": {"DEP": {"IN": ["xcomp", "ccomp", "advcl"]}, "TAG": {"IN": ['JJ', 'JJR', 'VBN', 'VBD']}},
    },
    # Cond_3: {}=N1>/nmod:in/ {}=N2
    # expressed_aspect -[nmod]-> expression_location (EL)
    {
        "LEFT_ID": "n0",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_1",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nmod", "dobj"]}},
    },
    # Cond_3 part_b: case:in
    # expression_location -[case]-> in
    {
        "LEFT_ID": "compared_entity_1",
        "REL_OP": ">>",
        "RIGHT_ID": "case_in",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": {"IN": ["in", "In"]}},
    },
]
# level_indicator is xcomp, expression_location depends on level_indicator
RBfoundIn_xcomp = [
    # Cond_4: {}=N0>/xcomp|conj/ {}=N3
    # n0 -[xcomp|conj]-> level_indicator (LI)
    {
        "LEFT_ID": "n0",
        "REL_OP": ">",
        "RIGHT_ID": "scale_indicator",
        "RIGHT_ATTRS": {"DEP": {"IN": ["xcomp", "ccomp"]}, "TAG": "RB"},
    },
    {
        "LEFT_ID": "scale_indicator",
        "REL_OP": ">",
        "RIGHT_ID": "adverb",
        "RIGHT_ATTRS": {"DEP": "acl"},
    },
    # Cond_3: {}=N1>/nmod:in/ {}=N2
    # expressed_aspect -[nmod]-> expression_location (EL)
    {
        "LEFT_ID": "adverb",
        "REL_OP": ">>",
        "RIGHT_ID": "compared_entity_1",
        "RIGHT_ATTRS": {"DEP": {"IN": ["nmod", "dobj"]}},
    },
    # Cond_3 part_b: case:in
    # expression_location -[case]-> in
    {
        "LEFT_ID": "compared_entity_1",
        "REL_OP": ">>",
        "RIGHT_ID": "case_in",
        "RIGHT_ATTRS": {"DEP": "case", "ORTH": {"IN": ["in", "In"]}},
    },
]


def relation_extraction(sentence, nlp, verbose=False, debug=False):
    """
    Relation Extraction Module

    :param sentence: (spacy.tokens.doc.Doc) input sentence
    :param nlp: (spacy.language) nlp object Spacy model.
    :param verbose: (Boolean) if True display diagnostic prints
    :param debug: (Boolean) if True not raise an exception but return 'rule_not_found'

    :return: list(dict()) list of dictionary of extracted components with the following keys: scale_indicator
            (spacy.tokens), compared_aspect (spacy.tokens.doc.Doc.ents), compared_entity_1 (spacy.tokens.doc.Doc.ents),
            compared_entity_2 (spacy.tokens.doc.Doc.ents)
    :return: string containing sentence_type
    :return: list of applied rules for debugging purposes
    """
    rules = []
    rules_list = find_rule(sentence, verbose)
    if not rules_list:
        if verbose:
            print('No rules for TypeA sentences, trying for TypeB')
        return re_module_b(sentence, nlp, verbose, debug)
    # List of matches that will be returned
    results = []
    check_duplicate = []
    matcher = DependencyMatcher(nlp.vocab)
    rule_name = rules_list[0]['name']
    rules.append(rule_name)
    print("Using rule: " + rule_name)
    matcher.add(rule_name, [rules_list[0]['starter'] + rules_list[0]['cmp']])
    matches = matcher(sentence)
    if matches:
        if verbose:
            print("Number of matches: " + str(len(matches)))
            print("Extracting components from matches")
        # Storing components in a dictionary
        for components in extract_components(sentence, 'TypeA', matches, matcher, rule_name, nlp, verbose):
            # Discard duplicate matches, if any
            tmp = [components['scale_indicator'].text, components['compared_aspect'].text,
                   components['compared_entity_1'].text, components['compared_entity_2'].text]
            if tmp not in check_duplicate:
                check_duplicate.append(tmp)
                results.append(components)
    prev_rule = rules_list[0]
    for j in range(1, len(rules_list)):
        # Removing previous rule
        matcher.remove(prev_rule['name'])
        # Adding next rule to the DependencyMatcher
        rule_name = rules_list[j]['name']
        rules.append(rule_name)
        print("Using rule: " + rule_name)
        # Adding comparison pattern based on retrieved information
        matcher.add(rule_name, [rules_list[j]['starter'] + rules_list[j]['cmp']])
        matches = matcher(sentence)
        # Extracting components from matched results
        if matches:
            if verbose:
                print("Number of matches: " + str(len(matches)))
                print("Extracting components from matches")
            # Storing components in a dictionary
            for components in extract_components(sentence, 'TypeA', matches, matcher, rule_name, nlp, verbose):
                # Discard duplicate matches, if any
                tmp = [components['scale_indicator'].text, components['compared_aspect'].text,
                       components['compared_entity_1'].text, components['compared_entity_2'].text]
                if tmp not in check_duplicate:
                    check_duplicate.append(tmp)
                    results.append(components)
        # Updating previous rule
        prev_rule = rules_list[j]
    if not results:
        if verbose:
            print('No TypeA matches, trying for typeB matches')
        return re_module_b(sentence, nlp, verbose, debug)
    if verbose:
        print('Returning TypeA matches')
    return results, 'TypeA', rules


def re_module_b(sentence, nlp, verbose, debug):
    """
    Relation Extraction module for TypeB sentences. If RE module fails and debug is False raise an Exception
    otherwise return None, string message, list of used rules

    :param sentence: (spacy.tokens.doc.Doc) input sentence
    :param nlp: (spacy.language) nlp object Spacy model.
    :param verbose: (Boolean) if True display diagnostic prints
    :param debug: (Boolean) if True also return list of rules used

    :return: list(dict()) list of dictionary of extracted components with the following keys: scale_indicator
            (spacy.tokens), compared_aspect (spacy.tokens.doc.Doc.ents), compared_entity_1 (spacy.tokens.doc.Doc.ents),
            compared_entity_2 (spacy.tokens.doc.Doc.ents)
    :return: string containing sentence_type
    :return: list of applied rules for debugging purposes
    """
    rules = []
    # Return list of rules that can be applied to the sentence
    rules_list = find_rule_b(sentence, verbose)
    if not rules_list:
        if verbose:
            print('No rule found')
        if debug:
            return None, 'match_not_found', rules
        else:
            raise MatchNotFound
    # List of matches that will be returned
    results = []
    # Create DependencyMatcher object
    matcher = DependencyMatcher(nlp.vocab)
    rule_name = rules_list[0]['name']
    rules.append(rule_name)
    if verbose:
        print("Using rule: " + rule_name)
    matcher.add(rule_name, [rules_list[0]['starter'] + rules_list[0]['cmp']])
    matches = matcher(sentence)
    if matches:
        if verbose:
            print("Number of matches: " + str(len(matches)))
            print("Extracting components from matches")
        # Storing components in a dictionary
        for components in extract_components(sentence, 'TypeB', matches, matcher, rule_name, nlp, verbose):
            results.append(components)
    prev_rule = rules_list[0]
    for j in range(1, len(rules_list)):
        matcher.remove(prev_rule['name'])
        rule_name = rules_list[j]['name']
        rules.append(rule_name)
        if verbose:
            print("Using rule: " + rule_name)
        # Adding comparison pattern based on retrieved information
        matcher.add(rule_name, [rules_list[j]['starter'] + rules_list[j]['cmp']])
        matches = matcher(sentence)
        # Extracting components from matched results
        if matches:
            if verbose:
                print("Number of matches: " + str(len(matches)))
                print("Extracting components from matches")
            # Storing components in a dictionary
            for components in extract_components(sentence, 'TypeB', matches, matcher, rule_name, nlp, verbose):
                results.append(components)
        prev_rule = rules_list[j]
    if not results:
        if verbose:
            print('RE module failed')
        if debug:
            return None, 'match_not_found', rules
        else:
            raise MatchNotFound
    if verbose:
        print('Returning TypeB matches')
    return results, 'TypeB', rules


def find_rule(sentence, verbose):
    """
    Finding TypeA rules that can be applied to the sentence based on its structure.

    :param sentence: (spacy.tokens.doc.Doc) input sentence
    :param verbose: (Boolean) if True display diagnostic prints

    :return: list(dict()) list of dictionaries with rule names and pattern to be applied to the sentence.
    """
    # Comparison word (i.e., 'than'|'versus'|'compared'|'comparison')
    cmps = [t for t in sentence if (t.text.lower() in cmp_triggers and t.dep_ in ['case', 'cc']) or
            (t.text.lower() in ['compared', 'comparison'] and t.dep_ in ['case', 'dep', 'xcomp', 'advcl', 'prep', 'nmod', 'acl'])]
    if cmps:
        rules = []
        # Checking for cmp1 triggers
        if [t for t in sentence if t.lemma_ in cmp1_triggers]:
            if verbose:
                print('There is a cmp1 trigger ***')
            # Check if there is a cmp_rule that can be applied
            cmp_rule = find_cmp_rule(sentence, cmps, cmp1_triggers, verbose)
            if cmp_rule is not None:
                if verbose:
                    print('*** cmp1 rules can be applied ***')
                # Both CE1 and CE2 depends on the scale_indicator
                rules.append({'name': 'cmp1_n0_' + cmp_rule[0], 'starter': cmp1_n0, 'cmp': cmp_rule[1]})
                # CE1 depends on the scale_indicator, CE2 depends on the compared_aspect
                rules.append({'name': 'cmp1_n1_' + cmp_rule[0], 'starter': cmp1_n1, 'cmp': cmp_rule[1]})
            else:
                if verbose:
                    print('cmp_rule is None, failed to apply cmp1 rules')
        # Checking for cmp2 triggers
        if [t for t in sentence if t.lemma_ in cmp2_triggers]:
            if verbose:
                print('There is a cmp2 trigger ***')
            # Check if there is a cmp_rule that can be applied
            cmp_rule = find_cmp_rule(sentence, cmps, cmp2_triggers, verbose)
            if cmp_rule is not None:
                if verbose:
                    print('*** cmp2 rules can be applied ***')
                # Both CE1 and CE2 depends on the scale_indicator
                rules.append({'name': 'cmp2_n0_' + cmp_rule[0], 'starter': cmp2_n0, 'cmp': cmp_rule[1]})
                # CE1 depends on the scale_indicator, CE2 depends on the compared_aspect
                rules.append({'name': 'cmp2_n1_' + cmp_rule[0], 'starter': cmp2_n1, 'cmp': cmp_rule[1]})
            else:
                if verbose:
                    print('cmp_rule is None, failed to apply cmp2 rules')
        # Checking for cmp3 triggers
        if [t for t in sentence if t.lemma_ in cmp3_triggers]:
            if verbose:
                print('There is a cmp3 trigger ***')
            # Check if there is a cmp_rule that can be applied
            cmp_rule = find_cmp_rule(sentence, cmps, cmp3_triggers, verbose)
            if cmp_rule is not None:
                if verbose:
                    print('*** cmp3 rules can be applied ***')
                # SI is amod dep on compared_aspect
                rules.append({'name': 'cmp3_n0_amod_' + cmp_rule[0], 'starter': cmp3_n0_amod, 'cmp': cmp_rule[1]})
                # SI is xcomp dep on compared_aspect, all the rest depends on cmp3 trig
                rules.append({'name': 'cmp3_n0_xcomp_n0_' + cmp_rule[0], 'starter': cmp3_n0_xcomp_n0, 'cmp': cmp_rule[1]})
                # SI is xcomp dep on cmp3 trig, all the rest depends on SI
                rules.append({'name': 'cmp3_n0_xcomp_SI_' + cmp_rule[0], 'starter': cmp3_n0_xcomp_SI, 'cmp': cmp_rule[1]})
                # CE1 depends on the scale_indicator, CE2 depends on the compared_aspect
                rules.append({'name': 'cmp3_n1_' + cmp_rule[0], 'starter': cmp3_n1, 'cmp': cmp_rule[1]})
            else:
                if verbose:
                    print('cmp_rule is None, failed to apply cmp3 rules')
        if [t for t in sentence if t.lemma_ in cmp1_triggers if t.dep_ == 'xcomp']:
            # Check if there is a cmp_rule that can be applied
            cmp_rule = find_cmp_rule(sentence, cmps, cmp1_triggers, verbose)
            if cmp_rule is not None:
                if verbose:
                    print('*** cmp3_n0_xcomp_SI rule can be applied ***')
                # SI is xcomp dep on cmp3 trig, all the rest depends on SI (cmp1 trigger)
                rules.append({'name': 'cmp3_n0_xcomp_SI_' + cmp_rule[0], 'starter': cmp3_n0_xcomp_SI, 'cmp': cmp_rule[1]})
        if [t for t in sentence if t.lemma_ in cmp2_triggers if t.dep_ == 'xcomp']:
            # Check if there is a cmp_rule that can be applied
            cmp_rule = find_cmp_rule(sentence, cmps, cmp2_triggers, verbose)
            if cmp_rule is not None:
                if verbose:
                    print('*** cmp3_n0_xcomp_SI rule can be applied ***')
                # SI is xcomp dep on cmp3 trig, all the rest depends on SI (cmp2 trigger)
                rules.append({'name': 'cmp3_n0_xcomp_SI_' + cmp_rule[0], 'starter': cmp3_n0_xcomp_SI, 'cmp': cmp_rule[1]})
        if rules:
            print('Returning TypeA rules')
            return rules
        else:
            if verbose:
                print('No comparison word in the sentence, try for type-B sentence')
            return None
    else:
        if verbose:
            print('No comparison word in the sentence, try for type-B sentence')
        return None


def find_cmp_rule(sentence, cmps, triggers, verbose):
    """
    Finding Comparison-word based patterns that can be applied to the TypeA sentence.

    :param sentence: (spacy.tokens.doc.Doc) input sentence
    :param cmps: (list(String)) list of comparison word found in the sentence.
    :param triggers: (list(String)) list of scale_indicator triggers.
    :param verbose: (Boolean) if True display diagnostic prints

    :return: list() list with rule names and pattern to be applied to the sentence.
    """

    for cmp_word in cmps:
        if cmp_word.text.lower() == "than":
            # than + in
            if [t for t in sentence if t.dep_ == 'case' and t.text == 'in' and t.head == cmp_word.head]:
                # CE2 depends on SI
                if cmp_word.head.head.lemma_ in triggers:
                    if verbose:
                        print('*** cmp_rule found: than_1_SI')
                    return ["than_1_SI", than_1_SI]
                # CE2 depends on CE1
                elif cmp_word.head.head.head.lemma_ in triggers or cmp_word.head.head.head.head.lemma_ in triggers:
                    if verbose:
                        print('*** cmp_rule found: than_1_CE1')
                    return ["than_1_CE1", than_1_CE1]
            # than
            else:
                # CE2 depends on SI
                if cmp_word.head.head.lemma_ in triggers:
                    if verbose:
                        print('*** cmp_rule found: than_2_SI')
                    return ["than_2_SI", than_2_SI]
                # CE2 depends on CE1
                elif cmp_word.head.head.head.lemma_ in triggers or cmp_word.head.head.head.head.lemma_ in triggers:
                    if verbose:
                        print('*** cmp_rule found: than_2_CE1')
                    return ["than_2_CE1", than_2_CE1]
        elif cmp_word.text.lower() == "versus" or cmp_word.text.lower() == "vs.":
            # Check 'versus' dependencies
            if cmp_word.dep_ == 'case':
                # versus + in
                if [t for t in sentence if t.dep_ == 'case' and t.text == 'in' and t.head == cmp_word.head]:
                    # CE2 depends on SI
                    if cmp_word.head.head.lemma_ in triggers:
                        if verbose:
                            print('*** cmp_rule found: vs_1_SI')
                        return ["vs_1_SI", vs_1_SI]
                    # CE2 depends on CE1
                    elif cmp_word.head.head.head.lemma_ in triggers or cmp_word.head.head.head.lemma_ in triggers:
                        if verbose:
                            print('*** cmp_rule found: vs_1_CE1')
                        return ["vs_1_CE1", vs_1_CE1]
                else:
                    # versus with dep "case"
                    if cmp_word.dep_ == 'case':
                        if verbose:
                            print('*** cmp_rule found: than_2')
                        return ["than_2_SI", than_2_SI]
            # versus with dep "cc"
            elif cmp_word.dep_ == 'cc':
                if verbose:
                    print('*** cmp_rule found: vs_2')
                return ["vs_2", vs_2]
            else:
                if verbose:
                    print('*** No cmp_rule found')
                return None
        elif cmp_word.text.lower() == "compared" or cmp_word.text.lower() == "comparison":
            # if compared have no children with dependency "nmod" then both CEs depends on the SI
            if not [t for t in cmp_word.children if t.dep_ == "nmod"]:
                # CE2 depends on SI
                if cmp_word.head.head.lemma_ in triggers:
                    if verbose:
                        print('*** cmp_rule found: compare_1_SI')
                    return ["compare_1_SI", compare_1_SI]
                # CE2 depends on CE1
                else:
                    if verbose:
                        print('*** cmp_rule found: compare_1_CE1')
                    return ["compare_1_CE1", compare_1_CE1]
            else:
                # SI|n0 > compared|comparison > CE2
                if cmp_word.head.lemma_ in triggers:
                    if verbose:
                        print('*** cmp_rule found: compare_2')
                    return ['compare_2', compare_2]
                # CE1 > compared|comparison > CE2, CE1 may depend on SI or CA
                elif cmp_word.head.head.lemma_ in triggers or cmp_word.head.head.head.lemma_ in triggers:
                    if verbose:
                        print('*** cmp_rule found: compare_3')
                    return ['compare_3', compare_3]
    if verbose:
        print('*** No cmp_rule found')
    return None


def find_rule_b(sentence, verbose):
    """
    Finding TypeB rules that can be applied to the sentence based on its structure.

    :param sentence: (spacy.tokens.doc.Doc) input sentence
    :param verbose: (Boolean) if True display diagnostic prints

    :return: list(dict()) list of dictionaries with rule names and pattern to be applied to the sentence.
    """
    rules = []
    # Check if any subject depends on a possible level indicator (i.e, cmp1/2 trigger) (t.head is the level indicator)
    subjs_trigs = [t for t in sentence if
                   t.dep_ in ['nsubjpass', 'nsubj', 'dep', 'dobj', 'acl'] and t.head.lemma_ in cmp1_triggers + cmp2_triggers]
    expIn_trigs = [t.head for t in subjs_trigs]
    # Check if any cmp1/2 trigger has a dep 'conj' and its head have a subject/appos dependant
    conj_expIn_trigs = [t for t in sentence if
                        t.dep_ in ['conj', 'acl', 'dep'] and t.lemma_ in cmp1_triggers + cmp2_triggers]
    appos_expIn_trigs = [t for t in sentence if t.dep_ in ['conj', 'acl', 'dep'] and
                        t.lemma_ in cmp1_triggers + cmp2_triggers and t.head.dep_ == 'appos']
    cmp3s = [t for t in sentence if t.lemma_ in cmp3_triggers]
    if subjs_trigs:
        if verbose:
            print('Rules where EA is the subject/acl of the sentence and depends on level indicator can be applied')
        # express_location depends on level_indicator
        rules.append({'name': 'subj_expressionIn_1', 'starter': subj_exp, 'cmp': expressionIn_1})
        # express_location depends on expressed_aspect
        rules.append({'name': 'subj_expressionIn_2', 'starter': subj_exp, 'cmp': expressionIn_2})
    if conj_expIn_trigs:
        if verbose:
            print('Rules where EA is linked to level indicator by a path subj-conj can be applied')
        # express_location depends on level_indicator
        rules.append({'name': 'conj_expressionIn_1', 'starter': conj_exp, 'cmp': expressionIn_1})
        # express_location depends on expressed_aspect
        rules.append({'name': 'conj_expressionIn_2', 'starter': conj_exp, 'cmp': expressionIn_2})
    if appos_expIn_trigs:
        if verbose:
            print('Rules where EA is appos depending on head of level indicator can be applied')
        # express_location depends on level_indicator
        rules.append({'name': 'appos_expressionIn_1', 'starter': appos_exp, 'cmp': expressionIn_1})
        # express_location depends on expressed_aspect
        rules.append({'name': 'appos_expressionIn_2', 'starter': appos_exp, 'cmp': expressionIn_2})
    if cmp3s:
        # Check if there is a subject/dobj/acl that depends on cmp3 trigs
        subj = [t for t in sentence if t.dep_ in ['nsubjpass', 'nsubj', 'dep', 'dobj', 'acl'] and t.head in cmp3s]
        # Check if any cmp3 trig have a dep 'conj' and its head have a subject dependant
        conj = [t for t in cmp3s if t.dep_ == "conj"
                and [c for c in t.head.children if c.dep_ in ['nsubj', 'nsubjpass', 'dep']]]
        starters = []
        if verbose:
            print('*** Sentence contains cmp3s triggers ***')
        if subj:
            if verbose:
                print('Rules where EA is the subject/dobj/acl of the sentence and depends on cmp3 trigger can be applied')
                print('Checking for cmp_rule')
            starters.append(['subj_fnd', subj_fnd])
        if conj:
            if verbose:
                print('Rules where EA is linked to n0 by a path subj-conj and depends on cmp3 trigger can be applied')
                print('Checking for cmp_rule')
            starters.append(['conj_fnd', conj_fnd])
        if starters:
            # level indicator is an adjective whose dep is 'amod'
            if [t for t in sentence if t.dep_ == 'amod' and t.tag_ in ['JJ', 'JJR', 'VBN', 'VBD']]:
                if verbose:
                    print('Rules where LI is amod can be applied')
                for s in starters:
                    # express_location depends on cmp3 trigger, LI dep 'amod' on cmp3 trigger
                    rules.append({'name': s[0] + '_foundIn_1', 'starter': s[1], 'cmp': foundIn_1})
                    # express_location depends on expressed_aspect, LI dep 'amod' on cmp3 trigger
                    rules.append({'name': s[0] + '_foundIn_2', 'starter': s[1], 'cmp': foundIn_2})
            # level indicator is an adverb
            if [t for t in sentence if t.dep_ in ['xcomp', 'ccomp'] and t.tag_ == 'RB' and t.head in cmp3s]:
                if verbose:
                    print('Rules where LI is adverb can be applied')
                for s in starters:
                    # level_indicator is xcomp, expression_location depends on level_indicator
                    rules.append({'name': s[0] + '_RBfoundIn_xcomp', 'starter': s[1], 'cmp': RBfoundIn_xcomp})
            # level indicator is an adjective whose dep is 'xcomp'/'ccomp'/'advcl'
            if [t for t in sentence if
                t.dep_ in ['xcomp', 'ccomp', 'advcl'] and t.tag_ in ['JJ', 'JJR', 'VBN', 'VBD'] and t.head in cmp3s]:
                if verbose:
                    print('Rules where LI is xcomp can be applied')
                for s in starters:
                    # level_indicator is xcomp, expression_location depends on level_indicator
                    rules.append({'name': s[0] + '_EXPfoundIn_xcomp_1', 'starter': s[1], 'cmp': EXPfoundIn_xcomp_1})
                    # level_indicator is xcomp, expression_location depends on cmp3 trigger
                    rules.append({'name': s[0] + '_EXPfoundIn_xcomp_2', 'starter': s[1], 'cmp': EXPfoundIn_xcomp_2})
    if rules:
        if verbose:
            print('Returning TypeB rules')
        return rules
    else:
        return None


def extract_components(sentence, sen_type, matches, matcher, rule_name, nlp, verbose):
    """
    Storing components in a dictionary {'match_id': {'comparison_component': (token|entity)}}.

    :param sentence: (spacy.tokens.doc.Doc) input sentence
    :param sen_type: (string) sentence type
    :param matches:  (list[tuple[int, list[int]]]) list of matches for the sentence
    :param matcher: (spacy.matcher.DependencyMatcher) matcher object
    :param rule_name: (string) rule used.
    :param nlp: (spacy.language) nlp object Spacy model.
    :param verbose: (Boolean) if True display diagnostic prints

    :return: list of dictionary {'comparison_component': (token|entity)} for each match.
    """
    # List of matches to be returned
    comp_list = []

    for idx in range(len(matches)):
        match_id, token_ids = matches[idx]
        on_match, [patterns] = matcher.get(nlp.vocab[match_id].text)
        # Create dictionary entry for the current match
        comp_dict = {}
        # Populate the new entry with token or entity corresponding to the component of the comparison
        for i in range(len(token_ids)):
            if verbose:
                print(f'Extracting {patterns[i]["RIGHT_ID"]}, expanding {sentence[token_ids[i]].text}')
            # Skip components used only for semgrex matching
            if patterns[i]["RIGHT_ID"] in component_keys:
                if patterns[i]["RIGHT_ID"] == 'n0' and (rule_name.startswith(('cmp1', 'cmp2', 'cmp3', 'cmp12')) or rule_name in
                        ['subj_foundIn_1', 'subj_foundIn_2', 'dobj_foundIn_2', 'conj_foundIn_1', 'conj_foundIn_2']):
                    # In such rules n0 corresponds to the scale_indicator
                    component = 'scale_indicator'
                else:
                    component = patterns[i]['RIGHT_ID']
                # Expanding "that" to retrieve the related entity
                if sentence[token_ids[i]].pos_ == "DET" and sentence[token_ids[i]].text in ['that', 'those']:
                    heads = [t for t in sentence if (t.head == sentence[token_ids[i]] and t.dep_ in ["nmod", "acl"])]
                    if heads:
                        token_ids[i] = heads[0].i
                # Expanding 'which' in CA/CE1/CE2
                if component in ['compared_aspect', 'compared_entity_1', 'compared_entity_2'] and sentence[token_ids[i]].text in ['which', 'that']:
                    # Expanding 'which' following the dependency 'acl:relcl'
                    if sentence[token_ids[i]].head.dep_ == 'acl:relcl':
                        token_ids[i] = sentence[token_ids[i]].head.head.i
                # Extracting components (all outgoing edges from matched token)
                children = [t for t in sentence[token_ids[i]].children]
                # Expanding CE1/CE2 if tokens have any children
                if children and component not in ['n0', 'scale_indicator']:
                    children.append(sentence[token_ids[i]])
                    children.sort(key=lambda t: t.i)
                    start = min(children[0].i, token_ids[i])
                    end = max(children[len(children)-1].i+1, token_ids[i]+1)
                    prev_component = sentence[token_ids[i]:token_ids[i]+1]
                    # Expanding until new tokens have children
                    while True:
                        children = []
                        for j in range(start, end):
                            if sentence[j] not in prev_component:
                                for c in sentence[j].children:
                                    children.append(c)
                        if verbose:
                            print(children)
                        if children:
                            children.sort(key=lambda t: t.i)
                            prev_component = sentence[start:end]
                            start = min(children[0].i, start)
                            end = max(children[len(children) - 1].i + 1, end)
                            if verbose:
                                print('new component:', sentence[start:end])
                        else:
                            break
                    # Bounding start-end of the compared_entities
                    for j in range(start, end):
                        # Bounding CE1 start:  CE1 must start with 'in'
                        if component == 'compared_entity_1':
                            prev_end = end
                            if sentence[start].text.lower() == 'of':
                                # Expanding CE1 with previous tokens until we find 'in'
                                k = start
                                while k > 0:
                                    if sentence[k].text.lower() == 'in' and sentence[k + 1].text.lower() not in cmp_triggers:
                                        # Updating start
                                        start = k
                                        break
                                    else:
                                        k = k-1
                            elif sentence[start].text.lower() != 'in' and sentence[j].text.lower() == 'in' and sentence[j + 1].text.lower() not in cmp_triggers:
                                # Start from j
                                start = j
                            # Bounding CE1 end:  CE1 must end before cmp_trigger (if sen_type == 'TypeA')
                            for k in range(start, end):
                                if sen_type == 'TypeA' and component == 'compared_entity_1' and sentence[k].text.lower() in cmp_triggers:
                                    # Updating end
                                    end = k
                                    # Expansion completed, exit inner for loop
                                    break
                            if end == prev_end:
                                # look for cmp_trigger after end, stop also if verb is found
                                for k in range(end, len([t for t in sentence])):
                                    if component == 'compared_entity_1':
                                        end = k
                                        if (sen_type == 'TypeA' and sentence[k].text.lower() in cmp_triggers) \
                                                or (sentence[k].tag_ == 'CC' and not [t for t in sentence[k].head.children if t.dep_ == 'conj']):
                                            # Expansion completed, exit loop
                                            break
                                # Expansion competed, exit outer loop
                                break
                            else:
                                # Expansion completed, exit outer loop
                                break
                        # Bounding CE2 start: CE2 must start with cmp_trigger
                        elif component == 'compared_entity_2':
                            prev_start = start
                            for k in range(start, end):
                                if sentence[j].text.lower() in cmp_triggers:
                                    start = j
                                    if verbose:
                                        print('new start detected:', sentence[start:end])
                                    break
                            if start == prev_start:
                                if verbose:
                                    print('bounding compared_entity_2 start outside')
                                # look for cmp_trigger before start
                                j = start
                                while j > 0:
                                    if sentence[j].text.lower() in cmp_triggers:
                                        start = j
                                        if verbose:
                                            print('new start detected:', sentence[start:end])
                                        # Expansion completed, exit while loop
                                        break
                                    else:
                                        j = j-1
                                if verbose:
                                    print('start remains unchanged')
                                # Expansion competed, exit outer loop
                                break
                            else:
                                # Expansion completed, exit outer loop
                                break
                    # Expand component if next token is a closing bracket
                    if end+1 < len([t for t in sentence]) and sentence[end+1].text == ')':
                        end = end+1
                    # Expand component if it does not contain an entity but there is an entity right after it
                    if not [e for e in sentence[start:end].ents] and [e for e in sentence.ents if (end+1 in range(e.start, e.end))]:
                        # Extracting the entity
                        end = [e for e in sentence.ents if (end+1 in range(e.start, e.end))][0].end
                    if verbose:
                        print(f'Adding expandend component {sentence[start:end]}')
                    comp_dict[component] = sentence[start:end]
                else:
                    if verbose:
                        print(f'Adding component {sentence[token_ids[i]]}')
                    # Other components remains unchanged (i.e., scale_indicator)
                    comp_dict[component] = sentence[token_ids[i]]
        if verbose:
            print('Adding components to the list of matches')
        comp_list.append(comp_dict)
    return comp_list
