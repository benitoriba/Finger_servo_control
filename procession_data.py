import numpy as np
import os
import matplotlib.pyplot as plt

# -----------------------------
# Load CSV from output folder
# -----------------------------
folder = "output"

# files = [f for f in os.listdir(folder) if f.endswith(".csv")]
# files.sort()

latest_file = os.path.join(folder, "20-160_10times_12-16-06.csv")
print("Reading:", latest_file)

data = np.loadtxt(latest_file, delimiter=",", skiprows=1)
initial_angle = 20
destination_angle = 160

# columns
time_col = 0
cmd_col = 1
fb_col = 2
current_col = 3

# -----------------------------
# Detect transitions 20 -> destination angle
# -----------------------------
runs = []
run_dict = {}

for i in range(1, len(data)):
    
    prev_cmd = data[i-1, cmd_col]
    curr_cmd = data[i, cmd_col]

    # detect transition 20 -> destination angle
    if prev_cmd == initial_angle and curr_cmd == destination_angle:
        
        start = i - 10
        end = i + 50

        # avoid index overflow
        if start >= 0 and end < len(data):

            segment = data[start:end].copy()

            # normalize time
            segment[:, time_col] = segment[:, time_col] - segment[0, time_col]

            runs.append(segment)

# -----------------------------
# Store runs as run1, run2...
# -----------------------------
for idx, r in enumerate(runs):
    run_name = f"run{idx+1}"
    run_dict[run_name] = r

print("Detected runs:", list(run_dict.keys()))

# -----------------------------
# Select run to plot
# -----------------------------
run = run_dict["run1"]

time = run[:, time_col]/1000
command = run[:, cmd_col]
feedback = run[:, fb_col]

# -----------------------------
# Plot a single run
# -----------------------------
plt.figure()

plt.plot(time, feedback, label="Feedback Angle")
plt.plot(time, command, 'r', label="Command Angle")

plt.xlabel("Time (s)")
plt.ylabel("Angle (deg)")
plt.title("Servo Step Response (Run 1)")
plt.legend()

plt.show()

# ---------------------------------
# Combine all runs for statistics
# ---------------------------------

runs = list(run_dict.values())
n_runs = len(runs)

time = runs[0][:,0]

feedback_matrix = np.array([r[:,2] for r in runs])
command = runs[0][:,1]

# Mean feedback response
feedback_mean = np.mean(feedback_matrix, axis=0)

# Standard deviation (error band)
feedback_std = np.std(feedback_matrix, axis=0)

upper = feedback_mean + feedback_std
lower = feedback_mean - feedback_std

# ---------------------------------
# Combined Plot std
# ---------------------------------

plt.figure()

# Command signal
plt.plot(time, command, 'r', label="Command")

# Mean feedback
plt.plot(time, feedback_mean, label="Mean Feedback")

# Error band
plt.fill_between(time, lower, upper, alpha=0.3, label="±1 std deviation")

plt.xlabel("Time (ms)")
plt.ylabel("Angle (deg)")
plt.title("Servo Step Response (Mean and Variability)")
plt.legend()

plt.show()

# ---------------------------------
# Step response metrics table generation
# ---------------------------------

def compute_metrics(run):

    t = run[:,0]
    cmd = run[:,1]
    fb = run[:,2]

    initial = cmd[0]
    final = cmd[-1]

    step = final - initial

    y10 = initial + 0.1*step
    y90 = initial + 0.9*step

    # Rise time
    t10 = None
    t90 = None

    for i in range(len(fb)):
        if t10 is None and fb[i] >= y10:
            t10 = t[i]
        if t90 is None and fb[i] >= y90:
            t90 = t[i]

    rise_time = t90 - t10 if (t10 is not None and t90 is not None) else np.nan

    # Overshoot
    peak = np.max(fb)
    overshoot = (peak - final) / step * 100

    # Settling time (±2%)
    band = 0.02 * abs(step)

    settling_time = np.nan

    for i in range(len(fb)):
        if np.all(np.abs(fb[i:] - final) <= band):
            settling_time = t[i]
            break

    return rise_time, settling_time, overshoot


print("\nStep Response Metrics")
print("Run\tRiseTime(ms)\tSettlingTime(ms)\tOvershoot(%)")

for name, run in run_dict.items():

    rise, settle, over = compute_metrics(run)

    print(f"{name}\t{rise:.2f}\t\t{settle:.2f}\t\t\t{over:.2f}")

# ---------------------------------
# Mean and 95% confidence interval
# ---------------------------------

feedback_mean = np.mean(feedback_matrix, axis=0)

feedback_std = np.std(feedback_matrix, axis=0)

n_runs = feedback_matrix.shape[0]

# Standard error of the mean
sem = feedback_std / np.sqrt(n_runs)

# 95% confidence interval
ci95 = 1.96 * sem

upper = feedback_mean + ci95
lower = feedback_mean - ci95

# ---------------------------------
# Combined Plot 95% 
# ---------------------------------

plt.figure()

plt.plot(time, command, 'r', label="Command")
plt.plot(time, feedback_mean, label="Mean Feedback")

plt.fill_between(time, lower, upper, alpha=0.3, label="95% confidence interval")

plt.xlabel("Time (ms)")
plt.ylabel("Angle (deg)")
plt.title("Servo Step Response (Mean ±95% CI)")
plt.legend()

plt.show()

# ---------------------------------
# Combine all runs max and min
# ---------------------------------

runs = list(run_dict.values())
n_runs = len(runs)

time = runs[0][:,0]

feedback_matrix = np.array([r[:,2] for r in runs])
command = runs[0][:,1]

# Mean feedback response
feedback_mean = np.mean(feedback_matrix, axis=0)

# Max Feedback response
feedback_max = np.max(feedback_matrix, axis=0)

# Min Feedback response
feedback_min = np.min(feedback_matrix, axis=0)

upper = feedback_max
lower = feedback_min
print ('the number of runs are:', len(runs))
print ('the maximun angle deviation in dregrees is:', max(upper-lower))

# ---------------------------------
# Combined Plot 
# ---------------------------------

plt.figure()

# Command signal
plt.plot(time, command, 'r', label="Command")

# Mean feedback
plt.plot(time, feedback_mean, label="Mean Feedback")

# Error band
plt.fill_between(time, lower, upper, alpha=0.3, label="Max and Min values")

plt.xlabel("Time (ms)")
plt.ylabel("Angle (deg)")
plt.title("Servo Step Response (Mean and Variability)")
plt.legend()

plt.show()