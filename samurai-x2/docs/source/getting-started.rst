Getting started with samurai-x2
===============================

Get it
------

Dependencies
~~~~~~~~~~~~

samurai-x2 needs:

 * Python >= 2.5
 * `ooxcb`_
 * `setuptools`_

ooxcb needs:

 * `libxcb`_

yahiko (a package containing a nice decoration plugin. Not required,
you can use :ref:`sx-cairodeco` instead) needs:

 * `cairo`_ (with the xcb backend)
 * `librsvg`_

.. _ooxcb: http://docs.samurai-x.org/ooxcb/
.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools
.. _libxcb: http://xcb.freedesktop.org
.. _cairo: http://www.cairographics.org
.. _librsvg: http://librsvg.sourceforge.net

Stable version
~~~~~~~~~~~~~~

The easiest way to get a samurai-x2 stable release is::

    easy_install ooxcb yahiko samurai-x2

Now, there is a `sx-wm` executable available. Without any plugins,
samurai-x2 isn't usable, so let's install some (here we install them
system-wide. That is possible, but you can also install the plugin
packages as eggs to `~/.samuraix/plugins` or any other directory
in your `search path`_)::

    easy_install sx-actions sx-desktops

In the default configuration, samurai-x2 uses the yahiko decorator plugin,
and since you already installed yahiko above, the decorator plugin is available.

If you type ``sx-wm`` now, a more or less usable window manager is launched.

If you want to run it on another X server, launch it with the
`DISPLAY` variable set::

    DISPLAY=:1 sx-wm

If you want to turn on synchronous checks (each X request is
checked immediately, so you get more detailed tracebacks), run::

    sx-wm -s

samurai-x2 will write its logfile to `/tmp/sx.lastrun.log`.

After having installed samurai-x2, the first step will normally be to
create a sample configuration file::

    sx-wm --default-config > ~/.samuraix/config.py

Development version
~~~~~~~~~~~~~~~~~~~

Since there is no current release of samurai-x2, you'll have
to clone the git repository to try it::

    git clone git://samurai-x.org/samuraix.git

Now, there is a `samuraix` directory with multiple subdirectories:

samurai-x
    the old samurai-x1, based on Xlib. Discontinued.
samurai-x2
    the new samurai-x2, based on our own X binding.
ooxcb
    our own X binding
sx-*
    some plugins

Because samurai-x2 is developed continously, it's not a good
idea to reinstall it after each revision. Because of that, we
created a simple script that creates a development environment::

    ./create-environment.py dev

will create a folder called `dev`, containing the samurai-x executable
`sx-wm` (and some other stuff). It will also install all available
plugins into `./samuraix/plugins`.
The advantage of this way of installing samurai-x2 is that if a new
revision is pushed to the git repository, you just have to type
`git pull`, and there is no need to reinstall anything. Even the
plugins are installed as so-called `egg links`_, so you can
change the code and do not have to rebuild eggs after each change.

In order to launch samurai-x2 then, you have to cd into this directory
and run `./setenv` before you do anything else. This will launch
a subshell with a custom PYTHONPATH set. In this subshell, you can
use the `sx-wm` executable.

To run samurai-x2, just type::

    ./sx-wm

If you want to run it on another X server, launch it with the
`DISPLAY` variable set::

    DISPLAY=:1 ./sx-wm

If you want to turn on synchronous checks (each X request is
checked immediately, so you get more detailed tracebacks), run::

    ./sx-wm -s

samurai-x2 will write its logfile to `/tmp/sx.lastrun.log`.

After having installed samurai-x2, the first step will normally be to
create a sample configuration file::

    ./sx-wm --default-config > ~/.samuraix/config.py

Configure it
------------

You can now edit the configuration file `~/.samuraix/config.py`. If there
is no such file, samurai-x2 uses the default configuration.

The config file is an executable Python script, so be careful about its content.

It has to contain a dictionary called `config` or a callable `config` that returns
a dictionary. There are some special dictionary keys:

.. _search path:

.. attribute:: core.plugin_paths

    A list of plugin search paths. Example::

       'core.plugin_paths': ['~/.samuraix/plugins']

.. attribute:: core.plugins

    A list of setuptools entry point names. The plugins these entry points to
    will be loaded. Example::

        'core.plugins': [
            'sxactions',
            'sxdesktops',
            'sxbind',
            'sxsimpledeco',
            'sxmoveresize',
            'sxclientbuttons',
            'sxfocus',
            'sxlayoutmgr',
        ]

If you have any further questions, you're welcome to join our
`irc channel`_ and our `mailing list`_!

.. _egg links: http://peak.telecommunity.com/DevCenter/EggFormats#egg-links
.. _irc channel: irc://irc.freenode.net/samuraix
.. _mailing list: http://samurai-x.org/mailman/listinfo/samuraix_users
