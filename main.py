import os
import re
import sys
from datetime import datetime
from collections import defaultdict


print("""
\033[96m
___________.__               .__  .__                
\\__    ___/|__| _____   ____ |  | |__| ____   ____   
  |    |   |  |/     \\_/ __ \\|  | |  |/    \\_/ __ \\  
  |    |   |  |  Y Y  \\  ___/|  |_|  |   |  \\  ___/  
  |____|   |__|__|_|  /\\___  >____/__|___|  /\\___  > 
                \\/     \\/             \\/     \\/  
\033[92m        https://github.com/Ahmed0or1
\033[0m
""")

def extract_datetime(line):
    match = re.match(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', line)
    if match:
        return match.group(1)
    return None

if len(sys.argv) != 2:
    print("Usage: python Timeline.py <folder>")
    sys.exit(1)

folder_path = sys.argv[1]
file_order = ["auth.log", "firewall.log", "workstations.log"]

events_summary = []
timeline = []

# Read and analyze logs
for log_name in file_order:
    path = os.path.join(folder_path, log_name)
    if not os.path.exists(path):
        print(f"[!] File not found: {log_name}")
        continue

    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        first_time = None
        last_time = None
        for line in lines:
            time_str = extract_datetime(line)
            if time_str:
                if not first_time:
                    first_time = time_str
                last_time = time_str

                if "Failed password" in line or "authentication failure" in line:
                    events_summary.append((time_str, log_name, "Authentication failure"))
                elif "session opened" in line:
                    events_summary.append((time_str, log_name, "Session opened"))
                elif "denied" in line:
                    events_summary.append((time_str, log_name, "Access denied"))
                elif "permitted" in line:
                    events_summary.append((time_str, log_name, "Access permitted"))
                elif "A process has exited" in line:
                    events_summary.append((time_str, log_name, "Process exited"))
                elif "A new process has been created" in line:
                    events_summary.append((time_str, log_name, "Process created"))
                elif "account failed to log on" in line.lower():
                    events_summary.append((time_str, log_name, "Account login failed"))

        if first_time and last_time:
            timeline.append((first_time, f"{first_time[-8:]} – {log_name} begins"))
            timeline.append((last_time, f" {last_time[-8:]}  – {log_name} ends"))

# Sort and group
timeline.sort(key=lambda x: x[0])
events_summary.sort(key=lambda x: x[0])

event_counts = defaultdict(int)
for time_str, _, event in events_summary:
    timestamp = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
    key = (timestamp.strftime("%Y-%m-%dT%H:%M:%S"), event)
    event_counts[key] += 1

# Build output
output = []
output.append("Timeline\n")
if timeline:
    output.append(f"• Start: {timeline[0][1]} ")
    output.append(f"• End:   {timeline[-1][1]}")
else:
    output.append("No valid timestamps found.")




previous_time = None
seen_set = set()

for time_str, log, event in events_summary:
    timestamp = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
    date_only = timestamp.strftime("%Y-%m-%d")
    time_only = timestamp.strftime("%H:%M:%S")
    key = (timestamp.strftime("%Y-%m-%dT%H:%M:%S"), event)

    if key in seen_set:
        continue
    seen_set.add(key)

    delta = f"+{str(timestamp - previous_time)}" if previous_time else ""
    count_display = f"(x{event_counts[key]})" if event_counts[key] > 1 else ""

    line = "{date:<12} | {time:<10} | {file:<18} | {event:<22} | {delta:<10} | {count}".format(
        date=date_only,
        time=time_only,
        file=log.replace(".log", ""),
        event=event,
        delta=delta,
        count=count_display
    )
    output.append("→ " + line)
    previous_time = timestamp

# Save to file
output_path = os.path.join(folder_path, "Timeline.txt")
with open(output_path, "w") as f:
    for line in output:
        f.write(line + "\n")

print(f"\n\033[92m Timeline saved to: {output_path}\033[0m")

# Color output to terminal
print("\n\033[96mTimeline Summary\033[0m")
print(f"\033[92m• Start: {timeline[0][1]}")
print(f"• End: {timeline[-1][1]}\033[0m")
print("\033[97m" + "_" * 100)
print(f"{  'Date':<12}   | {'Time':<10} | {'File':<18} | {'Event':<22} | {'+Delta':<10} | Count")
print("_" * 100 + "\033[0m")

for line in output[5:]:
    if line.startswith("→"):
        if "auth" in line:
            print(f"\033[92m{line}\033[0m")  # Green
        elif "firewall" in line:
            print(f"\033[91m{line}\033[0m")  # Red
        elif "workstations" in line:
            print(f"\033[94m{line}\033[0m")  # Blue
        else:
            print(line)
    else:
        print(line)

