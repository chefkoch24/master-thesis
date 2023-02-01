# This script preprocesses the data for the justification cue detection training
import tokenizations
import numpy as np
import pandas as pd
from transformers import AutoTokenizer
import config
import utils
from dataset import CustomJustificationCueDataset
import torch

# Helper functions
def _align_generate_labels_all_tokens(tokens_spacy, tokens_bert, l):
    a2b, b2a = tokenizations.get_alignments(tokens_spacy, tokens_bert)
    len_of_classification = len(tokens_bert)  # for CLS and end of seq
    label_ids = np.zeros((len_of_classification))
    previous_label_idx = 0
    label_idx = -1
    for j, e in enumerate(b2a):
        if len(e) >= 1:  # Not special token
            label_idx = e[0]
            # if label_idx < len_of_classification:
            label_ids[j] = l[label_idx]
            previous_label_idx = label_idx
        else:
            label_ids[j] = l[previous_label_idx]
    # label_ids[len_of_classification:] = -100
    return label_ids


def create_inputs(data, with_context=False):
    labels = []
    bert_tokens = []
    for d in data:
        student_answer = d['student_answer']
        l = d['silver_labels']
        nlp = config.nlp_de if d['lang'] == 'de' else config.nlp
        tokens_spacy = [t.text for t in nlp(student_answer)]
        # Tokenize the input
        tokenized = tokenizer(student_answer, add_special_tokens=False)
        tokens_bert = [tokenizer.decode(t) for t in tokenized['input_ids']]
        if with_context:
            context = d['reference_answer']
            length_stud_answer = len(tokenized['input_ids'])
            tokenized = tokenizer(student_answer, context)
            input_ids = tokenized['input_ids']
            attention_mask = np.ones(len(input_ids), dtype=np.int64)
            attention_mask[length_stud_answer:-1] = 0

        else:
            attention_mask = tokenized['attention_mask']
        item = {
            'input_ids': tokenized['input_ids'],
            'attention_mask': attention_mask ,
        }
        bert_tokens.append(item)
        # Generating the labels
        label_ids = _align_generate_labels_all_tokens(tokens_spacy, tokens_bert, l)
        labels.append(label_ids.tolist())

    return labels, bert_tokens


#Loading
train_data = utils.load_json(config.PATH_DATA + '/' + 'train_labeled_data.json')
dev_data = utils.load_json(config.PATH_DATA + '/' + 'dev_labeled_data.json')
tokenizer = AutoTokenizer.from_pretrained(config.TOKENIZER_NAME)

# Preprocess data
bert_labels_train, bert_tokens_train = create_inputs(train_data, with_context=True)
bert_labels_dev, bert_tokens_dev = create_inputs(dev_data, with_context=True)
training_dataset = CustomJustificationCueDataset(train_data, bert_tokens_train, bert_labels_train)
dev_dataset = CustomJustificationCueDataset(dev_data, bert_tokens_dev, bert_labels_dev)

#save data
torch.save(training_dataset, config.PATH_DATA + '/' + ' training_dataset.pt')
torch.save(dev_dataset, config.PATH_DATA + '/' + 'dev_dataset.pt')
