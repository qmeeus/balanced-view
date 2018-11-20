import pandas as pd
import numpy as np
import dask.dataframe as dd
from time import time


URL_RGX = r"((http|ftp|https):\/\/)?([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])?"


# --- Data ---
def load_dask(fn):
    # 3261930 rows
    # Using dask for multithread support
    df = dd.read_csv(fn, dtype='object')
    df = df.repartition(npartitions=128)
    print(f'{len(df.index)} rows x {len(df.columns)} cols')
    return df


def load_sample(fn, nrows):
    df = pd.read_csv(fn, nrows=nrows)
    print('{} rows x {} cols'.format(*df.shape))
    return df


def load_data(fn, sample=True, size=1000):
    t0 = time()
    df = load_sample(fn, size) if sample else load_dask(DATA_FILE)
    print(f'Loaded in {time() - t0:.2f}s'); t0 = time()
    df = clean(df)
    print(f'Cleaning ops done in {time() - t0:.2f}s')
    return df


def clean(df):
    df["tweet_time"] = dd.to_datetime(df["tweet_time"], format="%Y-%m-%d %H:%M")
    df["tweet_text"] = df["tweet_text"].str.replace(URL_RGX, "%URL%")
    return (df.set_index('tweet_time')
#            .drop(["longitude", "latitude", "tweet_language", "poll_choices", "urls"], axis=1)
    )


# --- Visualisation ---
def histogram_summary(ax, x, y, summary):
    textbox = "\n".join([": ".join([k, v]) for k, v in summary.items()])
    ax.text(.3, .7, textbox,
            horizontalalignment='left',
            verticalalignment='top',
            transform=ax.transAxes,
            fontsize=14);
    ax.get_figure().set_size_inches((16, 6))

    
def prep_frequency(matrix, feature_names, aggfunc):
    return (
        pd.DataFrame(aggfunc(matrix, axis=0).T, 
                     index=feature_names,
                     columns=["count"])
        .sort_values("count", ascending=False))


def frequency_histogram(matrix, feature_names, k=50, thres=100, aggfunc=np.sum):
    cnts = prep_frequency(matrix, feature_names, aggfunc)
    n = len(cnts)
    sel = cnts.iloc[:k, :]
    ax = sel.plot.bar()
    nunique_words = (cnts["count"] <= 1).sum()
    less_frequent = (cnts["count"] < thres).sum()
    ax.set_title(f"Top-{k}", fontsize=18)
    summary = {
        'size of vocabulary': f"{n:,}",
        f'cumulated frequency (Top-{k})': f"{(sel.sum() / cnts.sum()).values[0]:.2%}",
        f"n unique words": f"{nunique_words:,} (~ {nunique_words / n:.2%})",
        f"less frequent words (<{thres})": f"{less_frequent:,} (~ {less_frequent / n:.2%})"
    }
    histogram_summary(ax, .3, .7, summary)
    return cnts