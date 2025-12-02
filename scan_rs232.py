import serial
import json
import sys
import threading
import time
import os
import logging
import inspect

from datetime import datetime
from opcua import Client, ua
from logging.handlers import TimedRotatingFileHandler

global_barcode = ""
server_url = "opc.tcp://0.0.0.0:4840"

continue_reading = True

logger_name = os.path.splitext(os.path.basename(__file__))[0]

logging.getLogger('opcua').setLevel(logging.ERROR)
logging.getLogger(logger_name).setLevel(logging.DEBUG)

#-------------------------------------------------------------------------------------------------------------------
# Zapis do OPC serveru
#-------------------------------------------------------------------------------------------------------------------
def zapis_do_opc(nodeidrun, value):
    log_and_print(funkce=inspect.currentframe().f_code.co_name, text="Začátek", type_of_log="DEBUG")

    #server_url = "opc.tcp://0.0.0.0:4840"
    global server_url

    client = Client(server_url)

    try:
        client.connect()
    except Exception as ex:
        log_and_print(funkce=inspect.currentframe().f_code.co_name, text=nodeidrun + " - " + str(ex), type_of_log="ERROR")
    
    if isinstance(value, bool):
        variant_type = ua.VariantType.Boolean
    elif isinstance(value, int):
        variant_type = ua.VariantType.Int32
    elif isinstance(value, float):
        variant_type = ua.VariantType.Double
    elif isinstance(value, str):
        variant_type = ua.VariantType.String
    else:
        raise ValueError("Unsupported type")

    try:
        node = client.get_node(nodeidrun)

        if value != '':
            #node.set_value(ua.DataValue(ua.Variant(barcode, ua.VariantType.String)))
            node.set_value(ua.DataValue(ua.Variant(value, variant_type)))
            log_and_print(funkce=inspect.currentframe().f_code.co_name, text=str(value), type_of_log="DEBUG")
    except Exception as ex:
        log_and_print(funkce=inspect.currentframe().f_code.co_name, text=nodeidrun + " - " + str(ex), type_of_log="ERROR")

    finally:
    # Disconnect from the server
        client.disconnect()     
        #exit()
#-------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------------
# Cteni z OPC serveru
#-------------------------------------------------------------------------------------------------------------------
def cteni_z_opc(nodeidrun):
    log_and_print(funkce=inspect.currentframe().f_code.co_name, text="Začátek", type_of_log="DEBUG")

    #server_url = "opc.tcp://0.0.0.0:4840"
    global server_url

    ret = None

    client = Client(server_url)

    try:
        client.connect()
    except Exception as ex:
        log_and_print(funkce=inspect.currentframe().f_code.co_name, text=nodeidrun + " - " + str(ex), type_of_log="ERROR")

    try:
        node = client.get_node(nodeidrun)

        ret = node.get_value()
        log_and_print(funkce=inspect.currentframe().f_code.co_name, text=str(ret), type_of_log="DEBUG")
    except Exception as ex:
        log_and_print(funkce=inspect.currentframe().f_code.co_name, text=nodeidrun + " - " + str(ex), type_of_log="ERROR")

    finally:
    # Disconnect from the server
        client.disconnect()     
        #exit()
    return ret
#-------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------------
# Log and print taxt and messages at the same time
#-------------------------------------------------------------------------------------------------------------------
def log_and_print(text: str, funkce: str=None, type_of_log: str="INFO"):
    print(text)

    if funkce is not None:
        text = funkce + " : " + text

    if type_of_log == "INFO":
        logger.info(text)
    elif type_of_log == "DEBUG":
        logger.debug(text)
    elif type_of_log == "WARNING":
        logger.warning(text)
    elif type_of_log == "ERROR":
        logger.error(text)
    else:
        logger.info(text)
#------------------------------------------------------------------------------------------------------------------- 

#------------------------------------------------------------------------------------------------------------------- 
# Get the current date and time in the format YYYY_MM_DD__HH_MM_SS
#------------------------------------------------------------------------------------------------------------------- 
def actual_date_time():
    """
    Returns the current date and time in the format YYYY_MM_DD__HH_MM_SS
    """
    curr_time = datetime.now()
    return curr_time.strftime('%Y_%m_%d__%H_%M_%S_%f')
#------------------------------------------------------------------------------------------------------------------- 

