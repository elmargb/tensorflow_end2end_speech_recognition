#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Bidirectional LSTM Encoder class."""

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


class BLSTMEncoder(object):
    """Bidirectional LSTM Encoder.
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
                 keep_prob_input,
                 keep_prob_hidden,
                 parameter_init=0.1,
                 clip_activation=50,
                 num_proj=None,
                 name='blstm_encoder'):

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
        """Construct Bidirectional LSTM encoder.
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
        for i_layer in range(self.num_layer):
            with tf.name_scope('BiLSTM_encoder_hidden' + str(i_layer + 1)):

                initializer = tf.random_uniform_initializer(
                    minval=-self.parameter_init,
                    maxval=self.parameter_init)

                lstm_fw = tf.contrib.rnn.LSTMCell(
                    self.num_cell,
                    use_peepholes=True,
                    cell_clip=self.clip_activation,
                    initializer=initializer,
                    num_proj=None,
                    forget_bias=1.0,
                    state_is_tuple=True)
                lstm_bw = tf.contrib.rnn.LSTMCell(
                    self.num_cell,
                    use_peepholes=True,
                    cell_clip=self.clip_activation,
                    initializer=initializer,
                    num_proj=self.num_proj,
                    forget_bias=1.0,
                    state_is_tuple=True)

                # Dropout (output)
                lstm_fw = tf.contrib.rnn.DropoutWrapper(
                    lstm_fw,
                    output_keep_prob=self.keep_prob_hidden)
                lstm_bw = tf.contrib.rnn.DropoutWrapper(
                    lstm_bw,
                    output_keep_prob=self.keep_prob_hidden)

                # _init_state_fw = lstm_fw.zero_state(self.batch_size,
                #                                     tf.float32)
                # _init_state_bw = lstm_bw.zero_state(self.batch_size,
                #                                     tf.float32)
                # initial_state_fw=_init_state_fw,
                # initial_state_bw=_init_state_bw,

                (outputs_fw, outputs_bw), final_state = tf.nn.bidirectional_dynamic_rnn(
                    cell_fw=lstm_fw,
                    cell_bw=lstm_bw,
                    inputs=outputs,
                    sequence_length=seq_len,
                    dtype=tf.float32,
                    scope='BiLSTM_' + str(i_layer + 1))

                outputs = tf.concat(axis=2, values=[outputs_fw, outputs_bw])

        return EncoderOutput(outputs=outputs,
                             final_state=final_state,
                             attention_values=outputs,
                             attention_values_length=seq_len)
