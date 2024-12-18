"""Aviator Class"""
import math
import numpy as np
import sys
from copy import deepcopy

class AviatorClass:
    def __init__(self, rtp_version, step, max_crash_point):
        try:
            #checkong rtp_version value
            potential_rtp_versions = set([version for version in range(86, 97)] + [str(version) for version in range(86, 97)])
            if rtp_version not in potential_rtp_versions:
                raise ValueError("invalid rtp version")
            rtp_version = int(rtp_version)
            
            #checking step value
            if not isinstance(step, (int, float)):
                raise ValueError("step should be numeric type")
            if step <= 0:
                raise ValueError("step should be bigger than 0")
                
            log_step = math.log10(step)
            if log_step != int(log_step):
                raise ValueError("step should be power of 10")
            
            #checking max_crash_point
            if not isinstance(max_crash_point, int) or max_crash_point < 10:
                raise ValueError("invalid max_crash_point")
                
        except ValueError as e:
            print(e); sys.exit(1)
        
        self.rtp_version, self.step, self.max_crash_point, self.presition =  rtp_version/100, step, max_crash_point, int(-log_step)
        self.min_crash_point = self.min_cash_out = 1 + self.step
        self.crash_values, self.cash_out_values, self.crash_probabilities = [], [], []
        
        #create mass function
        self.create_mass_function()
        
    def create_mass_function(self):
        """
        rtp is const, crash_max = 100 for example, step = 0.1 for example, crash_min = 1
        (potential cash out range is from 1.01 to 99.9)
        
        desired cash out: 
        99.9 -> p(crash > 99.9)*99.9 + p(crash <= 99.9)*0 = rtp => p(crash > 99.9) = rtp/99.9 => p(crash = 100) = rtp/99.9
        99.8 -> p(crash > 99.8)*99.8 + p(crash <= 99.8)*0 = rtp => p(crash > 99.8) = rtp/99.8 => p(crash = 99.9) = rtp/99.8 - p(crash = 100)
        99.7 -> p(crash > 99.7)*99.7 = rtp => p(crash = 99.8) = rtp/99.7 - p(crash = 99.9) - p(crash = 100)
        ...
        ...
        ...
        1.01 -> p(crash > 1.01)*1.01 + p(crash <= 1.01)*0 = rtp => p(crash = 1.02) = rtp/1.01 - p(crash = 1.03) - ... - p(crash = 100)
        
        cash out of 1 is impossibe, so if crash = 1.01 or crash = 1.0 player won't ever get any reward...
        p(crash = 1) + p(crash = 1.1) = 1 - p(crash = 1.2) - ... - p(crash = 100)
        we can also say p(crash = 1) = 0 for simplicity... so then:
        p(crash = 1.1) = 1 - p(crash = 1.2) - ... - p(crash = 100)
        """
        
        running_probability_sum_right = 0
        for raw_crash_point in np.arange(self.max_crash_point, self.min_crash_point, -self.step):
            current_crash_point = round(raw_crash_point, self.presition)
            self.crash_values.append(current_crash_point);
            current_probability = self.rtp_version/(current_crash_point-self.step) - running_probability_sum_right
            self.crash_probabilities.append(float(current_probability)); 
            running_probability_sum_right += current_probability
            
        self.crash_values.append(self.min_crash_point); self.crash_probabilities.append(float(1-sum(self.crash_probabilities)))
        self.cash_out_values = deepcopy(self.crash_values[1:])
        
        # print(self.crash_values, "len: ", len(self.crash_values))
        # print("self.probabilities: ", self.crash_probabilities, "sum: ", sum(self.crash_probabilities))
        # print("self.cash_out_values: ", self.cash_out_values)
    
    def simulate_random_crash_point(self):
        return float(np.random.choice(a = self.crash_values, p = self.crash_probabilities))
    
    def simulate_random_cash_out_point(self):
        return float(np.random.choice(a = self.cash_out_values))
    
    def simulate_game_rtp_for_const_cash_out(self, cash_out_point, n_iterations = 100000):
        try:
            #checking cash_out_point
            if not isinstance(cash_out_point, (int, float)):
                raise ValueError("invalid type for: cash_out_point")
            elif cash_out_point < self.min_cash_out:
                raise ValueError("invalid cash_out_point value")
            elif cash_out_point != round(cash_out_point, self.presition):
                raise ValueError("invalid cash_out_point presition")
            
            #checking n_iterations
            if not isinstance(n_iterations, int):
                raise ValueError("invalid type for: n_iterations")
            if n_iterations < 1:
                raise ValueError("invalid value for: n_iterations")
        except ValueError as e:
            print(e); sys.exit(1)
        
        total_win = 0
        for _ in range(n_iterations):
            crash_point = self.simulate_random_crash_point()
            total_win += cash_out_point if crash_point > cash_out_point else 0
        
        print(f"simulated rtp for cash_out_point of {cash_out_point} is: {total_win/n_iterations}")
        
    
    def get_parsheet(self, n_iterations = 1000000, output_file = "output_file.txt"):
        try:
            # checking output file:
            if not isinstance(output_file, str):
                raise ValueError("invalid type for: output_file")
            elif output_file.split(".")[-1] != "txt":
                raise ValueError("invalid text file")
                
            #checking n_iterations
            if not isinstance(n_iterations, int):
                raise ValueError("invalid type for: n_iterations")
            if n_iterations < 1:
                raise ValueError("invalid value for: n_iterations")
                
        except ValueError as e:
            print(e); sys.exit(1)
        
        total_win = total_win_squared = 0
        for _ in range(n_iterations):
            random_crash_point = self.simulate_random_crash_point()
            random_cash_out_point = self.simulate_random_cash_out_point()
            current_win = random_cash_out_point if random_crash_point > random_cash_out_point else 0
            total_win += current_win; total_win_squared += pow(current_win, 2)
    
        
        print("rtp version: ", self.rtp_version)
        rtp = total_win / n_iterations; volatility = pow(total_win_squared/n_iterations - pow(rtp, 2), 0.5)
        print(f"n_iterations: {n_iterations}, rtp: {rtp}, volatility: {volatility}")
        
        #saving results
        with open(output_file, "a") as file:
            file.write(f"rtp version: {self.rtp_version}\n")
            file.write(f"n_iterations: {n_iterations}, rtp: {rtp}, volatility: {volatility}\n\n")
        
        
            
            
        
            
    
            
        
        
        
        
        
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
        
        
        