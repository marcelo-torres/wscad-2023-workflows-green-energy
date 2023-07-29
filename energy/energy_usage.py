from bintrees import FastAVLTree

# Bintrees doc: https://pypi.org/project/bintrees/


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
                #print(f'{time}s * Power={power}W = {energy}J')
                
                # s, W and J
                energy_trace.append((time, power, energy))
            else:
                energy_trace.append((time, 0, 0))
                
            lastTime = instant.timestamp
            
            for work in instant.worksBeginning:
                activeWorks[work] = instant.timestamp
                
            for work in instant.worksEnding:
                activeWorks.pop(work)
            
        return (total_energy_in_joules, energy_trace)
       
    def clear(self):
        self.instants.clear()


if __name__ == '__main__':

    # * * * * * * * * * * * * * * * * *  \/  * * * * * * * * * * * * * * * * * #
    #                                                                          #
    #                                  T E S T                                 #
    #                                                                          #
    # * * * * * * * * * * * * * * * * *  /\  * * * * * * * * * * * * * * * * * #


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
        
    total_energy_in_joules, energy_trace = e.calc()
    print(f'Energy usage intervals: {energy_trace}')
    print(f'Total energy: {total_energy_in_joules}')
  
  
    expected_total_energy_in_joules = 0
    for time, power, energy in intervals_expected:
        expected_total_energy_in_joules += energy
        
        t, p, e = energy_trace.pop(0)

        assert t == time, f'Time {t} should be {time}'
        assert p == power, f'Power {p} should be {power}'
        assert e == energy, f'Energy {e} should be {energy}'
  
    assert total_energy_in_joules == expected_total_energy_in_joules, f'Total energy should be {expected_total_energy_in_joules}'
    
    #e.add_work('A', 0, 30, 20)
    #e.add_work('B', 25, 70, 20)
    #e.add_work('C', 40, 80, 20)
    #e.add_work('D', 60, 100, 20)

