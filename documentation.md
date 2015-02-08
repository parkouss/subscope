---
layout: page
title: Documentation
---

## Command line tips

- Force the download of a subtitle even if there is already one near your
  movie file:

       subscope --force

   By default, subscope never overwrite a subtitle file (you will have
   a warning if a file already exists).

- download subtitles for a given language (by default english is used):

       subscope --language fr

   Note that you can list multiple languages (comma separated). They will
   act as fallbacks:

       subscope -l fr,ru,en

   subscope will search for subtitles with a preference for french first,
   then russian, and finally english.

- use the interactive mode

   Sometimes the subtitle downloaded by subscope is not good (yes, this may
   happen because subscope relies on external subtitle databases that can
   be corrupted). You still have a chance to get a better one by using the
   interactive mode:

       subscope --interactive --force

   You will be asked to choose the subtitle you want. the -\-force flag
   is not needed, but I suppose you may need it here. :)

Note that there are *more options* available! Just issue a:

    subscope --help

To see the complete list.

Also note that most common options have a short equivalent name. For example:

| -\-force       | -f |
| -\-language    | -l |
| -\-interactive | -i |

## Using a configuration file

subscope can be configured per user. Just create and edit a configuration file
*'~/.subscope.cfg'* according to your needs. Here is an example:

{% highlight ini %}
[subscope]

# I want my subtitles in french or english
language = fr,en

# I like to see the debug output
log-level = debug

# my network is bad, I need a higher requests timeout (in seconds)
requests-timeout = 25.0
{% endhighlight %}

Note:

- On GNU/Linux, *'~/.subscope.cfg'* expand to /home/{USER}/.subscope.cfg.
  On Windows, **HOME** and **USERPROFILE** will be used if set, otherwise
  a combination of **HOMEPATH** and **HOMEDRIVE**.

- You have to use the long name of the option in the configuration file.

- Not all options are taken in account. For now, only *language*,
  *log-level* and *requests-timeout* ae working (others does not make
  sense really)
