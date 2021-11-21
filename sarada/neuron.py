"""
Learning and generating data.
"""
from typing import Iterable, Tuple

import numpy as np
from keras import Sequential, callbacks, layers
from keras.engine.training import Model
from loguru import logger
from numpy.typing._shape import _Shape

from sarada.numeris import Series


def teach_from_series(dataset: Iterable[Series], nwords: int) -> Model:
    """
    Learn model from given dataset.
    """
    inputs, outputs = prepare_dataset(dataset)

    model = assemble_model(inputs.shape, nwords)

    teach(model, inputs, outputs)

    return model


def prepare_dataset(dataset: Iterable[Series]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert series to size appriopriate for the learning mechanism.
    """
    logger.debug("Preparing data")
    input_list = []
    output_list = []

    for series in dataset:
        input_list.append(series.input)
        output_list.append(series.output)

    inputs = np.reshape(input_list, (len(input_list), len(input_list[0]), 1))
    outputs = np.array(output_list)

    logger.debug("Inputs size: {shape}", shape=inputs.shape)
    logger.debug("Outputs size: {shape}", shape=outputs.shape)

    return inputs, outputs


def assemble_model(input_shape: _Shape, nwords: int) -> Model:
    """
    Create neuron network model.
    """
    logger.debug("Creating initial model")
    layer_list = [
        layers.LSTM(
            256, input_shape=(input_shape[1], input_shape[2]), return_sequences=True
        ),
        layers.Dropout(0.3),
        layers.LSTM(512, return_sequences=True),
        layers.Dropout(0.3),
        layers.LSTM(256),
        layers.Dense(256),
        layers.Dropout(0.3),
        layers.Dense(nwords),
        layers.Activation("softmax"),
    ]

    model = Sequential(layers=layer_list)
    model.compile(loss="categorical_crossentropy", optimizer="rmsprop")

    return model


def teach(model: Model, inputs: np.ndarray, outputs: np.ndarray) -> None:
    """
    Begin model learning with data given.

    Learning process is saved during the process.
    """
    filepath = "checkpoint"
    checkpoint = callbacks.ModelCheckpoint(
        filepath, monitor="loss", verbose=0, save_best_only=True, mode="min"
    )

    logger.debug("Starting fitting process")

    model.fit(inputs, outputs, epochs=200, batch_size=64, callbacks=[checkpoint])

    logger.info("Model fitting finished")
