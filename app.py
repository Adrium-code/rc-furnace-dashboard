import streamlit as st
import pandas as pd
import plotly.express as px
PASSWORD = st.secrets["admin_password"]

# bearing degradation influence weights

VIBRATION_WEIGHT = 0.8
TEMPERATURE_WEIGHT = 0.6
OPERATING_HOURS_WEIGHT = 0.4

st.set_page_config(
    page_title="RC Furnace Fan Dashboard",
    page_icon="⚙",
    layout="wide"
)
if "activity_log" not in st.session_state:

    st.session_state.activity_log = []

# page configuration
st.set_page_config(
    page_title="RC Fan Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# sticky top fan selector styling
st.markdown("""
<style>

div[data-testid="stVerticalBlock"] div:has(> div.sticky-container) {
    position: sticky;
    top: 0;
    background-color: #0e1117;
    z-index: 999;
    padding-top: 10px;
    padding-bottom: 10px;
}

.sticky-container {
    background-color: #0e1117;
}

</style>
""", unsafe_allow_html=True)
# dashboard title
st.title("RC Furnace Fan Monitoring Dashboard")

# load dataset
df = pd.read_csv("rc_fan_realistic_maintenance_dataset.csv")

# fan selection buttons
fan_list = df["Fan ID"].unique()
top_col1, top_col2 = st.columns([1, 1])

top_col1, top_col2 = st.columns([1, 1])

with st.expander(" Risk & Health Standards for the Furnace Fan"):

    col1, col2, col3 = st.columns(3)

    with col1:

        st.caption("""
        #### 🟢 Low Risk

        - Vibration < 2.5 mm/s
        - Bearing Temp < 70°C
        - Current < 23.5 A
        - Health > 90
        """)
        st.markdown("---")
        st.markdown("""
        :green[Healthy condition.]
        """)

    with col2:

        st.caption("""
        #### 🟠 Moderate Risk

        - Vibration = 2.5–4 mm/s
        - Bearing Temp = 70–78°C
        - Current = 23.5–25 A
        - Health = 78–90
        """)
        st.markdown("---")
        st.markdown("""
        :orange[Early degradation signs.]
        """)

    with col3:

        st.caption("""
        #### 🔴 High Risk

        - Vibration > 4 mm/s
        - Bearing Temp > 78°C
        - Current > 25 A
        - Health < 78
        """)
        st.markdown("---")
        st.markdown("""
        :red[Maintenance required.]
        """)

with st.sidebar:

    st.subheader("Admin Access")

    entered_password = st.text_input(
        "Enter Password",
        type="password"
        
    )

    authorized = entered_password == PASSWORD

    st.subheader("Recent Activities")

    if st.session_state.activity_log:

        for activity in reversed(
            st.session_state.activity_log[-5:]
        ):

            st.caption(activity)

    else:

        st.caption("No recent activities.")

    st.markdown("---")

    with st.expander("➕ Add Inspection"):

        with st.form("inspection_form"):

            fan_id = st.selectbox(
                "Fan ID",
                df["Fan ID"].unique()
            )

            inspection_date = st.date_input(
                "Inspection Date"
            )

            vib_x = st.number_input(
                "Vibration X (mm/s)",
                value=2.0
            )

            vib_y = st.number_input(
                "Vibration Y (mm/s)",
                value=2.0
            )

            bearing_temp = st.number_input(
                "Bearing Temp (°C)",
                value=65.0
            )

            furnace_temp = st.number_input(
                "Furnace Temp (°C)",
                value=910.0
            )

            rpm = st.number_input(
                "RPM",
                value=1478.0
            )

            current = st.number_input(
                "Motor Current (A)",
                value=23.0
            )

            power = st.number_input(
                "Power Consumption (kW)",
                value=15.5
            )

            operating_hours = st.number_input(
                "Operating Hours",
                value=1000
            )

            submitted = st.form_submit_button(
                "Submit Inspection Data"
            )

            if submitted:

                if not authorized:

                    st.error(
                        "Incorrect admin password."
                    )

                else:

                    health = (
                        100
                        - max(0, (vib_x - 2.4) * 7)
                        - max(0, (vib_y - 2.4) * 7)
                        - max(0, (bearing_temp - 70) * 1.3)
                        - max(0, (current - 23.8) * 5)
                    )

                    health = round(
                        max(62, min(98, health)),
                        1
                    )

                    degradation_score = (

                        (
                            (vib_x + vib_y) * 10
                        )
                        * VIBRATION_WEIGHT

                        +

                        (
                            max(0, bearing_temp - 50)
                        )
                        * TEMPERATURE_WEIGHT

                        +

                        (
                            operating_hours / 1000
                        )
                        * OPERATING_HOURS_WEIGHT
                    )

                    remaining_life = max(

                        1,

                        int(36 - degradation_score)

                    )

                    remaining_life = (
                        f"{remaining_life} months"
                    )

                    if health >= 90:

                        risk = "Low"

                    elif health >= 78:

                        risk = "Moderate"

                    else:

                        risk = "High"

                    next_maintenance = (
                        pd.Timestamp.today()
                        + pd.Timedelta(days=180)
                    )

                    new_row = {
                        "Date": inspection_date,
                        "Fan ID": fan_id,
                        "Furnace Temp (°C)": furnace_temp,
                        "Vibration X (mm/s)": vib_x,
                        "Vibration Y (mm/s)": vib_y,
                        "Bearing Temp (°C)": bearing_temp,
                        "RPM": rpm,
                        "Motor Current (A)": current,
                        "Power Consumption (kW)": power,
                        "Operating Hours": operating_hours,
                        "Health Score (%)": health,
                        "Risk Level": risk,
                        "Maintenance Performed": "No",
                        "Predicted Remaining Life": remaining_life,
                        "Next Maintenance Date": next_maintenance.strftime("%Y-%m-%d")
                    }

                    df = pd.concat(
                        [df, pd.DataFrame([new_row])],
                        ignore_index=True
                    )

                    df.to_csv(
                        "rc_fan_realistic_maintenance_dataset.csv",
                        index=False
                    )

                    st.session_state.activity_log.append(
                        f"Inspection added for {fan_id}"
                    )

                    st.success(
                        "New inspection data added successfully!"
                    )

selected_fan = st.session_state.get(
    "selected_fan",
    None
)

with st.sidebar:

    st.markdown("---")

    st.subheader("Recent Inspection Entries")

    history_view = st.radio(
        "View History",
        ["Fan-wise", "Chronological"],
        horizontal=True
    )

    if history_view == "Fan-wise":

        if selected_fan is not None:

            recent_entries = (
                df[df["Fan ID"] == selected_fan]
                .tail(10)
            )

        else:

            recent_entries = pd.DataFrame()

    else:

        recent_entries = df.tail(10)

    if not recent_entries.empty:

        recent_entries = recent_entries[[
            "Date",
            "Fan ID",
            "Health Score (%)",
            "Risk Level"
        ]]

        recent_entries.index = (
            recent_entries.index + 1
        )

        st.table(recent_entries)

        st.markdown("---")

        if "edit_mode" not in st.session_state:
          st.session_state.edit_mode = False

        if st.button("✏ Edit Recent Entry"):
           st.session_state.edit_mode = True
        
        if authorized:
          if st.session_state.edit_mode:

              editable_df = df.tail(5).copy()

              editable_df.index = (
                 editable_df.index + 1
               )

              edit_options = []

              for idx, row in editable_df.iterrows():

                  option = (
                      f"{idx} | "
                      f"{row['Date']} | "
                      f"{row['Fan ID']}"
                  )

                  edit_options.append(option)

              selected_option = st.selectbox(
                  "Select Entry",
                  edit_options
              )

              selected_index = int(
                  selected_option.split("|")[0].strip()
              ) - 1

              selected_entry = df.loc[selected_index]

              edit_furnace = st.number_input(
                  "Furnace Temp (°C)",
                  value=float(
                      selected_entry[
                          "Furnace Temp (°C)"
                      ]
                  ),
                  key="edit_ft"
              )

              edit_vx = st.number_input(
                  "Vibration X (mm/s)",
                  value=float(
                      selected_entry[
                          "Vibration X (mm/s)"
                      ]
                  ),
                  key="edit_vx"
              )

              edit_vy = st.number_input(
                  "Vibration Y (mm/s)",
                  value=float(
                      selected_entry[
                          "Vibration Y (mm/s)"
                      ]
                  ),
                  key="edit_vy"
              )

              edit_bearing = st.number_input(
                  "Bearing Temp (°C)",
                  value=float(
                      selected_entry[
                          "Bearing Temp (°C)"
                      ]
                  ),
                  key="edit_bt"
              )

              edit_rpm = st.number_input(
                  "RPM",
                  value=float(
                      selected_entry["RPM"]
                  ),
                  key="edit_rpm"
              )

              edit_current = st.number_input(
                  "Motor Current (A)",
                  value=float(
                      selected_entry[
                          "Motor Current (A)"
                      ]
                  ),
                  key="edit_current"
              )

              edit_power = st.number_input(
                  "Power Consumption (kW)",
                  value=float(
                      selected_entry[
                          "Power Consumption (kW)"
                      ]
                  ),
                  key="edit_power"
              )

              edit_hours = st.number_input(
                  "Operating Hours",
                  value=float(
                      selected_entry[
                          "Operating Hours"
                      ]
                  ),
                  key="edit_hours"
              )

              col_save, col_cancel = st.columns(2)

              save_clicked = col_save.button(
                  "Save Edited Entry"
              )

              cancel_clicked = col_cancel.button(
                  "Cancel"
              )

              if cancel_clicked:

                  st.session_state.edit_mode = False
                  st.rerun()

              if save_clicked:

                  health = (
                      100
                      - max(0, (edit_vx - 2.4) * 7)
                      - max(0, (edit_vy - 2.4) * 7)
                      - max(
                          0,
                          (edit_bearing - 70)
                          * 1.3
                      )
                      - max(
                          0,
                          (edit_current - 23.8)
                          * 5
                      )
                  )

                  health = round(
                      max(62, min(98, health)),
                      1
                  )

                  if health >= 90:

                      risk = "Low"
                      remaining_life = "24 months"

                  elif health >= 78:

                      risk = "Moderate"
                      remaining_life = "12 months"

                  else:

                      risk = "High"
                      remaining_life = "6 months"

                  df.at[
                      selected_index,
                      "Furnace Temp (°C)"
                  ] = edit_furnace

                  df.at[
                      selected_index,
                      "Vibration X (mm/s)"
                  ] = edit_vx

                  df.at[
                      selected_index,
                      "Vibration Y (mm/s)"
                  ] = edit_vy

                  df.at[
                      selected_index,
                      "Bearing Temp (°C)"
                  ] = edit_bearing

                  df.at[
                      selected_index,
                      "RPM"
                  ] = edit_rpm

                  df.at[
                      selected_index,
                      "Motor Current (A)"
                  ] = edit_current

                  df.at[
                      selected_index,
                      "Power Consumption (kW)"
                  ] = edit_power

                  df.at[
                      selected_index,
                      "Operating Hours"
                  ] = edit_hours

                  df.at[
                      selected_index,
                      "Health Score (%)"
                  ] = health

                  df.at[
                      selected_index,
                      "Risk Level"
                  ] = risk

                  df.at[
                      selected_index,
                      "Predicted Remaining Life"
                  ] = remaining_life

                  df.to_csv(
                      "rc_fan_realistic_maintenance_dataset.csv",
                      index=False
                  )
                  st.session_state.activity_log.append(
                    f"Entry edited for {selected_entry['Fan ID']}"
                  )

                  st.success(
                      "Entry updated successfully!"
                  )

                  st.rerun()

    else:

        st.info(
            "Select a fan to view fan-wise history."
        )

st.markdown('<div class="sticky-container">', unsafe_allow_html=True)

st.subheader("RC Fan Status Overview")
st.write("")

cols = st.columns(len(fan_list))



for i, fan in enumerate(fan_list):

    latest_fan = df[df["Fan ID"] == fan].iloc[-1]

    risk = latest_fan["Risk Level"]

    if risk == "Low":
        color = "green"

    elif risk == "Moderate":
        color = "orange"

    else:
        color = "red"

    with cols[i]:

        st.markdown(
            f"""
            <div style="
                border: {"6px" if selected_fan == fan else "3px"} solid {color};
                box-shadow: {"0 0 6px " + color if selected_fan == fan else "none"};
                transform: scale({"1.22" if selected_fan == fan else "1"});
                transition: 0.3s;
                border-radius: 12px;
                padding: 20px;
                text-align: center;
                font-weight: bold;
                font-size: 20px;
            ">
                {fan}
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
         "Close" if selected_fan == fan else "Select",
         key=fan,
         use_container_width=True
        ):

         if selected_fan == fan:
             st.session_state["selected_fan"] = None

         else:
             st.session_state["selected_fan"] = fan
         st.rerun()

selected_fan = st.session_state.get(
    "selected_fan",
    None
)
st.markdown("</div>", unsafe_allow_html=True)
if selected_fan is None:

    st.info("Select an RC Fan to view monitoring data.")

    st.stop()

st.markdown("---")

# filter selected fan
fan_data = df[df["Fan ID"] == selected_fan].reset_index(drop=True)

fan_data.index = fan_data.index + 1

# latest row
latest = fan_data.iloc[-1]

# top status cards
col1, col2, col3 = st.columns([1.2, 1.2, 1.2])

risk = latest["Risk Level"]

if risk == "Low":
    card_color = "#00c853"

elif risk == "Moderate":
    card_color = "#ff9800"

else:
    card_color = "#ff5252"

card_style = f"""
background-color: #111827;
padding: 10px;
border-radius: 12px;
border: 3px solid {card_color};
box-shadow: 0 0 6px {card_color};
text-align: center;
max-width: 310px;
min-height: 120px;
margin: auto;
font-size: 16px;
"""

with col1:

    st.markdown(
        f"""
        <div style="{card_style}">
            <h5>Health Score</h5>
            <h3 style="color:{card_color};">
            {latest['Health Score (%)']}%
            </h3>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:

    st.markdown(
        f"""
        <div style="{card_style}">
            <h5>Risk Level</h5>
            <h3 style="color:{card_color};">
            {latest['Risk Level']}
            </h3>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:

    st.markdown(
        f"""
        <div style="{card_style}">
            <h5>Remaining Life</h5>
            <h3 style="color:{card_color};">
            {latest['Predicted Remaining Life']}
            </h3>
        </div>
        """,
        unsafe_allow_html=True
    )

# maintenance information

next_inspection = (
    pd.Timestamp.today()
    + pd.Timedelta(days=7)
).strftime("%Y-%m-%d")

st.write("")

col4, col5 = st.columns(2)

with col4:

    st.info(
        f"Next Maintenance Date :  "
        f"{latest['Next Maintenance Date']}"
    )

with col5:

    st.info(
        f"Next Inspection Date :  "
        f"{next_inspection}"
    )

st.write("")

st.markdown("---")

if st.button("🔧 Mark Maintenance Done"):

    latest_index = df[
        df["Fan ID"] == selected_fan
    ].index[-1]

    df.at[
        latest_index,
        "Maintenance Status"
    ] = "Completed"

    df.at[
        latest_index,
        "Health Score (%)"
    ] = 98

    df.at[
        latest_index,
        "Risk Level"
    ] = "Low"

    df.at[
        latest_index,
        "Predicted Remaining Life"
    ] = "24 months"

    df.to_csv(
        "rc_fan_realistic_maintenance_dataset.csv",
        index=False
    )
    
    st.session_state.activity_log.append(
        f"Maintenance completed for {selected_fan}"
    )

    st.success(
        f"{selected_fan} maintenance marked completed!"
    )

    st.rerun()
st.markdown("---")

# health score graph
st.subheader("Health Score Trend")

fig3 = px.line(
    fan_data,
    x="Date",
    y="Health Score (%)",
    title="Health Score Over Time",
    markers=True
)

fig3.add_hline(
    y=90,
    line_dash="dash",
    line_color="green",
    annotation_text="Healthy Zone"
)

fig3.add_hline(
    y=78,
    line_dash="dash",
    line_color="orange",
    annotation_text="Risk Threshold"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

st.markdown("---")
# bearing temperature graph
st.subheader("Bearing Temperature Trend")

fig2 = px.line(
    fan_data,
    x="Date",
    y="Bearing Temp (°C)",
    title="Bearing Temperature Over Time",
    markers=True
)

fig2.add_hline(
    y=70,
    line_dash="dash",
    line_color="orange",
    annotation_text="Warning Limit"
)

fig2.add_hline(
    y=78,
    line_dash="dash",
    line_color="red",
    annotation_text="Critical Limit"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.markdown("---")
# vibration graph
st.subheader("Vibration Trend")

fig1 = px.line(
    fan_data,
    x="Date",
    y=[
        "Vibration X (mm/s)",
        "Vibration Y (mm/s)"
    ],
    title="Vibration Trend Over Time",
    markers=True
)

fig1.add_hline(
    y=2.5,
    line_dash="dash",
    line_color="orange",
    annotation_text="Warning Limit"
)

fig1.add_hline(
    y=4,
    line_dash="dash",
    line_color="red",
    annotation_text="Critical Limit"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


st.markdown("---")
# motor current graph
st.subheader("Motor Current Trend")

fig4 = px.line(
    fan_data,
    x="Date",
    y="Motor Current (A)",
    title="Motor Current Over Time",
    markers=True
)

fig4.add_hline(
    y=23.5,
    line_dash="dash",
    line_color="orange",
    annotation_text="Warning Limit"
)

fig4.add_hline(
    y=25,
    line_dash="dash",
    line_color="red",
    annotation_text="Critical Limit"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)
st.markdown("---")
# inspection table
st.subheader(f"{selected_fan} Inspection Data")
st.dataframe(fan_data)