#-------------------------------------------------------------------------------------------------------------------
# Return the path of the script
# This function is used to get the directory of the script, which is useful for loading configuration
#-------------------------------------------------------------------------------------------------------------------
def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))
#-------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------------
# Function to clean up old log files
#-------------------------------------------------------------------------------------------------------------------
def cleanup_old_logs(log_dir, days_to_keep=30):
    """
    Delete log files older than specified number of days
    
    Args:
        log_dir: Directory containing log files
        days_to_keep: Number of days to keep log files (default: 30)
    """
    try:
        from datetime import timedelta
        
        if not os.path.exists(log_dir):
            return
        
        # Calculate the cutoff date
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_timestamp = cutoff_date.timestamp()
        
        deleted_count = 0
        
        # Iterate through all files in log directory
        for filename in os.listdir(log_dir):
            if filename.endswith('.log'):
                file_path = os.path.join(log_dir, filename)
                
                # Get file modification time
                file_mtime = os.path.getmtime(file_path)
                
                # Delete if older than cutoff date
                if file_mtime < cutoff_timestamp:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                        log_and_print(funkce=inspect.currentframe().f_code.co_name, text=f"Deleted old log file: {filename}", type_of_log="DEBUG")
                    except Exception as e:
                        log_and_print(funkce=inspect.currentframe().f_code.co_name, text=f"Failed to delete {filename}: {e}", type_of_log="WARNING")
        
        if deleted_count > 0:
            log_and_print(funkce=inspect.currentframe().f_code.co_name, text=f"Cleaned up {deleted_count} old log file(s)", type_of_log="INFO")
            
    except Exception as e:
        log_and_print(funkce=inspect.currentframe().f_code.co_name, text=f"Error during log cleanup: {e}", type_of_log="ERROR")
#-------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------------
# Function to load configuration from JSON file
#-------------------------------------------------------------------------------------------------------------------
def load_config(config_file=None):
    """Load configuration from JSON file with default values"""
    if config_file is None:
        script_dir = get_script_path()
        config_file = os.path.join(script_dir, 'scan_rs232.json')
    
    try:
        with open(config_file) as f:
            config = json.load(f)
            
            # Load configuration with default values
            pPort = config.get('port', '/dev/ttyS0')
            pBudrate = config.get('baudrate', 9600)
            pTimeout = config.get('timeout', 10)
            pRtscts = config.get('rtscts', False)
            pDsrdtr = config.get('dsrdtr', False)
            barcode_node = config.get('barcode_node', 'ns=1;i=100001')
            barcode_response_node = config.get('barcode_response_node', 'ns=1;i=100002')
            barcode_beep_count = config.get('barcode_beep_count', 'ns=1;i=100003')
            log_retention_days = config.get('log_retention_days', 30)  # Keep logs for 30 days
            
            log_and_print(funkce=inspect.currentframe().f_code.co_name, text=f"Configuration loaded from: {config_file}", type_of_log="DEBUG")
            return {
                'port': pPort,
                'baudrate': pBudrate,
                'timeout': pTimeout,
                'rtscts': pRtscts,
                'dsrdtr': pDsrdtr,
                'barcode_node': barcode_node,
                'barcode_response_node': barcode_response_node,
                'barcode_beep_count': barcode_beep_count,
                'log_retention_days': log_retention_days
            }
    except FileNotFoundError:
        log_and_print(funkce=inspect.currentframe().f_code.co_name, text=f"Config file not found: {config_file}", type_of_log="WARNING")
        log_and_print(funkce=inspect.currentframe().f_code.co_name, text="Using default configuration values", type_of_log="INFO")
        return {
            'port': '/dev/ttyS0',
            'baudrate': 9600,
            'timeout': 10,
            'rtscts': False,
            'dsrdtr': False,
            'barcode_node': 'ns=1;i=100001',
            'barcode_response_node': 'ns=1;i=100002',
            'barcode_beep_count': 'ns=1;i=100003',
            'log_retention_days': 30
        }
    except json.JSONDecodeError as e:
        log_and_print(funkce=inspect.currentframe().f_code.co_name, text=f"Error decoding JSON config: {e}", type_of_log="ERROR")
        sys.exit(1)
    except Exception as e:
        log_and_print(funkce=inspect.currentframe().f_code.co_name, text=f"Error reading configuration: {e}", type_of_log="ERROR")
        sys.exit(1)
