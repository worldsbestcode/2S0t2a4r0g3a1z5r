import time
import psutil
import subprocess

from typing import Dict

from rkweb.lilmodels.base import Model, field

from rkweb.auth import login_required, perm_required
from rkweb.session import AuthSession
from rkweb.flaskutils import Blueprint, abort, respond
from rkweb.rkserver import ExcryptMsg, ServerConn

from dashboard import has_config_perm

# Blueprint
blp = Blueprint("hardware", "hardware", url_prefix="/dashboard/hardware", description="Get hardware information")
def HardwareBlueprint():
    return blp

# GET /hardware
class HardwareStats(Model):
    cpu: float = field(description="CPU usage percentage snapshot")
    memory: float = field(description="Memory usage percentage snapshot")

    disks: Dict[str, Dict[str, int]] = field(description="Data usage information for disks")
    dbSize: int = field(description="Database size in bytes")
    dirSize: Dict[str, int] = field(description="Size of data in some specific directories")

global data
data = None

global cache_time
cache_time = None

@blp.fxroute(
    endpoint="",
    method="GET",
    description="Get statistical information about the hardware",
    resp_schemas={
        200: HardwareStats,
    })
@login_required()
@perm_required("Device:Config")
async def get():
    # Check perms
    if not has_config_perm(AuthSession.get().perms):
        unauthorized("Missing device configuration permission")

    global data
    global cache_time
    # Cache results for 20 seconds
    if cache_time and cache_time < time.time() - 20:
        data = None

    if not data:
        data = {}
        data['cpu'] = float(psutil.cpu_percent(0))
        data['memory'] = float(psutil.virtual_memory().percent)
        # Disk usage for the 2 partitions
        disks = {
            '/': 'os',
            '/mnt/data': 'data',
        }
        data['disks'] = {}
        for path in disks:
            total = 0
            used = 0
            free = 0
            try:
                vals = shutil.disk_usage(path)
                total = vals.total
                used = vals.used
                free = vals.free
            except:
                pass

            data['disks'][disks[path]] = {
                'total': total,
                'used': used,
                'free': free,
            }

        # Ask the database for its size
        pg_data = []
        proc = subprocess.Popen(
                    executable="/usr/bin/psql",
                    args=["/usr/bin/psql", "rk", "-U", "futurex", "-c", "SELECT pg_database_size('rk')", "-z", "-A"],
                    stdout=subprocess.PIPE,
                )
        for line in proc.stdout:
            pg_data.append(line.decode('utf-8'))
        proc.wait()
        if len(pg_data) >= 2:
            data['dbSize'] = int(pg_data[1])
        else:
            data['dbSize'] = 0


        # Get the size of some important directories
        dirs = {
            '/rkdata': 'fxLogs',
            '/var/log': 'systemLogs',
            '/tmp': 'temp',
        }
        data['dirSizes'] = {}
        for curdir in dirs:
            du_data = []
            proc = subprocess.Popen(
                        executable="/usr/bin/du",
                        args=["/usr/bin/du", "-s", curdir],
                        stdout=subprocess.PIPE,
                    )
            for line in proc.stdout:
                du_data.append(line.decode('utf-8'))
            proc.wait()

            val = 0
            if len(du_data) > 0:
                pos = du_data[0].find("\t")
                if pos == -1:
                    val = du_data[0]
                else:
                    val = du_data[0][0:pos]
            data['dirSizes'][dirs[curdir]] = val

        cache_time = time.time()

    respond(200, data)
