from pathlib import Path
import json, os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from engine import pre_score_tests
from bedrock_client import invoke_bedrock, parse_json_response

BASE = Path(__file__).resolve().parent
load_dotenv(BASE / ".env")

st.set_page_config(page_title="TCoE Regression Skill Demo", page_icon="🧪", layout="wide")
st.title("AI-Native TCoE Demo — Regression Selection Skill")
st.caption("Agent reasons • SKILL.md standardizes • inventory grounds • Tosca/manual testers execute")

skill_text = (BASE/"skills"/"select-regression-tests"/"SKILL.md").read_text()
inventory = pd.read_csv(BASE/"data"/"test_inventory.csv")
default_change = json.loads((BASE/"data"/"change_event.json").read_text())

with st.sidebar:
    st.header("Runtime")
    live = st.toggle("Use live Amazon Bedrock", value=False)
    region = st.text_input("AWS Region", os.getenv("AWS_REGION","us-east-1"))
    profile = st.text_input("AWS Profile (optional)", os.getenv("AWS_PROFILE",""))
    model_id = st.text_input("Bedrock model / inference profile", os.getenv("BEDROCK_MODEL_ID","global.anthropic.claude-sonnet-4-5-20250929-v1:0"))
    st.caption("Leave Live Bedrock off for rehearsal mode.")

st.subheader("1. Change event")
a,b,c = st.columns([1,1,2])
change_id = a.text_input("Change ID", default_change["change_id"])
business_process = b.text_input("Business process", default_change["business_process"])
component = c.text_input("Changed component", default_change["changed_component"])
description = st.text_area("Change description", default_change["description"], height=90)
change_event = {"change_id":change_id,"business_process":business_process,"changed_component":component,"description":description}

st.subheader("2. Regression inventory")
edited = st.data_editor(inventory, use_container_width=True, hide_index=True, num_rows="dynamic")
scored = pre_score_tests(edited, " ".join(change_event.values()))

with st.expander("Show SKILL.md"):
    st.code(skill_text, language="markdown")
with st.expander("Show transparent deterministic pre-score"):
    st.dataframe(scored[["test_id","process","criticality","execution_type","historical_defects","financial_impact","pre_score","keyword_overlap"]], use_container_width=True, hide_index=True)

st.subheader("3. Build regression pack")
if st.button("Analyze change and select tests", type="primary", use_container_width=True):
    try:
        if live:
            raw = invoke_bedrock(skill_text, change_event, scored, region, model_id, profile or None)
            result = parse_json_response(raw)
        else:
            result = json.loads((BASE/"data"/"sample_output.json").read_text())

        selected = result.get("selected_tests",[])
        result_map = {x["test_id"]:x for x in selected}
        pack = edited[edited["test_id"].isin(result_map.keys())].copy()
        pack["ai_reason"] = pack["test_id"].map(lambda x: result_map[x]["reason"])
        pack["ai_risk_score"] = pack["test_id"].map(lambda x: result_map[x]["risk_score"])
        pack["execution_route"] = pack["test_id"].map(lambda x: result_map[x]["execution_route"])

        st.success("Regression pack generated")
        x1,x2,x3,x4 = st.columns(4)
        x1.metric("Overall risk", result.get("overall_risk",""))
        x2.metric("Selected tests", len(pack))
        x3.metric("Coverage gaps", len(result.get("coverage_gaps",[])))
        x4.metric("Confidence", f'{float(result.get("confidence",0))*100:.0f}%')

        st.markdown("#### Executive recommendation")
        st.write(result.get("executive_summary",""))
        st.markdown("#### Impacted processes")
        st.write(" → ".join(result.get("impacted_processes",[])))

        st.markdown("#### Selected regression pack")
        st.dataframe(pack[["test_id","process","description","criticality","execution_type","ai_risk_score","execution_route","ai_reason"]], use_container_width=True, hide_index=True)

        auto_pack = pack[pack["execution_route"].isin(["TOSCA","HYBRID"])]
        manual_pack = pack[pack["execution_route"].isin(["MANUAL","HYBRID"])]

        l,r = st.columns(2)
        with l:
            st.markdown("#### Tosca execution-ready")
            st.dataframe(auto_pack[["test_id","process","description","ai_reason"]], use_container_width=True, hide_index=True)
            st.download_button("Download Tosca pack", auto_pack.to_csv(index=False).encode(), file_name=f"{change_id}_tosca_pack.csv", mime="text/csv")
        with r:
            st.markdown("#### Manual execution-ready")
            st.dataframe(manual_pack[["test_id","process","description","ai_reason"]], use_container_width=True, hide_index=True)
            st.download_button("Download manual pack", manual_pack.to_csv(index=False).encode(), file_name=f"{change_id}_manual_pack.csv", mime="text/csv")

        if result.get("coverage_gaps"):
            st.markdown("#### Coverage gaps / recommended new tests")
            st.dataframe(pd.DataFrame(result["coverage_gaps"]), use_container_width=True, hide_index=True)

        with st.expander("Deferred tests"):
            st.dataframe(pd.DataFrame(result.get("deferred_tests",[])), use_container_width=True, hide_index=True)

        if result.get("human_review_required"):
            st.warning("Human review required before execution/release decision because the change affects high-risk financial controls.")
    except Exception as e:
        st.error(str(e))
        st.info("Turn Live Bedrock off to use the supplied sample response.")
