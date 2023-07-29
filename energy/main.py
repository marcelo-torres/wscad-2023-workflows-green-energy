import json


from energy_usage import EnergyUsage

def microsecond_to_second(microsecond):
    return microsecond / 1000000

def calc_energy_usage(events_file):
    e = EnergyUsage()

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
            
    print(f'[i] {count} events loaded')
    f.close()

    print('[i] Calculating energy usage...')
    total_energy_in_joules, energy_trace = e.calc()
    e.clear()
    
    return total_energy_in_joules, energy_trace

def calc_green_energy_usage(energy_trace, pv_energy_file):
    pass
    

if __name__ == '__main__':

    events_file = 'user_formatted.json'
    pv_energy_file = ''

    total_energy_in_joules, energy_trace = calc_energy_usage(events_file)
    
    watts_hour = total_energy_in_joules / 3600
    print('Total Energy:')
    print("\t{:.2f}J".format(total_energy_in_joules))
    print("\t{:.2f}Wh".format(watts_hour))
 
 
    # Closing file
    
