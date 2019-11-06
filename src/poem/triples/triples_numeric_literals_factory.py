# -*- coding: utf-8 -*-

"""Implementation of factory that create instances containing of triples and numeric literals.tsv."""

import logging
from typing import Dict, Optional, TextIO, Tuple, Union

import numpy as np

from .instances import MultimodalCWAInstances, MultimodalOWAInstances
from .triples_factory import TriplesFactory
from .utils import load_triples
from ..typing import EntityMapping, LabeledTriples

__all__ = [
    'TriplesNumericLiteralsFactory',
]

logger = logging.getLogger(__name__)


def create_matrix_of_literals(
    numeric_triples: np.array,
    entity_to_id: EntityMapping,
) -> Tuple[np.ndarray, Dict[str, int]]:
    """Create matrix of literals where each row corresponds to an entity and each column to a literal."""
    data_relations = np.unique(np.ndarray.flatten(numeric_triples[:, 1:2]))
    data_rel_to_id: Dict[str, int] = {
        value: key
        for key, value in enumerate(data_relations)
    }
    # Prepare literal matrix, set every literal to zero, and afterwards fill in the corresponding value if available
    num_literals = np.zeros([len(entity_to_id), len(data_rel_to_id)], dtype=np.float32)

    # TODO vectorize code
    for i, (h, r, lit) in enumerate(numeric_triples):
        try:
            # row define entity, and column the literal. Set the corresponding literal for the entity
            num_literals[entity_to_id[h], data_rel_to_id[r]] = lit
        except KeyError:
            logger.info("Either entity or relation to literal doesn't exist.")
            continue

    return num_literals, data_rel_to_id


class TriplesNumericLiteralsFactory(TriplesFactory):
    """Create multi-modal instances given the path to triples."""

    def __init__(
        self,
        *,
        path: Union[None, str, TextIO] = None,
        triples: Optional[LabeledTriples] = None,
        path_to_numeric_triples: Union[None, str, TextIO] = None,
        numeric_triples: Optional[np.ndarray] = None,
    ) -> None:
        """Initialize the multi-modal triples factory.

        :param path: The path to a 3-column TSV file with triples in it. If not specified,
         you should specify ``triples``.
        :param triples:  A 3-column numpy array with triples in it. If not specified,
         you should specify ``path``
        :param path_to_numeric_triples: The path to a 3-column TSV file with triples and
         numeric. If not specified, you should specify ``numeric_triples``.
        :param numeric_triples:  A 3-column numpy array with numeric triples in it. If not
         specified, you should specify ``path_to_numeric_triples``.
        """
        super().__init__(path=path, triples=triples)

        if path_to_numeric_triples is None and numeric_triples is None:
            raise ValueError('Must specify one of path_to_numeric_triples or numeric_triples')
        elif path_to_numeric_triples is not None and numeric_triples is not None:
            raise ValueError('Must not specify both path_to_numeric_triples and numeric_triples')
        elif path_to_numeric_triples is not None:
            self.path_to_numeric_triples = path_to_numeric_triples
            self.numeric_triples = load_triples(self.path_to_numeric_triples)
        else:  # numeric_triples is not None:
            self.path_to_numeric_triples = '<None>'
            self.numeric_triples = numeric_triples

        self.numeric_literals = None
        self.literals_to_id = None

        self._create_numeric_literals()

    def __repr__(self):  # noqa: D105
        return f'{self.__class__.__name__}(path="{self.path}", ' \
               f'path_to_numeric_triples="{self.path_to_numeric_triples}")'

    def _create_numeric_literals(self) -> None:
        self.numeric_literals, self.literals_to_id = create_matrix_of_literals(
            numeric_triples=self.numeric_triples,
            entity_to_id=self.entity_to_id,
        )

    def create_owa_instances(self) -> MultimodalOWAInstances:
        """Create multi-modal OWA instances for this factory's triples."""
        owa_instances = super().create_owa_instances()

        # FIXME is this ever possible, since this function is called in __init__?
        if self.numeric_literals is None:
            self._create_numeric_literals()

        return MultimodalOWAInstances(
            mapped_triples=owa_instances.mapped_triples,
            entity_to_id=owa_instances.entity_to_id,
            relation_to_id=owa_instances.relation_to_id,
            assumption=owa_instances.assumption,
            numeric_literals=self.numeric_literals,
            literals_to_id=self.literals_to_id,
        )

    def create_cwa_instances(self) -> MultimodalCWAInstances:
        """Create multi-modal CWA instances for this factory's triples."""
        cwa_instances = super().create_cwa_instances()

        if self.numeric_literals is None:
            self._create_numeric_literals()

        return MultimodalCWAInstances(
            mapped_triples=cwa_instances.mapped_triples,
            entity_to_id=cwa_instances.entity_to_id,
            relation_to_id=cwa_instances.relation_to_id,
            assumption=cwa_instances.assumption,
            numeric_literals=self.numeric_literals,
            literals_to_id=self.literals_to_id,
            labels=cwa_instances.labels,
        )