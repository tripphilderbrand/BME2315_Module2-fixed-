from pathlib import Path
from module2patient import Patient
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy import stats


# Find the CSV in the same folder as this Python file
csv_path = Path(__file__).resolve().parent / "Module2_FSHD_Dataset (1).csv"

# Load all subjects from the CSV
Patient.instantiate_from_csv(str(csv_path))

print("Number of subjects =", len(Patient.all_patients))

# Print a few subjects to make sure the data loaded
for patient in Patient.all_patients[:5]:
    print(patient)


# Interpolation chunk for right tibialis anterior fat fraction,
# right-leg dorsiflexion strength, and TUG
# This will also give us a new CSV that we can use later


# Find the common comparison times for everyone
year1_times = []
year2_times = []

for patient in Patient.all_patients:
    if patient.lag_months_y1 is not None:
        year1_times.append(patient.lag_months_y1)

    if patient.lag_months_y2 is not None:
        year2_times.append(patient.lag_months_y2)

T1 = min(year1_times)
T2 = min(year2_times)

print(f"\nCommon Year 1 time: {T1:.2f} months")
print(f"Common Year 2 time: {T2:.2f} months")


# Estimate a value at a common time using a straight line
def linear_interpolation(times, values, target_time):

    times = np.array(times, dtype=float)
    values = np.array(values, dtype=float)

    # Ignore visits where the time or measurement is missing
    valid = np.isfinite(times) & np.isfinite(values)
    times = times[valid]
    values = values[valid]

    if len(times) < 2:
        return np.nan

    # Put the visits in order
    order = np.argsort(times, kind="stable")
    times = times[order]
    values = values[order]

    # If two visits have the same recorded time, keep the first one
    # so the interpolation uses different time points
    unique_times, indices = np.unique(times, return_index=True)
    times = unique_times
    values = values[indices]

    if len(times) < 2:
        return np.nan

    # Do not estimate outside the available measurements
    if target_time < times[0] or target_time > times[-1]:
        return np.nan

    line = interp1d(times, values, kind="linear")
    return float(line(target_time))


# Work through each subject and estimate all three measurements
results = []

for patient in Patient.all_patients:

    # Actual visit times for this subject
    times = [
        patient.lag_months_baseline,
        patient.lag_months_y1,
        patient.lag_months_y2
    ]

    # Keep the real baseline measurements separate from the estimates
    result = {
        "subject_id": patient.subject_id,

        "fat_fraction_baseline": patient.ff_baseline_R,
        "fat_fraction_linear_T1": linear_interpolation(
            times,
            [patient.ff_baseline_R, patient.ff_y1_R, patient.ff_y2_R],
            T1
        ),
        "fat_fraction_linear_T2": linear_interpolation(
            times,
            [patient.ff_baseline_R, patient.ff_y1_R, patient.ff_y2_R],
            T2
        ),

        "dorsiflexion_baseline": patient.dorsiflexion_qmt_R_baseline,
        "dorsiflexion_linear_T1": linear_interpolation(
            times,
            [
                patient.dorsiflexion_qmt_R_baseline,
                patient.dorsiflexion_qmt_R_y1,
                patient.dorsiflexion_qmt_R_y2
            ],
            T1
        ),
        "dorsiflexion_linear_T2": linear_interpolation(
            times,
            [
                patient.dorsiflexion_qmt_R_baseline,
                patient.dorsiflexion_qmt_R_y1,
                patient.dorsiflexion_qmt_R_y2
            ],
            T2
        ),

        "tug_baseline": patient.tug_time_baseline,
        "tug_linear_T1": linear_interpolation(
            times,
            [
                patient.tug_time_baseline,
                patient.tug_time_y1,
                patient.tug_time_y2
            ],
            T1
        ),
        "tug_linear_T2": linear_interpolation(
            times,
            [
                patient.tug_time_baseline,
                patient.tug_time_y1,
                patient.tug_time_y2
            ],
            T2
        )
    }

    results.append(result)


# Put all the estimates into a table so we can use them later
interpolated = pd.DataFrame(results)

print("\nExample interpolation results:")
print(interpolated.head())


# Calculate changes from baseline and average rates per year
measures = ["fat_fraction", "dorsiflexion", "tug"]

