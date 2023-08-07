import json

if __name__ == '__main__':

    times = 255 * 2 # 5h

    source_file = '../data/OMPC_matmul_trace_data.json'
    target_file = f'../data/OMPC_matmul_trace_data_{times}x.json'
    
    
    f = open(source_file)
    data = json.load(f)
    
    
    new_data = {
        'traceEvents': []
    } 


    bigger_time_stamp = 0

    for i in range(times):
    
        bigger_time_stamp_iteration = bigger_time_stamp
    
        for event in data['traceEvents']:
            
            if 'ts' in event:
                event_ts = event['ts']
                if event_ts >= bigger_time_stamp_iteration:
                    bigger_time_stamp_iteration = event_ts
                    
                new_event = event.copy()
                new_event['ts'] += (i+1) * bigger_time_stamp
            new_data['traceEvents'].append(new_event)
            
        bigger_time_stamp = bigger_time_stamp_iteration
        
        
        print(f'{i} - Bigger TS {bigger_time_stamp}us = {((i+1) *bigger_time_stamp) / 1000000}s')
        

    with open(target_file, 'w') as outfile:
        json.dump(new_data, outfile)
