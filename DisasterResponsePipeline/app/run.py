"""
flask framework
"""
import json
import plotly
import pandas as pd

from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from flask import Flask
from flask import render_template, request, jsonify
from plotly.graph_objs import Bar
from plotly.graph_objs import Pie
from sklearn.externals import joblib
from sqlalchemy import create_engine

app = Flask(__name__)


def tokenize(text):
    """
    tokenize the text
    :param text:
    :return:
    """
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()

    clean_tokens = []
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)

    return clean_tokens


# load data
engine = create_engine('sqlite:///../data/DisasterResponse.db')
df = pd.read_sql_table('InsertTableName', engine)

# load model
model = joblib.load("../models/classifier.pkl")


# index webpage displays cool visuals and receives user input text for model
@app.route('/')
@app.route('/index')
def index():
    """
    entrance page
    :return:
    """
    # extract data needed for visuals
    related = ['related', 'other']
    related_count = [df['related'].sum(), df['related'].count()]
    medical_help = ['medical_help', 'other']
    medical_help_count = [df['medical_help'].sum(), df['medical_help'].count()]
    genre_counts = df.groupby('genre').count()['message']
    genre_names = list(genre_counts.index)
    # create visuals
    graphs = [
        {
            'data': [
                dict(
                    labels=related,
                    values=related_count,
                    type='pie'
                )
            ],
            'layout': {
                'title': 'related'
            }
        },
        {
            'data': [
                dict(
                    labels=medical_help,
                    values=medical_help_count,
                    type='pie'
                )
            ],
            'layout': {
                'title': 'medical help'
            }
        },
        {
            'data': [
                {
                    'x': genre_names,
                    'y': genre_counts,
                    'type': 'bar'
                }
            ],

            'layout': {
                'title': 'Distribution of Message Genres',
                'yaxis': {
                    'title': "Count"
                },
                'xaxis': {
                    'title': "Genre"
                }
            }
        }
    ]

    # encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    # render web page with plotly graphs
    return render_template('master.html', ids=ids, graphJSON=graphJSON)


# web page that handles user query and displays model results
@app.route('/go')
def go():
    """
    query page
    :return:
    """
    # save user input in query
    query = request.args.get('query', '')

    # use model to predict classification for query
    classification_labels = model.predict([query])[0]
    classification_results = dict(zip(df.columns[4:], classification_labels))

    # This will render the go.html Please see that file.
    return render_template(
        'go.html',
        query=query,
        classification_result=classification_results
    )


def main():
    """
    main entrance
    :return:
    """
    app.run(host='0.0.0.0', port=3001, debug=True)


if __name__ == '__main__':
    main()