import csv

class Patient:
    # This list will hold all of the subjects loaded from the CSV
    all_patients = []

    def __init__(
        self,
        subject_id,
        sex,
        age_baseline,
        d4z4,
        dux4_signature_baseline_R,
        dux4_signature_baseline_L,
        lag_months_baseline,
        lag_months_y1,
        lag_months_y2,
        ff_baseline_R,
        ff_y1_R,
        ff_y2_R,
        ff_baseline_L,
        ff_y1_L,
        ff_y2_L,
        fvar_baseline_R,
        fvar_y1_R,
        fvar_y2_R,
        fvar_baseline_L,
        fvar_y1_L,
        fvar_y2_L,
        stir_quant_baseline_R,
        stir_quant_y1_R,
        stir_quant_baseline_L,
        stir_quant_y1_L,
        dorsiflexion_qmt_R_baseline,
        dorsiflexion_qmt_R_y1,
        dorsiflexion_qmt_R_y2,
        dorsiflexion_qmt_L_baseline,
        dorsiflexion_qmt_L_y1,
        dorsiflexion_qmt_L_y2,
        tug_time_baseline,
        tug_time_y1,
        tug_time_y2,
        wr_10_baseline,
        wr_10_y1,
        wr_10_y2,
        ascend_4_baseline,
        ascend_4_y1,
        ascend_4_y2,
        descend_4_baseline,
        descend_4_y1,
        descend_4_y2,
        clinical_severity_score_baseline,
        clinical_severity_score_y1,
        clinical_severity_score_y2,
    ):
        # Basic information about the subject
        self.subject_id = subject_id
        self.sex = sex
        self.age_baseline = age_baseline
        self.d4z4 = d4z4

        # DUX4 biomarker measurements from baseline
        self.dux4_signature_baseline_R = dux4_signature_baseline_R
        self.dux4_signature_baseline_L = dux4_signature_baseline_L

        # Actual time between visits, in months
        self.lag_months_baseline = lag_months_baseline
        self.lag_months_y1 = lag_months_y1
        self.lag_months_y2 = lag_months_y2

        # MRI fat fraction for the right tibialis anterior
        self.ff_baseline_R = ff_baseline_R
        self.ff_y1_R = ff_y1_R
        self.ff_y2_R = ff_y2_R

        # MRI fat fraction for the left tibialis anterior
        self.ff_baseline_L = ff_baseline_L
        self.ff_y1_L = ff_y1_L
        self.ff_y2_L = ff_y2_L

        # Fat fraction variability measurements
        self.fvar_baseline_R = fvar_baseline_R
        self.fvar_y1_R = fvar_y1_R
        self.fvar_y2_R = fvar_y2_R

        self.fvar_baseline_L = fvar_baseline_L
        self.fvar_y1_L = fvar_y1_L
        self.fvar_y2_L = fvar_y2_L

        # STIR measurements related to muscle inflammation
        self.stir_quant_baseline_R = stir_quant_baseline_R
        self.stir_quant_y1_R = stir_quant_y1_R
        self.stir_quant_baseline_L = stir_quant_baseline_L
        self.stir_quant_y1_L = stir_quant_y1_L

        # Right-leg dorsiflexion strength
        self.dorsiflexion_qmt_R_baseline = dorsiflexion_qmt_R_baseline
        self.dorsiflexion_qmt_R_y1 = dorsiflexion_qmt_R_y1
        self.dorsiflexion_qmt_R_y2 = dorsiflexion_qmt_R_y2

        # Left-leg dorsiflexion strength
        self.dorsiflexion_qmt_L_baseline = dorsiflexion_qmt_L_baseline
        self.dorsiflexion_qmt_L_y1 = dorsiflexion_qmt_L_y1
        self.dorsiflexion_qmt_L_y2 = dorsiflexion_qmt_L_y2

        # Timed Up and Go (TUG) test results
        self.tug_time_baseline = tug_time_baseline
        self.tug_time_y1 = tug_time_y1
        self.tug_time_y2 = tug_time_y2

        # Ten-meter walk test results
        self.wr_10_baseline = wr_10_baseline
        self.wr_10_y1 = wr_10_y1
        self.wr_10_y2 = wr_10_y2

        # Four-step ascent test results
        self.ascend_4_baseline = ascend_4_baseline
        self.ascend_4_y1 = ascend_4_y1
        self.ascend_4_y2 = ascend_4_y2

        # Four-step descent test results
        self.descend_4_baseline = descend_4_baseline
        self.descend_4_y1 = descend_4_y1
        self.descend_4_y2 = descend_4_y2

        # Clinical Severity Score
        self.clinical_severity_score_baseline = clinical_severity_score_baseline
        self.clinical_severity_score_y1 = clinical_severity_score_y1
        self.clinical_severity_score_y2 = clinical_severity_score_y2

        # Add this subject to the list of all subjects
        Patient.all_patients.append(self)

    def __repr__(self):
        # Show a few important values when printing a subject
        return (
            f"{self.subject_id}: "
            f"({self.sex} | Age = {self.age_baseline} | "
            f"Right TA Fat Fraction = {self.ff_baseline_R} | "
            f"Right Dorsiflexion = {self.dorsiflexion_qmt_R_baseline} | "
            f"TUG = {self.tug_time_baseline})"
        )

    @classmethod
    def instantiate_from_csv(cls, filename: str):
        # Read the CSV and clear the list before loading it again
        cls.all_patients = []

        with open(filename, encoding="utf8", newline="") as f:
            reader = csv.DictReader(f)
            rows_of_patients = list(reader)

        # A blank measurement should be None instead of an empty string
        # This lets us skip missing measurements when doing calculations
        def get_number(row, column):
            if row[column].strip() == "":
                return None
            return float(row[column])

        for row in rows_of_patients:
            cls(
                subject_id=row["subject_id"],
                sex=row["sex"],

                age_baseline=get_number(row, "age_baseline"),
                d4z4=get_number(row, "d4z4"),

                dux4_signature_baseline_R=get_number(
                    row, "dux4_signature_baseline_R"
                ),
                dux4_signature_baseline_L=get_number(
                    row, "dux4_signature_baseline_L"
                ),

                lag_months_baseline=get_number(
                    row, "lag_months_baseline"
                ),
                lag_months_y1=get_number(row, "lag_months_y1"),
                lag_months_y2=get_number(row, "lag_months_y2"),

                ff_baseline_R=get_number(row, "ff_baseline_R"),
                ff_y1_R=get_number(row, "ff_y1_R"),
                ff_y2_R=get_number(row, "ff_y2_R"),

                ff_baseline_L=get_number(row, "ff_baseline_L"),
                ff_y1_L=get_number(row, "ff_y1_L"),
                ff_y2_L=get_number(row, "ff_y2_L"),

                fvar_baseline_R=get_number(row, "fvar_baseline_R"),
                fvar_y1_R=get_number(row, "fvar_y1_R"),
                fvar_y2_R=get_number(row, "fvar_y2_R"),

                fvar_baseline_L=get_number(row, "fvar_baseline_L"),
                fvar_y1_L=get_number(row, "fvar_y1_L"),
                fvar_y2_L=get_number(row, "fvar_y2_L"),

                stir_quant_baseline_R=get_number(
                    row, "stir_quant_baseline_R"
                ),
                stir_quant_y1_R=get_number(
                    row, "stir_quant_y1_R"
                ),
                stir_quant_baseline_L=get_number(
                    row, "stir_quant_baseline_L"
                ),
                stir_quant_y1_L=get_number(
                    row, "stir_quant_y1_L"
                ),

                dorsiflexion_qmt_R_baseline=get_number(
                    row, "dorsiflexion_qmt_R_baseline"
                ),
                dorsiflexion_qmt_R_y1=get_number(
                    row, "dorsiflexion_qmt_R_y1"
                ),
                dorsiflexion_qmt_R_y2=get_number(
                    row, "dorsiflexion_qmt_R_y2"
                ),

                dorsiflexion_qmt_L_baseline=get_number(
                    row, "dorsiflexion_qmt_L_baseline"
                ),
                dorsiflexion_qmt_L_y1=get_number(
                    row, "dorsiflexion_qmt_L_y1"
                ),
                dorsiflexion_qmt_L_y2=get_number(
                    row, "dorsiflexion_qmt_L_y2"
                ),

                tug_time_baseline=get_number(row, "tug_time_baseline"),
                tug_time_y1=get_number(row, "tug_time_y1"),
                tug_time_y2=get_number(row, "tug_time_y2"),

                wr_10_baseline=get_number(row, "wr_10_baseline"),
                wr_10_y1=get_number(row, "wr_10_y1"),
                wr_10_y2=get_number(row, "wr_10_y2"),

                ascend_4_baseline=get_number(row, "ascend_4_baseline"),
                ascend_4_y1=get_number(row, "ascend_4_y1"),
                ascend_4_y2=get_number(row, "ascend_4_y2"),

                descend_4_baseline=get_number(row, "descend_4_baseline"),
                descend_4_y1=get_number(row, "descend_4_y1"),
                descend_4_y2=get_number(row, "descend_4_y2"),

                clinical_severity_score_baseline=get_number(
                    row, "clinical_severity_score_baseline"
                ),
                clinical_severity_score_y1=get_number(
                    row, "clinical_severity_score_y1"
                ),
                clinical_severity_score_y2=get_number(
                    row, "clinical_severity_score_y2"
                ),
            )

    @classmethod
    def filter(cls, patient_list, sex="any"):
        # This lets us look at just one group if we need to
        filtered_patients = list(patient_list)

        if sex != "any":
            new_list = []

            for patient in filtered_patients:
                if patient.sex == sex:
                    new_list.append(patient)

            filtered_patients = new_list

        return filtered_patients

