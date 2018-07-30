# -*- coding: utf-8 -*-add # -*- coding: utf-8 -*-
import random
from collections import OrderedDict

import numpy as np

from hyper_parameter_optimizer.abstract_hyper_params_optimizer import AbstractHPOptimizer
from utilities.constants import LEARNING_RATE, MARGIN_LOSS, EMBEDDING_DIM, BATCH_SIZE, NUM_EPOCHS, \
    KG_EMBEDDING_MODEL, NUM_ENTITIES, NUM_RELATIONS, SEED, HYPER_PARAMTER_OPTIMIZATION_PARAMS, NUM_OF_MAX_HPO_ITERS, \
    NORMALIZATION_OF_ENTITIES
from utilities.initialization_utils.module_initialization_utils import get_kg_embedding_model
from utilities.train_utils import train
from utilities.triples_creation_utils.instance_creation_utils import create_mapped_triples


class RandomSearchHPO(AbstractHPOptimizer):

    def __init__(self, evaluator):
        self.evaluator = evaluator

    def optimize_hyperparams(self, train_pos, test_pos, entity_to_id, rel_to_id, mapped_pos_train_tripels, config,
                             device, seed):
        np.random.seed(seed=seed)

        hyperparams_dict = config[HYPER_PARAMTER_OPTIMIZATION_PARAMS]
        learning_rates = hyperparams_dict[LEARNING_RATE]
        margins = hyperparams_dict[MARGIN_LOSS]
        embedding_dims = hyperparams_dict[EMBEDDING_DIM]
        max_iters = hyperparams_dict[NUM_OF_MAX_HPO_ITERS]
        num_epochs = hyperparams_dict[NUM_EPOCHS]
        embedding_model = hyperparams_dict[KG_EMBEDDING_MODEL]
        kg_embedding_model_config = OrderedDict()
        kg_embedding_model_config[KG_EMBEDDING_MODEL] = embedding_model
        metric_string = self.evaluator.METRIC

        trained_models = []
        eval_results = []
        entity_to_ids = []
        rel_to_ids = []
        models_params = []

        for _ in range(max_iters):
            lr = random.choice(learning_rates)
            margin = random.choice(margins)
            embedding_dim = random.choice(embedding_dims)

            kg_embedding_model_config[NUM_ENTITIES] = len(entity_to_id)
            kg_embedding_model_config[NUM_RELATIONS] = len(rel_to_id)
            kg_embedding_model_config[EMBEDDING_DIM] = embedding_dim
            kg_embedding_model_config[MARGIN_LOSS] = margin
            kg_embedding_model_config[NORMALIZATION_OF_ENTITIES] = hyperparams_dict[NORMALIZATION_OF_ENTITIES]
            kg_embedding_model = get_kg_embedding_model(config=kg_embedding_model_config)
            params = kg_embedding_model_config.copy()
            params[LEARNING_RATE] = lr
            params[NUM_EPOCHS] = random.choice(num_epochs)
            params[SEED] = seed
            batch_size = random.choice(hyperparams_dict[BATCH_SIZE])
            models_params.append(params)

            entity_to_ids.append(entity_to_id)
            rel_to_ids.append(rel_to_id)

            trained_model = train(kg_embedding_model=kg_embedding_model, learning_rate=lr,
                                  num_epochs=params[NUM_EPOCHS],
                                  batch_size=batch_size, pos_triples=mapped_pos_train_tripels,
                                  device=device, seed=seed)

            # Evaluate trained model
            mapped_pos_test_tripels, _, _ = create_mapped_triples(test_pos, entity_to_id=entity_to_id,
                                                                  rel_to_id=rel_to_id)
            eval_result, _ = self.evaluator.start_evaluation(test_data=mapped_pos_test_tripels,
                                                             kg_embedding_model=trained_model)

            trained_models.append(trained_model)
            eval_results.append(eval_result)

        index_of_max = np.argmax(a=eval_results)

        return trained_models[index_of_max], entity_to_ids[index_of_max], rel_to_ids[index_of_max], \
               eval_results[index_of_max], metric_string, models_params[index_of_max]
