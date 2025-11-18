from datetime import datetime
import xml.etree.ElementTree as ET

def build_ccd(patient, allergies, meds, problems, immunizations, procedures,
              vitals, encounters, labs, imaging, careplans):
    
    root = ET.Element("ClinicalDocument", {
        "xmlns": "urn:hl7-org:v3",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance"
    })

    # ---------------- HEADER ---------------- #
    ET.SubElement(root, "typeId", {
        "root": "2.16.840.1.113883.1.3",
        "extension": "POCD_HD000040"
    })

    ET.SubElement(root, "id", {"root": f"CCD-{patient.get('id')}"} )

    ET.SubElement(root, "effectiveTime").text = datetime.now().strftime("%Y%m%d%H%M%S")

    record_target = ET.SubElement(root, "recordTarget")
    patient_role = ET.SubElement(record_target, "patientRole")

    # Patient ID
    ET.SubElement(patient_role, "id", {"extension": str(patient.get("id", ""))})

    # Address
    addr = ET.SubElement(patient_role, "addr")
    addr.text = patient.get("address", "Unknown")

    # Patient Info
    p = ET.SubElement(patient_role, "patient")
    ET.SubElement(p, "name").text = patient.get("name", "Unknown")
    ET.SubElement(p, "administrativeGenderCode", {"code": patient.get("gender", "U")})
    ET.SubElement(p, "birthTime", {
        "value": patient.get("dob", "").replace("-", "") if patient.get("dob") else ""
    })

    # ============================================================
    # GENERIC SAFE SECTION BUILDER TO PREVENT ALL FUTURE KEYERRORS
    # ============================================================

    def create_section(code, title, items):
        sec = ET.SubElement(root, "section")

        ET.SubElement(sec, "code", {
            "code": code,
            "codeSystem": "2.16.840.1.113883.6.1"
        })

        ET.SubElement(sec, "title").text = title

        for item_dict in items:
            entry = ET.SubElement(sec, "entry")

            # Add every field dynamically
            for key, value in item_dict.items():
                ET.SubElement(entry, key).text = str(value or "")

        return sec

    # ---------------- Build All Sections (SAFE) ---------------- #

    create_section("48765-2", "Allergies", allergies)
    create_section("10160-0", "Medications", meds)
    create_section("11450-4", "Problem List", problems)
    create_section("11369-6", "Immunizations", immunizations)
    create_section("47519-4", "Procedures", procedures)
    create_section("8716-3", "Vitals", vitals)
    create_section("46240-8", "Encounters", encounters)
    create_section("30954-2", "Labs", labs)
    create_section("18748-4", "Radiology", imaging)
    create_section("18776-5", "Care Plans", careplans)

    # ---------------- RETURN XML STRING ---------------- #

    return ET.tostring(root, encoding="unicode")

import xml.dom.minidom

def pretty_xml(xml_string: str) -> str:
    """Formats XML with indentation."""
    dom = xml.dom.minidom.parseString(xml_string)
    return dom.toprettyxml(indent="  ")