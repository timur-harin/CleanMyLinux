import os
import subprocess
import shutil
import time

import psutil

import gi
import subprocess
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


os.system("sudo -S apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 glade pip clamav clamav-daemon -y")
os.system("pip install psutil")

def remove_files(files_to_remove):
    ind = 1
    print("The following files can be removed:")
    for file in files_to_remove:
        print(f'{ind}. {file}')
        ind += 1
    user_input = input(
        "What files should be deleted? Print 0, you want to remove all files, -1 if nothing should be deleted."
        "In other case list indexes of files to be deleted and put commas between them.")
    user_input = user_input.replace(" ", "")
    files = user_input.split(',')
    if files[0] == '-1':
        return
    elif files[0] == '0':
        for index in range(len(files_to_remove)):
            try:
                if os.path.isfile(files_to_remove[index]):
                    os.remove(files_to_remove[index])
                elif os.path.isdir(files_to_remove[index]):
                    shutil.rmtree(files_to_remove[int(index)])
            except:
                print(f"Couldn't remove file {files_to_remove[index]}")
    else:
        for file in files:
            try:
                index = int(file) - 1
                if os.path.isfile(files_to_remove[index]):
                    os.remove(files_to_remove[index])
                elif os.path.isdir(files_to_remove[index]):
                    shutil.rmtree(files_to_remove[index])
            except:
                print(f"Couldn't remove file {files_to_remove[int(file) - 1]}")


def remove_junk():
    # Create a list of files to be removed
    files_to_remove = []
    # Add old kernels to the list
    output = subprocess.check_output(["sudo", "apt-get", "autoremove", "--dry-run", "-y"])
    for line in output.decode().split("\n"):
        if line.startswith("Removing") and "/boot" in line:
            files_to_remove.append(line.split()[-1])
    # Add unused packages to the list
    output = subprocess.check_output(["sudo", "apt-get", "clean", "--dry-run", "-y"])
    for line in output.decode().split("\n"):
        if line.startswith("Cleaning") and "/var/cache/apt/archives" in line:
            files_to_remove.append(line.split()[-1])
    # Add temporary files to the list
    files_to_remove.append("/tmp")
    remove_files(files_to_remove)


file_extensions = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".jpg", ".jpeg", ".png",
                   ".gif", ".mp3", ".mp4", ".avi", ".mov", ".zip", ".tar", ".gz"]


def is_old_file(path):
    """
            Returns True if the file at `path` has not been accessed within the
            threshold time, False otherwise.
            """
    try:
        access_time = os.path.getatime(path)
        file_info = os.stat(path)
        now = time.time()
        return (now - access_time) > 2592000 and path.endswith(tuple(file_extensions))
    except:
        return False


def remove_old_files(path):
    exclude_list = ['/var', '/usr', '/etc/passwd', '/etc/shadow', '/snap']

    deletable_files = []
    for root, dirs, files in os.walk(path):
        # Exclude files in the exclude list
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in exclude_list]
        files[:] = [f for f in files if os.path.join(root, f) not in exclude_list]

        for name in files:
            file_path = os.path.join(root, name)
            if is_old_file(file_path) and '/snap/' not in file_path and '/.' not in file_path:
                deletable_files.append(file_path)
    remove_files(deletable_files)


def remove_malware():
    # Scan for malware using Clam Antivirus
    scan_result = None
    try:
        scan_result = subprocess.check_output(['clamscan', '-r', '/'], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = e.output
        print(output)


    if scan_result is not None:
        # Parse the scan result to get a list of infected files
        infected_files = []
        for line in scan_result.splitlines():
            if 'FOUND' in str(line):
                infected_files.append(str(line).split(': ')[0])

        # Remove any infected files
        for file_path in infected_files:
            try:
                os.remove(file_path)
            except:
                print(f'Cannot remove infected file: {file_path}')


def tune_system():
    try:
        # Optimize using preload
        subprocess.run(["sudo", "systemctl", "enable", "--now", "preload"])

        # Clear caches and thumbnail folders
        subprocess.run(["rm", "-rf", "~/.cache"])
        subprocess.run(["rm", "-rf", "~/.thumbs"])

        # Remove junks
        remove_junk()

    except Exception:
        print("Trying to kill zombie processes...")
    
    # Kill zombie processes
    processes = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    output, error = processes.communicate()

    lines = output.splitlines()
    for line in lines:
        if 'Z' in str(line):
            # Get the PID of the zombie process
            pid = int(line.split(None, 1)[0])
            # Kill the zombie process
            subprocess.call(['kill', '-9', str(pid)])

    # Benchmark the system
    # ...


def monitor_system():
    # Monitor CPU usage
    print("CPU usage:", psutil.cpu_percent())

    # Monitor memory usage
    print("Memory usage:", psutil.virtual_memory().percent)

    # Monitor disk usage
    print("Disk usage:", psutil.disk_usage('/').percent)

    # Analyze system logs
    # ...



builder = Gtk.Builder()
builder.add_from_file("window.glade")

class GUI:
    def __init__(self):

        self.builder = builder
        self.builder.connect_signals(self)
        
        self.cache_button = self.builder.get_object("cache_button")
        self.old_button = self.builder.get_object("old_button")
        self.speed_button = self.builder.get_object("speed_button")
        self.malware_button = self.builder.get_object("malware_button")
        
        self.cache_button.connect("clicked", self.clear_cache)
        self.old_button.connect("clicked", self.remove_old)
        self.speed_button.connect("clicked", self.speed_up)
        self.malware_button.connect("clicked", self.check_malware)
        
        self.window = self.builder.get_object("main_window")
        self.window.show_all()

    def clear_cache(self, button):
        remove_junk()

        print("Cleared cache")

    def remove_old(self, button):
        remove_old_files('/')
        print("Removed old files")

    def speed_up(self, button):
        tune_system()
        print("Speed up")

    def check_malware(self, button):
        remove_malware()
        print("Checking malware")

try:
   gui = GUI()
   Gtk.main()
except KeyboardInterrupt:
   print('Program finished')
