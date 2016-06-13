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

## ck-maintain

<pre>
<b>Usage:</b> ck-maintain off|on TIME

Switches maintenance modus for CKAN on or off. The maintenance-page, to which
users will be redirected, contains the string TIME as the expected time
when the service will become available again.

<b>Note:</b>
Here is an example for the maintenance-page:<a href="https://github.com/eawag-rdm/eaw-ckan-tools/blob/master/maintenance.html>maintenance.html</a>.
That page has to be put in the nginx document-root: /usr/share/nginx/html.
</pre>

`codeexample`

</pre>
