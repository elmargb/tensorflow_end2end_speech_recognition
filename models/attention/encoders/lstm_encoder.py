#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""LSTM Encoder class."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from collections import namedtuple
import tensorflow as tf

# template
EncoderOutput = namedtuple(
    "EncoderOutput",
    [
        "outputs",
        "final_state",
        "attention_values",
        "attention_values_length"
    ])


class LSTMEncoder(object):
    """LSTM Encoder.
    Args:
        num_cell:
        num_layer:
        keep_prob_input:
        keep_prob_hidden:
        parameter_init:
        clip_activation:
        num_proj:
    """

    def __init__(self,
                 num_cell,
                 num_layer,
                 keep_prob_input=1.0,
                 keep_prob_hidden=1.0,
                 parameter_init=0.1,
                 clip_activation=50,
                 num_proj=None,
                 name='lstm_encoder'):

        self.num_cell = num_cell
        self.num_layer = num_layer
        self.keep_prob_input = keep_prob_input
        self.keep_prob_hidden = keep_prob_hidden
        self.parameter_init = parameter_init
        self.clip_activation = clip_activation
        self.num_proj = num_proj
        self.name = name

    def __call__(self, *args, **kwargs):
        # TODO: variable_scope
        with tf.name_scope('Encoder'):
            return self._build(*args, **kwargs)

    def _build(self, inputs, seq_len):
        """Construct LSTM encoder.
        Args:
            inputs:
            seq_len:
        Returns:
            EncoderOutput: A tuple of
                `(outputs, final_state,
                        attention_values, attention_values_length)`
                outputs:
                final_state: LSTMStateTuple
                attention_values:
                attention_values_length:
        """
        self.inputs = inputs
        self.seq_len = seq_len

        # Input dropout
        outputs = tf.nn.dropout(inputs,
                                self.keep_prob_input,
                                name='dropout_input')
        # Hidden layers
        lstm_list = []
        for i_layer in range(self.num_layer):
            with tf.name_scope('LSTM_encoder_hidden' + str(i_layer + 1)):

                initializer = tf.random_uniform_initializer(
                    minval=-self.parameter_init,
                    maxval=self.parameter_init)

                lstm = tf.contrib.rnn.LSTMCell(self.num_cell,
                                               use_peepholes=True,
                                               cell_clip=self.clip_activation,
                                               initializer=initializer,
                                               num_proj=self.num_proj,
                                               forget_bias=1.0,
                                               state_is_tuple=True)

                # Dropout (output)
                lstm = tf.contrib.rnn.DropoutWrapper(
                    lstm, output_keep_prob=self.keep_prob_hidden)

                lstm_list.append(lstm)

        # Stack multiple cells
        stacked_lstm = tf.contrib.rnn.MultiRNNCell(
            lstm_list, state_is_tuple=True)

        outputs, final_state = tf.nn.dynamic_rnn(cell=stacked_lstm,
                                                 inputs=inputs,
                                                 sequence_length=seq_len,
                                                 dtype=tf.float32)

        return EncoderOutput(outputs=outputs,
                             final_state=final_state,
                             attention_values=outputs,
                             attention_values_length=seq_len)
