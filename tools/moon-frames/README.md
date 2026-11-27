# Moon phase frames

The images in `nasa/` are renders from NASA's Scientific Visualization Studio
("Moon Phase and Libration, 2025"), taken from the copy of the hourly video on
Wikimedia Commons. They are in the public domain as NASA works.

- `frames.csv` lists the 30 hourly frames used, one per 12 degrees of the lunar
  cycle, with NASA's figures for the Moon's tilt, axis angle and apparent size.
- `fetch_frames.py` downloads the video and saves those frames. The
  "Fetch moon phase frames" workflow runs it and stores the result on the
  `nasa-raw` branch.
- Each frame was then turned north-up and resized so the disc matches
  `moon.jpg`, and saved as `nasa/00.jpg` to `nasa/29.jpg`.
