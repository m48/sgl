SGL Core Reference
==================

SGL divided into two components--``sgl.lib`` and ``sgl.core``. ``sgl.core`` is the part of the library that provides the low-level drawing commands, similar to what you might find built into BlitzBasic or Processing. While ideally you should be able to spend most of your time in ``sgl.lib``, it is essential to use ``sgl.core`` to make even the simplest SGL program. 
 
To import ``sgl.core``, currently this is all that is required::

    import sgl

Then, to call any of the functions defined in ``sgl.core``, simply prefix them with ``sgl.``, such as this::

    sgl.init(640, 480)
    graphic = sgl.load_image("smiley.png")

.. warning:: This may change in the future. I may make it so to import ``sgl.core``, you must do it like this::

        import sgl.core as sgl

    **The benefits of this approach:** 
 
    * It will make the internal structure of the library easier to maintain
    * It will make it more obvious that ``sgl.core`` is actually called ``sgl.core``.

    **The detriments of this approach:** 

    * It is more typing for little benefit for the end-user.
    * The user must explicitly rename ``sgl.core`` to ``sgl`` to keep their command invocations short.

    I still haven't made up my mind which approach to take. Keep in mind you may have to change your import statements later. The command invocation will remain the same regardless, though--it is just the importing syntax that may change.

Concepts
----

Philosophy
^^^^

Most of ``sgl.core`` is fairly simple--it is a non-object-oriented module with various functions. This may irritate people who like object-oriented programming, and does create some clumsiness. For example, to get the width of a drawing surface, you cannot do something like this::
  
    graphic = sgl.load_image("smiley.png")
    print(graphic.width)
 
You must instead do this::
  
    graphic = sgl.load_image("smiley.png")
    with sgl.with_buffer(graphic):
       print(sgl.get_width())

People coming to SGL from non-object-oriented languages, like BlitzBasic, may be used to this, but this will undoubtedly bother Python programmers. I assure you, however, this is an intentional choice. In SGL, you have the freedom to choose how you want to program your game--whether you want to use object-oriented programming or not, and even how you organize the objects and classes of your game. ``sgl.lib`` is but one approach of organizing classes to wrap the internals of SGL. You can easily make your own if you wish, and I encourage you to do so.

I feel like existing Python game development frameworks are a little too dogmatic in how they force a certain structure on your programs, and I want to avoid that at all costs, even if my approach is a bit excessive. If you can wrap your head around this philosophy, most of ``sgl.core`` should make sense to you.

Fake types
^^^^

In the function reference, you may see references to types such as "SGL Surface" or "SGL Sound." These are not real types, however--whenever a function claims to accept or return values of these types, in reality, they are dealing with *classes of whatever the current backend is.* So, if you're using the Pygame backend, and you examine the type of an "SGL Surface", you will find that it is, in reality, a `pygame.Surface <http://www.pygame.org/docs/ref/surface.html>`_.

So, hypothetically, there's nothing stopping you from calling ``pygame.Surface`` commands on an SGL surface, like this::

                graphic = sgl.load_image("smiley.png")
                graphic.set_at((3, 3), (255, 0, 0))

Please don't do this, though. For one, this will obviously not work when different backends are introduced. And also, I may eventually actually wrap SGL Surfaces and such in classes like ``sglSurface`` or something, which will make your code broken on *all* backends.

Ideally, your code should be completely ignorant of what backend SGL is currently using. This'll make your game/program more portable, which is one of the main points of SGL existing.

Color arguments
^^^^

Color arguments in SGL are kind of ridiculously flexible, and take some influence from how `Processing works <https://processing.org/reference/fill_.html>`_.

Whenever you see an argument named ``*colors``, it can accept the values in the following formats:

* ``number`` - If you specify a single value as a color, it will specify shade of gray with that value used for the R, G, and B values of that color.
* ``number, number`` - If you specify to values as a color, the first number will specify the shade of gray, as it would with a single number, but the second number will specify the *transparency* of that shade of gray.
* ``number, number, number`` - If you specify three values, it will be interpreted as a normal RGB color.
* ``number, number, number, number`` - If you specify for values, it will be interpreted as a normal RGBA color.
* ``tuple/list`` - If you specify color as a tuple or list, it will be unpacked and interpreted as the arguments would.

In addition, for each number, the following rules apply:

* If the number is an integer, it will be interpreted as a normal RGB value that ranges from 0 to 255.
* If any numbers outside of this range, it will be clamped within that range.
* If the number is a float, it will be interpreted as a *percentage* of 255. So, for example, 0.5 would be half of 255.

This is perhaps a little complicated, but allows you to do some very convenient things. For example, if you want to clear the screen with 50% gray, it is as simple as doing this::

  sgl.clear(0.5)

If you want to make a surface that is black and 75% transparent, you can do this::

  surface = sgl.make_surface(320, 32, 0.0, 0.75)

And, if you feel it is confusing that the color data is getting mixed in with the rest of their arguments, you can pass in tuples as well::

  surface = sgl.make_surface(320, 32, (0.0, 0.75))

And, of course, you can use plain RGB values for everything::

  sgl.clear(100, 175, 93)  

Function reference
----

This is a reference of every single function in ``sgl.core``. It is not complete yet, but all of the most essential functions have been documented in some detail. Hopefully this is helpful.
 
Base functions
^^^^
These functions have to do with the base functioning of your program, and are essential for nearly everything you'd want to do with SGL.

