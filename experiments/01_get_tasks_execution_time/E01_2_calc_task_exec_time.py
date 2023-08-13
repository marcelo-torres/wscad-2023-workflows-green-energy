import os
import json

def microsecond_to_second(microsecond):
    return microsecond / 1000000

def calc_tasks_exe_time_for_file(trace_file):
    with open(trace_file) as f:
        data = json.load(f)

        tasks_duration = []

        for event in data['traceEvents']:
            if event['ph'] == 'X' and event['name'] == 'Execute / Target Execution':
                duration = microsecond_to_second(float(event['dur']))
                tasks_duration.append(duration)

        return tasks_duration
    

def calc_tasks_exec_time(traces_dir):

    durations = []

    for trace_path in os.listdir(traces_dir):
        full_path = traces_dir + '/' + trace_path
        print(f'Reading ${full_path}')

        tasks_duration = calc_tasks_exe_time_for_file(full_path)
        durations.append(tasks_duration)

        


if __name__ == '__main__':

    processors = [
        {
            'id': 0,
            'name': 'i5_10300H_POWER_SAVE',
            'traces_dir': './i5_10300H_POWER_SAVE'
        },
        {
            'id': 1,
            'name': 'i5_10300H_PERFORMANCE',
            'traces_dir': './i5_10300H_PERFORMANCE'
        }
    ]

    for processor in processors:
        calc_tasks_exec_time(processor['traces_dir'])

    pass