import machine
import math

# Define pins here
thermistor1 = machine.ADC(28)
thermistor2 = machine.ADC(27)
photoresistor = machine.ADC(26)

#define known resistors
thermistor1_resistor = 4670 #4.7k ohms
thermistor2_resistor = 4540 #4.5k ohms

#define Steinhart-Hart coefficients for 10k thermistor
A = 0.001125308852122
B = 0.000234711863267
C = 0.000000085663516
TEMP_OFFSET = 4
TEMP_OFFSET_2 = 4

#luminance threshold
LUMINANCE_THRESHOLD = 3.1 #3.1V - 3.18 tends to be ambient levels, 2V tends to be max brightness, and 3.24V tends to be max darkness

#modes: R = resistance, V = voltage, T = temperature
def getValue(thermNum, mode): 
    #switch case for thermNum
    if thermNum == 1:
        adc = thermistor1
        r = thermistor1_resistor
        offset = TEMP_OFFSET
    if thermNum == 2:
        adc = thermistor2
        r = thermistor2_resistor
        offset = TEMP_OFFSET_2
    if thermNum == 3:
        adc = photoresistor
        if mode == 'V':
            return round((adc.read_u16() / 65535) * 3.3, 2)
    #poll the thermistor
    adc_value = adc.read_u16()
    voltage = round((adc_value / 65535) * 3.3, 2)
    if mode == 'V':
        return voltage
    resistance = (voltage * r) / (3.3 - voltage)
    if mode == 'R':
        return resistance
    #temperature via steinhart-hart equation
    T = 1 / (A + B * math.log(resistance) + C * math.pow(math.log(resistance), 3)) - offset
    T = T - 273.15
    return round(T, 2) #base case if mode is T, or anything else. 
    
def getPhotoVoltage():
    adc_value = photoresistor.read_u16()
    voltage = round((adc_value / 65535) * 3.3, 2)
    return voltage