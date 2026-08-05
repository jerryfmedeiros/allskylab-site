# allskylab.ca

Static one-page site for All-Sky Lab, served from GitHub Pages at
[allskylab.ca](https://allskylab.ca).

```
index.html            the page
style.css             all styles
images/triptych.*     hero composite (webp served first, png fallback)
tools/                build scripts and parked markup, not part of the page
```

No build step and no dependencies — `index.html` and `style.css` are edited
directly. `.nojekyll` keeps GitHub Pages from running the files through Jekyll.

## Regenerating the hero image

```sh
python3 tools/build_triptych.py /path/to/frames
```

Writes `images/triptych.png` and `images/triptych.webp`. Requires Pillow and
NumPy. Source frame names and per-panel cropping are set at the top of the
script.
