# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| `fonts/OpenSans-Semibold.ttf` | Open Sans 1.10 (Google, digitized data © 2011 Google; copied from Windows' bundled copy, same as fonts.google.com) | Apache 2.0 (name table: "Licensed under the Apache License, Version 2.0") | yes (rendered glyphs only ship) | dialogue/UI ASCII glyphs in HG_G18.TFP (tools/font.py, 14 px) | none; rendered at 14 px, ink 0-12 |