for measure in measures:

    baseline_column = f"{measure}_baseline"

    # Baseline is 0% change, as long as the baseline measurement exists
    # A zero baseline cannot be used to calculate percentage change
    baseline_values = interpolated[baseline_column].replace(0, np.nan)

    interpolated[f"{measure}_percent_change_baseline"] = np.where(
        baseline_values.notna(),
        0.0,
        np.nan
    )

    for timepoint, months in [("T1", T1), ("T2", T2)]:

        estimate_column = f"{measure}_linear_{timepoint}"
        change_column = f"{measure}_change_{timepoint}"
        rate_column = f"{measure}_rate_{timepoint}_per_year"
        percent_column = f"{measure}_percent_change_{timepoint}"

        # Change is the estimate minus the baseline measurement
        interpolated[change_column] = (
            interpolated[estimate_column] - interpolated[baseline_column]
        )

        # Divide by elapsed time in years
        interpolated[rate_column] = (
            interpolated[change_column] / (months / 12)
        )

        # Calculate percentage change for the point/line graphs
        interpolated[percent_column] = (
            (interpolated[estimate_column] - baseline_values)
            / baseline_values * 100
        )


# Print a simple summary of the changes
print("\nMean and median changes from baseline")

for measure in measures:

    print(f"\n{measure.replace('_', ' ').title()}")

    for timepoint in ["T1", "T2"]:

        changes = interpolated[
            f"{measure}_change_{timepoint}"
        ].dropna()

        rates = interpolated[
            f"{measure}_rate_{timepoint}_per_year"
        ].dropna()

        print(
            f"{timepoint}: n = {len(changes)}, "
            f"mean change = {changes.mean():.2f}, "
            f"median change = {changes.median():.2f}, "
            f"mean rate per year = {rates.mean():.2f}"
        )


# Save the estimates so we can use the same data later
output_path = (
    Path(__file__).resolve().parent
    / "Module2_interpolation_results.csv"
)

interpolated.to_csv(output_path, index=False)

print(f"\nSaved interpolation results to: {output_path}")


# Analysis A: Fat fraction change vs. TUG change

# Compare the average annual rate of change from baseline
# TUG is measured in seconds, so a positive change means a longer time


analysis_A_data = {}

print("\nAnalysis A: Fat fraction vs. TUG")

for timepoint in ["T1", "T2"]:

    fat_column = f"fat_fraction_rate_{timepoint}_per_year"
    tug_column = f"tug_rate_{timepoint}_per_year"

    # Only use subjects who have both measurements
    analysis_data = interpolated[
        [fat_column, tug_column]
    ].replace([np.inf, -np.inf], np.nan).dropna()

    fat_change = analysis_data[fat_column].to_numpy()
    tug_change = analysis_data[tug_column].to_numpy()

    n = len(analysis_data)

    if (
        n >= 3
        and len(np.unique(fat_change)) > 1
        and len(np.unique(tug_change)) > 1
    ):

        # Pearson and Spearman correlations
        pearson_r, pearson_p = stats.pearsonr(
            fat_change, tug_change
        )

        spearman_r, spearman_p = stats.spearmanr(
            fat_change, tug_change
        )

        # Linear regression
        slope, intercept, r_value, p_value, standard_error = stats.linregress(
            fat_change, tug_change
        )

        r_squared = r_value ** 2

        print(
            f"{timepoint}: n = {n}, "
            f"Pearson r = {pearson_r:.3f}, p = {pearson_p:.4f}, "
            f"Spearman rho = {spearman_r:.3f}, "
            f"p = {spearman_p:.4f}, "
            f"slope = {slope:.3f}, R2 = {r_squared:.3f}, "
            f"SE = {standard_error:.3f}"
        )

        analysis_A_data[timepoint] = (
            fat_change, tug_change, slope, intercept
        )

    else:
        print(f"{timepoint}: n = {n}, not enough usable data for testing")


# Scatter plot for Analysis A: show T1 and T2 together
plt.figure(figsize=(8, 5))

for timepoint, color, marker in [
    ("T1", "C0", "o"),
    ("T2", "C1", "s")
]:

    if timepoint in analysis_A_data:

        fat_change, tug_change, slope, intercept = analysis_A_data[timepoint]

        plt.scatter(
            fat_change,
            tug_change,
            color=color,
            marker=marker,
            label=f"{timepoint} (n={len(fat_change)})"
        )

        # Add a trend line for each time point
        line_x = np.linspace(
            min(fat_change), max(fat_change), 100
        )
        line_y = intercept + slope * line_x

        plt.plot(line_x, line_y, color=color)

plt.xlabel("Fat Fraction Change (percentage points/year)")
plt.ylabel("TUG Time Change (seconds/year)")
plt.title("Fat Fraction Change vs. TUG Change")
plt.axhline(y=0, linestyle="--", alpha=0.5)
plt.axvline(x=0, linestyle="--", alpha=0.5)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()


