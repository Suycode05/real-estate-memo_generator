class RealEstateFinancialCalculator:
    def __init__(self, price_lakhs: float, size_sqft: float, expected_monthly_rent: float = None):
        self.price = price_lakhs * 100000          # Convert to actual rupees
        self.size = size_sqft
        self.expected_monthly_rent = expected_monthly_rent

    def price_per_sqft(self):
        return round(self.price / self.size, 2)

    def calculate_cap_rate(self, annual_rent: float = None):
        """Capitalization Rate"""
        if annual_rent is None and self.expected_monthly_rent:
            annual_rent = self.expected_monthly_rent * 12
        if annual_rent:
            return round((annual_rent / self.price) * 100, 2)
        return None

    def cash_on_cash_return(self, annual_rent: float, down_payment_percent: float = 20):
        """Cash on Cash Return"""
        down_payment = self.price * (down_payment_percent / 100)
        annual_cash_flow = annual_rent - (self.price * 0.01)  # Rough maintenance + tax
        return round((annual_cash_flow / down_payment) * 100, 2)

    def projected_5yr_roi(self, annual_appreciation: float = 8, annual_rent_growth: float = 5):
        """Simple 5-Year ROI Projection"""
        current_value = self.price
        total_rent = 0
        monthly_rent = self.expected_monthly_rent or (self.price * 0.0004)  # Default 0.04% of price

        for year in range(1, 6):
            monthly_rent *= (1 + annual_rent_growth/100)
            total_rent += monthly_rent * 12
            current_value *= (1 + annual_appreciation/100)

        total_return = total_rent + (current_value - self.price)
        roi = (total_return / self.price) * 100
        return round(roi, 2)

    def get_summary(self, monthly_rent: float = None):
        if monthly_rent is None:
            monthly_rent = self.expected_monthly_rent or (self.price * 0.00045)  # Default assumption

        annual_rent = monthly_rent * 12

        return {
            "price_per_sqft": self.price_per_sqft(),
            "cap_rate": self.calculate_cap_rate(annual_rent),
            "cash_on_cash": self.cash_on_cash_return(annual_rent),
            "projected_5yr_roi": self.projected_5yr_roi(),
            "monthly_rent_assumed": round(monthly_rent),
            "annual_rent": round(annual_rent),
            "yield_percent": round((annual_rent / self.price) * 100, 2)
        }