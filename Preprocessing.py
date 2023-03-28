import itertools
from collections import Counter

import pandas as pd


def create_rap_df():
    # load in top50_2018_2022.csv
    df = pd.read_csv("data/top50_2018_2022.csv")
    # this csv has a column with the lyrics in one string

    # we should split the primary artists for explode to work
    df["Primary Artists"] = df["Primary Artists"].str.replace(" & ",",")
    df["Primary Artists"] = df["Primary Artists"].str.replace(", ", ",")
    df["Primary Artists"] = df["Primary Artists"].str.split(",")

    # apply preprocess function to each list in the lyrics column
    df["Lyrics"] = df["Lyrics"].apply(lambda x: preprocess(x))

    return df


def preprocess(lyrics):

    # 1. split
    lyrics = lyrics.split()
    # 2. lemmatization to convert words to their root form
    # IMPORTANT: remove punctuation but leave in apostrophes

    ### i think converting the lyrics to lower() would be good too

    return lyrics


def create_word_count_dict(df):
    # create a dictionary of words and their counts and their relative frequencies
    # without grouping, just combine all lists into one list and count
    words = list(itertools.chain.from_iterable(df['Lyrics']))
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
