# https://github.com/marshmallow-code/webargs/blob/dev/examples/flaskrestful_example.py

import io
from os import environ
import os

from flask.helpers import send_file
from datetime import datetime
from LexicalItemApproximator import LexicalItemApproximator
from gensim.models import KeyedVectors
from flask import Flask, jsonify, session
from flask_session import Session
from flask_cors import CORS
from flask_restful import Api, Resource
import PIL.Image as Image
import pytz

from webargs import fields
from webargs.flaskparser import use_args, parser, abort

# region Models
MODELS_PATH = environ.get('MODELS_PATH')

models = [
    {'id': 0,
     'name': 'bert_uncased_L-12_H-768_A-12',
     'itemName': 'word',
     'description': 'Vectors of items from dialogues of about 600 Simpsons episodes. Vectors generated with "BERT base uncased" (pre-trained on English Wikipedia and BookCorpus).',
     'instructions': 'Think of a word and keep selecting the most similar word from the suggested ones until you see the word you\'re thinking of. Then click the green button.',
     # Load vectors using Gensim KeyedVectors
     'vectors': KeyedVectors.load_word2vec_format(
         f'{MODELS_PATH}/bert-vectors-simpsons.txt')},

    {'id': 1,
     'name': 'bluebert_pubmed_mimic_uncased_L-12_H-768_A-12',
     'itemName': 'symptom',
     'description': 'Vectors of items from a list of medical symptoms. Vectors generated with a BERT model pre-trained on PubMed abstracts and clinical notes (MIMIC-III dataset).',
     'instructions': 'Think of a symptom and keep selecting the most similar symptom from the suggested ones until you see the symptom you\'re thinking of. Then click the green button.',
     'vectors': KeyedVectors.load_word2vec_format(
         f'{MODELS_PATH}/bluebert-vectors-symptoms.txt')},
]
# endregion

# region Resources


class ModelsRessource(Resource):
    model_id_arg = {"id": fields.Integer(required=False)}

    @use_args(model_id_arg, location='query')
    def get(self, query):
        if not query:
            # Return models without vectors
            return jsonify([{key:model[key] 
            for key in model if key!='vectors'} 
            for model in models])

        # The /models?id=number request means that the model with the given id is selected.
        session['model'] = models[query['id']]
        return "OK"

class SuggestionsResource(Resource):
    suggestion_args = {"item": fields.String(required=False)}

    @use_args(suggestion_args, location='query')
    def get(self, query):
        """Get a selection of similar items for a item."""
        if not query or not 'approximator' in session:
            # Create a new instance of LexicalItemApproximator for every session and return the start_items
            approximator = LexicalItemApproximator(
                vectors=session['model']['vectors'])
            session['approximator'] = approximator
            return jsonify({'items': approximator.start_items})
        else:
            # If a selected item is provided, select it and get suggestions
            approximator: LexicalItemApproximator = session['approximator']
            approximator.select_item(query['item'])
            return jsonify({"items": approximator.suggest_items(), "excluded": list(approximator.excluded_items)})


class UndoResource(Resource):
    def get(self):
        approximator: LexicalItemApproximator = session['approximator']
        approximator.undo()
        return jsonify({"currentItem": approximator.selected_item, "items": approximator.suggestions_sequence[-1], "excluded": list(approximator.excluded_items)})


class PlotResource(Resource):
    def get(self):
        approximator: LexicalItemApproximator = session['approximator']
        return send_file(
            io.BytesIO(approximator.get_plot_image()),
            mimetype='image/png',
            attachment_filename=f'plot{datetime.now()}.png')


class DoneResource(Resource):
    suggestion_args = {"item": fields.String(required=True)}

    @use_args(suggestion_args, location='query')
    def get(self, query):
        """Get start items and number of iterations needed."""
        approximator: LexicalItemApproximator = session['approximator']
        return jsonify({"start_items": approximator.start_items, "iterations": approximator.iterations, "sequence": approximator.selection_sequence})


class ResultPlotResource(Resource):
    result_args = {"item": fields.String(required=True)}

    @use_args(result_args, location='query')
    def get(self, item):
        """Get the concluding plot for this session and a result item."""
        approximator: LexicalItemApproximator = session['approximator']
        session['result_plot'] = approximator.get_result_plot_image(
            item['item'])
        return send_file(
            io.BytesIO(session['result_plot']),
            mimetype='image/png',
            attachment_filename=f'plot{datetime.now()}.png')


class SaveResultsResource(Resource):
    def get(self):
        utc_time = datetime.utcnow()
        time = pytz.utc.localize(utc_time, is_dst=None).astimezone(
            pytz.timezone('Europe/Berlin'))
        approximator: LexicalItemApproximator = session['approximator']
        save_dir = f'./results/results_{time.year}-{time.month:02d}-{time.day:02d}-{time.hour:02d}-{time.minute:02d}-{time.second:02d}_{approximator.selected_item}'
        os.makedirs(save_dir, exist_ok=True)
        with open(f'{save_dir}/results.txt', "a") as myfile:
            myfile.write(f"Timestamp: {time.year}-{time.month:02d}-{time.day:02d}, {time.hour:02d}:{time.minute:02d}:{time.second:02d} h\
            \nIterations needed: {approximator.iterations}\
            \n\
            \n\
            \n---- Selection history: ----\
            \n{approximator.selection_sequence}\
            \n\
            \n\
            \n---- Most similar of suggested history: ----\
            \n{approximator.most_similar_of_suggested_sequence}\
            \n\
            \n\
            \n---- Suggestion history: ----\
            \n{(os.linesep * 2).join([str(suggestions) for suggestions in approximator.suggestions_sequence])}\
            \n\
            \n\
            \n---- Plot Cosine similarity values: ----\
            \nselected item:\
            \n{approximator.y_vals_selection}\
            \n\
            \naverage of suggested:\
            \n{approximator.y_vals_suggestions_avg}\
            \n\
            \nmost similar of suggested:\
            \n{approximator.y_vals_closest}\
                ")
        image = Image.open(io.BytesIO(session['result_plot']))
        image.save(f'{save_dir}/result_plot.png')
        return "OK"

# endregion

# This error handler is necessary for usage with Flask-RESTful


@parser.error_handler
def handle_request_parsing_error(err, req, schema, *, error_status_code, error_headers):
    """webargs error handler that uses Flask-RESTful's abort function to return
    a JSON error response to the client.
    """
    abort(error_status_code, errors=err.messages)


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    api = Api(app)
    sess = Session(app)
    app.config.from_pyfile('settings.py')
    sess.init_app(app)
    api.add_resource(ModelsRessource, "/models")
    api.add_resource(SuggestionsResource, "/suggestions")
    api.add_resource(PlotResource, "/plot")
    api.add_resource(DoneResource, '/done')
    api.add_resource(UndoResource, '/undo')
    api.add_resource(ResultPlotResource, '/result-plot')
    api.add_resource(SaveResultsResource, '/save-results')
    return app
