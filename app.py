# pip install streamlit 

import streamlit as st
import numpy as np
import pandas as pd
import joblib
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import logging
from typing import Optional, Dict, Any
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExamScorePredictor:    
    def __init__(self, model_path: str = "best_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.feature_names = [
            "Study Hours", "Attendance %", "Mental Health", 
            "Sleep Hours", "Part-Time Job"
        ]
        self.load_model()
        
    def load_model(self) -> bool:
        """Load the trained model with error handling."""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                logger.info(f"Model loaded successfully from {self.model_path}")
                return True
            else:
                st.error(f"Model file '{self.model_path}' not found!")
                return False
        except Exception as e:
            st.error(f"Error loading model: {str(e)}")
            logger.error(f"Model loading error: {str(e)}")
            return False
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> Dict[str, str]:
        """Validate user inputs and return any errors."""
        errors = {}
        
        if inputs['study_hours'] < 0 or inputs['study_hours'] > 24:
            errors['study_hours'] = "Study hours must be between 0-24"
            
        if inputs['attendance'] < 0 or inputs['attendance'] > 100:
            errors['attendance'] = "Attendance must be between 0-100%"
            
        if inputs['mental_health'] < 1 or inputs['mental_health'] > 10:
            errors['mental_health'] = "Mental health rating must be between 1-10"
            
        if inputs['sleep_hours'] < 0 or inputs['sleep_hours'] > 24:
            errors['sleep_hours'] = "Sleep hours must be between 0-24"
            
        return errors
    
    def predict(self, inputs: Dict[str, Any]) -> Optional[float]:
        """Make prediction with error handling."""
        if not self.model:
            st.error("Model not loaded!")
            return None
            
        try:
            input_array = np.array([[
                inputs['study_hours'],
                inputs['attendance'],
                inputs['mental_health'],
                inputs['sleep_hours'],
                inputs['part_time_job']
            ]])
            
            prediction = self.model.predict(input_array)[0]
            # Clamp prediction to realistic range
            prediction = max(0, min(100, prediction))
            
            logger.info(f"Prediction made: {prediction:.2f}")
            return prediction
            
        except Exception as e:
            st.error(f"Error making prediction: {str(e)}")
            logger.error(f"Prediction error: {str(e)}")
            return None


def create_input_visualization(inputs):
    """Create a radar chart showing current input values."""
    categories = ['Study Hours<br>(0-12)', 'Attendance<br>(%)', 'Mental Health<br>(1-10)', 
                 'Sleep Hours<br>(0-12)', 'Part-Time Job<br>(0-1)']
    
    # Normalize values for radar chart
    values = [
        inputs['study_hours'] / 12 * 100,  # Normalize to 0-100
        inputs['attendance'],
        inputs['mental_health'] / 10 * 100,
        inputs['sleep_hours'] / 12 * 100,
        inputs['part_time_job'] * 100
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Your Input',
        marker_color='lightgreen'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Your Input Profile",
        height=500
    )
    
    return fig

def get_recommendations(inputs, prediction):
    """Provide personalized recommendations based on inputs."""
    recommendations = []
    
    if inputs['study_hours'] < 3:
        recommendations.append("📚 Consider increasing study time. Aim for at least 3-4 hours daily.")
    
    if inputs['attendance'] < 75:
        recommendations.append("📋 Improve attendance. Aim for at least 80% to maximize learning.")
    
    if inputs['mental_health'] < 6:
        recommendations.append("🧠 Consider stress management techniques or counseling support.")
    
    if inputs['sleep_hours'] < 7:
        recommendations.append("😴 Get more sleep. 7-9 hours is optimal for academic performance.")
    elif inputs['sleep_hours'] > 10:
        recommendations.append("⏰ Too much sleep might indicate other issues. Consider a consistent 7-9 hour schedule.")
    
    if inputs['part_time_job'] == 1 and inputs['study_hours'] < 4:
        recommendations.append("⚖️ Balance work and study. Consider reducing work hours if possible.")
    
    # Performance-based recommendations
    if prediction < 60:
        recommendations.append("🎯 Focus on fundamental concepts and seek additional help if needed.")
    elif prediction >= 85:
        recommendations.append("🌟 Great potential! Consider advanced study techniques to excel further.")
    
    return recommendations

