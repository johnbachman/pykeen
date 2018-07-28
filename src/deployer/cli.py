import os
import sys

w_dir = os.path.dirname(os.getcwd())
sys.path.append(w_dir)
from collections import OrderedDict

from prompt_toolkit import prompt

from utilities.constants import PREFERRED_DEVICE, GPU, CPU, EMBEDDING_DIMENSIONS_PRINT_MSG, \
    EMBEDDING_DIMENSIONS_PROMPT_MSG, EMBEDDING_DIMENSIONS_ERROR_MSG, MARGIN_LOSSES_PRINT_MSG, MARGIN_LOSSES_PROMPT_MSG, \
    MARGIN_LOSSES_ERROR_MSG, LEARNING_RATES_PRINT_MSG, LEARNING_RATES_PROMPT_MSG, LEARNING_RATES_ERROR_MSG, \
    BATCH_SIZES_PRINT_MSG, BATCH_SIZES_PROMPT_MSG, BATCH_SIZES_ERROR_MSG, EPOCHS_PRINT_MSG, EPOCHS_PROMPT_MSG, \
    EPOCHS_ERROR_MSG, MAX_HPO_ITERS_PRINT_MSG, MAX_HPO_ITERS_PROMPT_MSG, MAX_HPO_ITERS_ERROR_MSG, TRAINING, \
    HYPER_PARAMTER_SEARCH, HYPER_PARAMTER_OPTIMIZATION_PARAMS, EMBEDDING_DIM, KG_EMBEDDING_MODEL, MARGIN_LOSS, \
    LEARNING_RATE, BATCH_SIZE, NUM_EPOCHS, NUM_OF_MAX_HPO_ITERS, EVAL_METRICS
from utilities.pipeline import Pipeline

# ----------Constants--------------

# TODO: Adapt


# ---------------------------------

mapping = {'yes': True, 'no': False}
embedding_models_mapping = {1: 'TransE', 2: 'TransH', 3: 'TransR', 4: 'TransD'}
metrics_maping = {1: 'mean_rank'}
normalization_mapping = {1: 'l1', 2: 'l2'}
execution_mode_mapping = {1: TRAINING, 2: HYPER_PARAMTER_SEARCH}


def print_welcome_message():
    print('#########################################################')
    print('#\t\t\t\t\t\t\t#')
    print('#\t\t Welcome to KEEN\t\t\t#')
    print('#\t\t\t\t\t\t\t#')
    print('#########################################################')
    print()


def select_execution_mode():
    print('Please select the mode in which KEEN should be started:')
    print('Training: 1')
    print('Hyper-parameter search: 2')
    is_valid_input = False

    while is_valid_input == False:
        user_input = prompt('> Please select one of the options: ')

        if user_input != '1' and user_input != '2':
            print("Invalid input, please type \'1\' or \'2\' to chose one of the provided execution modes")
        else:
            is_valid_input = True
            user_input = int(user_input)

    return user_input


def select_embedding_model():
    print('Please select the embedding model you want to use:')
    print("TransE: 1")
    print("TransH: 2")
    print("TransR: 3")
    print("TransD: 4")
    is_valid_input = False

    while is_valid_input == False:
        user_input = prompt('> Please select one of the options: ')

        if user_input != '1' and user_input != '2':
            print(
                "Invalid input, please type a number between \'1\' and \'4\' for choosing one of the embedding models")
        else:
            is_valid_input = True
            user_input = int(user_input)

    return user_input


def select_positive_integer_values(print_msg, prompt_msg, error_msg):
    print(print_msg)
    is_valid_input = False
    integers = []

    while is_valid_input == False:
        is_valid_input = True
        user_input = prompt(prompt_msg)
        user_input = user_input.split(',')

        for integer in user_input:
            if integer.isnumeric():
                integers.append(int(integer))
            else:
                print(error_msg)
                is_valid_input = False
                break

    return integers


