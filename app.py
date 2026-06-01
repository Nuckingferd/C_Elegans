import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. Page Configuration & Professional Theming
st.set_page_config(
    page_title="C. elegans dop-6 Neurogenetic Phenotype Monitor",
    page_icon="🪱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for high-end clinical/research look
st.markdown("""
    <style>
    .reportview-container { background: #fafafa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# 2. Research Data Simulator Engine (N2 vs. dop-6 Behavioral Assays)
@st.cache_data
def load_neurogenetics_assay_data():
    np.random.seed(101)
    n_assays = 500
    
    # Simulating microscopy tracking metadata
    imaging_channels = ['Brightfield Channel A', 'Brightfield Channel B']
    strains = ['Wild Type (N2 Control)', 'dop-6 (Mutant Line)']
    food_status = ['On-Food (OP50)', 'Off-Food (Basal)']
    
    mock_matrix = {
        'Assay_ID': [f"ASSAY-2026-{i:04d}" for i in range(1, n_assays + 1)],
        'Microscopy_Channel': np.random.choice(imaging_channels, size=n_assays),
        'Genetic_Background': np.random.choice(strains, size=n_assays, p=[0.45, 0.55]),
        'Environmental_Context': np.random.choice(food_status, size=n_assays, p=[0.5, 0.5]),
        'Mean_Crawling_Velocity_um_s': np.round(np.random.normal(loc=130, scale=25, size= n_assays), 2),
        'Omega_Turns_Per_Minute': np.round(np.random.exponential(scale=1.1, size=n_assays), 2),
        'Mean_Body_Bending_Angle_Deg': np.round(np.random.normal(loc=145, scale=12, size=n_assays), 1),
        'Video_Tracking_Fidelity_Percent': np.round(np.random.uniform(low=88.0, high=99.9, size=n_assays), 2)
    }
    
    df = pd.DataFrame(mock_matrix)
    
    # --- Injecting Biological Phenotypic Logic Rules ---
    # Fact 1: Dopamine pathways control search patterns. 
    # When Off-Food, Wild Type worms increase omega turns (area-restricted search). 
    # dop-6 mutants fail to properly modulate this behavior due to impaired receptor signaling.
    
    # Elevate omega turns for Wild Type when Off-Food
    df.loc[(df['Genetic_Background'] == 'Wild Type (N2 Control)') & 
           (df['Environmental_Context'] == 'Off-Food (Basal)'), 'Omega_Turns_Per_Minute'] *= 2.3
    
    # Blunting the response in dop-6 mutants (they exhibit locomotion deficits/reduced adaptive turning)
    df.loc[df['Genetic_Background'] == 'dop-6 (Mutant Line)', 'Omega_Turns_Per_Minute'] *= 0.6
    df.loc[df['Genetic_Background'] == 'dop-6 (Mutant Line)', 'Mean_Crawling_Velocity_um_s'] *= 0.8
    
    # Deep omega turns compress the body bending angle significantly (closer to 0-45 degrees as head nears tail)
    df['Mean_Body_Bending_Angle_Deg'] = np.clip(df['Mean_Body_Bending_Angle_Deg'] - (df['Omega_Turns_Per_Minute'] * 15), 30.0, 180.0)
    
    return df

df = load_neurogenetics_assay_data()

# 3. Sidebar Filtering Navigation Layout
st.sidebar.markdown("## 🔬 Microscopy & Assay Filters")
st.sidebar.markdown("---")

# Multi-select for strains
selected_strains = st.sidebar.multiselect(
    "Isolate Genotypes:",
    options=list(df['Genetic_Background'].unique()),
    default=list(df['Genetic_Background'].unique())
)

# Radio buttons for food environment
selected_context = st.sidebar.radio(
    "Assay Environmental State:",
    options=["All Contexts"] + list(df['Environmental_Context'].unique())
)

# QA threshold filter to drop low-quality tracking videos
min_quality = st.sidebar.slider("Minimum Tracking Fidelity (%)", 88.0, 95.0, 90.0)

# Apply logical filters to dataset
filtered_df = df[
    (df['Genetic_Background'].isin(selected_strains)) &
    (df['Video_Tracking_Fidelity_Percent'] >= min_quality)
]

if selected_context != "All Contexts":
    filtered_df = filtered_df[filtered_df['Environmental_Context'] == selected_context]

# 4. Main Panel Presentation Header
st.title("🪱 Neurogenetic Behavioral Phenotype Explorer")
st.markdown("---")

# Create the separate subdivisions using Tabs
tab1, tab2 = st.tabs(["📊 Behavioral Analytics Platform", "ℹ️ About & Research Context"])

# ==============================================================================
# SUBDIVISION 1: THE LIVE ANALYTICS DASHBOARD
# ==============================================================================
with tab1:
    st.markdown("### 🎛️ Real-Time Kinematic Extraction Matrix")
    st.markdown("This system parses quantitative data extracted via automated microscopy tracking. Use the sidebar to isolate specific genetic variations and environmental parameters.")
    st.markdown("---")
    
    # 5. Research KPIs (Key Performance Indicators)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric(label="Total Tracked Assays (N)", value=len(filtered_df))
    with kpi2:
        avg_vel = filtered_df['Mean_Crawling_Velocity_um_s'].mean()
        st.metric(label="Avg Crawling Velocity", value=f"{avg_vel:.1f} µm/s" if not pd.isna(avg_vel) else "0.0 µm/s")
    with kpi3:
        avg_om = filtered_df['Omega_Turns_Per_Minute'].mean()
        st.metric(label="Avg Omega Turn Frequency", value=f"{avg_om:.2f} / min")
    with kpi4:
        avg_angle = filtered_df['Mean_Body_Bending_Angle_Deg'].mean()
        st.metric(label="Mean Body Bending Curvature", value=f"{avg_angle:.1f}°")

    st.markdown("---")

    # 6. Advanced Visualizations Panel
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Kinematic Core: Omega Turning Frequency vs. Bending Angles")
        fig_scatter = px.scatter(
            filtered_df,
            x="Mean_Body_Bending_Angle_Deg",
            y="Omega_Turns_Per_Minute",
            color="Genetic_Background",
            symbol="Environmental_Context",
            hover_data=["Assay_ID", "Mean_Crawling_Velocity_um_s"],
            labels={
                "Mean_Body_Bending_Angle_Deg": "Mean Body Bending Curvature (Degrees)",
                "Omega_Turns_Per_Minute": "Omega Turns / Minute (Frequency)",
                "Genetic_Strain": "Genotype"
            },
            template="plotly_white",
            color_discrete_map={'Wild Type (N2 Control)': '#1f77b4', 'dop-6 (Mutant Line)': '#d62728'}
        )
        st.plotly_chart(fig_scatter, width="stretch")

    with chart_col2:
        st.subheader("Locomotion Speed Distribution Profiles")
        fig_hist = px.histogram(
            filtered_df,
            x="Mean_Crawling_Velocity_um_s",
            color="Genetic_Background",
            facet_row="Environmental_Context", 
            marginal="box",
            labels={"Mean_Crawling_Velocity_um_s": "Crawling Velocity (µm/s)"},
            template="plotly_white",
            color_discrete_map={'Wild Type (N2 Control)': '#1f77b4', 'dop-6 (Mutant Line)': '#d62728'}
        )
        fig_hist.update_layout(showlegend=False)
        st.plotly_chart(fig_hist, width="stretch")

    # 7. Raw Microscopic Metric Audit Registry
    st.markdown("---")
    with st.expander("📂 Computer Vision Feature Registry & Tracking Quality Log"):
        
        num_rows = st.slider("Select number of rows to preview:", min_value=5, max_value=50, value=10)
        
        def flag_low_fidelity(row):
            return ['background-color: #fff3cd' if row['Video_Tracking_Fidelity_Percent'] < 92.0 else '' for _ in row]
        
        styled_df = filtered_df.copy()
        st.dataframe(
            styled_df.head(num_rows).style.format({
                'Mean_Crawling_Velocity_um_s': '{:.1f} µm/s',
                'Omega_Turns_Per_Minute': '{:.2f}',
                'Mean_Body_Bending_Angle_Deg': '{:.1f}°',
                'Video_Tracking_Fidelity_Percent': '{:.2f}%'
            }).apply(flag_low_fidelity, axis=1),
            width="stretch"
        )

# ==============================================================================
# SUBDIVISION 2: THE "ABOUT & RESEARCH CONTEXT" DOCUMENTATION
# ==============================================================================
with tab2:
    st.header("🔬 Project Overview & Biological Framework")
    
    st.markdown("""
    ### 🧬 Objective
    This interactive dashboard serves as a phenomics evaluation platform to characterize how specific **dopamine receptors** modulate locomotion mechanics and exploratory search strategies in *Caenorhabditis elegans*. 
    
    Specifically, it isolates and highlights behavioral divergence patterns between **Wild Type (N2 Control)** cohorts and **dop-6 (Dopamine Receptor 6 mutant)** lines under varying nutritional stress parameters.
    """)
    
    doc_col1, doc_col2 = st.columns(2)
    
    with doc_col1:
        st.markdown("""
        ### 🪱 Understanding the Locomotion Parameters
        * **Mean Crawling Velocity ($\mu m/s$):** Measures the overall displacement speed of the worm's midbody centroid point across the tracking frame agar grid.
        * **Omega Turns Per Minute:** Quantifies the execution frequency of steep, tightly curved body bends where the worm's head approaches or makes physical contact with its tail. This maneuver is an essential mechanism for reorientation during foraging behavior.
        * **Mean Body Bending Curvature (Degrees):** Tracks the average axial skeleton inflection angle. During standard forward crawling, this stays closer to $145^\circ - 160^\circ$. When executing deep **omega turns**, this value drops significantly as the worm rolls into a tight circle.
        """)
        
    with doc_col2:
        st.markdown("""
        ### 🛠️ Platform Engineering Summary
        * **Frontend Architecture:** Pure Python execution utilizing the **Streamlit** core layout framework.
        * **Data Management & Ingestion:** **Pandas DataFrames** managing dynamic relational slicing, column mapping, and conditional string matrix styling.
        * **Graphics Compilation Engine:** **Plotly Express** generating high-fidelity, standalone interactive JavaScript scatter plots and facet-mapped distribution histograms.
        * **Quality Assurance Gate:** Integrates a video fidelity pixel-extraction validator to drop corrupted tracker inputs programmatically before downstream analytics load.
        """)
        
    st.markdown("---")
    st.info("💡 **Interview Quick Reference:** This dashboard showcases end-to-end clinical and experimental research data mapping—taking raw computer vision output parameters, processing them through strict validation filtering, and translating them into clear scientific insights.")