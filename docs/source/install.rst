.. highlight:: none

Installing
====

One of these days, you should be able to install SGL by going::

                pip install sgl

We're not quite there yet, though.

Other methods of installing
----

For the record, no, I am not expecting random members of the public actually go through this amount of effort to test a crappy, half completed game development framework. This is mostly here because I'm currently forcing some friends to set the framework for me in an early stage of development, and want them to have some good instructions to follow to do so.

Install in pip's developer mode
^^^^

#. First, download the repository in its current state. You can either do this with the git client, or the lazy way--by downloading `the zip file Github provides. <https://github.com/m48/sgl/archive/master.zip>`_
#. Open a command line window, and navigate to the root folder of the repository.
#. Run the following command::

                     pip install -e .
    
#. Go into the examples folder, and run ``sgl-core-demo/demo.py`` to make sure SGL is working correctly.

This will make pip add a temporary link to the folder where SGL is located to your ``Python/Lib/site-packages`` directory. If you look in there after doing this, you should find a ``sgl.egg-link`` file that contains the path to the SGL folder.

So, make sure to be careful moving around your SGL folder after this--if you move it without updating this file, SGL will stop in your programs working.

When I update SGL, clear out the contents of this folder, and replace it with the contents of `the latest Github zip file of my repository. <https://github.com/m48/sgl/archive/master.zip>`_

When I finally get sgl on the real Python package directory, you will want to uninstall this local copy. To do this, just run the following command in any folder::
    
                pip uninstall sgl

Then reinstall it with the real pip command at the top of the page.

Don't install it at all
^^^^

If you're really lazy, download `the Github zip file of my repository. <https://github.com/m48/sgl/archive/master.zip>`_, and then copy and paste the ``sgl`` folder into any folder in which you want to have access to sgl. 

So, for example, to make the example work, you would copy the ``sgl`` folder into the ``examples/sgl-core-demo/`` folder, so you would end up with a ``examples/sgl-core-demo/sgl/`` folder. If you have all the dependencies installed correctly, the example should work like that.

This is, however, a bit inconvenient--you will have to replace this SGL folder whenever it is upgraded. This may be what you're after, though--this early in development, SGL may change enough that your programs may depend on specific versions, and it may be convenient to be able to use multiple versions simultaneously without dealing with virtualenvs for a package that isn't even published anywhere.

Dependencies
----

This should be automatically managed, but things may get screwy, so I will say it explicitly. 

SGL depends on PyGame 1.9.0+ to work correctly. It may work on earlier versions, but I have not tested this, and some advanced features may behave unexpectedly.

Some functions of SGL depend on NumPy being installed. I think nearly any version will work fine.

To render videos from SGL, you will need to install MoviePy. In my experience, on Windows, this is a fairly smooth, but annoying and long process. You have been warned. Installing MoviePy is not necessary for normal SGL development, though.

To the best of my knowledge, SGL only will work on Python 2.7. I am pretty sure I have done some stuff that will make it broken on Python 3, like using the old-style of print statements. You're welcome to give it a shot on Python 3, though.

Install these dependencies however you wish. Some of them offer Windows installers--if they do, prefer these. At the moment, this usually works a bit more smoothly than using pip. I know some libraries, such as MoviePy, do not support this, though, and others are slowly moving away from it, so you might  have no choice but to use pip in some cases.
