import pickle
from .settings import path
PAST = 4*7
FUTURE = 1


def predict(df, currency):
    START = len(df.date) - PAST
    END = len(df.date) - FUTURE
    df.close = df.close.astype('float32')
    df.open = df.open.astype('float32')
    df.low = df.low.astype('float32')
    df.high = df.high.astype('float32')
    open_, high, low, close = df.open, df.high, df.low, df.close
    new_df = []
    for i in range(START, END + 2):
        new_df.append(list(open_[i - PAST:i]) + list(high[i - PAST:i]) + list(low[i - PAST:i]) + list(close[i - PAST:i]))
    X = new_df[-1]
    print(X)
    filename_cl = f'{path}models/{currency}_rise.sav'
    classifier = pickle.load(open(filename_cl, 'rb'))
    filename_re = f'{path}models/{currency}_value.sav'
    regressor = pickle.load(open(filename_re, 'rb'))
    return classifier.predict_proba([X])[0], regressor.predict([X])[0]

