required_fields_validation
==========================

.. py:module:: required_fields_validation


Functions
---------

.. autoapisummary::

   required_fields_validation.validate_requiredFields


Module Contents
---------------

.. py:function:: validate_requiredFields(dataF, setReqd)

   Validates that required fields are present in JSON data.
   Treats null values as missing attributes.

   :param dataF: Path to JSON file containing data
   :param setReqd: Set of required field names

   :returns:

             - num_samples: Total number of samples processed
             - num_missing_prop: Total number of missing properties across all samples
   :rtype: Tuple containing


