import os
import json
import functools

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
    

def calc_tasks_mean_exec_time(traces_dir):

    durations = []

    for trace_path in os.listdir(traces_dir):
        full_path = traces_dir + '/' + trace_path
        #print(f'Reading ${full_path}')

        tasks_duration = calc_tasks_exe_time_for_file(full_path)
        durations.append(tasks_duration)

    size = len(durations[0])
    for d in durations:
            assert size == len(d), 'All tasks_duration sets must have the same size'
        

    mean_durations = []
    for i in range(len(durations[0])):

        sum = 0
        for tasks_duration in durations:
            sum += tasks_duration[i]

        mean = sum / len(durations)
        mean_durations.append(mean)

    return mean_durations

def get_task_computation_cost_env_variable(graph, task, rank, comp_cost):
    return f'OMPCLUSTER_HEFT_COMP_G_{graph}_T_{task}_P_{rank}={comp_cost}'

def get_task_energy_env_variable(graph, task, rank, energy):
    return f'OMPCLUSTER_MOHEFT_CONS_G_{graph}_T_{task}_P_{rank}={energy}'

if __name__ == '__main__':

    processors = [
        {
            'id': 0,
            'name': 'i5_10300H_POWER_SAVE',
            'traces_dir': './i5_10300H_POWER_SAVE',
            'power_in_W': 35 / 8
        },
        {
            'id': 1,
            'name': 'i5_10300H_PERFORMANCE',
            'traces_dir': './i5_10300H_PERFORMANCE',
            'power_in_W': 45 / 8
        }
    ]

    
    for processor in processors:
        tasks_mean_exec_time  = calc_tasks_mean_exec_time(processor['traces_dir'])

        calc_energy = lambda duration: duration * processor['power_in_W']
        tasks_energy = list(
            map(calc_energy, tasks_mean_exec_time)
        )

        # print(processor['name'])
        # print(
        #     functools.reduce(lambda a, b: a+b, tasks_mean_exec_time)
        # )
        # print(
        #     functools.reduce(lambda a, b: a+b, tasks_energy)
        # )

        for i in range(len(tasks_mean_exec_time)):
            graph = 1
            task = i
            rank = processor['id']

            exec_time = tasks_mean_exec_time[i]
            comp_cost_env_var = get_task_computation_cost_env_variable(graph, task, rank, exec_time)
            print(comp_cost_env_var)

            energy = tasks_energy[i]
            energy_env_var = get_task_energy_env_variable(graph, task, rank, energy)
            print(energy_env_var)
