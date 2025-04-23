import streamlit as st
import pandas as pd
import numpy as np
from loan_model import LoanEligibilityModel
from gemini_service import GeminiService
import logging
import sys
import os
from dotenv import load_dotenv

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def validate_inputs(age, income, employment_years, credit_score, loan_amount, debt_to_income, down_payment, loan_term):
    """Validate user inputs and return error messages if any"""
    errors = []
    
    if age < 18:
        errors.append("Age must be at least 18 years")
    
    if income <= 0:
        errors.append("Annual income must be greater than 0")
    
    if employment_years < 0:
        errors.append("Employment years cannot be negative")
    
    if credit_score < 300 or credit_score > 850:
        errors.append("Credit score must be between 300 and 850")
    
    if loan_amount <= 0:
        errors.append("Loan amount must be greater than 0")
    
    if debt_to_income < 0 or debt_to_income > 100:
        errors.append("Debt-to-income ratio must be between 0 and 100")
    
    if down_payment < 0:
        errors.append("Down payment cannot be negative")
    
    if down_payment > loan_amount:
        errors.append("Down payment cannot be greater than loan amount")
    
    if loan_term not in [15, 20, 30]:
        errors.append("Loan term must be 15, 20, or 30 years")
    
    return errors

def check_environment():
    """Check if all required environment variables and dependencies are set up"""
    issues = []
    
    # Check .env file
    if not os.path.exists('.env'):
        issues.append("❌ .env file is missing")
    else:
        load_dotenv(override=True)
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            issues.append("❌ GEMINI_API_KEY not found in .env file")
        else:
            issues.append("✅ GEMINI_API_KEY found in .env file")
    
    # Check required packages
    try:
        import google.generativeai
        issues.append("✅ google-generativeai package is installed")
    except ImportError:
        issues.append("❌ google-generativeai package is not installed")
    
    try:
        import streamlit
        issues.append("✅ streamlit package is installed")
    except ImportError:
        issues.append("❌ streamlit package is not installed")
    
    return issues

def initialize_gemini():
    """Initialize Gemini service with proper error handling"""
    try:
        service = GeminiService()
        return service, True
    except Exception as e:
        logger.error(f"Failed to initialize Gemini service: {str(e)}", exc_info=True)
        return None, False

def main():
    st.set_page_config(page_title="Loan Eligibility Checker", page_icon="💰")
    
    st.title("Loan Eligibility Checker")
    st.write("""
    This AI-powered tool helps you check your loan eligibility based on various factors.
    Please fill in your details below to get an instant assessment.
    """)
    
    # Check environment setup
    env_issues = check_environment()
    
    # Initialize Gemini service
    gemini_service, gemini_available = initialize_gemini()
    if not gemini_available:
        st.warning("""
        AI-powered advice is currently unavailable. Basic eligibility checking will still work.
        
        Environment Check Results:
        """)
        for issue in env_issues:
            st.write(issue)
        
        st.write("""
        To fix these issues:
        1. Make sure you have created a .env file with your GEMINI_API_KEY
        2. Run `pip install -r requirements.txt` to install all dependencies
        3. Check your internet connection
        4. Restart the application
        """)
    
    # Create input fields
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.number_input("Age", min_value=18, max_value=100, value=30)
        income = st.number_input("Annual Income (₹)", min_value=0, step=100000, value=500000)
        employment_years = st.number_input("Years of Employment", min_value=0, max_value=50, value=5)
        credit_score = st.slider("Credit Score", min_value=300, max_value=850, value=700)
    
    with col2:
        loan_amount = st.number_input("Loan Amount (₹)", min_value=0, step=100000, value=2000000)
        debt_to_income = st.slider("Debt-to-Income Ratio (%)", min_value=0, max_value=100, value=30)
        down_payment = st.number_input("Down Payment (₹)", min_value=0, step=100000, value=400000)
        loan_term = st.selectbox("Loan Term (Years)", [15, 20, 30], index=2)
    
    # Create model instance
    model = LoanEligibilityModel()
    
    if st.button("Check Eligibility"):
        # Validate inputs
        errors = validate_inputs(age, income, employment_years, credit_score, 
                               loan_amount, debt_to_income, down_payment, loan_term)
        
        if errors:
            st.error("Please correct the following errors:")
            for error in errors:
                st.write(f"• {error}")
            return
        
        # Prepare input data
        input_data = {
            'age': age,
            'income': income,
            'employment_years': employment_years,
            'credit_score': credit_score,
            'loan_amount': loan_amount,
            'debt_to_income': debt_to_income,
            'down_payment': down_payment,
            'loan_term': loan_term
        }
        
        try:
            # Get prediction
            eligibility, probability, reasons = model.predict(input_data)
            
            # Display results
            st.write("---")
            st.subheader("Results")
            
            if eligibility:
                st.success(f"✅ Congratulations! You are eligible for the loan. (Confidence: {probability:.1f}%)")
            else:
                st.error(f"❌ Sorry, you are not eligible for the loan at this time. (Confidence: {probability:.1f}%)")
            
            st.write("---")
            st.subheader("Analysis")
            for reason in reasons:
                st.write(f"• {reason}")
                
            # Display monthly payment information
            monthly_payment = model._calculate_monthly_payment(
                loan_amount - down_payment,
                loan_term
            )
            
            st.write("---")
            st.subheader("Monthly Payment Details")
            st.write(f"• Principal: ₹{loan_amount - down_payment:,.2f}")
            st.write(f"• Monthly Payment: ₹{monthly_payment:,.2f}")
            st.write(f"• Annual Interest Rate: {model.annual_rate:.1%}")
            
            # Get AI-powered advice if Gemini is available
            if gemini_available and gemini_service:
                st.write("---")
                st.subheader("AI-Powered Financial Advice")
                with st.spinner("Getting personalized financial advice..."):
                    try:
                        advice = gemini_service.get_loan_advice(input_data, eligibility, probability, reasons)
                        st.markdown(advice)
                    except Exception as e:
                        logger.error(f"Error getting AI advice: {str(e)}", exc_info=True)
                        st.error("Failed to get AI advice. Please try again later.")
            
        except Exception as e:
            logger.error(f"Error processing application: {str(e)}", exc_info=True)
            st.error(f"An error occurred while processing your application: {str(e)}")
            st.write("Please try again or contact support if the problem persists.")
    
    # Add financial education section
    if gemini_available and gemini_service:
        st.write("---")
        st.subheader("Financial Education")
        topics = [
            "Understanding Credit Scores",
            "Debt-to-Income Ratio",
            "Down Payment Strategies",
            "Loan Terms and Interest Rates",
            "Financial Planning"
        ]
        selected_topic = st.selectbox("Learn about:", topics)
        
        if st.button("Get Information"):
            with st.spinner("Getting educational content..."):
                try:
                    education = gemini_service.get_financial_education(selected_topic)
                    st.markdown(education)
                except Exception as e:
                    logger.error(f"Error getting educational content: {str(e)}", exc_info=True)
                    st.error("Failed to get educational content. Please try again later.")

if __name__ == "__main__":
    main() 