# Point/line graph for Analysis A: average percentage change over time
time_labels = [
    "Baseline",
    f"T1 ({T1:.1f} months)",
    f"T2 ({T2:.1f} months)"
]

fat_means = [
    interpolated["fat_fraction_percent_change_baseline"].mean(),
    interpolated["fat_fraction_percent_change_T1"].mean(),
    interpolated["fat_fraction_percent_change_T2"].mean()
]

tug_means = [
    interpolated["tug_percent_change_baseline"].mean(),
    interpolated["tug_percent_change_T1"].mean(),
    interpolated["tug_percent_change_T2"].mean()
]

plt.figure(figsize=(8, 5))
plt.plot(time_labels, fat_means, marker="o", label="Right TA fat fraction")
plt.plot(time_labels, tug_means, marker="s", label="TUG time")
plt.xlabel("Time")
plt.ylabel("Mean change from baseline (%)")
plt.title("Fat Fraction and TUG Changes Over Time")
plt.axhline(y=0, linestyle="--", alpha=0.5)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()


# Analysis B: Fat fraction change vs. dorsiflexion strength change

# Compare the average annual rate of change from baseline
# A negative dorsiflexion change means strength has decreased


analysis_B_data = {}

print("\nAnalysis B: Fat fraction vs. dorsiflexion strength")

for timepoint in ["T1", "T2"]:

    fat_column = f"fat_fraction_rate_{timepoint}_per_year"
    strength_column = f"dorsiflexion_rate_{timepoint}_per_year"

    # Only use subjects who have both measurements
    analysis_data = interpolated[
        [fat_column, strength_column]
    ].replace([np.inf, -np.inf], np.nan).dropna()

    fat_change = analysis_data[fat_column].to_numpy()
    strength_change = analysis_data[strength_column].to_numpy()

    n = len(analysis_data)

    if (
        n >= 3
        and len(np.unique(fat_change)) > 1
        and len(np.unique(strength_change)) > 1
    ):

        # Pearson and Spearman correlations
        pearson_r, pearson_p = stats.pearsonr(
            fat_change, strength_change
        )

        spearman_r, spearman_p = stats.spearmanr(
            fat_change, strength_change
        )

        # Linear regression
        slope, intercept, r_value, p_value, standard_error = stats.linregress(
            fat_change, strength_change
        )

        r_squared = r_value ** 2

        print(
            f"{timepoint}: n = {n}, "
            f"Pearson r = {pearson_r:.3f}, p = {pearson_p:.4f}, "
            f"Spearman rho = {spearman_r:.3f}, "
            f"p = {spearman_p:.4f}, "
            f"slope = {slope:.3f}, R2 = {r_squared:.3f}, "
            f"SE = {standard_error:.3f}"
        )

        analysis_B_data[timepoint] = (
            fat_change, strength_change, slope, intercept
        )

    else:
        print(f"{timepoint}: n = {n}, not enough usable data for testing")


# Scatter plot for Analysis B: show T1 and T2 together
plt.figure(figsize=(8, 5))

for timepoint, color, marker in [
    ("T1", "C0", "o"),
    ("T2", "C1", "s")
]:

    if timepoint in analysis_B_data:

        fat_change, strength_change, slope, intercept = analysis_B_data[timepoint]

        plt.scatter(
            fat_change,
            strength_change,
            color=color,
            marker=marker,
            label=f"{timepoint} (n={len(fat_change)})"
        )

        # Add a trend line for each time point
        line_x = np.linspace(
            min(fat_change), max(fat_change), 100
        )
        line_y = intercept + slope * line_x

        plt.plot(line_x, line_y, color=color)

plt.xlabel("Fat Fraction Change (percentage points/year)")
plt.ylabel("Dorsiflexion Strength Change (units/year)")
plt.title("Fat Fraction Change vs. Dorsiflexion Change")
plt.axhline(y=0, linestyle="--", alpha=0.5)
plt.axvline(x=0, linestyle="--", alpha=0.5)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()


# Point/line graph for Analysis B: average percentage change over time

strength_means = [
    interpolated["dorsiflexion_percent_change_baseline"].mean(),
    interpolated["dorsiflexion_percent_change_T1"].mean(),
    interpolated["dorsiflexion_percent_change_T2"].mean()
]

plt.figure(figsize=(8, 5))
plt.plot(time_labels, fat_means, marker="o", label="Right TA fat fraction")
plt.plot(time_labels, strength_means, marker="s", label="Right dorsiflexion strength")
plt.xlabel("Time")
plt.ylabel("Mean change from baseline (%)")
plt.title("Fat Fraction and Dorsiflexion Changes Over Time")
plt.axhline(y=0, linestyle="--", alpha=0.5)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

