
from thermometer import CPUTemp

def main():
    temperature = CPUTemp()
    temperature.start_climate_station(2, True, 180)

if __name__ == '__main__':
    main()