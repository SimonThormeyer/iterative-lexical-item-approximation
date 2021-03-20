# Iterative Lexical Item Approximation

 The code for the system presented in my bachelor thesis.

 ## Abstract

In clinical and ambulatory settings, as well as prior to patients searching the internet for appropriate interventions for their conditions, it is important that symptoms are accurately specified, especially when symptoms that are similar in perception but have different causes and therefore require different treatment.
A system that can know and communicate fine-grained differences between similar symptoms is therefore beneficial.
Such a system is presented in this bachelor thesis.


The presented system leverages advances in word embeddings in the NLP domain.
A preprocessing pipeline uses a *Transformer*-based language model (BERT) to build a semantic space with the lexical items contained in a symptom list.
Each symptom is assigned a vector.
These vectors are then used by the system to approximate, via their differences and similarities, a symptom searched for by the user. 
The approximation takes place through iterative user interactions with the system.


Analyses of the system show that symptoms that are similar are indeed also close-by in the semantic space.
With a user study, this thesis shows that the approximation of lexical items (symptoms) with the system can be performed well by both healthcare professionals and amateurs.

## Demo  

<https://thormeyer.eu/thesis/> — Model 2 for symptom approximation  
<https://thormeyer.eu/thesis/symptoms.txt> — All symptoms  


## Important Contents of the Repository

.  
├── Readme.md – *This file*  
├── pre-processing.py – *The preprocessing pipeline needed to produce static embeddings*  
└── web-application – *Contains the actual system*  
    ├── docker-compose.yml – *Needed for building the system using docker*  
    ├── frontend – *Contains the React frontend*  
    └── backend  
        ├── LexicalItemApproximator.py – *Contains all essential functionality*  
        ├── models – *Contains static embeddings for the models available*  
        └── api – *Contains Flask application*  

