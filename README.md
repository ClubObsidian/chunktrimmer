# chunktrimmer

[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://opensource.org/licenses/gpl-3.0.html)

A tool to trim chunks that don't have players that have inhabited them. By default the number of ticks is set to `72000`.

This is written by using the nbt code from the [minecraft region fixer](https://github.com/Fenixin/Minecraft-Region-Fixer).
This code was tweaked to work with chunkmerger, imports were changed to load in from the current directory
and `get_chunk` returns `None` if a chunk does not exist. Region files are also now closeable.

## Usage

Put files that you want to trim into the other world in the `sourceworldname/region` folder.

Put files that you output will be put into in the `destinationworldname/region` folder.

Run by using `trimmer.py -s sourcefolder -d destinationfolder`, you will need Python 3.

**Other Arguments**

| Arguments | Description             |
|-----------|-------------------------|
| -th #     | Set number of threads   |
| -ti #     | Set number of ticks     |
| -v        | Enable verbose logging  |



## Warning

**Run at your own risk and make sure to have backups.**
