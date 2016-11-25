import tensorflow as tf
from tensorflow.contrib.layers.python.layers import initializers

import layers


class HRED():

    def __init__(self):
        # We do not need to define parameters explicitly since tf.get_variable() also creates parameters for us

        self.vocab_size = 6
        self.embedding_size = 3
        self.query_hidden_size = 4
        self.session_hidden_size = 5
        self.decoder_hidden_size = self.query_hidden_size
        self.eoq_symbol = 0  # End of Query symbol

    def step(self, X, start_hidden_query, start_hidden_session, start_hidden_decoder, start_output):

        embedder = layers.embedding_layer(X, vocab_dim=self.vocab_size, embedding_dim=self.embedding_size)

        # Mask used to reset the query encoder when symbol is End-Of-Query symbol
        x_mask = tf.expand_dims(tf.cast(tf.not_equal(X, self.eoq_symbol), tf.float32), 2)

        query_encoder_packed = tf.scan(
            lambda result_prev, x: layers.gru_layer_with_reset(
                result_prev[1],  # h_reset_prev
                x,
                name='query_encoder',
                x_dim=self.embedding_size,
                y_dim=self.query_hidden_size
            ),
            (embedder, x_mask),  # scan does not accept multiple tensors so we need to pack and unpack
            initializer=start_hidden_query
        )

        query_encoder, _ = tf.unpack(query_encoder_packed, axis=1)

        session_encoder_packed = tf.scan(
            lambda result_prev, x: layers.gru_layer_with_retain(
                result_prev[1], # h_retain_prev
                x,
                name='session_encoder',
                x_dim=self.query_hidden_size,
                y_dim=self.session_hidden_size
            ),
            (query_encoder, x_mask),
            initializer=start_hidden_session
        )

        session_encoder, _ = tf.unpack(session_encoder_packed, axis=1)

        decoder = tf.scan(
            lambda result_prev, x: layers.gru_layer_with_state_reset(
                result_prev,
                x,
                name='decoder',
                x_dim=self.embedding_size,
                h_dim=self.session_hidden_size,
                y_dim=self.decoder_hidden_size
            ),
            (embedder, x_mask, session_encoder),  # scan does not accept multiple tensors so we need to pack and unpack
            initializer=start_hidden_decoder
        )

        def output_func(_, x_packed):
            decoder, embedder, session_encoder = x_packed

            output = layers.output_layer(
                decoder,
                embedder,
                session_encoder,
                x_dim=self.embedding_size,
                h_dim=self.decoder_hidden_size,
                y_dim=self.decoder_hidden_size,
                s_dim=self.session_hidden_size
            )

            return layers.softmax_layer(
                output,
                x_dim=self.decoder_hidden_size,
                y_dim=self.vocab_size
            )

        output = tf.scan(
            output_func,
            (decoder, embedder, session_encoder),
            initializer=start_output
        )

        return output