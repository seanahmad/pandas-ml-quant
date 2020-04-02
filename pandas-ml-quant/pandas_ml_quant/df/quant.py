import pandas as pd

import pandas_ml_quant.analysis as analysis
import pandas_ml_quant.trading.strategy.optimized as optimized_strategies
from pandas_ml_quant.df.plot import TaPlot


class Quant(object):

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def ta_plot(self, rows=2, cols=1, figsize=(18, 10), main_height_ratio=4):
        return TaPlot(self.df, figsize, rows, cols, main_height_ratio)


# FIXME remove all this stuff below as we use the "ta." namespace for indicators and such and keep the "q."
#  namespace for plotting and such.

# add wrapper to call all indicators on data frames
def wrapper(func):
    def wrapped(quant, *args, **kwargs):
        print(f"obsolete use df.ta.{func.__name__[3:]}")
        return func(quant.df, *args, **kwargs)

    return wrapped


# add indicators
for indicator_functions in [analysis, optimized_strategies]:
    for indicator_function in dir(indicator_functions):
        if indicator_function.startswith("ta_"):
            setattr(Quant, indicator_function, wrapper(getattr(indicator_functions, indicator_function)))



