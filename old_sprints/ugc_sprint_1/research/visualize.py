from pathlib import Path

import numpy as np
import pandas as pd
import seaborn as sns


def read_result(path: Path):
    _data_frame = pd.read_json(path).T
    _data_frame.columns = [" ".join((path.stem, item)) for item in _data_frame.columns]
    return _data_frame


data_frames = map(read_result, Path(".").glob("*.json"))
df = pd.concat(data_frames, axis=1).applymap(np.median)
df.reset_index(inplace=True)
df.columns = ["count"] + list(df.columns[1:])

df = df.melt("count", var_name="type", value_name="elapsed")

plot = sns.lineplot(df, x="count", y="elapsed", hue="type")

plot.get_figure().savefig("diagram.png")
