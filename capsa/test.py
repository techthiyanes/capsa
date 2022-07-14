import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras import layers

from wrapper import Wrapper
from mve import MVEWrapper
from utils.utils import get_user_model, plt_vspan, plot_results, plot_loss
from data.regression import get_data_v1, get_data_v2

def plot_aleatoric(x_val, y_val, y_pred, variance):
    fig, axs = plt.subplots(2)
    axs[0].scatter(x_val, y_val, s=.5, label="gt")
    axs[0].scatter(x_val, y_pred, s=.5, label="yhat")
    plt_vspan()
    axs[1].scatter(x_val, variance, s=.5, label="aleatoric")
    plt_vspan()
    plt.legend()
    plt.show()

def test_regression(use_case=None):

    their_model = get_user_model()
    ds_train, ds_val, x_val, y_val = get_data_v2(batch_size=256)

    # user can interact with a MetricWrapper directly
    if use_case == 1:
        model = MVEWrapper(their_model)
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=2e-3),
            loss=tf.keras.losses.MeanSquaredError(),
        )
        history = model.fit(ds_train, epochs=30)
        plot_loss(history)

        plt.plot(history.history['loss'])
        plt.show()
        
        y_pred, variance = model(x_val)

    # user can interact with a MetricWrapper through Wrapper (what we call a "controller wrapper")
    elif use_case == 2:
        model = Wrapper(their_model, metrics=[MVEWrapper])

        model.compile(
            # user needs to specify optim and loss for each metric
            optimizer=[tf.keras.optimizers.Adam(learning_rate=2e-3)],
            # note reduction needs to be NONE, model reduces to mean under the hood
            loss=[tf.keras.losses.MeanSquaredError(reduction=tf.keras.losses.Reduction.NONE)],
        )

        history = model.fit(ds_train, epochs=30)
        plot_loss(history)

        metrics_out = model(x_val)
        y_pred, variance = metrics_out[0]

    plot_aleatoric(x_val, y_val, y_pred, variance)

def test_regression_predict():

    their_model = get_user_model()
    ds_train, ds_val, _, _ = get_data_v2(batch_size=256)

    model = Wrapper(their_model, metrics=[MVEWrapper])

    model.compile(
        # user needs to specify optim and loss for each metric
        optimizer=[tf.keras.optimizers.Adam(learning_rate=2e-3)],
        # note reduction needs to be NONE, model reduces to mean under the hood
        loss=[tf.keras.losses.MeanSquaredError(reduction=tf.keras.losses.Reduction.NONE)],
    )

    history = model.fit(ds_train, epochs=30)
    plot_loss(history)

    # predict cats batch output to a single tensor under the hood
    # metrics_out is a list (of len 1) of tuples (x_val_batch, y_val_batch)
    metrics_out = model.predict(ds_val)
    y_pred, variance = metrics_out[0]

    # need this for plotting -- cat all batches
    # list(ds_val) is a list (of len num of batches) of tuples (x_val_batch, y_val_batch)
    cat = np.concatenate(list(ds_val), 1) # (2, 2304, 1)
    x_val, y_val = cat[0], cat[1]

    plot_aleatoric(x_val, y_val, y_pred, variance)

test_regression(use_case=1)
test_regression(use_case=2)
test_regression_predict()