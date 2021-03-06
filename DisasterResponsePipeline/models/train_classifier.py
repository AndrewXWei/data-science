"""
train model
"""
import sys
from sqlalchemy import create_engine
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV
import numpy as np
import pickle
import nltk
nltk.download(['punkt', 'wordnet'])

def load_data(database_filepath):
    """
    load data from database
    :param database_filepath:
    :return:
    """
    engine = create_engine('sqlite:///' + database_filepath)
    df = pd.read_sql_table('InsertTableName', con = engine)
    X = df['message']
    Y = df.iloc[:, 4:]
    return(X, Y, Y.columns)

def tokenize(text):
    """
    tokenize the messages
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


def build_model():
    """
    training
    :return:
    """
    pipeline = Pipeline([
        ('vect', CountVectorizer(tokenizer=tokenize)),
        ('tfidf', TfidfTransformer()),
        ('clf', MultiOutputClassifier(estimator=RandomForestClassifier()))
    ])
    parameters = {
        'vect__ngram_range': ((1, 1), (1, 2)),
        'vect__max_df': (0.5, 0.75, 1.0),
        'vect__max_features': (None, 5000, 10000),
        'tfidf__use_idf': (True, False),
        'clf__estimator__n_estimators': [50, 100, 200],
        'clf__estimator__min_samples_split': [2, 3, 4]
    }
    cv = GridSearchCV(pipeline, param_grid=parameters)
    return cv
    # return pipeline


def evaluate_model(model, X_test, Y_test, category_names):
    """
    evaluate the model
    :param model:
    :param X_test:
    :param Y_test:
    :param category_names:
    :return:
    """
    Y_pred = model.predict(X_test)
    for index in range(0, len(category_names)):
        print(category_names[index])
        print(classification_report(np.array(Y_test)[:, index], Y_pred[:, index]))


def save_model(model, model_filepath):
    """
    save model to file
    :param model:
    :param model_filepath:
    :return:
    """
    pickle.dump(model, open(model_filepath, 'wb'))


def main():
    """
    main entrance
    :return:
    """
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, Y, category_names = load_data(database_filepath)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
        
        print('Building model...')
        model = build_model()
        
        print('Training model...')
        model.fit(X_train, Y_train)
        
        print('Evaluating model...')
        evaluate_model(model, X_test, Y_test, category_names)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')


if __name__ == '__main__':
    main()