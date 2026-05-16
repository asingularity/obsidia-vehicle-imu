# Obsidia Vehicle IMU

A system for detecting driving events (hard acceleration, braking, swerving) from a vehicle-mounted IMU sensor. A Raspberry Pi reads accelerometer and gyroscope data at 833 Hz from an ISM330DHCX sensor, and either records it for offline analysis or runs real-time detection with alerts displayed on a phone via a web dashboard.

Two detection methods are implemented: matched filtering (designed in MATLAB, executed in Cython) and a simpler threshold-with-hysteresis approach in Python. Ground truth events are annotated during recording via keyboard input.

Developed January to March 2023.

## Hardware

- **IMU sensor**: ISM330DHCX (6-axis: 3-axis accelerometer + 3-axis gyroscope), connected via I2C
- **Processor**: Raspberry Pi with GPIO-connected RGB LED for status feedback
- **Input**: USB keyboard for ground truth annotation and start/stop control
- **Vehicle mounting**: sensor and Pi mounted in the vehicle, powered during drives

The Raspberry Pi can operate in access point mode (192.168.4.1) so a phone can connect directly to view the web dashboard without external WiFi.

## Detection Methods

### Matched Filtering

Four matched filter kernels (designed in MATLAB, stored as `.mat` files) detect specific maneuver signatures:

| Filter | Event | Axis | Kernel length | Threshold |
|--------|-------|------|---------------|-----------|
| mfiltd1 | Acceleration | X | 884 samples | 5.99 |
| mfiltd2 | Braking | X | 882 samples | 2.48 |
| mfiltd3 | Swerve left | Y | 820 samples | 2.33 |
| mfiltd4 | Swerve right | Y | 820 samples | 3.00 |

The filters are cross-correlated with the accelerometer buffer in a Cython-optimized loop. A detection fires when the filter output crosses its threshold from below.

### Threshold Method

A simpler approach: an event is detected when acceleration on the relevant axis exceeds a threshold (default: 3.0 m/s² for acceleration/braking, 2.5 m/s² for cornering) for at least 100 ms. A 17% hysteresis margin prevents chatter at the threshold boundary.

## Data Pipeline

### Recording

`record_dataset.py` reads the IMU at 833 Hz and writes timestamped CSV files (one per sensor per dataset). An operator in the vehicle presses keys 1-4 to mark ground truth events (acceleration, braking, turn left, turn right) and ESC to end an event. The LED blinks blue at 1 Hz when idle and 4 Hz when recording.

### Calibration (MATLAB)

The MATLAB script (`matlab/IMU_Data_Real_Time_Test677_v32_e1234.m`) handles data preprocessing:
1. Uses the first 6 seconds of stationary data to estimate the gravity vector
2. Computes rotation matrices (Euler angles) to align the sensor axes with the vehicle axes and remove gravitational bias
3. Resamples data uniformly at 410.36 Hz using piecewise cubic interpolation

### Post-processing

`postprocess.py` converts raw CSV recordings to `.mat` files and generates plots of accelerometer/gyroscope data overlaid with ground truth event markers.

`postprocess_threshold_method.py` runs the threshold-based detector on recorded data and compares its detections against ground truth, generating comparison plots.

### Real-time Detection

`run_realtime.py` streams IMU data into 1000-sample buffers (with overlap equal to the longest filter length), applies the four matched filters via Cython, and sends detection alerts to the web dashboard every 200 ms. The LED flashes red during real-time operation.

### Web Dashboard

`run_webserver.py` serves a Bottle.py web page at `192.168.4.1:8000` showing:
- Six bar graphs for live accelerometer and gyroscope values (3 axes each)
- An alert banner: green "Normal Driving" or red with the event type ("Unusual Acceleration!", "Unusual Braking!", "Swerve Left!", "Swerve Right!")

The page polls the server every 200 ms for updates.

## Project Structure

```
record_dataset.py                       # IMU recording with ground truth annotation
run_realtime.py                         # Real-time matched filter detection
run_webserver.py                        # Phone dashboard (Bottle.py)
postprocess.py                          # Convert recordings to .mat, generate plots
postprocess_threshold_method.py         # Threshold-based detection on recorded data
parameters.py                           # Dataset and results folder paths
fps_counter.py                          # Frame rate monitoring
matlab_utils.py                         # scipy.io .mat file wrappers
try_keyboard.py                         # Keyboard input test script

ref_cython/
  cython_ref.pyx                        # Cython matched filter implementation
  setup.py                              # Cython build config (with OpenMP)

matlab/
  IMU_Data_Real_Time_Test677_v32_e1234.m  # MATLAB calibration and detection pipeline
  mfiltd1.mat                           # Matched filter kernel: acceleration
  mfiltd2.mat                           # Matched filter kernel: braking
  mfiltd3.mat                           # Matched filter kernel: swerve left
  mfiltd4.mat                           # Matched filter kernel: swerve right
```

## Dependencies

Listed in `requirements.txt`:

- `adafruit-circuitpython-lsm6ds` — ISM330DHCX sensor driver
- `keyboard` — ground truth annotation (requires root)
- `numpy` — numerical operations
- `matplotlib` — visualization
- `scipy` — `.mat` file I/O
- `psutil` — memory monitoring
- `requests` — HTTP PUT to web dashboard
- `bottle` — web server
- `cython` — matched filter compilation

## Running

### Recording datasets

```bash
sudo python3 record_dataset.py
```

The device starts in standby (blue LED, 1 Hz blink). Press spacebar to start recording (4 Hz blink). Press 1/2/3/4 to mark ground truth events, ESC to end an event. Press spacebar again to stop.

### Real-time detection

On a desktop, generate any needed system matrices, then deploy to the Pi. On the Pi:

```bash
# In separate terminals:
python3 run_webserver.py
sudo python3 run_realtime.py
```

Access the dashboard at `http://192.168.4.1:8000` on a phone connected to the Pi's WiFi.

### Building the Cython module

```bash
cd ref_cython
python setup.py build_ext --inplace
```

### Post-processing

```bash
python3 postprocess.py                      # Convert recordings to .mat and plot
python3 postprocess_threshold_method.py     # Run threshold detection on recorded data
```

## Notes

- The matched filter kernels (`mfiltd*.mat`) were designed in MATLAB from training data; the MATLAB script in `matlab/` shows the full calibration and detection pipeline but the filter design/training code is not included.
- Paths in `parameters.py` are hardcoded and will need to be updated for a different setup.
- The `record_dataset.py` and `run_realtime.py` scripts require root privileges for the `keyboard` library.
- The system can be configured to start automatically on boot via `/etc/rc.local` on the Pi.
