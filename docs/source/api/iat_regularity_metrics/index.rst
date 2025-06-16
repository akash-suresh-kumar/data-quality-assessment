iat_regularity_metrics
======================

.. py:module:: iat_regularity_metrics


Functions
---------

.. autoapisummary::

   iat_regularity_metrics.computeModeDeviation
   iat_regularity_metrics.iatRegularityMetric


Module Contents
---------------

.. py:function:: computeModeDeviation(dataframe)

   Computes mode deviation for a given dataframe series.

   :param dataframe: Series or array of values

   :returns: Mode deviation value


.. py:function:: iatRegularityMetric(dataframe)

   Computes IAT regularity metric using Relative Absolute Error (RAE).

   :param dataframe: DataFrame with 'IAT' column

   :returns: IAT regularity metric score (0-1)


