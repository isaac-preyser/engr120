import time
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

def poll():
    #poll thermistor1
    adc_value = thermistor1.read_u16()
    voltage = round((adc_value / 65535) * 3.3, 2)
    print('ADC Value (thermo1): ', adc_value)
    print('ADC Voltage (thermo1): ', voltage , 'V')
   #using R2 = V_adc * r1 / (Vcc - V_adc)
    resistance = (voltage * thermistor1_resistor) / (3.3 - voltage)
    print('Resistance: ', resistance, 'ohms')

    #using NTC DKA103*2 thermistor, resistance should be 10k ohms at 25C
    #using the Steinhart-Hart equation, we can calculate the temperature
    # 1/T = A+B*ln(R)+C*ln(R)^3
    #T = 1 / (A + B*ln(R) + C*ln(R)^3)
    T = 1 / (A + B * math.log(resistance) + C * math.pow(math.log(resistance), 3)) - TEMP_OFFSET
    T = T - 273.15
    print('Temperature: ', round(T, 2), 'C')

    print('\n')
    #poll thermistor2, doing the same thing as above. 
    adc_value = thermistor2.read_u16()
    voltage = round((adc_value / 65535) * 3.3, 2)
    print('ADC Value (thermo2): ', adc_value)
    print('ADC Voltage (thermo2): ', voltage , 'V')
    #using R2 = V_adc * r1 / (Vcc - V_adc)
    resistance = (voltage * thermistor2_resistor) / (3.3 - voltage)
    print('Resistance: ', resistance, 'ohms')

    #using NTC DKA103*2 thermistor, resistance should be 10k ohms at 25C
    #using the Steinhart-Hart equation, we can calculate the temperature
    # 1/T = A+B*ln(R)+C*ln(R)^3
    #T = 1 / (A + B*ln(R) + C*ln(R)^3)
    T = 1 / (A + B * math.log(resistance) + C * math.pow(math.log(resistance), 3)) - TEMP_OFFSET_2
    T = T - 273.15
    print('Temperature: ', round(T, 2), 'C')

    print('\n')

    #poll photoresistor
    adc_value = photoresistor.read_u16()
    voltage = round((adc_value / 65535) * 3.3, 2)
    print('ADC Value (photo): ', adc_value)
    print('ADC Voltage (photo): ', voltage , 'V')
    if voltage > LUMINANCE_THRESHOLD:
        print('It is dark')
    else:
        print('It is bright')
    print('\n')


    


#main loop
while True:   
    #clear the terminal 
    print('\033c')
    poll()
    time.sleep(0.1)
    