#-------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------------
# Function to read from the serial port and process scanned barcodes
#-------------------------------------------------------------------------------------------------------------------
def read(pPort, pBudrate, pTimeout, pRtscts, pDsrdtr):
    global continue_reading

    global barcode_node
    global barcode_response_node
    global barcode_beep_count 

    try:
        # Zde to chce nastavit práva pro skupinu dialout
        # sudo usermod -a -G dialout $USER
        # viz poznamky.txt -> Připojení scanneru
        # Momentálnš rtscts a dsrdtr ponechat false

        ser = serial.Serial(pPort, baudrate=pBudrate, timeout=pTimeout, rtscts=pRtscts, dsrdtr=pDsrdtr)
            
        print("Listening for barcodes...")
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return

    try:
        while continue_reading:
            if ser.in_waiting:               

                barcode = ser.readline().decode('utf-8').strip()
                print("Scanned:", barcode)

                zapis_do_opc(barcode_response_node, False) 
                zapis_do_opc(barcode_node, barcode)    

                potrvzeni = False

                pocet = 0
                while potrvzeni is False and pocet < 20:
                    potrvzeni = cteni_z_opc(barcode_response_node)
                    time.sleep(0.1)
                    pocet = pocet + 1

                log_and_print("Počet:" + str(pocet))

                if potrvzeni == True:
                    bytestosend = bytes([0x06])

                    log_and_print("Potvrzení ACK")
                    ser.write(bytestosend) 

                    zapis_do_opc(barcode_response_node, False) 

                    pocet_pipnuti = cteni_z_opc(barcode_beep_count)
                    for i in range(pocet_pipnuti):
                        bytestosend = bytes([0x07])
                        ser.write(bytestosend)
                        time.sleep(0.5)

                    log_and_print(text=f"Potvrzení - {potrvzeni}", type_of_log="DEBUG")

                if potrvzeni == False:
                    log_and_print(text=f"Potvrzení - {potrvzeni}", type_of_log="DEBUG")

            time.sleep(0.1)  # Prevent busy waiting
    except KeyboardInterrupt as ki:
        log_and_print(text=f"Stopped - {ki}", type_of_log="ERROR")
    except Exception as ex:
        log_and_print(text=f"Error - {ex}", type_of_log="ERROR")
    finally:
        ser.close()
#-------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------------
# Main function to start the scanner thread
#-------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    #---------------------------------------------------------
    # Setting for logging
    #---------------------------------------------------------
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    actual_dir = get_script_path()
    actual_file_name_py = os.path.basename(__file__)
    actual_file_name = actual_file_name_py.split('.')[0]

    log_dir = actual_dir + "/log"

    if os.path.exists(log_dir) == False:
        os.makedirs(log_dir)

    log_file = actual_file_name + ".log"
    log_path = os.path.join(log_dir, log_file)
    #---------------------------------------------------------

    #-------------------------------------------------
    # Nastavení logování s rotací každý den
    #-------------------------------------------------
    class LogWithDateExtensionHandler(TimedRotatingFileHandler):
        def rotation_filename(self, default_name):
            """
            Rebuild the rotated filename to keep .log extension at the end
            """
            try:
                base, _ = os.path.splitext(default_name)
                root_base, ext = os.path.splitext(base)
                # Use current timestamp for rotation
                date_str = datetime.now().strftime("%Y-%m-%d")
                return f"{root_base}_{date_str}.log"
            except Exception as e:
                return default_name
    # Rotate daily at midnight (or "M" for minutes)
    handler = LogWithDateExtensionHandler(
        log_path,
        when="midnight",
        interval=1,
        backupCount=7
    )
    '''
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    '''
    formatter = logging.Formatter(
        fmt='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    #-------------------------------------------------

    log_and_print(text='-----------------------------------------------------')
    log_and_print(text="Začátek")

    # Load configuration from JSON file
    config = load_config()
    pPort = config['port']
    pBudrate = config['baudrate']
    pTimeout = config['timeout']
    pRtscts = config['rtscts']
    pDsrdtr = config['dsrdtr']
    barcode_node = config['barcode_node']
    barcode_response_node = config['barcode_response_node']
    barcode_beep_count = config['barcode_beep_count']
    log_retention_days = config['log_retention_days']
    
    # Clean up old log files
    cleanup_old_logs(log_dir, log_retention_days)

    scanner = threading.Thread(target=read, args=(pPort, pBudrate, pTimeout, pRtscts, pDsrdtr))
    scanner.start()

    while True:
        try:
            # Keep the main thread alive to allow the scanner thread to run
            scanner.join(timeout=1)
            if not scanner.is_alive():
                log_and_print("Vlákno scanner nežije", type_of_log="WARNING")
                continue_reading = False              
                break
        except KeyboardInterrupt as ki:
            print()
            log_and_print(f"Error in while cycle {ki} Exiting...", type_of_log="ERROR")
            continue_reading = False
            break

    scanner.join()

    log_and_print("Konec", actual_date_time())
    log_and_print('-----------------------------------------------------')
#-------------------------------------------------------------------------------------------------------------------
    #read(pPort=pPort, pBudrate=pBudrate, pTimeout=pTimeout)