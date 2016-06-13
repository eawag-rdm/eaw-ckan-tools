# eaw-ckan-tools

Various CKAN-external bits and pieces. Varying degrees of documentation, generality, usefulness. Not for public consumption.

## ck_choices.py

<pre>
<b>usage:</b> ck_choices.py [-h] [--del] [--resource] FIELD TERM [TERM ...]
Make modifications to the controlled vocabulary FIELD
(implemented as ckanext-scheming "choices").

<b>positional arguments:</b>
FIELD       the schema field to be modified
TERM        the terms to be added (removed). Have the format "value,label"
                for adding, and "value" for removing.

<b>optional arguments:</b>
  -h, --help  show this help message and exit
  --del       delete terms (default is adding terms)
  --resource  action refers to resource field (default is dataset field)

<b>Examples:</b>
  ck_choices.py variables "new_var_1,New Variable One" newvar2,"Another One"
  adds two new terms to the dataset_field "variables".

  ck_choices.py variables --del new_var_1 newvar2
  deletes them.
</pre>

