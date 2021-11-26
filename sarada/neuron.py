"""
Learning and generating data.
"""
from __future__ import annotations

import itertools
import random

from typing import Final, Iterable, List, Optional, Tuple

import numpy as np
import tensorflow

from keras import Sequential, callbacks, layers
from keras.engine.training import Model
from loguru import logger

from sarada.numeris import Series


class Neuron:
    """
    Manages model, it's inputs and data generetion.
    """

    def __init__(self, input_length: int, output_length: int):
        self.input_length: Final = input_length
        self.output_length: Final = output_length
        self._model: Optional[Model] = None

    def learn(self, dataset: Iterable[Series]) -> None:
        """
        Begin model learning with provided data.

        Learning process is saved during the process.
        """
        filepath = "checkpoint"

        inputs, outputs = self.prepare_dataset(dataset)

        logger.debug("Initializong fitting checkpoint as {f}", f=filepath)

        checkpoint = callbacks.ModelCheckpoint(
            filepath, monitor="loss", verbose=0, save_best_only=True, mode="min"
        )

        logger.debug("Starting fitting model")
        self.model.fit(
            inputs, outputs, epochs=200, batch_size=64, callbacks=[checkpoint]
        )
        logger.info("Model fitting finished")

    def assemble(self) -> Model:
        """
        Create neuron network model.
        """
        if not tensorflow.config.list_physical_devices("GPU"):
            logger.warning("No GPU detected")

        logger.debug("Creating initial model")
        layer_list = [
            layers.LSTM(256, input_shape=(self.input_length, 1), return_sequences=True),
            layers.Dropout(0.3),
            layers.LSTM(512, return_sequences=True),
            layers.Dropout(0.3),
            layers.LSTM(256),
            layers.Dense(256),
            layers.Dropout(0.3),
            layers.Dense(self.output_length),
            layers.Activation("softmax"),
        ]

        model = Sequential(layers=layer_list)
        model.compile(loss="categorical_crossentropy", optimizer="rmsprop")

        return model

    def prepare_dataset(
        self, dataset: Iterable[Series]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert series to size appriopriate for the learning mechanism.
        """
        logger.debug("Preparing dataset")
        input_list = []
        output_list = []

        for series in dataset:
            input_list.append(series.input)
            output_list.append(series.output)

        inputs = np.reshape(input_list, (len(input_list), self.input_length, 1))
        outputs = np.array(output_list)

        logger.debug("Inputs size: {shape}", shape=inputs.shape)
        logger.debug("Outputs size: {shape}", shape=outputs.shape)

        return inputs, outputs

    def generate(self, length: int) -> List[float]:
        """
        Generate sequence of requested length musing model.
        """
        logger.info("Generating data")
        logger.debug("Attempting to generate series of {} values", length)

        inset = [random.random() for _ in itertools.repeat(None, self.input_length)]

        results: List[float] = []
        for i in range(length + self.input_length):
            state = np.reshape(inset, (1, self.input_length, 1))

            prediction = self.model.predict(state)

            idx: int = int(np.argmax(prediction))

            inset = inset[1:]
            normalized_output = idx / self.output_length
            inset.append(normalized_output)

            if i >= self.input_length:
                results.append(normalized_output)

        return results

    @property
    def model(self) -> Model:
        """Lazily created model instance."""
        if self._model is None:
            self._model = self.assemble()

        return self._model
