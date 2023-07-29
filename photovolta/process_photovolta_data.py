import csv

from datetime import datetime

def to_date_time(date_time_str):
    date_format = '%Y-%m-%d %H:%M:%S'
    return datetime.strptime(date_time_str, date_format)


def process_photovolta_data(source_file, new_file):

    INTERVAL_SIZE = 300 # 300s = 5min
    ERROR_TOLERANCE_IN_SECONDS = 2

    with open(source_file, 'r', encoding='UTF-8') as photovolta_file:
        with open(new_file, 'w', encoding='UTF8') as photovolta_new_file:
            writer = csv.writer(photovolta_new_file)
    
            previous_time_stamp = None
            offset = 0
            
            for line_number, line in enumerate(photovolta_file):
                if(line_number == 0): 
                    writer.writerow(['timestamp', 'interval_in_seconds', 'solar_irradiance_in_W_m2'])
                    continue # skip header
                
                row = line.strip().split(',')
                date_time = to_date_time(row[0])
                solar_irradiance = row[1]
                
                time_stamp = date_time.timestamp()
                if previous_time_stamp is None:
                    previous_time_stamp = time_stamp
                    time_stamp_diff = 0
                    diff = 0
                else:
                    time_stamp_diff = time_stamp - previous_time_stamp
                    diff = time_stamp_diff - INTERVAL_SIZE
                
                # Adjust intervals with a small error
                m = time_stamp_diff % INTERVAL_SIZE
                if m <= ERROR_TOLERANCE_IN_SECONDS:
                    time_stamp_diff -= m
                elif m >= (INTERVAL_SIZE - ERROR_TOLERANCE_IN_SECONDS):
                    time_stamp_diff += (INTERVAL_SIZE-m)
                
                
                if diff == 0:
                    # The time stamp diff is equal to INTERVAL_SIZE
                    offset+=INTERVAL_SIZE
                    
                elif diff >= -ERROR_TOLERANCE_IN_SECONDS and diff <= ERROR_TOLERANCE_IN_SECONDS:
                    # Some intervals have size equal between INTERVAL_SIZE-2 and INTERVAL_SIZE+2
                    offset+=INTERVAL_SIZE
                
                elif(time_stamp_diff > INTERVAL_SIZE and time_stamp_diff % INTERVAL_SIZE == 0):
                    # Include omitted intervalds due no solar irradiation
                
                    omitted_intervals = int(time_stamp_diff / INTERVAL_SIZE) - 1
                    
                    for i in range(omitted_intervals):
                        omitted_time_stamp = previous_time_stamp + (i+1)*INTERVAL_SIZE
                        omitted_date_time = datetime.fromtimestamp(omitted_time_stamp)
                        omitted_solar_irradiance = 0
                        offset+=INTERVAL_SIZE
                        #print(f'{omitted_date_time} {INTERVAL_SIZE} {omitted_solar_irradiance} ({i}) {offset}')
                        
                        writer.writerow([omitted_date_time, offset, omitted_solar_irradiance])
                        
                    offset+=INTERVAL_SIZE
                else:
                    print(date_time)
                    print(f'Error: Diff={diff} cannot be handled')
               
                #print(f'{date_time} {time_stamp_diff} {solar_irradiance} {offset}')
                writer.writerow([date_time, offset, solar_irradiance])
                
                previous_time_stamp = time_stamp

if __name__ == '__main__':
    process_photovolta_data('photovolta_2016_raw_data_part_1.csv', 'photovolta_2016_part_1.csv')
    process_photovolta_data('photovolta_2016_raw_data_part_2.csv', 'photovolta_2016_part_2.csv')

