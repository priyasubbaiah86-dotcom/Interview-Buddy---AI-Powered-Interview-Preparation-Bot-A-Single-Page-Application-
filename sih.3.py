# 🏗️ CONSTRUCTION PROGRESS AI - COMPLETE SINGLE FILE
# Run this with: python construction_ai_single.py

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import json
import sys

# Check and install required packages
def install_packages():
    required_packages = {
        'streamlit': 'streamlit',
        'opencv-python': 'cv2', 
        'pillow': 'PIL',
        'numpy': 'numpy',
        'pandas': 'pandas',
        'matplotlib': 'matplotlib'
    }
    
    for pkg, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {pkg} is installed")
        except ImportError:
            print(f"📦 Installing {pkg}...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

# Install packages if needed
install_packages()

# Now import everything
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import json

class ConstructionAnalyzer:
    def __init__(self):
        self.stages = {
            'site-prep': {'name': 'Site Preparation', 'order': 0, 'color': '#FF6B35'},
            'foundation': {'name': 'Foundation Work', 'order': 1, 'color': '#4ECDC4'},
            'superstructure': {'name': 'Super Structure', 'order': 2, 'color': '#45B7D1'},
            'façade': {'name': 'Façade Work', 'order': 3, 'color': '#96CEB4'},
            'interiors': {'name': 'Interior Work', 'order': 4, 'color': '#FFEAA7'}
        }
        
        # Create data directory
        os.makedirs('construction_data', exist_ok=True)
        self.history_file = 'construction_data/analysis_history.csv'
        
    def analyze_construction(self, image_array, selected_stage, project_name="Default Project"):
        """Analyze construction stage from image"""
        try:
            # Convert to grayscale if needed
            if len(image_array.shape) == 3:
                gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = image_array
            
            # Multiple analysis techniques
            edge_analysis = self.edge_based_analysis(gray)
            color_analysis = self.color_based_analysis(image_array) if len(image_array.shape) == 3 else {'total_score': 0}
            texture_analysis = self.texture_based_analysis(gray)
            
            # Combine scores
            total_score = (
                edge_analysis['total_score'] * 0.6 +
                color_analysis.get('total_score', 0) * 0.3 +
                texture_analysis['total_score'] * 0.1
            )
            
            # Determine stage
            detected_stage = self.get_stage_from_score(total_score)
            confidence = self.calculate_confidence(edge_analysis, texture_analysis)
            
            # Detect elements
            elements = self.detect_construction_elements(image_array)
            
            # Validate
            validation = self.validate_stage(detected_stage, selected_stage, confidence)
            if validation:
                return validation
            
            # Generate report
            report = self.generate_report(detected_stage, selected_stage, confidence, elements, 
                                       edge_analysis, color_analysis, project_name)
            
            # Save to history
            self.save_to_history(report)
            
            return report
            
        except Exception as e:
            return {'error': f'Analysis failed: {str(e)}'}
    
    def edge_based_analysis(self, gray_image):
        """Analyze edges and structures"""
        # Edge detection
        edges = cv2.Canny(gray_image, 50, 150)
        edge_density = np.sum(edges) / (gray_image.shape[0] * gray_image.shape[1])
        
        # Structure detection
        sobelx = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
        structure_score = np.mean(gradient_magnitude)
        
        return {
            'edge_density': edge_density,
            'structure_score': structure_score,
            'total_score': edge_density * 5000 + structure_score * 0.1
        }
    
    def color_based_analysis(self, image_array):
        """Analyze colors for material detection"""
        if len(image_array.shape) != 3:
            return {'total_score': 0}
            
        hsv = cv2.cvtColor(image_array, cv2.COLOR_RGB2HSV)
        
        # Detect construction materials
        concrete_mask = self.detect_concrete(hsv)
        soil_mask = self.detect_soil(hsv)
        sky_mask = self.detect_sky(hsv)
        
        concrete_area = np.sum(concrete_mask) / 255
        soil_area = np.sum(soil_mask) / 255
        sky_area = np.sum(sky_mask) / 255
        
        total_pixels = image_array.shape[0] * image_array.shape[1]
        
        material_score = (concrete_area * 2 + soil_area * 1.5) / total_pixels
        
        return {
            'concrete_area': concrete_area,
            'soil_area': soil_area,
            'sky_area': sky_area,
            'material_score': material_score,
            'total_score': material_score * 10000
        }
    
    def texture_based_analysis(self, gray_image):
        """Analyze texture complexity"""
        # Laplacian variance for texture
        laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
        texture_variance = np.var(laplacian)
        
        return {
            'texture_variance': texture_variance,
            'total_score': texture_variance * 0.1
        }
    
    def detect_concrete(self, hsv):
        """Detect concrete areas"""
        lower_gray = np.array([0, 0, 50])
        upper_gray = np.array([180, 50, 200])
        return cv2.inRange(hsv, lower_gray, upper_gray)
    
    def detect_soil(self, hsv):
        """Detect soil/earth areas"""
        lower_brown = np.array([10, 50, 20])
        upper_brown = np.array([20, 255, 200])
        return cv2.inRange(hsv, lower_brown, upper_brown)
    
    def detect_sky(self, hsv):
        """Detect sky areas"""
        lower_blue = np.array([100, 50, 50])
        upper_blue = np.array([130, 255, 255])
        return cv2.inRange(hsv, lower_blue, upper_blue)
    
    def detect_construction_elements(self, image_array):
        """Detect construction elements"""
        elements = []
        
        if len(image_array.shape) == 3:
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = image_array
        
        # Detect vertical structures
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=50, maxLineGap=10)
        
        if lines is not None:
            vertical_lines = 0
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.abs(np.arctan2(y2-y1, x2-x1) * 180/np.pi)
                if 80 < angle < 100:  # Vertical lines
                    vertical_lines += 1
            
            if vertical_lines > 5:
                elements.append('vertical-structures')
        
        # Detect large uniform areas (concrete slabs)
        if len(image_array.shape) == 3:
            hsv = cv2.cvtColor(image_array, cv2.COLOR_RGB2HSV)
            concrete_mask = self.detect_concrete(hsv)
            if np.sum(concrete_mask) > 10000:
                elements.append('concrete-surfaces')
        
        return elements
    
    def get_stage_from_score(self, score):
        """Determine construction stage from score"""
        if score < 1000:
            return 'site-prep'
        elif score < 2500:
            return 'foundation'
        elif score < 5000:
            return 'superstructure'
        elif score < 7500:
            return 'façade'
        else:
            return 'interiors'
    
    def calculate_confidence(self, edge_analysis, texture_analysis):
        """Calculate confidence score"""
        edge_consistency = min(edge_analysis['edge_density'] * 10, 1.0)
        texture_consistency = min(texture_analysis['texture_variance'] / 1000, 0.3)
        return min(edge_consistency + texture_consistency, 0.95)
    
    def validate_stage(self, detected_stage, selected_stage, confidence):
        """Validate stage match"""
        stage_order = ['site-prep', 'foundation', 'superstructure', 'façade', 'interiors']
        detected_idx = stage_order.index(detected_stage)
        selected_idx = stage_order.index(selected_stage)
        
        if abs(detected_idx - selected_idx) > 1 and confidence > 0.6:
            return {
                'error': f'Stage mismatch: Image shows {detected_stage}, but you selected {selected_stage}'
            }
        return None
    
    def generate_report(self, detected_stage, selected_stage, confidence, elements, 
                       edge_analysis, color_analysis, project_name):
        """Generate comprehensive report"""
        
        progress_ranges = {
            'site-prep': '0-20%',
            'foundation': '20-40%',
            'superstructure': '40-70%', 
            'façade': '70-90%',
            'interiors': '90-100%'
        }
        
        return {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'project_name': project_name,
            'detected_stage': detected_stage,
            'selected_stage': selected_stage,
            'confidence': confidence,
            'progress_range': progress_ranges.get(detected_stage, 'Unknown'),
            'elements_found': elements,
            'technical_metrics': {
                'edge_density': f"{edge_analysis['edge_density']:.4f}",
                'structure_score': f"{edge_analysis['structure_score']:.2f}",
                'material_score': f"{color_analysis.get('material_score', 0):.4f}",
                'texture_variance': f"{edge_analysis.get('texture_variance', 0):.2f}"
            },
            'status': 'VALID' if detected_stage == selected_stage else 'REVIEW_NEEDED',
            'message': self.generate_insight(detected_stage, elements, confidence)
        }
    
    def generate_insight(self, stage, elements, confidence):
        """Generate insight message"""
        insights = {
            'site-prep': "Early stage: Land clearing, excavation, and site preparation.",
            'foundation': "Foundation work: Concrete pouring, reinforcement placement.",
            'superstructure': "Structural work: Columns, beams, and slabs construction.",
            'façade': "Exterior work: Windows, cladding, and external finishes.",
            'interiors': "Interior work: Partitions, electrical, plumbing, finishes."
        }
        
        base = insights.get(stage, "Construction activity detected.")
        
        if 'concrete-surfaces' in elements:
            base += " Significant concrete work visible."
        if 'vertical-structures' in elements:
            base += " Structural elements detected."
            
        if confidence > 0.8:
            base += " High confidence assessment."
        elif confidence > 0.6:
            base += " Moderate confidence."
        else:
            base += " Verification recommended."
            
        return base
    
    def save_to_history(self, report):
        """Save analysis to history"""
        history_data = {
            'timestamp': [report['timestamp']],
            'project': [report['project_name']],
            'detected_stage': [report['detected_stage']],
            'selected_stage': [report['selected_stage']],
            'confidence': [report['confidence']],
            'status': [report['status']],
            'elements': [', '.join(report['elements_found'])]
        }
        
        df = pd.DataFrame(history_data)
        
        if os.path.exists(self.history_file):
            existing_df = pd.read_csv(self.history_file)
            df = pd.concat([existing_df, df], ignore_index=True)
        
        df.to_csv(self.history_file, index=False)
    
    def get_analysis_history(self):
        """Get analysis history"""
        if os.path.exists(self.history_file):
            return pd.read_csv(self.history_file)
        return pd.DataFrame()
    
    def export_report(self, report, filename=None):
        """Export report to JSON"""
        if filename is None:
            filename = f"construction_data/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filename

def main():
    """Main Streamlit application"""
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
        .element-badge {
            background: #e0e0e0;
            padding: 0.3rem 0.6rem;
            margin: 0.2rem;
            border-radius: 15px;
            display: inline-block;
            font-size: 0.9rem;
        }
    </style>
    """, unsafe_allow_html=True)

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
        elements_html = "".join([f"<span class='element-badge'>{elem.replace('-', ' ').title()}</span>" 
                               for elem in result['elements_found']])
        st.markdown(elements_html, unsafe_allow_html=True)
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
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(history_df['timestamp'], history_df['stage_numeric'], 
                marker='o', linewidth=3, markersize=8, color='#1f77b4')
        ax.set_yticks(range(len(stage_order)))
        ax.set_yticklabels([s.upper() for s in stage_order])
        ax.set_xlabel("Date & Time")
        ax.set_ylabel("Construction Stage")
        ax.grid(True, alpha=0.3)
        ax.set_title("Construction Progress Over Time", fontsize=14, fontweight='bold')
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        st.pyplot(fig)
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