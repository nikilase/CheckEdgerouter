import sys

import paramiko
from paramiko.client import SSHClient
from influxdb import InfluxDBClient
from apscheduler.schedulers.blocking import BlockingScheduler

try:
    from config.config import SshConf as SSH
    from config.config import InfluxConf as INF
except ImportError as e:
    print("Please configure your config file before running this app!")
    raise e


def get_data(printing: bool = False) -> list[list[float]]:

    with SSHClient() as client:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        client.connect(
            SSH.HOST, port=SSH.PORT, username=SSH.USER, password=SSH.PASSWORD
        )

        # Get Memory info
        _, stdout, _ = client.exec_command(
            'egrep "MemTotal|MemFree|Available" /proc/meminfo'
        )
        mem_lines = stdout.read().decode().strip().split("\n")

        # Get Storage info
        _, stdout, _ = client.exec_command("df -h /")
        storage_lines = stdout.read().decode().strip().split("\n")

    mem = []
    for line in mem_lines:
        line = float(line.strip().split(":")[1].strip().split(" ")[0].strip())
        mem.append(line)
    mem_total, mem_free, mem_available = mem
    if printing:
        print("Memory")
        print(f"Total {mem_total / 1024:.1f}MB")
        print(f"Free {mem_free / mem_total * 100:.1f}%")
        print(f"Available {mem_available / mem_total * 100:.1f}%\n")

    size_line = storage_lines[1].split()
    storage_size = float(size_line[1].strip().replace("M", ""))
    storage_used = float(size_line[2].strip().replace("M", ""))
    storage_free = float(size_line[3].strip().replace("M", ""))
    storage_percent = float(size_line[4].strip().replace("%", ""))
    storage = [
        storage_size,
        storage_used,
        storage_free,
        storage_percent,
    ]
    if printing:
        print("Storage")
        print(f"Total {storage_size}MB")
        print(f"Used {storage_used}MB")
        print(f"Free {storage_free}MB")
        print(f"Used {storage_percent}%\n")

    return mem, storage


def send_influx(mem: list[float], stor: list[float]):
    points = []
    body = {
        "measurement": INF.MSRMT,
        "fields": {
            "mem_total": mem[0],
            "mem_free": mem[1],
            "mem_available": mem[2],
            "mem_avail_percent": mem[2] / mem[0] * 100,
            "storage_size": stor[0],
            "storage_used": stor[1],
            "storage_free": stor[2],
            "storage_free_percent": 100 - stor[3],
        },
        "tags": {"location": SSH.TAG_LOCATION, "mac": SSH.TAG_MAC},
    }
    points.append(body)

    client = InfluxDBClient(
        host=INF.HOST,
        port=INF.PORT,
        username=INF.USER,
        password=INF.PASSWORD,
        ssl=INF.SSL,
        verify_ssl=INF.VERIFY_SSL,
        database=INF.DB,
    )
    client.write_points(points)
    client.close()


def task():
    mem, stor = get_data(True)
    send_influx(mem, stor)


def main():
    try:
        scheduler = BlockingScheduler()
        scheduler.add_job(task, "cron", minute="0/1")

        scheduler.start()
    except KeyboardInterrupt:
        print("Shutting down from Keyboard Interrupt!")
        sys.exit()


if __name__ == "__main__":
    main()
