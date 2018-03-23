"""This file provides functions and clases that aim to help the statistical analyse of text.
"""

from nltk.tokenize import word_tokenize
from textstat import *
from helper_functions import *

###############
# dispatchers #
###############


class funcstat(object):
    """Defines a set of methods designed to simplify the mental overhead of making statistics on a list of data.

    This class takes a functional approach, by identifying some orthogonal functions, each resolving a part of the problem :
     - scorer
     - data_tagger
     - data_fetcher TODO: think about wether this has any use
     - stat_mesurer
     - comparator

    Those functions are described in more details in the __init__ method.
    """
    tokenizers = {
        'delim': lambda x: delimiter_tokenizer(x).split(),
        'nltk': word_tokenize
    }

    comparators = {
        'normalize': normalized_ratio,
        'ratio': lambda x, y: x / y
    }

    def __init__(self,
                 scorer,
                 data_tagger,
                 data_fetcher=lambda x: x,
                 stat_mesurer=average,
                 comparator=normalized_ratio):
        """Initialize the criterions on which the stats will be made.

        Parameters
        ----------
        scorer : function(data) -> score
            The function that will associate the data to a score.

        data_tagger : function(data) -> tag
            The function tagging a data element in order to split the data.

            Take a single element from the source and output something describing
            the category to which the element belongs.

            An exemple of tagger would be a function that will tag an integer as even
            or odd.

        data_fetcher : function(raw_data) -> data
            The function that will transform the data in order to make it ready for
            the other functions to use.

        stat_mesurer : function(Container of score) -> mesure
            The function that will compute the desired statistical mesure (ex: average)

        comparator : function(score|mesure, score|mesure) -> ratio
            The function that will compute ratios, thus comparing the scores.
        """
        self.scorer = scorer
        self.data_tagger = data_tagger
        self.data_fetcher = data_fetcher
        self.stat_mesurer = stat_mesurer
        self.comparator = comparator

    def split_data(self, source, data_tagger=None,
                   data_fetcher=None):
        """Split the source data into categories according to the preset data tagger or to a custom one.

        Parameters
        ----------
        source : Container of data
            The data to split.

        data_tagger : function(data) -> tag, optional
            The function tagging a data element in order to split the data.

        Returns
        -------
        out : dict{tag: list of data}
            A dictionary associating a tags with the list of data corresponding to this tag.
        """
        data_tagger = data_tagger or self.data_tagger
        data_fetcher = data_fetcher or self.data_fetcher

        return tag_container(data_tagger, data_fetcher(source))

    def getscores(self, source, scorer=None, data_tagger=None,
                  data_fetcher=None):
        """Compute the score of the source data.

        Parameters
        ----------
        source : Container of data
            The data to score.

        Returns
        -------
        out : dict{tag: list of score}
            The tagged scores.
        """
        scorer = scorer or self.scorer
        data_tagger = data_tagger or self.data_tagger
        data_fetcher = data_fetcher or self.data_fetcher

        return {
            tag: [scorer(data) for data in datalist]
            for tag, datalist in self.split_data(
                source,
                data_tagger=data_tagger,
                data_fetcher=data_fetcher).items()}
        return result

    def getmesures(self, source, scorer=None, data_tagger=None,
                   data_fetcher=None, stat_mesurer=None):
        """Compute the statistical mesure of the source data.

        Parameters
        ----------
        source : Container of data
            The data to mesure.

        Returns
        -------
        out : dict{tag: mesure}
            The mesure data.
        """
        scorer = scorer or self.scorer
        data_tagger = data_tagger or self.data_tagger
        data_fetcher = data_fetcher or self.data_fetcher
        stat_mesurer = stat_mesurer or self.stat_mesurer

        return {
            tag: stat_mesurer(scores)
            for tag, scores in self.getscores(
                source,
                scorer=scorer,
                data_tagger=data_tagger,
                data_fetcher=data_fetcher).items()}
