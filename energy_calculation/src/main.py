import json
import logging, sys

from datetime import datetime

from energy_usage import EnergyUsage
from energy_usage import calc_green_energy_usage


logging.basicConfig(stream=sys.stderr, level=logging.INFO, format='[%(asctime)s][%(levelname)s] %(message)s')
logger = logging.getLogger('main')


def to_date_time(date_time_str):
    date_format = '%Y-%m-%d %H:%M:%S'
    return datetime.strptime(date_time_str, date_format)

def microsecond_to_second(microsecond):
    return microsecond / 1000000
    
def joules_to_watts_hour(joules):
    return joules/ 3600 # Wh = J/h = J/60*60 = J/3600s

def print_energy(description, energy_in_joules):
    energy_in_wh = joules_to_watts_hour(energy_in_joules)
    logger.info('{}: {:.2f}Wh ({:.2f}J)'.format(description, energy_in_wh, energy_in_joules))
    
    

def calc_energy_usage(events_file):
    e = EnergyUsage()

    logger.info('Loading events...')
    f = open(events_file)
    data = json.load(f)
    
    count = 0
    for event in data['traceEvents']:
        if event['ph'] == 'X':
            
            timestamp = microsecond_to_second(float(event['ts']))
            duration = microsecond_to_second(float(event['dur']))

            count += 1
            
            start = timestamp
            end = timestamp + duration
            
            e.add_work('X', start, end, 35/4)
            
    logger.info(f'{count} events loaded')
    f.close()

    logger.info('Calculating energy usage intervals...')
    total_energy_in_joules, energy_trace = e.calc()
    e.clear()
    
    return total_energy_in_joules, energy_trace
   
   
def calc_pv_energy_usage_2(energy_trace, pv_energy_file_name, pv_area, offset = 0):
    
    def read_pv_energy_line(pv_energy_file):
        line = next(pv_energy_file, None)
        if line is None:
            raise Exception('End of pv energy file')
            
        row = line.strip().split(',')
        return to_date_time(row[0]), int(row[1]), float(row[2])
        
    def next_pv_energy_interval():
        d, pv_interval_time, solar_irradiance = read_pv_energy_line(pv_energy_file)
        pv_available_power = pv_area * solar_irradiance
        return pv_interval_time, pv_available_power
        
        
    pv_energy_file = open(pv_energy_file_name)

    # ignore header
    next(pv_energy_file)

    if offset > 0:
        pv_interval_time = 0
        while pv_interval_time < offset:
            d, pv_interval_time, solar_irradiance = read_pv_energy_line(pv_energy_file)

    r = calc_green_energy_usage(energy_trace, next_pv_energy_interval)
    
    print_energy('Total Energy', r['total_energy'])
    print_energy('Total Brown Energy Used', r['total_brown_energy_used'])
    print_energy('Total Green Energy Used', r['total_green_energy_used'])
    print_energy('Total Green Energy Not Used', r['total_green_energy_not_used'])

    pv_energy_file.close()
    

if __name__ == '__main__':

    #events_file = '../data/OMPC_matmul_trace_data.json'
    events_file = '../data/OMPC_matmul_trace_data_510x.json'

    pv_energy_file = './../../photovolta/data/photovolta_2016_part_1.csv'
    pv_area = 1
    offset = 29400 #start time

    total_energy_in_joules, energy_trace = calc_energy_usage(events_file)
    
    watts_hour = total_energy_in_joules / 3600
    logger.info('Total Energy: {:.2f}Wh {:.2f}J'.format(watts_hour, total_energy_in_joules))
 
    logger.info('Calculating green energy usage...')
    calc_pv_energy_usage_2(energy_trace, pv_energy_file, pv_area, offset)
