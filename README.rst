Sarada
======

*PoC* aimed in an attempt to generate music.

What is it?
-----------

Proof of concept prediction software that will attempt to generate music.
It works based on simple recursive multilayer model that is trained using
existing model files.

Supported file formats are:

- abc

Current attemp is to apply text prediction mechanics on the series of notes to predict
the next note.

Note: At the moment only simple notes (corresponding to music21.notes.Note) are
supported.

Usage
-----

Currently there is only one way to run command

.. code-block:: bash

 $ sarada prepare <PATH>  [model_path]

 This will initialize model and preparse datasets from ``PATH``.

Then to start learning process you must use:

.. code-block:: bash

 $ sarada fit <model_path> --epochs 100

To generate new data please try:

.. code-block:: bash

 $ sarada generate <model_path>

Note: CLI interface is being reworked, will change.

License
-------

See `LICENSE <https://github.com/wikii122/sarada/LICENSE>`__.
