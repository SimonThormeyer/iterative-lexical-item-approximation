import pandas as pd
# Symptoms list used: https://www.kaggle.com/plarmuseau/sdsort?select=symptoms2.csv
df = pd.read_csv('/path/to/symptoms_list.csv')
df = df.rename(columns={"name": "symptom"})
df.drop(df.columns.difference(['_id','symptom']), 1, inplace=True)
df = df.dropna().reset_index(drop=True)
df = df.drop_duplicates(subset=['symptom'])
# resulting df shape: (388, 2)

from transformers import BertTokenizer
tokenizer = BertTokenizer.from_pretrained(
        'bionlp/bluebert_pubmed_mimic_uncased_L-12_H-768_A-12')

symptoms_tokenized = [tokenizer.tokenize('[CLS] ' + symptom + ' [SEP]')
                      for symptom in df['symptom']]

import torch

 # Mark each of the tokens as belonging to sentence "1".
symptoms_segments_ids = [ 
  [1] * len(symptom_tokenized) 
  for symptom_tokenized in symptoms_tokenized]

# Map the token strings to their vocabulary indeces.
indexed_tokens = [tokenizer.convert_tokens_to_ids(
        symptom_tokenized) for symptom_tokenized in symptoms_tokenized]

# Convert inputs to PyTorch tensors
tokens_tensors = [
                torch.tensor([indexed_tokens]) 
                for indexed_tokens 
                in indexed_tokens]
segments_tensors = [
 torch.tensor([symptom_segments_ids]) for symptom_segments_ids in 
 symptoms_segments_ids
 ]

from transformers import BertModel
    
model = BertModel.from_pretrained(
    'bionlp/bluebert_pubmed_mimic_uncased_L-12_H-768_A-12',
    # Whether the model returns all hidden-states:
    output_hidden_states = True)

model.eval() 

# Run the text through BERT, and collect all of the hidden 
# states produced from all 12 layers. 

with torch.no_grad():
  symptoms_outputs = [
    model(tokens_tensor, segments_tensor)
    for tokens_tensor, segments_tensor in zip(
        tokens_tensors, 
        segments_tensors)]

# the third item will be the hidden states from all layers. 
symptoms_hidden_states = [symptom_outputs[2] 
                                  for symptom_outputs in symptoms_outputs]

# for each symptom take the average of the 
# outputs of its tokens for 2nd to last hidden layer
symptoms_embeddings = [
        torch.mean(torch.squeeze(hidden_states[-2]), dim=0) for hidden_states in symptoms_hidden_states
    ]

import os

# dimensions, number of symptoms
dims, n_symptoms = len(symptoms_embeddings[0]), len(df['symptom'])

# no whitespace allowed in word2vec format 
symptoms_no_whitespace = df['symptom'].replace(' ', '_', regex=True)

outputfile = "/path/to/symptoms_embeddings.txt"
if os.path.exists(outputfile): os.remove(outputfile)
with open(outputfile, "a") as myfile:
        myfile.write(f"{n_symptoms} {dims}\n")
        for symptom, embedding in zip(
            symptoms_no_whitespace, symptoms_embeddings):
            vector = embedding.detach().cpu().numpy()
            vector = vector.flatten()
            # Values of each dimension of the symptom's embedding 
            # vector, correct to ten decimal places, separated by space
            vector_string = ' '.join([f'{value:10.10f}'
                for value in vector])
            myfile.write(f'{symptom} {vector_string}\n')