import cv2
import numpy as np
import pandas as pd
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