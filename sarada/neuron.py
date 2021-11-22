"""
Learning and generating data.
"""
from typing import Final, Iterable, Optional, Tuple

import numpy as np
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
        inputs, outputs = self.prepare_dataset(dataset)

        filepath = "checkpoint"
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
        logger.debug("Preparing data")
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

    @property
    def model(self) -> Model:
        """Lazily created model instance."""
        if self._model is None:
            self._model = self.assemble()

        return self._model
