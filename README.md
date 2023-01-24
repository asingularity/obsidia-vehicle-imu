# obsidia-vehicle-imu
vehicle imu recording and real-time processing

## recording datasets

Turn on device in wifi proximity. Device should blink blue at 1 Hz.

Go to car. 

Press start/stop button to start a dataset. Device should blink blue at 4 Hz.

Record data. 

Press 1, 2, 3, 4 for starting a ground truth event. Device LED will blink red at 4 Hz. 

Press ESC to end ground truth event. Device will go back to blinking blue at 4 Hz.

Press start/stop button to stop dataset. Device should go back to blinking blue at 1 Hz.

Ground truth events will be in one file over the whole recording session; datasets for accel and gyro will be divided by dataset id.
Postprocessing will combine these correctly.

Example:

## running real-time demo

