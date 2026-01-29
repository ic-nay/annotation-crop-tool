# annotation-crop-tool
Just a small script that crops images based on annotations (just YOLO for now, I'll add more later if I'm bored). Pass it a directory and let it crunch away.

## Required libraries
Given that this is meant to crop images based on annotations for machine learning, I'm making use of OpenCV. In the future it'd be nice to make this modifiable.

You'll also want a YAML parsing library of some sort which can be imported as `import yaml`.