def select_float_values(print_msg, prompt_msg, error_msg):
    print(print_msg)
    is_valid_input = False
    float_values = []

    while is_valid_input == False:
        user_input = prompt(prompt_msg)
        user_input = user_input.split(',')

        for float_value in user_input:
            try:
                float_value = float(float_value)
                float_values.append(int(float_value))
            except ValueError:
                print(error_msg)
                break

        is_valid_input = True

    return float_values


def select_eval_metrics():
    print('Please select the evaluation metrics you want to use:')
    print("Mean rank: 1")
    print("Hits@k: 2")

    metrics = []

    is_valid_input = False

    while is_valid_input == False:
        user_input = prompt('> Please select the options comma separated:')
        user_input = user_input.split(',')

        for choice in user_input:
            if choice.isnumeric():
                metrics.append(int(choice))
            else:
                print('Invalid input, please type in a sequence of integers (\'1\' and/or \'2\')')
                is_valid_input = False
                break

    return metrics

def _select_trans_x_params():
    hpo_params = OrderedDict()
    embedding_dimensions = select_positive_integer_values(EMBEDDING_DIMENSIONS_PRINT_MSG,
                                                          EMBEDDING_DIMENSIONS_PROMPT_MSG,
                                                          EMBEDDING_DIMENSIONS_ERROR_MSG)
    hpo_params[EMBEDDING_DIM] = embedding_dimensions

    # ---------
    margin_losses = select_float_values(MARGIN_LOSSES_PRINT_MSG, MARGIN_LOSSES_PROMPT_MSG, MARGIN_LOSSES_ERROR_MSG)
    hpo_params[MARGIN_LOSS] = margin_losses

    return hpo_params


def select_hpo_params(model_id):
    hpo_params = OrderedDict()
    hpo_params[KG_EMBEDDING_MODEL] = embedding_models_mapping[model_id]

    if 1 <= model_id and model_id <= 4:
        # Model is one of the TransX versions
        param_dict = _select_trans_x_params()
        hpo_params.update(param_dict)
    elif model_id == 'X':
        # TODO: ConvE
        exit(0)
    elif model_id == 'Y':
        # TODO: RESCAL
        exit(0)
    elif model_id == 'Z':
        # TODO: COMPLEX
        exit(0)

    # General params
    # --------
    learning_rates = select_float_values(LEARNING_RATES_PRINT_MSG, LEARNING_RATES_PROMPT_MSG, LEARNING_RATES_ERROR_MSG)
    hpo_params[LEARNING_RATE] = learning_rates

    # --------------
    batch_sizes = select_positive_integer_values(BATCH_SIZES_PRINT_MSG, BATCH_SIZES_PROMPT_MSG, BATCH_SIZES_ERROR_MSG)
    hpo_params[BATCH_SIZE] = batch_sizes

    epochs = select_positive_integer_values(EPOCHS_PRINT_MSG,EPOCHS_PROMPT_MSG,EPOCHS_ERROR_MSG )
    hpo_params[NUM_EPOCHS] = epochs


    hpo_iter = select_positive_integer_values(MAX_HPO_ITERS_PRINT_MSG,MAX_HPO_ITERS_PROMPT_MSG, MAX_HPO_ITERS_ERROR_MSG)
    hpo_params[NUM_OF_MAX_HPO_ITERS] = hpo_iter

    return hpo_params

def get_data_input_path():
    print('Please provide the path to the dataset:')

    is_valid_input = False

    while is_valid_input == False:
        user_input = prompt('> Path:')

        if not os.path.exists(os.path.dirname(user_input)):
            print('Path doesn\'t exist, please type in new path')
        else:
            return user_input

def select_ratio_for_validation_set():
    print('Select the ratio of the training set used for validation (e.g. 0.5):')
    is_valid_input = False

    while is_valid_input == False:
        user_input = prompt('> Ratio: ')

        try:
            ratio = float(ratio)
            if ratio>0. and ratio<1.:
                return ratio
            else:
                print('Invalid input, please type in a number > 0. and < 1.')
            return ratio
        except ValueError:
            print('Invalid input, please type in a number > 0. and < 1.')

    return ratio

