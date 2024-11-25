"""Market analysis utilities for real estate investment."""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import plotly.graph_objects as go
from dataclasses import dataclass

from src.models.property import PropertyDetails
from src.utils.analysis import PropertyAnalyzer

@dataclass
class MarketMetrics:
    """Container for market analysis metrics."""
    median_price: float
    median_price_per_sqft: float
    median_rent: float
    median_cap_rate: float
    price_range: Dict[str, float]
    rent_range: Dict[str, float]
    property_types: Dict[str, int]
    days_on_market: Dict[str, float]

class MarketAnalyzer:
    """Market analysis utility class."""
    
    def __init__(self, comparable_properties: List[PropertyDetails]):
        """Initialize analyzer with comparable properties."""
        self.properties = comparable_properties
        self.df = self._create_dataframe()
    
    def _create_dataframe(self) -> pd.DataFrame:
        """Create DataFrame from properties."""
        data = []
        for prop in self.properties:
            data.append({
                'price': prop.price,
                'square_feet': prop.square_feet,
                'price_per_sqft': prop.price / prop.square_feet if prop.square_feet else None,
                'bedrooms': prop.bedrooms,
                'bathrooms': prop.bathrooms,
                'year_built': prop.year_built,
                'property_type': prop.property_type,
                'days_on_zillow': prop.days_on_zillow,
                'rent_estimate': prop.rent_estimate,
                'cap_rate': (prop.rent_estimate * 12) / prop.price if prop.rent_estimate else None
            })
        return pd.DataFrame(data)
    
    def calculate_market_metrics(self) -> MarketMetrics:
        """Calculate market metrics from comparable properties."""
        return MarketMetrics(
            median_price=self.df['price'].median(),
            median_price_per_sqft=self.df['price_per_sqft'].median(),
            median_rent=self.df['rent_estimate'].median(),
            median_cap_rate=self.df['cap_rate'].median(),
            price_range={
                'min': self.df['price'].min(),
                'max': self.df['price'].max(),
                'p25': self.df['price'].quantile(0.25),
                'p75': self.df['price'].quantile(0.75)
            },
            rent_range={
                'min': self.df['rent_estimate'].min(),
                'max': self.df['rent_estimate'].max(),
                'p25': self.df['rent_estimate'].quantile(0.25),
                'p75': self.df['rent_estimate'].quantile(0.75)
            },
            property_types=self.df['property_type'].value_counts().to_dict(),
            days_on_market={
                'median': self.df['days_on_zillow'].median(),
                'mean': self.df['days_on_zillow'].mean(),
                'min': self.df['days_on_zillow'].min(),
                'max': self.df['days_on_zillow'].max()
            }
        )
    
    def analyze_property_position(self, property: PropertyDetails) -> Dict[str, Any]:
        """Analyze property's position in the market."""
        metrics = {}
        
        # Price analysis
        metrics['price_percentile'] = (
            self.df['price'].lt(property.price).mean() * 100
        )
        metrics['price_vs_median'] = (
            (property.price - self.df['price'].median()) /
            self.df['price'].median() * 100
        )
        
        # Price per sqft analysis
        property_ppsf = property.price / property.square_feet
        metrics['ppsf_percentile'] = (
            self.df['price_per_sqft'].lt(property_ppsf).mean() * 100
        )
        metrics['ppsf_vs_median'] = (
            (property_ppsf - self.df['price_per_sqft'].median()) /
            self.df['price_per_sqft'].median() * 100
        )
        
        # Rent analysis if available
        if property.rent_estimate:
            metrics['rent_percentile'] = (
                self.df['rent_estimate'].lt(property.rent_estimate).mean() * 100
            )
            metrics['rent_vs_median'] = (
                (property.rent_estimate - self.df['rent_estimate'].median()) /
                self.df['rent_estimate'].median() * 100
            )
        
        return metrics
    
    def get_similar_properties(
        self,
        property: PropertyDetails,
        max_results: int = 5
    ) -> List[PropertyDetails]:
        """Find most similar properties based on features."""
        # Calculate similarity scores
        scores = []
        for comp in self.properties:
            score = self._calculate_similarity(property, comp)
            scores.append((score, comp))
        
        # Sort by similarity score and return top matches
        scores.sort(key=lambda x: x[0], reverse=True)
        return [prop for _, prop in scores[:max_results]]
    
    def _calculate_similarity(
        self,
        property1: PropertyDetails,
        property2: PropertyDetails
    ) -> float:
        """Calculate similarity score between two properties."""
        # Weight factors
        weights = {
            'price': 0.3,
            'square_feet': 0.2,
            'bedrooms': 0.15,
            'bathrooms': 0.15,
            'year_built': 0.1,
            'property_type': 0.1
        }
        
        score = 0
        
        # Price similarity (within 20% range)
        price_diff = abs(property1.price - property2.price) / property1.price
        score += weights['price'] * max(0, 1 - price_diff / 0.2)
        
        # Square footage similarity (within 20% range)
        if property1.square_feet and property2.square_feet:
            sqft_diff = abs(property1.square_feet - property2.square_feet) / property1.square_feet
            score += weights['square_feet'] * max(0, 1 - sqft_diff / 0.2)
        
        # Bedroom similarity
        if property1.bedrooms and property2.bedrooms:
            bed_diff = abs(property1.bedrooms - property2.bedrooms)
            score += weights['bedrooms'] * max(0, 1 - bed_diff / 2)
        
        # Bathroom similarity
        if property1.bathrooms and property2.bathrooms:
            bath_diff = abs(property1.bathrooms - property2.bathrooms)
            score += weights['bathrooms'] * max(0, 1 - bath_diff / 2)
        
        # Year built similarity (within 20 years)
        if property1.year_built and property2.year_built:
            year_diff = abs(property1.year_built - property2.year_built)
            score += weights['year_built'] * max(0, 1 - year_diff / 20)
        
        # Property type similarity
        if property1.property_type and property2.property_type:
            score += weights['property_type'] * (
                1 if property1.property_type == property2.property_type else 0
            )
        
        return score

