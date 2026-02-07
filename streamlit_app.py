import tempfile
from io import BytesIO
from pathlib import Path

import streamlit as st

from app.extractor import extract_data
from app.generator_docx import generate_docx
from app.generator_lesson_plan import generate_lesson_plan

st.set_page_config(page_title="CASL Course Document Generator", page_icon="📄", layout="wide")

# --- Header ---
st.title("CASL Course Document Generator")
st.markdown("Upload a Course Planning Excel file to extract course information and generate **Course Document** and **Lesson Plan** documents.")
st.divider()

# --- File Upload ---
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"], help="Select the .xlsx course planning file")

if uploaded_file is not None:
    st.success(f"**{uploaded_file.name}** uploaded ({uploaded_file.size / 1024:.0f} KB)")

    if st.button("Generate Documents", type="primary", use_container_width=True):
        with st.spinner("Extracting data and generating documents..."):
            # Save uploaded file to a temp location for openpyxl
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_path = Path(tmp_dir) / uploaded_file.name
                tmp_path.write_bytes(uploaded_file.getvalue())

                # Extract
                data = extract_data(tmp_path)

                # Generate Word doc into memory
                docx_path = Path(tmp_dir) / "output.docx"
                generate_docx(data, docx_path)
                docx_bytes = docx_path.read_bytes()

                # Generate Lesson Plan into memory
                lp_path = Path(tmp_dir) / "lesson_plan.docx"
                generate_lesson_plan(data, lp_path)
                lp_bytes = lp_path.read_bytes()

            safe_name = data.particulars.course_title.replace(" ", "_")

            # Store in session state so downloads persist after re-render
            st.session_state["generated"] = True
            st.session_state["docx_bytes"] = docx_bytes
            st.session_state["lp_bytes"] = lp_bytes
            st.session_state["safe_name"] = safe_name
            st.session_state["data"] = data

    # --- Show results if generated ---
    if st.session_state.get("generated"):
        data = st.session_state["data"]
        safe_name = st.session_state["safe_name"]
        docx_bytes = st.session_state["docx_bytes"]
        lp_bytes = st.session_state["lp_bytes"]

        st.divider()
        st.subheader("Downloads")

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download Course Document (.docx)",
                data=docx_bytes,
                file_name=f"{safe_name}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        with col2:
            st.download_button(
                label="Download Lesson Plan (.docx)",
                data=lp_bytes,
                file_name=f"{safe_name}_Lesson_Plan.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )

        # --- Preview extracted data ---
        st.divider()
        st.subheader("Extracted Data Preview")

        # Section 1
        with st.expander("Section 1: Course Particulars", expanded=True):
            st.markdown(f"**Training Provider:** {data.particulars.training_provider}")
            st.markdown(f"**Course Title:** {data.particulars.course_title}")
            st.markdown(f"**Course Type:** {data.particulars.course_type}")
            st.markdown(f"**Unique Skill:** {', '.join(data.particulars.unique_skill_names)}")
            st.markdown("---")
            st.markdown("**About This Course**")
            st.text(data.particulars.about_course[:500] + ("..." if len(data.particulars.about_course) > 500 else ""))
            st.markdown("**What You Will Learn**")
            st.text(data.particulars.what_youll_learn[:500] + ("..." if len(data.particulars.what_youll_learn) > 500 else ""))

        # Section 2
        with st.expander("Section 2: Course Background"):
            st.text(data.background.targeted_sectors[:500] + ("..." if len(data.background.targeted_sectors) > 500 else ""))

        # Section 3
        with st.expander("Section 3: Instructional Design"):
            st.markdown("**Learning Outcomes**")
            lo_rows = [
                {
                    "Day": lo.day,
                    "Duration (min)": lo.duration_minutes,
                    "LO#": lo.lo_number,
                    "Learning Outcome": lo.learning_outcome,
                    "Topic": lo.topic,
                }
                for lo in data.learning_outcomes
            ]
            st.dataframe(lo_rows, use_container_width=True, hide_index=True)

            st.markdown("**Instruction Methods**")
            meth_rows = [
                {
                    "Day": im.day,
                    "Method": im.method,
                    "Duration (min)": im.duration_minutes,
                    "Mode": im.mode_of_training,
                }
                for im in data.instruction_methods
            ]
            st.dataframe(meth_rows, use_container_width=True, hide_index=True)

        # Section 4
        with st.expander("Section 4: Assessment"):
            assess_rows = [
                {
                    "Day": am.day,
                    "Mode": am.mode,
                    "Duration (min)": am.duration_minutes,
                    "Assessors": am.num_assessors,
                    "Candidates": am.num_candidates,
                }
                for am in data.assessment_modes
            ]
            st.dataframe(assess_rows, use_container_width=True, hide_index=True)

        # Summary
        with st.expander("Summary"):
            st.markdown("**Topics covered in this course:**")
            for lo in data.learning_outcomes:
                st.markdown(f"- {lo.topic}")

            st.markdown("")
            unique_methods = list(dict.fromkeys(im.method for im in data.instruction_methods))
            st.markdown(f"**Instructional methods:** {', '.join(unique_methods)}")

            st.markdown("")
            st.markdown("**Duration for each topic:**")
            dur_rows = [{"Topic": lo.topic, "Duration (min)": lo.duration_minutes} for lo in data.learning_outcomes]
            st.dataframe(dur_rows, use_container_width=True, hide_index=True)

            st.markdown("")
            st.markdown(f"- **Total Course Duration:** {data.summary.total_course_duration}")
            st.markdown(f"- **Total Instructional Duration:** {data.summary.total_instructional_duration}")
            st.markdown(f"- **Total Assessment Duration:** {data.summary.total_assessment_duration}")
            st.markdown(f"- **Mode of Training:** {data.summary.mode_of_training}")
