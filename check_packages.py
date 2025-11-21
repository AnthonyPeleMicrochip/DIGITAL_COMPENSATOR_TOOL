import string
import sys
import os
from enum import Enum

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
display_output = False

"""        
**************************************************************************************************************************************
* FUNCTIONS
**************************************************************************************************************************************
"""
def check_package_installed(package_name: string) -> flag:
    try:
        import importlib.util
        
    except ImportError as e:
        stream = os.popen('pip install importlib')
        answer = stream.read()
        import importlib.util
        return flag.OK if importlib.util.find_spec('importlib') is not None else flag.KO
    
    """Check if a package is installed."""
    return flag.OK if importlib.util.find_spec(package_name) is not None else flag.KO

def install_package(package_name: string) -> flag:
    try:
        import pip
    except ImportError as e:
        stream = os.popen('pip install pip')
        answer = stream.read()
        import pip
        return flag.OK if importlib.util.find_spec('pip') is not None else flag.KO
    
    """Install a package using pip."""
    stream = os.popen(f'pip install {package_name}')
    answer = stream.read()
    return check_package_installed(package_name)



"""        
**************************************************************************************************************************************
* MAIN
**************************************************************************************************************************************
"""
def main():
    package_name_test ='numpy123'
    retval = check_package_installed(package_name_test)
    if display_output:
        if retval == flag.OK:
            print("Package is installed.")
        else:
            print("Package is NOT installed.")
            install_package(package_name_test)
    return retval

if __name__ == "__main__":
    display_output = True
    main()
    sys.exit(main())