# Setzer

![Screenshot](https://github.com/cvfosammmm/Setzer/raw/master/resources/images/screenshot.png)

Setzer is a LaTeX editor written in Python with Gtk. It still lacks features and likely has some bugs but I find it quite useful already. I'm happy if you give it a try and provide feedback via the issue tracker here on GitHub, be it about design, code architecture, bugs, feature requests, ... I try to respond to issues immediately.

## Running Setzer on Debian (Ubuntu, other Distributions too?)

I develop Setzer on Debian and that's what I exclusively tested it with. On Debian derivatives (like Ubuntu) it should probably work the same. On distributions other than Debian and Debian derivatives it should work more or less the same. If you want to run Setzer on another distribution and don't know how please open an issue here on GitHub. I will then try to provide instructions for your system.

1. Run the following command to install prerequisite Debian packages:<br />
`apt-get install libgtk-3-dev libgtksourceview-3.0-dev libpoppler-glib-dev`

2. Download und Unpack Setzer from GitHub

3. cd to Setzer folder

4. Run the following command to start Setzer:<br />
`python3 __main__.py`

## Building your documents from within the app

To build your documents from within the app you have to specify a build command. I recommend building with latexmk, which on Debian can be installed like so:
`apt-get install latexmk`

To specify a build command open the "Preferences" dialog and type in the command you want to use under "Build command", which in the case of latexmk could be the following:
`latexmk -synctex=1 -interaction=nonstopmode -pdf -output-directory=%OUTDIR %FILENAME`

## Getting in touch

Setzer development / discussion takes place on GitHub at [https://github.com/cvfosammmm/Setzer](https://github.com/cvfosammmm/Setzer "project url").

## Acknowledgements

Setzer draws some inspiration from other LaTeX editors. For example the symbols in the sidebar are mostly the same as in Latexila, though I continue to change / reorganize them. The autocomplete suggestions are mostly the same as in Texmaker. I took some icons from Gnome Builder. Syntax highlighting schemes are based on the Tango scheme in GtkSourceView and the Gnome Builder Scheme.

## License

Setzer is licensed under GPL version 3 or later. See the COPYING file for details.