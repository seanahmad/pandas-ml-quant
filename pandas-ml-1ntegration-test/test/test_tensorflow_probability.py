import os
from unittest import TestCase

import numpy as np
import pandas as pd
import tensorflow as tf
import tensorflow_probability as tfp

import pandas_ml_utils as pmu
from pandas_ml_quant import PostProcessedFeaturesAndLabels
from pandas_ml_quant.keras.time_2_vec import Time2Vec
from pandas_ml_quant.keras.time_2_vec import tf_Time2Vec as Time2Vec
from pandas_ml_quant_test.config import DF_TEST
from pandas_ml_utils.keras.callbacks import plot_losses
from pandas_ml_utils.ml.summary import RegressionSummary

os.environ["CUDA_VISIBLE_DEVICES"] = ""
print(pmu.__version__)


class TestTensorflowProbability(TestCase):

    def test_ftp_model(self):
        df = DF_TEST.copy()

        features_and_labels = PostProcessedFeaturesAndLabels(
            features=[
                # lambda df: df.ta.candles_as_culb(relative_close=True)
                lambda df: df["Close"].ta.returns()
            ],
            feature_post_processor=[
                lambda df: df.ta.rnn(28)
            ],
            labels=[
                df["Close"].pct_change().rolling(30).std()
            ],
            labels_post_processor=[
                lambda df: pd.DataFrame({i: df.iloc[:, 0] * np.sqrt(1 / 30 * i) for i in range(1, 8)}, index=df.index)
            ],
        )

        def model_provider():
            model = tf.keras.Sequential([
                Time2Vec(8, input_shape=(28, 1)),
                tf.keras.layers.LSTM(8, activation='tanh'),
                tf.keras.layers.Dense(2, activation='tanh'),
                tfp.layers.DenseFlipout(7, activation='tanh'),
            ])

            model.compile(tf.keras.optimizers.Adam(), loss='mse')

            return model

        model_provider()

        fit = df.model.fit(
            pmu.KerasModel(
                model_provider,
                features_and_labels,
                summary_provider=RegressionSummary,
                # keras args
                callbacks=[plot_losses(tf.keras.callbacks.Callback)],
                verbose=1,
                epochs=2,
                batch_size=128
            )
        )

        fit