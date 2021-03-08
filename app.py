import sshtunnel
import os
import stat
import calendar
from datetime import datetime, timedelta
import pysftp
from zipfile import ZipFile
import time
from pathlib import Path
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

startTime = datetime.now()

############### Configuration ################

priv_key = config['keys']['private_key']
jh = config['servers']['netact_jh']
netact_ip = config['servers']['netact_ip']
jh_username = config['usernames']['jh_username']
netact_username = config['usernames']['netact_username']
netact_pwd = config['passwords']['netact_pwd']
localhost = config['servers']['localhost']
path_a = config['paths']['path_a']
path_b = config['paths']['path_b']
local_path = Path(config['paths']['local_path'])


current_date = datetime.now().date()
current_month = datetime.now().month
mont_abbr = calendar.month_abbr[current_month]

start_date = (current_date - timedelta(days=7)).strftime('%d-%m')
end_date = current_date.strftime('%d-%m')

current_files = []

with sshtunnel.open_tunnel(
        (jh, 22),
        ssh_username=jh_username,
        ssh_pkey=priv_key,
        remote_bind_address=(netact_ip, 22),
        local_bind_address=('0.0.0.0', 10022)
) as tunnel:
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection(host=localhost, username=netact_username, password=netact_pwd, port=10022, cnopts=cnopts) as sftp:
        print("Connection succesfully established...\n")
        sftp.chdir(path_a)
        for file in sftp.listdir(path_a):
            if "old_stats" not in file:
                ts = sftp.stat(path_a + file).st_mtime
                mod_ts = datetime.fromtimestamp(ts).date() # strip timestamp from datetime object
                if mod_ts == current_date:
                    current_files.append(file)
                    sftp.get(remotepath= path_a + file, localpath = Path.joinpath(local_path, file))
        for file in sftp.listdir(path_b):
            ts = sftp.stat(path_b + file).st_mtime
            mod_ts = datetime.fromtimestamp(ts).date() # strip timestamp from datetime object
            if mod_ts == current_date:
                current_files.append(file)
                sftp.get(remotepath= path_b + file, localpath = Path.joinpath(local_path, file))
    sftp.close()

for kpi in current_files:
    print("Today's files are: ", kpi)

os.chdir(local_path)

# Fix change of month to write day/previous_month - day/next_month
kpizip = start_date + '_' + end_date + '.zip'

with ZipFile(kpizip, 'w') as zipObj2:
    zipObj2.write(current_files[0])
    zipObj2.write(current_files[1])
    zipObj2.write(current_files[2])
    zipObj2.write(current_files[3])

print(kpizip + " created")

print(datetime.now() - startTime)
