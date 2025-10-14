import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from construction_ai import ConstructionAnalyzer

# Page configuration
st.set_page_config(
    page_title="Construction Progress AI - Offline",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .offline-badge {
        background: #4CAF50;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .stage-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 5px solid;
        background: #f8f9fa;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize session state
    if 'ai_model' not in st.session_state:
        st.session_state.ai_model = ConstructionAnalyzer()
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = st.session_state.ai_model.get_analysis_history()
    
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<h1 class="main-header">🏗️ Construction Progress AI</h1>', unsafe_allow_html=True)
        st.markdown('<div style="text-align: center;"><span class="offline-badge">OFFLINE MODE</span></div>', unsafe_allow_html=True)
        st.markdown("### *Automated Construction Monitoring Desktop Application*")
    
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Project Settings")
        project_name = st.text_input("Project Name", "Construction Site Alpha")
        project_location = st.text_input("Location", "Mumbai, India")
        project_manager = st.text_input("Project Manager", "John Doe")
        
        st.header("📊 Data Management")
        if st.button("🔄 Clear History"):
            if os.path.exists('construction_data/analysis_history.csv'):
                os.remove('construction_data/analysis_history.csv')
                st.session_state.analysis_history = pd.DataFrame()
                st.success("History cleared!")
        
        if st.button("📁 Export All Data"):
            export_all_data()
        
        st.header("ℹ️ About")
        st.info("""
        This is an **offline** construction progress monitoring system.
        
        **Features:**
        • No internet required
        • Local data storage
        • Real-time analysis
        • Progress tracking
        """)
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Image Analysis")
        
        # Image upload
        uploaded_file = st.file_uploader(
            "Upload Construction Site Image",
            type=['jpg', 'jpeg', 'png'],
            help="Select a clear image of the construction site"
        )
        
        # Live camera (optional)
        use_camera = st.checkbox("🎥 Use Camera (if available)")
        camera_image = None
        if use_camera:
            camera_file = st.camera_input("Take construction site photo")
            if camera_file:
                uploaded_file = camera_file
        
        # Stage selection
        selected_stage = st.selectbox(
            "Expected Construction Stage",
            options=['site-prep', 'foundation', 'superstructure', 'façade', 'interiors'],
            index=2,
            help="Select what stage you expect to see in the image"
        )
        
        # Analyze button
        analyze_btn = st.button("🚀 Analyze Construction Progress", type="primary", use_container_width=True)
    
    with col2:
        st.subheader("📊 Live Dashboard")
        
        if uploaded_file and analyze_btn:
            # Process image
            image = Image.open(uploaded_file)
            image_array = np.array(image)
            
            # Display image
            st.image(image, caption="Uploaded Construction Image", use_column_width=True)
            
            # Analyze with progress
            with st.spinner('🤖 AI is analyzing construction progress...'):
                progress_bar = st.progress(0)
                for i in range(100):
                    # Simulate processing steps
                    progress_bar.progress(i + 1)
                
                # Perform analysis
                result = st.session_state.ai_model.analyze_construction(
                    image_array, selected_stage, project_name
                )
            
            # Display results
            if 'error' in result:
                st.error(f"**Analysis Error:** {result['error']}")
            else:
                display_results(result)
                
                # Export option
                if st.button("💾 Save Report"):
                    filename = st.session_state.ai_model.export_report(result)
                    st.success(f"Report saved: {filename}")
        
        elif not uploaded_file:
            st.info("👆 Upload a construction site image to begin analysis")
    
    # History Section
    st.markdown("---")
    st.subheader("📋 Analysis History")
    
    if not st.session_state.analysis_history.empty:
        # Display history table
        st.dataframe(st.session_state.analysis_history, use_container_width=True)
        
        # Progress chart
        st.subheader("📈 Progress Timeline")
        plot_progress_chart(st.session_state.analysis_history)
        
        # Statistics
        st.subheader("📊 Project Statistics")
        display_statistics(st.session_state.analysis_history)
    else:
        st.info("No analysis history yet. Upload images to build history.")

def display_results(result):
    """Display analysis results"""
    st.success("✅ Analysis Complete!")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Detected Stage", result['detected_stage'].upper())
    with col2:
        st.metric("Confidence", f"{result['confidence']:.1%}")
    with col3:
        st.metric("Progress", result['progress_range'])
    with col4:
        status_emoji = "✅" if result['status'] == 'VALID' else "⚠️"
        st.metric("Status", f"{status_emoji} {result['status']}")
    
    # Elements found
    st.subheader("🔧 Detected Elements")
    if result['elements_found']:
        for element in result['elements_found']:
            st.markdown(f"- **{element.replace('-', ' ').title()}**")
    else:
        st.write("No specific elements detected")
    
    # Technical metrics
    st.subheader("🔬 Technical Analysis")
    metrics = result['technical_metrics']
    tech_cols = st.columns(len(metrics))
    for idx, (key, value) in enumerate(metrics.items()):
        with tech_cols[idx]:
            st.metric(key.replace('_', ' ').title(), value)
    
    # AI Insights
    st.subheader("💡 AI Insights")
    st.info(result['message'])

def plot_progress_chart(history_df):
    """Plot progress chart"""
    if len(history_df) > 1:
        # Convert stages to numerical values for plotting
        stage_order = ['site-prep', 'foundation', 'superstructure', 'façade', 'interiors']
        history_df['stage_numeric'] = history_df['detected_stage'].map(
            {stage: i for i, stage in enumerate(stage_order)}
        )
        
        # Create progress chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=history_df['timestamp'],
            y=history_df['stage_numeric'],
            mode='lines+markers',
            name='Construction Progress',
            line=dict(color='#1f77b4', width=4),
            marker=dict(size=8, color='#ff7f0e')
        ))
        
        fig.update_layout(
            title="Construction Progress Over Time",
            xaxis_title="Date & Time",
            yaxis_title="Construction Stage",
            yaxis=dict(
                tickvals=list(range(len(stage_order))),
                ticktext=[s.upper() for s in stage_order]
            ),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Need more data points to show progress chart")

def display_statistics(history_df):
    """Display project statistics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_analyses = len(history_df)
        st.metric("Total Analyses", total_analyses)
    
    with col2:
        avg_confidence = history_df['confidence'].mean() if 'confidence' in history_df.columns else 0
        st.metric("Avg Confidence", f"{avg_confidence:.1%}")
    
    with col3:
        if 'detected_stage' in history_df.columns:
            current_stage = history_df['detected_stage'].iloc[-1] if len(history_df) > 0 else 'Unknown'
            st.metric("Current Stage", current_stage.upper())
    
    with col4:
        valid_analyses = len(history_df[history_df['status'] == 'VALID']) if 'status' in history_df.columns else 0
        st.metric("Valid Analyses", valid_analyses)

def export_all_data():
    """Export all data to ZIP"""
    import zipfile
    from datetime import datetime
    
    zip_filename = f"construction_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for root, dirs, files in os.walk('construction_data'):
            for file in files:
                zipf.write(os.path.join(root, file))
    
    st.success(f"Data exported to {zip_filename}")

if __name__ == "__main__":
    main()