class MarketVisualizer:
    """Visualization utility class for market analysis."""
    
    @staticmethod
    def plot_price_distribution(df: pd.DataFrame, property_price: float = None) -> go.Figure:
        """Create price distribution visualization."""
        fig = go.Figure()
        
        # Add histogram
        fig.add_trace(go.Histogram(
            x=df['price'],
            name='Price Distribution',
            nbinsx=20
        ))
        
        # Add property price line if provided
        if property_price is not None:
            fig.add_vline(
                x=property_price,
                line_dash="dash",
                line_color="red",
                annotation_text="Subject Property"
            )
        
        fig.update_layout(
            title='Price Distribution',
            xaxis_title='Price ($)',
            yaxis_title='Count',
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def plot_market_metrics(metrics: MarketMetrics) -> go.Figure:
        """Create market metrics visualization."""
        fig = go.Figure()
        
        # Price range box plot
        fig.add_trace(go.Box(
            y=[
                metrics.price_range['min'],
                metrics.price_range['p25'],
                metrics.median_price,
                metrics.price_range['p75'],
                metrics.price_range['max']
            ],
            name='Price Range',
            boxpoints=False
        ))
        
        # Rent range box plot
        fig.add_trace(go.Box(
            y=[
                metrics.rent_range['min'],
                metrics.rent_range['p25'],
                metrics.median_rent,
                metrics.rent_range['p75'],
                metrics.rent_range['max']
            ],
            name='Rent Range',
            boxpoints=False
        ))
        
        fig.update_layout(
            title='Market Metrics Overview',
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def plot_property_comparison(
        property: PropertyDetails,
        similar_properties: List[PropertyDetails]
    ) -> go.Figure:
        """Create property comparison visualization."""
        fig = go.Figure()
        
        # Prepare data
        properties = [property] + similar_properties
        x = ['Subject'] + [f'Comp {i+1}' for i in range(len(similar_properties))]
        
        # Add price bars
        fig.add_trace(go.Bar(
            x=x,
            y=[p.price for p in properties],
            name='Price',
            marker_color='blue'
        ))
        
        # Add price per sqft line
        fig.add_trace(go.Scatter(
            x=x,
            y=[p.price/p.square_feet for p in properties],
            name='Price/SqFt',
            yaxis='y2',
            line=dict(color='red')
        ))
        
        fig.update_layout(
            title='Property Comparison',
            yaxis=dict(title='Price ($)'),
            yaxis2=dict(
                title='Price/SqFt ($)',
                overlaying='y',
                side='right'
            ),
            showlegend=True,
            barmode='group'
        )
        
        return fig
