from datetime import datetime
import platform
import re
import socket
import subprocess
import time

from influxdb import InfluxDBClient


class PsByProcess:
    def __init__(self,
                 host='127.0.0.1',
                 port=8086,
                 username='root',
                 password='root',
                 database='stats_by_process'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.interval = 1
        self.cpu_proc_count = 10
        self.mem_proc_count = 10
        self.hostname = socket.gethostname()
        self.ps_cmd = 'ps -eo pid,ppid,%mem,%cpu'
        if platform.system() == 'Darwin':
            self.ps_cmd += ',command'
        else:
            self.ps_cmd += ',cmd'
        self.re = re.compile(r"""
            (?P<PID>\d+)
            \s+
            (?P<PPID>\d+)
            \s+
            (?P<MEM>[.0-9]+)
            \s+
            (?P<CPU>[.0-9]+)
            \s+
            (?P<PROC>.*)
            """,
            re.VERBOSE
        )

    @property
    def client(self):
        if not hasattr(self, '_client'):
            self._client = InfluxDBClient(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                database=self.database,
            )
            self._client.create_database(self.database)
        return self._client

    def get_ps_stats(self):
        """
        Run ps and get top X processes consuming CPU and memory.
        """
        out = subprocess.run(
            self.ps_cmd.split(),
            stdout=subprocess.PIPE,
        )
        lines = out.stdout.decode().split('\n')

        stats = []
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.lower().startswith('pid'):
                # header line, move on
                continue

            match = self.re.match(line)
            if not match:
                continue

            stats.append({
                'pid': int(match.group('PID')),
                'ppid': int(match.group('PPID')),
                'mem': float(match.group('MEM')),
                'cpu': float(match.group('CPU')),
                'proc': match.group('PROC'),
            })

        return stats

    def get_point_for_stat(self, stat, field):
        """
        Return stat data in format correct for influxdb.

        >>> json_body = [
            {
                "measurement": "cpu",
                "tags": {
                    "hostname": "web12",
                    "process": "/srv/app/uwsgi"
                },
                "time": "2009-11-10T23:00:00Z",
                "fields": {
                    "value": 0.64
                }
            }
        ]
        """
        now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        return {
            "measurement": field,
            "tags": {
                "hostname": self.hostname,
                "pid": stat['pid'],
                "ppid": stat['ppid'],
                "process": stat['proc'][:50],
            },
            "time": now,
            "fields": {
                "value": stat[field],
            }
        }

    def get_points_for_stats(self, stats):
        points = []
        cpu = sorted(stats, key=lambda d: d['cpu'], reverse=True)[:self.cpu_proc_count]
        for stat in cpu:
            points.append(self.get_point_for_stat(stat, 'cpu'))

        mem = sorted(stats, key=lambda d: d['mem'], reverse=True)[:self.mem_proc_count]
        for stat in mem:
            points.append(self.get_point_for_stat(stat, 'mem'))

        return points

    def run(self):
        try:
            while True:
                stats = self.get_ps_stats()
                points = self.get_points_for_stats(stats)
                self.client.write_points(points)
                time.sleep(self.interval)
        except KeyboardInterrupt:
            return


if __name__ == '__main__':
    PsByProcess().run()

