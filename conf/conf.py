import json
import os
import sys
import socket
import ssl
import urllib.request
import urllib.error

_config = None
_version = None
_remote_config = None

# Remote API configuration
API_BASE_URL = "https://api.oczsvalitcvat.zb.if.atcsg.net"
DEVICE_NAME = socket.gethostname()  # Auto-detect hostname, or set manually

#-------------------------------------------------------------------------------------------------------------------
# Path Functions
#-------------------------------------------------------------------------------------------------------------------
def get_script_path():
    """Return the path of the main script (not this module)"""
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def get_conf_path():
    """Return the path to the conf directory"""
    if __name__ == "__main__":
        return os.path.join(get_script_path())
    else:
        return os.path.join(get_script_path(), "conf")

#-------------------------------------------------------------------------------------------------------------------
# Local Config Functions
#-------------------------------------------------------------------------------------------------------------------
def get_config():
    """Load scanner configuration from scan_rs232.json"""
    global _config
    if _config is None:  # load only once
        config_path = os.path.join(get_conf_path(), "scan_rs232.json")
        with open(config_path, "r") as f:
            _config = json.load(f)
    return _config

#-------------------------------------------------------------------------------------------------------------------
# Version Functions
#-------------------------------------------------------------------------------------------------------------------
def get_version():
    """Load version information from verze.json"""
    global _version
    if _version is None:  # load only once
        version_path = os.path.join(get_conf_path(), "verze.json")
        try:
            with open(version_path, "r") as f:
                _version = json.load(f)
        except FileNotFoundError:
            _version = {"verze": "unknown"}
    return _version.get('verze', _version.get('version', 'unknown'))

#-------------------------------------------------------------------------------------------------------------------
# Scanner Configuration Functions
#-------------------------------------------------------------------------------------------------------------------
def get_scanner_configurations():
    """Get list of scanner configurations with defaults"""
    config = get_config()
    scanner_configs = config.get('scanner_configurations', [])
    
    # Backward compatibility
    if not scanner_configs:
        if isinstance(config, list):
            scanner_configs = config
        else:
            scanner_configs = [config]
    
    scanners = []
    for idx, scanner_config in enumerate(scanner_configs):
        scanner = {
            'port': scanner_config.get('port', '/dev/ttyS0'),
            'baudrate': scanner_config.get('baudrate', 9600),
            'timeout': scanner_config.get('timeout', 10),
            'rtscts': scanner_config.get('rtscts', False),
            'dsrdtr': scanner_config.get('dsrdtr', False),
            'barcode_node': scanner_config.get('barcode_node', f'ns=1;i={100001 + idx * 5}'),
            'barcode_response_node': scanner_config.get('barcode_response_node', f'ns=1;i={100002 + idx * 5}'),
            'barcode_beep_count': scanner_config.get('barcode_beep_count', f'ns=1;i={100003 + idx * 5}'),
            'barcode_health_check': scanner_config.get('barcode_health_check', f'ns=1;i={100004 + idx * 5}'),
            'barcode_health_check_message': scanner_config.get('barcode_health_check_message', f'ns=1;i={100005 + idx * 5}')
        }
        scanners.append(scanner)
    
    return scanners

#-------------------------------------------------------------------------------------------------------------------
# Log Configuration Functions
#-------------------------------------------------------------------------------------------------------------------
def get_log_level():
    """Get log level from config, default INFO"""
    config = get_config()
    return config.get('log_level', 'INFO').upper()

def get_log_retention_days():
    """Get log retention days from config, default 30"""
    config = get_config()
    return config.get('log_retention_days', 30)

