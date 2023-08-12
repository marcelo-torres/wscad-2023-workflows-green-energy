from datetime import datetime

def to_date_time(date_time_str):
    date_format = '%Y-%m-%d %H:%M:%S'
    return datetime.strptime(date_time_str, date_format)

def create_env_variable(processor_id, time, pv_available_power):
    # OMPCLUSTER_MOHEFT_GREEN_P_x_I_y_S
    return f'OMPCLUSTER_MOHEFT_GREEN_P_{processor_id}_I_{time}_S={pv_available_power}'


def create_env_variables_for_processor(processor):
    processor_id = processor['processor_id']
    pv_energy_file = open(processor['pv_energy_file'])
    pv_area = processor['pv_area']

    env_variables = []

    next(pv_energy_file, None) # Skip Header
    line = next(pv_energy_file, None)
    while line is not None:
        
        row = line.strip().split(',')
        dt, time, solar_irradiance = row[0], int(row[1]), float(row[2])
        pv_available_power = pv_area * solar_irradiance

        env_variables.append(
            create_env_variable(processor_id, time, pv_available_power)
        )

        line = next(pv_energy_file, None)
    return env_variables


if __name__ == '__main__':

    output_file = './../data/ompc/moheft_energy_variables.txt'

    processors = [
        {
            'processor_id': 0,
            'pv_energy_file': './../data/ompc/compressed/photovolta_compressed_interval_1.csv',
            'pv_area': 1
        },
        {
            'processor_id': 1,
            'pv_energy_file': './../data/ompc/compressed/photovolta_compressed_interval_2.csv',
            'pv_area': 1
        },
        {
            'processor_id': 2,
            'pv_energy_file': './../data/ompc/compressed/photovolta_compressed_interval_3.csv',
            'pv_area': 1
        },
        {
            'processor_id': 3,
            'pv_energy_file': './../data/ompc/compressed/photovolta_compressed_interval_4.csv',
            'pv_area': 1
        },
        {
            'processor_id': 4,
            'pv_energy_file': './../data/ompc/compressed/photovolta_compressed_interval_5.csv',
            'pv_area': 1
        }
    ]

    env_variables = []

    for processor in processors:
        env_variables.extend(
            create_env_variables_for_processor(processor)
        )
        
    f = open(output_file, 'w')
    for env_variable in env_variables:
        f.write(f'{env_variable}\n')
    f.close()