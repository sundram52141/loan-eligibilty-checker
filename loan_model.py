import numpy as np

class LoanEligibilityModel:
    def __init__(self):
        # Define thresholds for different criteria
        self.min_credit_score = 620
        self.max_debt_to_income = 43
        self.min_down_payment_ratio = 0.20  # 20% down payment
        self.min_employment_years = 2
        self.min_income_to_loan_ratio = 0.28  # Monthly payment should not exceed 28% of monthly income
        self.annual_rate = 0.06  # 6% annual interest rate
        
    def predict(self, input_data):
        # Validate input data
        if not self._validate_input(input_data):
            return False, 0, ["Invalid input data. Please check your inputs."]
            
        reasons = []
        score = 0
        total_criteria = 5
        weights = {
            'credit_score': 0.25,
            'debt_to_income': 0.25,
            'down_payment': 0.20,
            'employment_years': 0.15,
            'income_to_loan': 0.15
        }
        
        # Check credit score
        credit_score_weight = self._calculate_credit_score_weight(input_data['credit_score'])
        score += credit_score_weight * weights['credit_score']
        if credit_score_weight < 1:
            reasons.append(f"Credit score ({input_data['credit_score']}) is below the minimum required ({self.min_credit_score})")
        
        # Check debt-to-income ratio
        dti_weight = self._calculate_dti_weight(input_data['debt_to_income'])
        score += dti_weight * weights['debt_to_income']
        if dti_weight < 1:
            reasons.append(f"Debt-to-income ratio ({input_data['debt_to_income']}%) exceeds the maximum allowed ({self.max_debt_to_income}%)")
        
        # Check down payment
        down_payment_ratio = input_data['down_payment'] / input_data['loan_amount']
        down_payment_weight = self._calculate_down_payment_weight(down_payment_ratio)
        score += down_payment_weight * weights['down_payment']
        if down_payment_weight < 1:
            reasons.append(f"Down payment ratio ({down_payment_ratio:.1%}) is below the minimum required ({self.min_down_payment_ratio:.1%})")
        
        # Check employment history
        employment_weight = self._calculate_employment_weight(input_data['employment_years'])
        score += employment_weight * weights['employment_years']
        if employment_weight < 1:
            reasons.append(f"Employment history ({input_data['employment_years']} years) is below the minimum required ({self.min_employment_years} years)")
        
        # Check income to loan ratio
        monthly_income = input_data['income'] / 12
        monthly_payment = self._calculate_monthly_payment(
            input_data['loan_amount'] - input_data['down_payment'],
            input_data['loan_term']
        )
        income_to_loan_ratio = monthly_payment / monthly_income
        income_weight = self._calculate_income_weight(income_to_loan_ratio)
        score += income_weight * weights['income_to_loan']
        if income_weight < 1:
            reasons.append(f"Monthly payment to income ratio ({income_to_loan_ratio:.1%}) exceeds the maximum allowed ({self.min_income_to_loan_ratio:.1%})")
        
        # Calculate eligibility and probability
        eligibility = score >= 0.7  # Need to meet at least 70% of weighted criteria
        probability = score * 100
        
        # If eligible but no reasons were added, add a positive message
        if eligibility and not reasons:
            reasons.append("All criteria have been met successfully!")
        
        return eligibility, probability, reasons
    
    def _validate_input(self, input_data):
        """Validate input data for basic sanity checks"""
        required_fields = ['age', 'income', 'employment_years', 'credit_score', 
                         'loan_amount', 'debt_to_income', 'down_payment', 'loan_term']
        
        # Check if all required fields are present
        if not all(field in input_data for field in required_fields):
            return False
            
        # Check for negative or zero values where inappropriate
        if input_data['income'] <= 0 or input_data['loan_amount'] <= 0:
            return False
            
        # Check if down payment is greater than loan amount
        if input_data['down_payment'] > input_data['loan_amount']:
            return False
            
        return True
    
    def _calculate_credit_score_weight(self, credit_score):
        """Calculate weight for credit score with a gradual scale"""
        if credit_score >= self.min_credit_score + 100:
            return 1.0
        elif credit_score >= self.min_credit_score:
            return 0.5 + (credit_score - self.min_credit_score) / 200
        else:
            return max(0, 0.5 + (credit_score - self.min_credit_score) / 200)
    
    def _calculate_dti_weight(self, dti):
        """Calculate weight for debt-to-income ratio with a gradual scale"""
        if dti <= self.max_debt_to_income - 10:
            return 1.0
        elif dti <= self.max_debt_to_income:
            return 0.5 + (self.max_debt_to_income - dti) / 20
        else:
            return max(0, 0.5 + (self.max_debt_to_income - dti) / 20)
    
    def _calculate_down_payment_weight(self, down_payment_ratio):
        """Calculate weight for down payment ratio with a gradual scale"""
        if down_payment_ratio >= self.min_down_payment_ratio + 0.1:
            return 1.0
        elif down_payment_ratio >= self.min_down_payment_ratio:
            return 0.5 + (down_payment_ratio - self.min_down_payment_ratio) / 0.2
        else:
            return max(0, 0.5 + (down_payment_ratio - self.min_down_payment_ratio) / 0.2)
    
    def _calculate_employment_weight(self, employment_years):
        """Calculate weight for employment history with a gradual scale"""
        if employment_years >= self.min_employment_years + 3:
            return 1.0
        elif employment_years >= self.min_employment_years:
            return 0.5 + (employment_years - self.min_employment_years) / 6
        else:
            return max(0, 0.5 + (employment_years - self.min_employment_years) / 6)
    
    def _calculate_income_weight(self, income_to_loan_ratio):
        """Calculate weight for income to loan ratio with a gradual scale"""
        if income_to_loan_ratio <= self.min_income_to_loan_ratio - 0.05:
            return 1.0
        elif income_to_loan_ratio <= self.min_income_to_loan_ratio:
            return 0.5 + (self.min_income_to_loan_ratio - income_to_loan_ratio) / 0.1
        else:
            return max(0, 0.5 + (self.min_income_to_loan_ratio - income_to_loan_ratio) / 0.1)
    
    def _calculate_monthly_payment(self, principal, years, annual_rate=None):
        """Calculate monthly mortgage payment using the loan amortization formula"""
        if annual_rate is None:
            annual_rate = self.annual_rate
            
        if principal <= 0 or years <= 0:
            return 0
            
        monthly_rate = annual_rate / 12
        num_payments = years * 12
        
        # Handle edge case where rate is 0
        if monthly_rate == 0:
            return principal / num_payments
            
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        return monthly_payment 