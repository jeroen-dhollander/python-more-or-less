Python More or Less
*******************

This library makes it easy to add ``more`` paginating to your application.


This means that it will print a full page of output,
after which it will prompt the user on how to continue.

It supports multiple continue actions, and full control over where the input
comes from, and where the output is printed to.

Available continue actions
===========================

This library supports all the usual continue actions, like space for another page,
enter for a single more line, and many more.

To see all the available operations, press ``h`` at the ``--More--`` prompt::

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
    .                      Repeat previous command
    h or ?                 Display this help text
    -------------------------------------------------------------------------------

How to use this library
=======================

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
      more_or_less.paginate(input=iterator,  output=myCustomOutput())

To use another screen height than your terminal session, pass in a ``ScreenDimensions`` object, like the built-in ``FixedSizeScreen``:

.. code:: python

    import more_or_less

    more_or_less.paginate(
        input=iterator,
        screen_dimensions=more_or_less.FixedSizeScreen(height=25)
    )

Finally, to run the paginator asynchronously, simply pass in ``asynchronous=True``

.. code:: python

    more_or_less.paginate(
        input=iterator,
        asynchronous=True
    )

This is especially useful if you use a ``queue.Queue`` as input.
In this case, use ``more_or_less.END_OF_INPUT`` to let our paginator know it should stop,
and join the returned object to wait for the paginator to end:

.. code:: python

    my_queue = queue.Queue()
    controller = more_or_less.paginate(input=my_queue, asynchronous=True)

    my_queue.put('first line\n')
    my_queue.put('second line\n')
    # Signal we're done
    my_queue.put(more_or_less.END_OF_INPUT)
    # Wait for the pagination to complete
    controller.join()

Advanced topics
###############

Adding plugins
----------------

All actions you take at the ``more`` prompt (space for one more page, enter for one more line, and so on) are installed using plugins.

This makes it easy to extend the functionality, by creating your own ``MorePlugin``
and installing it through ``more_or_less.add_plugin``.

For examples, see our `rainbow plugin <https://github.com/jeroen-dhollander/python-more-or-less/blob/master/examples/more_with_rainbow_page_plugin.py>`_ and our `rainbow toggle <https://github.com/jeroen-dhollander/python-more-or-less/blob/master/examples/more_with_rainbow_toggle_plugin.py>`_.


Changing prompt reader
-----------------------

When the output is paused waiting for a continue action,
we read this action from ``stdin``.

This can be changed by passing in a custom ``Input`` object.
For example, any time we hit a more prompt the following code will automatically search for ``"the search pattern"``:

.. code:: python

	class MyCustomInput(more_or_less.Input):

		def prompt(self, message):
		    # Return a full line of input.
		    # Used for example after typing a '/'
		    return "the search pattern"

		def get_character(self, message):
		    # Returns a single input character
		    return '/'
	
	more_or_less.paginate(input=iterator, prompt=MyCustomInput())	    
		   

Running unittests
------------------

Checkout this code, go to the root directory and execute

     python -m unittest discover tests