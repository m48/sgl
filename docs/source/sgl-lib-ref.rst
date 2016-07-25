SGL Library Reference
====

``sgl.lib`` is where a lot of the functions useful for making games will live. Not much of it is written right now, and you should probably avoid using most of what's there, as it might change. Here's a brief summary of the modules it currently includes, though:

* ``sgl.lib.Script`` - Provides a small domain specific markup language for writing in game cut scenes. Is designed to be easy for writers to understand and for programmers to implement support for. The syntax of this language is currently undergoing a great revision. This is the module that you should avoid using the most right now.
* ``sgl.lib.Time`` - Provides the ability to register functions to happen at specific times or intervals. Useful for making pieces of code happen at a specific frame rate, for animated sprites and such.
* ``sgl.lib.Tween`` - Provides "tweening" functionality, which lets you specify start and end values for any numerical property of any object, and animate them moving from point A to point B in a given amount of time with the given interpolation. Makes it much easier to add dynamic animations to in game GUIs and game elements.
 
Sound exciting? Hopefully, because there will be even more in the future! :p
  
.. automodule:: sgl.lib.Sprite
                :members:

