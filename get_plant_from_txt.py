import sys, os
from enum import Enum
import numpy as np

"""        
**************************************************************************************************************************************
* DEFINES
**************************************************************************************************************************************
"""

"""        
***************************************************************************************************************************************
* CLASSES
**************************************************************************************************************************************
"""
# ----------------------------------------------------------------------------------------------------------------------------------------
# Class which defines type of flag as Enum
class flag(Enum):
    OK = 1
    KO = 0
    ERROR = -1

"""        
**************************************************************************************************************************************
* GLOBALS
**************************************************************************************************************************************
"""

"""        
**************************************************************************************************************************************
* FUNCTIONS
**************************************************************************************************************************************
"""
def reshape_plant_data(plant_data, freq_vector_to_match):
    reshape_plant_data = []
    for freq in freq_vector_to_match:
        # look for closest frequency in plant_data
        diff_array = np.abs(np.array(plant_data)[:,0] - freq)
        index_min = np.argmin(diff_array)
        reshape_plant_data.append(plant_data[index_min])
    return reshape_plant_data
        
def main(plant_text_file = None , verbose = False):
    if plant_text_file is None:
        return (flag.ERROR)
    else:
        try:
            f = open(plant_text_file, 'r')
            data_string = f.read()
            f.close()
            data = []
            for line in data_string.split('\n'):
                if line != '':
                    line_array = line.split("\t")
                    line_array = [item.strip() for item in line_array]
                    data.append(line_array)
            data.pop(0)  # Remove header
            for point in data:
                point[0] = float(point[0])
                point[1] = float(point[1])
                point[2] = float(point[2])
            if verbose:
                print(data)
                print(type(data))
                print(len(data))
            return (flag.OK, data)
        except FileNotFoundError as fnfe:
            return (flag.KO)

"""        
**************************************************************************************************************************************
* MAIN
**************************************************************************************************************************************
"""
if __name__ == "__main__":
    # Retrieve config file name if any
    try :
        sys.argv[1]
        flag, data = main(sys.argv[1], True)
    except IndexError:
        flag, data = main()
    print(flag.value)
    sys.exit()