PreProcessing
=============

.. py:module:: PreProcessing


Attributes
----------

.. autoapisummary::

   PreProcessing.custom_style


Functions
---------

.. autoapisummary::

   PreProcessing.readFile
   PreProcessing.timeRange
   PreProcessing.dropDupes
   PreProcessing.outRemove
   PreProcessing.dataStats
   PreProcessing.radarChart
   PreProcessing.bars
   PreProcessing.plotDupesID
   PreProcessing.plotDupes
   PreProcessing.IAThist
   PreProcessing.outScatterPlot
   PreProcessing.boxPlot
   PreProcessing.normalFitPlot
   PreProcessing.piePlot
   PreProcessing.gaugePlot
   PreProcessing.outagePlot
   PreProcessing.outliersPlot


Module Contents
---------------

.. py:data:: custom_style

.. py:function:: readFile(configFile)

.. py:function:: timeRange(dataframe)

.. py:function:: dropDupes(dataframe, input1, input2)

.. py:function:: outRemove(df, dataFile, input1)

.. py:function:: dataStats(df)

.. py:function:: radarChart(regularityScore, outliersScore, dupeScore, formatScore, completeScore, addnlScore)

.. py:function:: bars(score, name)

.. py:function:: plotDupesID(df, df1, input1)

.. py:function:: plotDupes(dataframe, input1, input2)

.. py:function:: IAThist(df)

.. py:function:: outScatterPlot(df)

.. py:function:: boxPlot(df, fileName, input1)

.. py:function:: normalFitPlot(df)

.. py:function:: piePlot(df, df1, name)

.. py:function:: gaugePlot(metricScore, name)

.. py:function:: outagePlot(df, meanStat, stdStat)

.. py:function:: outliersPlot(dataframe)

