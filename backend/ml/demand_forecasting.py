"""
Demand Forecasting for Cooperative
Uses historical job data to predict next 7 days demand per service
Simple but explainable models for SIH demo
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

class DemandForecaster:
    def __init__(self):
        self.models = {}
    
    def prepare_features(self, jobs_df: pd.DataFrame) -> pd.DataFrame:
        """Create time-based features"""
        df = jobs_df.copy()
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['day_of_week'] = df['created_at'].dt.dayofweek
        df['month'] = df['created_at'].dt.month
        df['day_of_month'] = df['created_at'].dt.day
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Aggregate daily counts per service
        daily = df.groupby([pd.Grouper(key='created_at', freq='D'), 'service']).size().reset_index(name='count')
        daily['day_of_week'] = daily['created_at'].dt.dayofweek
        daily['month'] = daily['created_at'].dt.month
        daily['day_of_month'] = daily['created_at'].dt.day
        daily['is_weekend'] = (daily['day_of_week'] >= 5).astype(int)
        daily['days_since_start'] = (daily['created_at'] - daily['created_at'].min()).dt.days
        
        return daily
    
    def forecast_service(self, daily_df: pd.DataFrame, service: str, days_ahead=7) -> Dict:
        service_data = daily_df[daily_df['service'] == service].copy()
        
        if len(service_data) < 14:
            # Not enough data, use simple average
            avg = service_data['count'].mean() if len(service_data) > 0 else 5
            forecast = [avg] * days_ahead
            return {
                "service": service,
                "current_avg": round(avg, 1),
                "forecast": forecast,
                "forecast_avg": round(np.mean(forecast), 1),
                "change_percent": 0,
                "trend": "stable",
                "confidence": "low - insufficient data"
            }
        
        # Features
        X = service_data[['day_of_week', 'month', 'is_weekend', 'days_since_start']].values
        y = service_data['count'].values
        
        # Train simple model
        model = RandomForestRegressor(n_estimators=50, random_state=42, max_depth=8)
        model.fit(X, y)
        
        # Forecast next 7 days
        last_date = service_data['created_at'].max()
        future_dates = [last_date + timedelta(days=i+1) for i in range(days_ahead)]
        
        future_features = []
        for d in future_dates:
            future_features.append([
                d.weekday(),
                d.month,
                1 if d.weekday() >= 5 else 0,
                (d - service_data['created_at'].min()).days
            ])
        
        future_features = np.array(future_features)
        forecast = model.predict(future_features)
        forecast = np.maximum(forecast, 0)  # No negative demand
        
        current_avg = service_data.tail(14)['count'].mean()
        forecast_avg = np.mean(forecast)
        change_pct = ((forecast_avg - current_avg) / current_avg * 100) if current_avg > 0 else 0
        
        if change_pct > 20:
            trend = "increasing"
        elif change_pct < -20:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "service": service,
            "current_avg": round(float(current_avg), 1),
            "forecast": [round(float(x), 1) for x in forecast],
            "forecast_avg": round(float(forecast_avg), 1),
            "change_percent": round(float(change_pct), 1),
            "trend": trend,
            "confidence": "medium" if len(service_data) > 60 else "low",
            "recommendation": self.generate_recommendation(service, change_pct, forecast_avg, current_avg)
        }
    
    def generate_recommendation(self, service: str, change_pct: float, forecast_avg: float, current_avg: float) -> str:
        if change_pct > 30:
            return f"Electrical demand expected +{change_pct:.0f}%. Train {int(change_pct/3)} {service}s, recruit {int(change_pct/10)} additional members, increase availability."
        elif change_pct > 15:
            return f"{service.capitalize()} demand rising +{change_pct:.0f}%. Increase availability, prepare workforce."
        elif change_pct < -20:
            return f"{service.capitalize()} demand down {change_pct:.0f}%. Promote service, investigate causes, offer training in other skills."
        else:
            return f"{service.capitalize()} demand stable. Maintain current workforce level."
    
    def forecast_all(self, jobs_df: pd.DataFrame, days_ahead=7) -> List[Dict]:
        daily = self.prepare_features(jobs_df)
        services = jobs_df['service'].unique()
        
        results = []
        for service in services:
            result = self.forecast_service(daily, service, days_ahead)
            results.append(result)
        
        return results
    
    def get_cooperative_insights(self, forecasts: List[Dict]) -> List[str]:
        insights = []
        for f in forecasts:
            if f['change_percent'] > 25:
                insights.append(f"⚡ {f['service'].capitalize()} demand expected +{f['change_percent']:.0f}% → Train {max(2,int(f['change_percent']/3))} workers, recruit {max(1,int(f['change_percent']/10))} members")
            elif f['change_percent'] < -15:
                insights.append(f"🪚 {f['service'].capitalize()} allocation below average ({f['change_percent']:.0f}%) → Investigate demand and promote service")
        
        # Overall
        total_current = sum(f['current_avg'] for f in forecasts)
        total_forecast = sum(f['forecast_avg'] for f in forecasts)
        overall_change = ((total_forecast - total_current) / total_current * 100) if total_current > 0 else 0
        
        if overall_change > 15:
            insights.append(f"📈 Overall demand rising {overall_change:.0f}% → Cooperative should increase workforce capacity")
        
        return insights

# Demo function for API
def demo_forecast():
    """Generate demo forecast with synthetic data"""
    from .data_generator import SahakaarDataGenerator
    gen = SahakaarDataGenerator()
    dfs = gen.to_dataframes()
    jobs_df = dfs['jobs']
    
    forecaster = DemandForecaster()
    forecasts = forecaster.forecast_all(jobs_df)
    insights = forecaster.get_cooperative_insights(forecasts)
    
    return {
        "forecasts": forecasts,
        "insights": insights,
        "generated_at": datetime.now().isoformat(),
        "note": "Demo uses synthetic historical data. Production model will train on anonymized cooperative data."
    }
