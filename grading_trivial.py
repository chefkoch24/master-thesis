# This script finally grades the student answers
import numpy as np
import torch
from pytorch_lightning import Trainer
from pytorch_lightning.loggers import CSVLogger
from torch.utils.data import DataLoader, Sampler
from transformers import AutoTokenizer, AutoModelForTokenClassification
from incremental_trees.models.classification.streaming_rfc import StreamingRFC

# Define the model checkpoint
import config
from dataset import GradingDataset
from grading_model import GradingModelTrivial
import myutils as utils

model_checkpoint = 'logs/justification_cue_distilbert-base-multilingual-cased_context-False/version_7/checkpoints/checkpoint-epoch=04-val_loss=0.64.ckpt'
tokenizer = AutoTokenizer.from_pretrained(config.MODEL_NAME)


def preprocess(data, class2idx={'CORRECT': 0, 'PARTIAL_CORRECT': 1, 'INCORRECT': 2}):
    for d in data:
        tokenized = tokenizer(d['student_answer'], truncation=True, padding='max_length', max_length=512, return_tensors='pt')
        d['input_ids'] = tokenized['input_ids']
        d['attention_mask'] = tokenized['attention_mask']
        d['class'] = class2idx[d['label']]
    return data

train_file = 'training_dataset.json'
dev_file = 'dev_dataset.json'
# Create dataset and dataloader
training_data = utils.load_json(config.PATH_DATA + '/' + train_file)
dev_data = utils.load_json(config.PATH_DATA + '/' + dev_file)
rubrics = utils.load_rubrics(config.PATH_RUBRIC)

training_data = preprocess(training_data)
dev_data = preprocess(dev_data)

training_dataset = GradingDataset(training_data)
dev_dataset = GradingDataset(dev_data)

train_loader = DataLoader(training_dataset, batch_size=config.BATCH_SIZE, shuffle=True)
val_loader = DataLoader(dev_dataset, batch_size=config.BATCH_SIZE, shuffle=False)
model = GradingModelTrivial(model_checkpoint, rubrics=rubrics, model_name=config.MODEL_NAME, th=0.85)

EXPERIMENT_NAME = "grading_trivial_" + config.MODEL_NAME
logger = CSVLogger("logs", name=EXPERIMENT_NAME)
trainer = Trainer(max_epochs=config.NUM_EPOCHS,
                  #gradient_clip_val=0.5,
                  #accumulate_grad_batches=2,
                  #auto_scale_batch_size='power',
                  callbacks=[
                      config.checkpoint_callback,
                      config.early_stop_callback
                             ],
                  logger=logger,
                  num_sanity_val_steps=0,
                  )
trainer.fit(model, train_loader, val_loader)
# trainer.test(model, val_loader) TODO: add test_step