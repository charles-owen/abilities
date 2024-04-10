# Example configurations and data files

This page describes some example files and configurations 
to use for running these scripts.

## camera-calibration

This is an example camera-calibration command line:

camera-calibration --camera=p1 --show --offset=-13.5,-8.5,0 --write="../local/calibration-basler.yaml"

## projector-calibration.py

The file `projector-calibration-config.json` is an example configuration file that can be 
used by projector-calibration.py to configure a calibration session.

The program is run with a single command line argument that is the 
configuration file name. Example:

`project-calibration ../local/projector-calibration-config.json`

This is the contents of projector-calibration-config.json:

```{
  "screen": 4,
  "camera": "p1",
  "camera-calibration": "calibration-basler.yaml",
  "write": "projector-calibration-home.yaml",
  "invert": true,
  "surfaces": [
    [[0, 0, 0], [520, 0, 0], [520, 0, -520], [0, 0, -520]],
    [[0, 0, 0], [0, 470, 0], [500, 470, 0], [500, 0, 0]]
  ]
}
```

### screen

The screen configuration specifies which screen output on a 
multiple-monitor system is the projector screen. This is a value
starting at 1 and may vary in value depending on what order 
screens were attached.

### camera

The camera configuration specified the camera input to use. 
A prefix of 'p' indicates a Pylon camera such as the Basler ACE.

### camera-calibration

This specifies the camera calibration file to load.

### write 

This specifies the projector calibration file name to write.

### invert

The invert configuration item is optional. If set to true, it
will invert the displayed image. This is useful for cameras that
are mounted upside down.

### surfaces

The surfaces configuration is an array of surfaces specified as 
polygons. Only markers projected into the surfaces will be considered
for the calibration. 

