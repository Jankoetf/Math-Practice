"""main program"""
from aviator_class import AviatorClass

if __name__ == "__main__":
    #general constants
    rtp_versions_list = list(range(86, 97)); step = 0.1; max_crash_point = 100
    
    #simulation constants
    n_iterations = 1000000;
    
    #txt
    output_file = "results.txt"
    with open(output_file, "w") as file:
        pass
    
    """get parsheets"""
    for rtp_version in rtp_versions_list:
        #class instance
        aviator_class_instance = AviatorClass(rtp_version, step, max_crash_point)
        #simulations
        aviator_class_instance.get_parsheet(n_iterations = n_iterations, output_file = output_file)
        
        
    

    
    
    
    