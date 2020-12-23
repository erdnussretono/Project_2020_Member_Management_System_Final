import spidev
import RPi.GPIO as GPIO
from time import sleep

SCE = 22
sensor = 0xA1
object1 = 0xA0
isensor = 0
iobject = 0
spi = spidev.SpiDev()


def temp_init():
    global spi, SCE
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SCE, GPIO.OUT)
    spi.open(0, 0)
    spi.max_speed_hz = 1000000
    spi.mode = 3
    spi.bits_per_word = 8
    GPIO.output(SCE, True)


def spi_command(addr):
    global SCE
    databuf = []
    databuf.append(addr)
    databuf.append(0x22)
    databuf.append(0x22)

    GPIO.output(SCE, False)
    sleep(0.001)
    spi.xfer([databuf[0]])
    sleep(0.001)
    data1 = spi.xfer([databuf[1]])
    sleep(0.001)
    data2 = spi.xfer([databuf[2]])
    sleep(0.001)

    GPIO.output(SCE, True)
    return data2[-1] * 256 + data1[-1]


def sense_object():
    return spi_command(object1)


def sense_env():
    return spi_command(sensor)


def clean_up():
    GPIO.cleanup()
    spi.close()


if __name__ == "__main__":
    try:
        temp_init()
        sleep(0.05)
        while True:
            isensor = spi_command(sensor)
            sleep(0.001)
            iobject = spi_command(object1)
            sleep(0.001)
            print(f"sensor : {isensor}, object {iobject}")
            sleep(0.5)
    except KeyboardInterrupt:
        GPIO.cleanup()
        spi.close()

