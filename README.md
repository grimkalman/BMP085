## BMP085
Driver for the BMP085 pressure sensor

## Information
This code is a simple driver intended to be used in a flight computer. The code was implemented using references:
* BMP085 Data Sheet Rev.1.2

## Example usage:
```
>>import time
>>import BMP085

>>sensor = bmp085(0x77)
>>while True:
>>      print(sensor.get_altitude())
>>      time.sleep(0.01)
96.39241785321701
96.70571460232259
96.34116135346417
96.36395809273974
96.63544990521315
95.98612366673795
96.21964641374117
96.14939142081859
96.09813287889422
95.9766207488987
96.02788031187684...
```
