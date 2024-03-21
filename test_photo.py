import machine
import time
adc = machine.ADC(27) #create an ADC object on pin 27, physical pin 32

while True:
    adc_value = adc.read_u16() #read the ADC value
    print('ADC Value: ', adc_value)
    time.sleep(0.5) #sleep for 0.5 seconds
    