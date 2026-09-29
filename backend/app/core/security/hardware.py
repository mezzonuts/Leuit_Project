import hashlib
import platform
import subprocess
import uuid
from functools import lru_cache


@lru_cache(maxsize=1)
def get_machine_fingerprint() -> str:
    """
    Generate unique hash based on hardware components (motherboard + CPU).
    Used for license binding to prevent license transfer between machines.
    """
    system = platform.system()
    raw_id = ""

    try:
        if system == "Windows":
            # Get Motherboard UUID
            uuid_cmd = subprocess.check_output(
                "wmic csproduct get uuid",
                shell=True,
                stderr=subprocess.DEVNULL,
                timeout=5
            ).decode().strip().split('\n')

            # Get CPU Processor ID
            cpu_cmd = subprocess.check_output(
                "wmic cpu get processorid",
                shell=True,
                stderr=subprocess.DEVNULL,
                timeout=5
            ).decode().strip().split('\n')

            motherboard_uuid = uuid_cmd[1].strip() if len(uuid_cmd) > 1 else ""
            cpu_id = cpu_cmd[1].strip() if len(cpu_cmd) > 1 else ""

            raw_id = f"{motherboard_uuid}_{cpu_id}"

        elif system == "Darwin":  # macOS
            cmd = "ioreg -rd1 -c IOPlatformExpertDevice | grep IOPlatformUUID"
            raw_id = subprocess.check_output(
                cmd,
                shell=True,
                stderr=subprocess.DEVNULL,
                timeout=5
            ).decode().strip().split('"')[-2]

        else:  # Linux
            try:
                with open("/etc/machine-id") as f:
                    raw_id = f.read().strip()
            except FileNotFoundError:
                # Fallback to CPU info
                with open("/proc/cpuinfo") as f:
                    for line in f:
                        if line.startswith("Serial"):
                            raw_id = line.split(":")[1].strip()
                            break

    except Exception:
        # Ultimate fallback: MAC address
        raw_id = str(uuid.getnode())

    # Return SHA256 hash of the raw identifier
    return hashlib.sha256(raw_id.strip().encode()).hexdigest()

def get_hardware_info() -> dict:
    """Get detailed hardware information for display/debugging."""
    system = platform.system()
    info = {
        "system": system,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "machine": platform.machine(),
    }

    try:
        if system == "Windows":
            info["motherboard_uuid"] = subprocess.check_output(
                "wmic csproduct get uuid", shell=True, stderr=subprocess.DEVNULL
            ).decode().strip().split('\n')[1].strip()
            info["cpu_id"] = subprocess.check_output(
                "wmic cpu get processorid", shell=True, stderr=subprocess.DEVNULL
            ).decode().strip().split('\n')[1].strip()
    except Exception:
        pass

    return info