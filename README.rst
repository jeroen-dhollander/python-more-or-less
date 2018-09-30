Python More or Less
*******************

This library makes it easy to add ``more`` paginating to your application.

To see the operations available, press ``h`` at the ``--More--`` prompt::

    -------------------------------------------------------------------------------
    Most commands can optionally be preceded by an integer argument k.
    The default values are printed in brackets.
    A star (*) indicates the value of k becomes the new default.
    -------------------------------------------------------------------------------
    <space>                Display next k lines of text [current screen size]
    <return>               Display next k lines of text [1]*
    q or Q or <interrupt>  Exit from more
    =                      Display current line number
    l                      Toggle printing line number on every line [currently disabled]
    /<regular expression>  Search for kth occurrence of the regular expression [1]
    n                      Search for kth occurrence of the last regular expression [1]
    h or ?                 Display this help text
    -------------------------------------------------------------------------------

How to use this
===============

All you need to do is call ``paginate`` and pass in your input lines:

.. code:: python

  import more_or_less

  more_or_less.paginate(input=iterator_or_queue)

This uses your terminal's screen height, and prints the text to ``stdout``.

Do you want to use something other than ``stdout``? Just pass in what output to use

.. code:: python

   more_or_less.paginate(input=iterator, output=stderr)

This can be any object that has a ``write`` and ``flush`` method

.. code:: python

  class MyCustomOutput(object):
      def write(self, text):
          pass

      def flush(self): 
          pass

  def paginate(iterator):
      more_or_less.paginate(input=iterator, myCustomOutput())


Advanced topics
###############

Adding plugins
-------------------

All actions you take at the ``more`` prompt (space for one more page, enter for one more line, and so on) are installed using plugins.

This makes it easy to extend the functionality.

TODO: Flesh out