def ask_for_validation_set():
    print('Do you provide a validation set?')
    is_valid_input = False

    while is_valid_input == False:
        user_input = prompt('> \'yes\' or \'no\': ')

        if user_input != 'yes' and user_input!= 'no':
            print('Invalid input, please type in \'yes\' or \'no\'')
        elif user_input == 'yes':
            return get_data_input_path()
        elif user_input == 'no':
            return select_ratio_for_validation_set()


def start_cli():
    config = OrderedDict()

    print_welcome_message()
    print('----------------------------')
    exec_mode = select_execution_mode()
    exec_mode = execution_mode_mapping[exec_mode]
    print('----------------------------')
    embedding_model_id = select_embedding_model()
    print('----------------------------')

    if exec_mode == HYPER_PARAMTER_SEARCH:
        hpo_params = select_hpo_params(model_id=embedding_model_id)
        config[HYPER_PARAMTER_OPTIMIZATION_PARAMS] = hpo_params
    else:
        kg_model_params = select_embedding_model_params(model_id=embedding_model_id)
        config[KG_EMBEDDING_MODEL] = kg_model_params

    print('----------------------------')
    config[EVAL_METRICS] = select_eval_metrics()
    print('----------------------------')

    config['training_set_path'] = get_data_input_path()

    print('Do you provide a validation set?')
    user_input = prompt('> \'yes\' or \'no\': ')
    user_input = mapping[user_input]

    if user_input:
        print('Please provide the path to the validation set')
        validation_data_path = prompt('> Path: ')
        config['validation_set_path'] = validation_data_path
    else:
        print('Select the ratio of the training set used for validation (e.g. 0.5)')
        user_input = prompt('> Ratio: ')
        validation_ratio = float(user_input)
        config['validation_set_ratio'] = validation_ratio

    print('Do you want to use a GPU if available?')
    user_input = prompt('> \'yes\' or \'no\': ')
    if user_input == 'yes':
        config[PREFERRED_DEVICE] = GPU
    else:
        config[PREFERRED_DEVICE] = CPU

    return config


def select_embedding_model_params(model_id):
    kg_model_params = OrderedDict()
    kg_model_params['model_name'] = embedding_models_mapping[model_id]

    if 1 <= model_id and model_id <= 4:
        print('Please type the embedding dimensions:')
        user_input = prompt('> Embedding dimension: ')
        embedding_dimension = int(user_input)

        kg_model_params['embedding_dim'] = embedding_dimension

        if model_id == 1:
            print('Please select the normalization approach for the entities: ')
            print('L1-Norm: 1')
            print('L1-Norm: 2')
            user_input = prompt('> Normalization approach: ')
            normalization_of_entities = int(user_input)

            kg_model_params['normalization_of_entities'] = normalization_of_entities

        print('Please type the maring loss: ')
        user_input = prompt('> Margin loss: ')
        margin_loss = int(user_input)

        kg_model_params['margin_loss'] = margin_loss

    print('Please type the learning rate: ')
    user_input = prompt('> Learning rate: ')
    lr = float(user_input)
    kg_model_params['learning_rate'] = lr

    print('Please type the batch size: ')
    user_input = prompt('> Batch size: ')
    batch_size = int(user_input)
    kg_model_params['batch_size'] = batch_size

    print('Please type the number of epochs: ')
    user_input = prompt('> Epochs: ')
    epochs = int(user_input)

    kg_model_params['num_epochs'] = epochs

    return kg_model_params





import pickle


def main():
    config = start_cli()

    config_in = '/Users/mehdi/PycharmProjects/kg_embeddings_pipeline/data/config_files/hpo_wn_18_test_test.pkl'
    with open(config_in, 'rb') as handle:
        config = pickle.load(handle)
    pipeline = Pipeline(config=config, seed=2)

    if 'hyper_param_optimization' in config:
        trained_model, eval_summary, entity_to_embedding, relation_to_embedding, params = pipeline.start_hpo()
    else:
        trained_model, eval_summary, entity_to_embedding, relation_to_embedding, params = pipeline.start_training()

    summary = eval_summary.copy()
    summary.update(params)

    print(summary)


if __name__ == '__main__':
    main()
