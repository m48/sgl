SGL Core Reference
==================
 
Base functions
----
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
 
Audio functions
----
These functions have to do with playing music and sound effects.
 
.. autofunction:: sgl.load_sound 
.. autofunction:: sgl.play_sound
.. autofunction:: sgl.stop_sound
.. autofunction:: sgl.stop_all_sounds
.. autofunction:: sgl.is_sound_plying
.. autofunction:: sgl.play_music
.. autofunction:: sgl.pause_music
.. autofunction:: sgl.resume_music 
.. autofunction:: sgl.set_music_volume
.. autofunction:: sgl.stop_music
.. autofunction:: sgl.is_music_playing

Image commands
----
These commands have to do with loading images and stuff.
 
.. autofunction:: sgl.set_transparent_color
.. autofunction:: sgl.load_image
.. autofunction:: sgl.load_alpha_image
.. autofunction:: sgl.blit
.. autofunction:: sgl.blitf
  
Drawing commands
----
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
.. autofunction:: sgl.clear
.. autofunction:: sgl.draw_line
.. autofunction:: sgl.draw_rect
.. autofunction:: sgl.draw_ellipse
.. autofunction:: sgl.draw_circle

Text commands
----
These commands have to do with rendering text.

.. autofunction:: sgl.set_font_smooth
.. autofunction:: sgl.get_font_smooth
.. autofunction:: sgl.load_font
.. autofunction:: sgl.load_system_font
.. autofunction:: sgl.set_font
.. autofunction:: sgl.draw_text
.. autofunction:: sgl.get_text_width
.. autofunction:: sgl.get_text_height

Surface commands
----
These commands have to do with using surfaces and changing the current drawing buffer.

.. autofunction:: sgl.push
.. autofunction:: sgl.pop
.. autofunction:: sgl.with_state
.. autofunction:: sgl.set_buffer
.. autofunction:: sgl.with_state
.. autofunction:: sgl.make_surface
.. autofunction:: sgl.get_chunk
.. autofunction:: sgl.reset_buffer
.. autofunction:: sgl.get_width
.. autofunction:: sgl.get_height
.. autofunction:: sgl.save_image
.. autofunction:: sgl.to_numpy
.. autofunction:: sgl.from_numpy

Special Effect commands
----
These commands do cool special effects.

.. autofunction:: sgl.invert
.. autofunction:: sgl.grayscale

Fake input commands
----
These commands have to do the fake input system, in which on platforms without certain types of input, such as smart phones, you can simulate unavailable input devices with the ones that are available.

.. autofunction:: sgl.add_fake_input
.. autofunction:: sgl.got_key_down
.. autofunction:: sgl.got_key_up
.. autofunction:: sgl.got_mouse_move
.. autofunction:: sgl.got_mouse_down
.. autofunction:: sgl.got_mouse_up

Input commands
----
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