#-------------------------------------------------------------------------------------------------------------------
# Remote Config Functions
#-------------------------------------------------------------------------------------------------------------------
def fetch_remote_config(device_name=None, timeout=10, verify_ssl=False):
    """
    Fetch scanner configuration from remote API.
    
    Args:
        device_name: Device/machine name (default: hostname)
        timeout: Request timeout in seconds (default: 10)
        verify_ssl: Verify SSL certificate (default: True, set False for self-signed certs)
        
    Returns:
        dict: Configuration from remote API
        
    Raises:
        Exception: If request fails
    """
    global _remote_config
    
    if device_name is None:
        device_name = DEVICE_NAME
    
    url = f"{API_BASE_URL}/getConfigScanner?name={device_name}"
    
    try:
        # Create SSL context
        if verify_ssl:
            ssl_context = ssl.create_default_context()
        else:
            # For self-signed or internal certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        
        # Create request with headers
        request = urllib.request.Request(
            url,
            headers={
                'Accept': 'application/json',
                'User-Agent': 'at_scanner/1.0'
            }
        )
        
        # Make the request
        with urllib.request.urlopen(request, timeout=timeout, context=ssl_context) as response:
            if response.status == 200:
                data = response.read().decode('utf-8')
                _remote_config = json.loads(data)
                return _remote_config
            else:
                raise Exception(f"HTTP {response.status}: {response.reason}")
                
    except urllib.error.HTTPError as e:
        raise Exception(f"HTTP Error {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        raise Exception(f"URL Error: {e.reason}")
    except json.JSONDecodeError as e:
        raise Exception(f"JSON decode error: {e}")
    except Exception as e:
        raise Exception(f"Request failed: {e}")
#-------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------------
# Remote Root Config Functions
#-------------------------------------------------------------------------------------------------------------------
def fetch_remote_root_config(device_name=None, timeout=10, verify_ssl=False):
    """
    Fetch scanner configuration from remote API.
    
    Args:
        device_name: Device/machine name (default: hostname)
        timeout: Request timeout in seconds (default: 10)
        verify_ssl: Verify SSL certificate (default: True, set False for self-signed certs)
        
    Returns:
        dict: Configuration from remote API
        
    Raises:
        Exception: If request fails
    """
    global _remote_config
    
    if device_name is None:
        device_name = DEVICE_NAME
    
    url = f"{API_BASE_URL}/getConfigRoot?name={device_name}"
    
    try:
        # Create SSL context
        if verify_ssl:
            ssl_context = ssl.create_default_context()
        else:
            # For self-signed or internal certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        
        # Create request with headers
        request = urllib.request.Request(
            url,
            headers={
                'Accept': 'application/json',
                'User-Agent': 'at_scanner/1.0'
            }
        )
        
        # Make the request
        with urllib.request.urlopen(request, timeout=timeout, context=ssl_context) as response:
            if response.status == 200:
                data = response.read().decode('utf-8')
                _remote_config = json.loads(data)
                return _remote_config
            else:
                raise Exception(f"HTTP {response.status}: {response.reason}")
                
    except urllib.error.HTTPError as e:
        raise Exception(f"HTTP Error {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        raise Exception(f"URL Error: {e.reason}")
    except json.JSONDecodeError as e:
        raise Exception(f"JSON decode error: {e}")
    except Exception as e:
        raise Exception(f"Request failed: {e}")
#-------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------------
# Get Remote Config with Fallback
#-------------------------------------------------------------------------------------------------------------------
def get_remote_config(device_name=None, timeout=10, fallback_to_local=True, verify_ssl=False):
    """
    Get configuration from remote API with optional fallback to local config.
    
    Args:
        device_name: Device/machine name (default: hostname)
        timeout: Request timeout in seconds (default: 10)
        fallback_to_local: If True, use local config on failure (default: True)
        verify_ssl: Verify SSL certificate (default: True)
        
    Returns:
        dict: Configuration dictionary
    """
    try:
        config = fetch_remote_config(device_name, timeout, verify_ssl)
        print(f"Remote config loaded for device: {device_name or DEVICE_NAME}")
        return config
    except Exception as e:
        print(f"Failed to fetch remote config: {e}")
        if fallback_to_local:
            print("Falling back to local configuration...")
            return get_config()
        raise

#-------------------------------------------------------------------------------------------------------------------
# Update Local Config from Remote
#-------------------------------------------------------------------------------------------------------------------
def update_local_config_from_remote(device_name=None, timeout=10, verify_ssl=False):
    """
    Fetch remote config and save it to local scan_rs232.json file.
    
    Args:
        device_name: Device/machine name (default: hostname)
        timeout: Request timeout in seconds (default: 10)
        verify_ssl: Verify SSL certificate (default: True)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        remote_config = fetch_remote_config(device_name, timeout, verify_ssl)
        remote_root_config = fetch_remote_root_config(device_name, timeout, verify_ssl)

        config_path = os.path.join(get_conf_path(), "scan_rs232.json")
        
        # Backup existing config
        backup_path = config_path + ".backup"
        if os.path.exists(config_path):
            import shutil
            shutil.copy2(config_path, backup_path)
        

        final_data = {
            "log_level": remote_root_config["log_level"],
            "log_retention_days": int(remote_root_config["log_retention_days"]),  # Convert to int
            "scanner_configurations": remote_config["scanner_configurations"]
        }


        with open(config_path, "w") as f:
            json.dump(final_data, f, indent=4)
        
        # Clear cached config so it reloads
        global _config
        _config = None
        
        print(f"Local config updated from remote API")
        return True
        
    except Exception as e:
        print(f"Failed to update local config: {e}")
        return False

#-------------------------------------------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    update_local_config_from_remote()