def main():
    """Main application function."""
    
    # Page configuration
    st.set_page_config(
        page_title="Exam Score Predictor",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS for Styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .prediction-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize predictor
    predictor = ExamScorePredictor()
    
    # Header
    st.markdown('<h1 class="main-header">🎓 Student Exam Score Predictor</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    This tool predicts your exam score based on study habits and personal factors. 
    Adjust the parameters below to see how different factors might affect your performance.
    """)
    
    # Sidebar for inputs
    st.sidebar.header("📝 Input Your Information")
    
    # Input collection with better UI components
    study_hours = st.sidebar.number_input(
        "📚 Study Hours per Day", 
        min_value=0.0, max_value=12.0, value=2.0, step=0.5,
        help="Average hours spent studying per day"
    )
    
    attendance = st.sidebar.number_input(
        "📋 Attendance Percentage", 
        min_value=0.0, max_value=100.0, value=80.0, step=1.0,
        help="Percentage of classes attended"
    )
    
    mental_health = st.sidebar.select_slider(
        "🧠 Mental Health Rating", 
        options=list(range(1, 11)), value=5,
        help="Rate your mental health (1=Poor, 10=Excellent)"
    )
    
    sleep_hours = st.sidebar.number_input(
        "😴 Sleep Hours per Night", 
        min_value=0.0, max_value=12.0, value=7.0, step=0.5,
        help="Average hours of sleep per night"
    )
    
    part_time_job = st.sidebar.radio(
        "💼 Part-Time Job", 
        ["No", "Yes"],
        help="Do you have a part-time job?"
    )
    
    # Create inputs dictionary
    inputs = {
        'study_hours': study_hours,
        'attendance': attendance,
        'mental_health': mental_health,
        'sleep_hours': sleep_hours,
        'part_time_job': 1 if part_time_job == "Yes" else 0
    }
    
    # Validate inputs
    errors = predictor.validate_inputs(inputs)
    if errors:
        st.sidebar.error("⚠️ Input Validation Errors:")
        for field, error in errors.items():
            st.sidebar.error(f"• {error}")
    
    # Main content area 
    st.subheader("📊 Your Input Profile")
    input_chart = create_input_visualization(inputs)
    if input_chart:
        st.plotly_chart(input_chart, use_container_width=True)
    
    # Prediction section
    st.subheader("🎯 Prediction Results")
    
    if st.button("🚀 Predict Exam Score", type="primary", use_container_width=True):
        if errors:
            st.error("Please fix the input errors before predicting.")
        else:
            with st.spinner("Making prediction..."):
                prediction = predictor.predict(inputs)
                
                if prediction is not None:
                    # Display prediction with styling
                    st.markdown(f"""
                    <div class="prediction-box">
                        <h2 style="color: #1f77b4; margin: 0;">Predicted Exam Score: {prediction:.1f}/100</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Performance categorization
                    if prediction >= 85:
                        st.success("🌟 Excellent performance predicted!")
                    elif prediction >= 75:
                        st.success("✅ Good performance predicted!")
                    elif prediction >= 60:
                        st.warning("⚠️ Average performance predicted.")
                    else:
                        st.error("❌ Below average performance predicted.")
                    
                    # Progress bar
                    st.progress(prediction / 100)
                    
                    # Recommendations 
                    st.subheader("💡 Personalized Recommendations")
                    recommendations = get_recommendations(inputs, prediction)
                    
                    if recommendations:
                        for i, rec in enumerate(recommendations):
                            st.info(f"💡 **Tip {i+1}:** {rec}")
                    else:
                        st.success("🎉 Great job! Keep up the excellent habits!")
                    
                    # Save prediction log 
                    log_data = {
                        'timestamp': datetime.now().isoformat(),
                        'inputs': inputs,
                        'prediction': prediction
                    }
                    
                    # Display input summary
                    st.subheader("📋 Input Summary")
                    summary_df = pd.DataFrame([{
                        'Factor': 'Study Hours/Day',
                        'Value': f"{study_hours:.1f} hours"
                    }, {
                        'Factor': 'Attendance',
                        'Value': f"{attendance:.0f}%"
                    }, {
                        'Factor': 'Mental Health',
                        'Value': f"{mental_health}/10"
                    }, {
                        'Factor': 'Sleep Hours',
                        'Value': f"{sleep_hours:.1f} hours"
                    }, {
                        'Factor': 'Part-Time Job',
                        'Value': part_time_job
                    }])
                    
                    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    # Footer with additional information
    st.markdown("---")
    st.markdown("""
    **Note:** This prediction is based on historical data and should be used as a guide only. 
    Individual results may vary based on many factors not captured in this model.
    
    **Tips for Better Performance:**
    - Maintain consistent study habits
    - Prioritize mental health and well-being
    - Get adequate sleep (7-9 hours)
    - Attend classes regularly
    - Seek help when needed
    """)

if __name__ == "__main__":
    main()
    
# In Terminal: streamlit run app.py