.. autofunction:: sgl.init 
.. autofunction:: sgl.run
.. autofunction:: sgl.make_movie 
.. autofunction:: sgl.set_fps_limit
.. autofunction:: sgl.get_fps_limit
.. autofunction:: sgl.get_fps
.. autofunction:: sgl.get_scale
.. autofunction:: sgl.has
.. autofunction:: sgl.set_title
.. autofunction:: sgl.get_title
.. autofunction:: sgl.get_actual_screen_width
.. autofunction:: sgl.get_actual_screen_height
.. autofunction:: sgl.get_dt
.. autofunction:: sgl.is_running
.. autofunction:: sgl.end

Drawing commands
^^^^
These commands have to do with drawing shapes.

.. autofunction:: sgl.set_smooth
.. autofunction:: sgl.get_smooth
.. autofunction:: sgl.set_fill
.. autofunction:: sgl.get_fill
.. autofunction:: sgl.set_stroke
.. autofunction:: sgl.get_stroke
.. autofunction:: sgl.set_stroke_weight
.. autofunction:: sgl.get_stroke_weight
.. autofunction:: sgl.no_stroke
.. autofunction:: sgl.no_fill
.. autofunction:: sgl.push
.. autofunction:: sgl.pop
.. autofunction:: sgl.with_state
.. autofunction:: sgl.clear
.. autofunction:: sgl.draw_line
.. autofunction:: sgl.draw_rect
.. autofunction:: sgl.draw_ellipse
.. autofunction:: sgl.draw_circle

Text commands
^^^^
These commands have to do with rendering text.

.. autofunction:: sgl.set_font_smooth
.. autofunction:: sgl.get_font_smooth
.. autofunction:: sgl.load_font
.. autofunction:: sgl.load_system_font
.. autofunction:: sgl.set_font
.. autofunction:: sgl.draw_text
.. autofunction:: sgl.get_text_width
.. autofunction:: sgl.get_text_height

Image commands
^^^^
These commands have to do with loading images and stuff.
 
.. autofunction:: sgl.set_transparent_color
.. autofunction:: sgl.load_image
.. autofunction:: sgl.load_alpha_image

Surface commands
^^^^
These commands have to do with using surfaces and changing the current drawing buffer.

.. autofunction:: sgl.blit
.. autofunction:: sgl.blitf
.. autofunction:: sgl.make_surface
.. autofunction:: sgl.get_chunk
.. autofunction:: sgl.set_clip_rect
.. autofunction:: sgl.get_clip_rect
.. autofunction:: sgl.no_clip_rect
.. autofunction:: sgl.set_buffer
.. autofunction:: sgl.reset_buffer
.. autofunction:: sgl.with_buffer
.. autofunction:: sgl.get_width
.. autofunction:: sgl.get_height
.. autofunction:: sgl.save_image
.. autofunction:: sgl.to_numpy
.. autofunction:: sgl.from_numpy

Special Effect commands
^^^^
These commands do cool special effects.

.. autofunction:: sgl.invert
.. autofunction:: sgl.grayscale
 
Audio functions
^^^^
These functions have to do with playing music and sound effects.
 
.. autofunction:: sgl.load_sound 
.. autofunction:: sgl.play_sound
.. autofunction:: sgl.stop_sound
.. autofunction:: sgl.stop_all_sounds
.. autofunction:: sgl.is_sound_playing
.. autofunction:: sgl.play_music
.. autofunction:: sgl.pause_music
.. autofunction:: sgl.resume_music 
.. autofunction:: sgl.set_music_volume
.. autofunction:: sgl.stop_music
.. autofunction:: sgl.is_music_playing

Input commands
^^^^
These commands have to do with getting input.

.. autofunction:: sgl.add_input
.. autofunction:: sgl.supports_input
.. autofunction:: sgl.remove_input
.. autofunction:: sgl.has_input
.. autofunction:: sgl.on_key_down
.. autofunction:: sgl.on_key_up
.. autofunction:: sgl.is_key_pressed
.. autofunction:: sgl.get_keys_pressed
.. autofunction:: sgl.get_letters_pressed
.. autofunction:: sgl.show_mouse
.. autofunction:: sgl.hide_mouse
.. autofunction:: sgl.get_mouse_x
.. autofunction:: sgl.get_mouse_y
.. autofunction:: sgl.get_prev_mouse_x
.. autofunction:: sgl.get_prev_mouse_y
.. autofunction:: sgl.on_mouse_down
.. autofunction:: sgl.is_mouse_pressed
.. autofunction:: sgl.get_mouse_buttons_pressed
.. autofunction:: sgl.on_joy_down
.. autofunction:: sgl.on_joy_up
.. autofunction:: sgl.is_joy_pressed
.. autofunction:: sgl.get_joy_axis
.. autofunction:: sgl.get_joy_num_axes

Fake input commands
^^^^
These commands have to do the fake input system, in which on platforms without certain types of input, such as smart phones, you can simulate unavailable input devices with the ones that are available.

.. warning:: I don't think this API actually makes any sense. I might remove or change it later.

.. autofunction:: sgl.add_fake_input
.. autofunction:: sgl.got_key_down
.. autofunction:: sgl.got_key_up
.. autofunction:: sgl.got_mouse_move
.. autofunction:: sgl.got_mouse_down
.. autofunction:: sgl.got_mouse_up


