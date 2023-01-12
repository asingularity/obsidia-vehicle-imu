
import time
from datetime import datetime
import board
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX
from fps_counter import FPSCounter


def record_dataset():

    i2c = board.I2C()  # uses board.SCL and board.SDA
    # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
    sensor = LSM6DSOX(i2c)
    fps = FPSCounter(params={'display_every_k_seconds': 1})

    f = open('tmp_accel_gyro.txt')

    print()
    print('starting recording...')
    print()

    t0 = time.time()
    while time.time() < t0 + 10:
        #print("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2" % (sensor.acceleration))
        #print("Gyro X:%.2f, Y: %.2f, Z: %.2f radians/s" % (sensor.gyro))
        #print("")

        timestamp = datetime.now().isoformat()
        accel = sensor.acceleration
        gyro = sensor.gyro
        f.write(timestamp + ', ' + str(accel) + ', ' + str(gyro))

        fps.update()

    print('finished recording.')
    print()

    fps.update(force_display=True)
    f.close()



if __name__ == '__main__':
    # use without a venv for now for adafruit stuff on raspberry pi
    record_dataset()
