# define Python user-defined exceptions
class Error(Exception):
    """Base class for other exceptions"""
    def __str__(self):
        return 'Test'


class PubMedIDNotFound(Exception):
    """Raised when PubTator cannot find the required pmid"""
    def __str__(self):
        return 'Failed to retrieve the annotations for the given PubMed ID'


class MatchNotFound(Exception):
    """Raised when RE module cannot find a match in the sentence"""
    def __str__(self):
        return 'RE module failed to retrieve the components'


class InvalidArgument(Exception):
    """Raised when Arguments found by RE module do not meet the type constraints."""
    def __str__(self):
        return 'Arguments found by RE module do not meet the type constraints'


class GeneNotFound(Exception):
    """Raised when there is no gene/miRNA mention in the CA/EA."""
    def __str__(self):
        return 'Failed to extract gene/miRNA from Compared Aspect or Expressed Aspect'


class DiseaseNotFound(Exception):
    """Raised when there is no disease mention."""
    def __str__(self):
        return 'Failed to extract the disease'


class MistypedExpressionLevel(Exception):
    """Raise when the scale indicator cannot be normalized."""
    def __str__(self):
        return 'Failed to normalize the expression level'
