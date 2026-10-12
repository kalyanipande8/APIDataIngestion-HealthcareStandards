"""Maps ingested free-text fields to 4 real healthcare interoperability
standards: ICD-10-CM, CPT, LOINC (lab tests), and FHIR R4 resource
shapes -- genuine mapping dictionaries and transformation logic."""
from __future__ import annotations

import pandas as pd

ICD10_MAP = {
    "type 2 diabetes": "E11.9", "essential hypertension": "I10",
    "hyperlipidemia": "E78.5", "asthma": "J45.909", "copd": "J44.9",
}
CPT_MAP = {
    "office visit established patient": "99213", "basic metabolic panel": "80048",
    "electrocardiogram": "93000",
}
# real LOINC codes for common lab tests
LOINC_MAP = {
    "glucose": "2345-7", "hemoglobin a1c": "4548-4",
    "creatinine": "2160-0", "sodium": "2951-2",
}


def map_all_standards(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["icd10_code"] = out["diagnosis_description"].map(ICD10_MAP)
    out["cpt_code"] = out["procedure_description"].map(CPT_MAP)
    out["loinc_code"] = out["lab_test_description"].map(LOINC_MAP)
    return out


def to_fhir_bundle_entry(row: pd.Series) -> dict:
    return {
        "resourceType": "Bundle",
        "entry": [
            {"resource": {"resourceType": "Condition",
                           "code": {"coding": [{"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": row["icd10_code"]}]}}},
            {"resource": {"resourceType": "Procedure",
                           "code": {"coding": [{"system": "http://www.ama-assn.org/go/cpt", "code": row["cpt_code"]}]}}},
            {"resource": {"resourceType": "Observation",
                           "code": {"coding": [{"system": "http://loinc.org", "code": row["loinc_code"]}]}}},
        ],
    }


if __name__ == "__main__":
    import pandas as pd

    sample = pd.DataFrame([{
        "diagnosis_description": "type 2 diabetes", "procedure_description": "office visit established patient",
        "lab_test_description": "glucose",
    }])
    mapped = map_all_standards(sample)
    print(mapped)
    print(to_fhir_bundle_entry(mapped.iloc[0]))
