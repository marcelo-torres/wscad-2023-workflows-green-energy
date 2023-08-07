from bintrees import FastAVLTree
import logging, sys

# Bintrees doc: https://pypi.org/project/bintrees/


if __name__ == '__main__':
    log_level = logging.DEBUG
else:
    log_level = logging.INFO
logging.basicConfig(stream=sys.stderr, level=log_level, format='[%(asctime)s][%(levelname)s] %(message)s')
logger = logging.getLogger('energy_usage')


class Work:
    def __init__(self, name, power):
        self.name = name
        self.power = power # in Watts, that is J/s
      
    def __str__(self):
        return f'{self.name} {self.power}W'


class Instant:
    def __init__(self, timestamp, worksBeginning, worksEnding):
        self.timestamp = timestamp
        self.worksBeginning = worksBeginning
        self.worksEnding = worksEnding
    
    def __str__(self):
        return str(self.timestamp)


class EnergyUsage:
    
    def __init__(self):
        self.instants = FastAVLTree()
    
    
    def __get_instant(self, timestamp):
        instant = self.instants.get(timestamp)
        if instant is None:
            instant = Instant(timestamp, [], [])
            self.instants.insert(timestamp, instant)
        return instant
    
    def add_work(self, name, start, end, power):
        work = Work(name, power)
        self.__get_instant(start).worksBeginning.append(work)
        self.__get_instant(end).worksEnding.append(work)


    def calc(self):
        lastTime = 0
        activeWorks = {}
        
        energy_trace = []
        total_energy_in_joules = 0
        
        for key, instant in self.instants.items():
            time = instant.timestamp - lastTime
            if activeWorks:
                
                power = 0
                for w in activeWorks.keys():
                    power += w.power
                    
                energy = time * power # 1W * 1s = 1J
                total_energy_in_joules += energy
                logger.debug(f'{time}s * {power}W = {energy}J')
                
                # s, W and J
                energy_trace.append((time, power, energy))
            else:
                logger.debug(f'{time}s * 0W = 0J (No active works)')
                energy_trace.append((time, 0, 0))
                
            lastTime = instant.timestamp
            
            for work in instant.worksBeginning:
                activeWorks[work] = instant.timestamp
                
            for work in instant.worksEnding:
                activeWorks.pop(work)
            
        return (total_energy_in_joules, energy_trace)
       
    def clear(self):
        self.instants.clear()


def calc_green_energy_usage(energy_trace, next_green_interval):

    now = 0    
    green_interval_time = 0
    green_available_power = 0

    total_energy = 0
    total_brown_energy_used = 0
    total_green_energy_used = 0
    total_green_energy_not_used = 0
    
    for time, power, energy in energy_trace:
        
        logger.debug('')
        logger.debug(f'Energy Trace: {time}s, {power}W, {energy}J')

        while time > 0:

            if now >= green_interval_time:
                green_interval_time, green_available_power = next_green_interval()

            if now + time > green_interval_time:
                logger.debug('Breaking the work duration to fit in the green interval')
                t = green_interval_time - now
            else:
                t = time
                
            # Calculation
            energy = t * power
            green_energy = t * green_available_power
            green_energy_used = energy if green_energy >= energy else green_energy
            
            total_energy += energy
            total_brown_energy_used += energy - green_energy_used
            total_green_energy_used += green_energy_used
            total_green_energy_not_used += green_energy - green_energy_used
            
            logger.debug(f'({now}s t={t}s Energy={energy}J)')

            now += t
            time -= t
            

    return {
        'total_energy': total_energy,
        'total_brown_energy_used': total_brown_energy_used,
        'total_green_energy_used': total_green_energy_used,
        'total_green_energy_not_used': total_green_energy_not_used
    }


# * * * * * * * * * * * * * * * * *  \/  * * * * * * * * * * * * * * * * * #
#                                                                          #
#                                  T E S T                                 #
#                                                                          #
# * * * * * * * * * * * * * * * * *  /\  * * * * * * * * * * * * * * * * * #

def __test_get_data():
    intervals_expected = [
    # duration (s), total power (W) and energy (J)
        (0, 0, 0),
        (5, 10, 50), # A
        (10, 100, 1000), # B
        (6, 0, 0),
        (1, 7, 7), # C
        (4, 16, 64), # C + D
        (1, 9, 9), # D
        (8, 0, 0),
        (5, 1, 5) # E
    ]

    expected_total_energy_in_joules = 0
    for data in intervals_expected:
        time, power, energy = data
        expected_total_energy_in_joules += energy

    return intervals_expected, expected_total_energy_in_joules


def __test_calc():

    # Works (Power)
    # 
    # E (  1W)                                    #####    
    # D (  9W)                       #####             
    # C (  7W)                      #####              
    # B (100W)      ##########                         
    # A ( 10W) #####                                     
    #          ----+----+----+----+----+----+----+----+
    #          1s  5s  10s  15s  20s  25s  30s  35s  40s


    e = EnergyUsage()
    
    e.add_work('A', 0, 5, 10)
    e.add_work('B', 5, 15, 100)
    e.add_work('C', 21, 26, 7)
    e.add_work('D', 22, 27, 9)
    e.add_work('E', 35, 40, 1)
    
    total_energy_in_joules, energy_trace = e.calc()
    logger.info(f'Energy usage intervals: {energy_trace}')
    logger.info(f'Total energy: {total_energy_in_joules}')
  
    intervals_expected, expected_total_energy_in_joules = __test_get_data()
    assert total_energy_in_joules == expected_total_energy_in_joules, f'Total energy should be {expected_total_energy_in_joules}'


    for i, data in enumerate(intervals_expected):
        time, power, energy = data  
        t, p, e = energy_trace[i]

        assert t == time, f'Time {t} should be {time}'
        assert p == power, f'Power {p} should be {power}'
        assert e == energy, f'Energy {e} should be {energy}'   


def __test_calc_green_energy_usage():

    # Power Usage: *
    # Green Power Available: .
    #
    # 100W          **********
    #  64W          '        '       ****
    #  50W     *****' .............  '  '
    #   9W        ....       '     ..'  '*    
    #   7W     ...  '        '      *..................
    #   5W          '        '      '    '        *****
    #          ----+----+----+----+----+----+----+----+
    #          1s  5s  10s  15s  20s  25s  30s  35s  40s

    energy_trace, expected_total_energy_in_joules = __test_get_data()

    green_power_intervals = [
        #(0, 0), #??? TODO
        (3, 7),
        (7, 9),
        (20, 50),
        (22, 9),
        (40, 7),
        (0,0)
    ]

    i = iter(green_power_intervals)
    def next_green_interval():
        pv_interval_time, pv_available_power = next(i)
        logger.debug(f'New Green Interval Read: {pv_interval_time}s Available Power: {pv_available_power}W')
        return pv_interval_time, pv_available_power

    logger.info('Calculating green energy usage...')
    r = calc_green_energy_usage(energy_trace, next_green_interval)
    logger.info(r)

    assert r['total_energy'] == expected_total_energy_in_joules, f'Total energy should be {expected_total_energy_in_joules}'

if __name__ == '__main__':

    __test_calc()
    __test_calc_green_energy_usage()
