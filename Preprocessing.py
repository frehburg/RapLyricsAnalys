import itertools
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
nltk.download("omw-1.4")
nltk.download("wordnet")
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")
nltk.download("stopwords")
from collections import Counter

import pandas as pd


def create_rap_df(remove_stopwords=False, lemmatize=False, trim_swearwords=False):
    # load in top50_2018_2022.csv
    df = pd.read_csv("data/top50_2018_2022.csv", encoding = 'unicode_escape')
    # this csv has a column with the lyrics in one string

    # we should split the primary artists for explode to work
    df["Primary Artists"] = df["Primary Artists"].str.replace(" & ", ",")
    df["Primary Artists"] = df["Primary Artists"].str.replace(", ", ",")
    df["Primary Artists"] = df["Primary Artists"].str.split(",")

    # apply preprocess function to each list in the lyrics column
    df["Lyrics"] = df["Lyrics"].apply(lambda x: preprocess(x, remove_stopwords=remove_stopwords, lemmatize=lemmatize, trim_swearwords=trim_swearwords))

    return df

# trims chosen swear words to their core
def preprocess_swear_word(word):
    if "motherfuck" in word or word.startswith("mothaf"):
        return "motherfuck"
    if word.startswith("fuck"):
        return "fuck"
    return word

def preprocess(lyrics, remove_stopwords=False, lemmatize=False, trim_swearwords=False):

    # feel free to change it if needed. the steps are left below.
    # not removing the apostrophe caused problems for me, so thats why i did remove it ( i think "dont" is fine instead of "don't)

    # Remove punctuation
    lyrics = re.sub("[^a-zA-Z0-9\s]", "", lyrics)
    # Convert to lowercase
    lyrics = lyrics.lower()
    # Tokenize into individual words
    stop_words = []
    if remove_stopwords:
        stop_words = set(stopwords.words("english"))
    tokens = []
    if lemmatize:
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(i,j[0].lower()) if j[0].lower() in ["a","n","v"] else lemmatizer.lemmatize(i) for i,j in nltk.pos_tag(nltk.word_tokenize(lyrics))]
    else:
        tokens = lyrics.split()
    if trim_swearwords:
        words = [preprocess_swear_word(w) for w in tokens if w not in stop_words]
    else:
        words = [w for w in tokens if w not in stop_words]
    # 1. split
    #lyrics = lyrics.lower().split()
    # 2. lemmatization to convert words to their root form
    # IMPORTANT: remove punctuation but leave in apostrophes
    return words


def create_word_count_dict(df):
    # create a dictionary of words and their counts and their relative frequencies
    # without grouping, just combine all lists into one list and count
    words = df["Lyrics"].sum()
    return dict(Counter(words))

def create_word_count_dict_grouped(df, artists=False, year=False):
    assert artists or year

    songs = df.copy()
    groupby = []

    if artists:
        songs = songs.explode('Primary Artists')
        groupby.append("Primary Artists")
    if year:
        groupby.append("year")

    grouped_lyrics = songs.groupby(groupby)['Lyrics'].sum().reset_index()

    word_counts = {}
    for i, row in grouped_lyrics.iterrows():
        key = tuple(row[gb] for gb in groupby)
        counts = dict(Counter(row['Lyrics']))
        if key in word_counts:
            word_counts[key].update(counts)
        else:
            word_counts[key] = counts

    return word_counts

#%%
