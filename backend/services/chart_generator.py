"""
Smart Chart Data Generator for Mike Ross AI
==========================================

Detects when user prompts require statistical visualization and generates
Chart.js compatible JSON data for pie charts, bar charts, line charts, etc.

Features:
- Intelligent prompt analysis to detect stats requests
- Chart.js compatible JSON output
- Legal-specific data visualization
- Context-aware chart recommendations
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import random

class ChartDataGenerator:
    """Generates Chart.js compatible data for legal analytics"""
    
    # Keywords that indicate user wants statistical data
    STATS_KEYWORDS = [
        'stats', 'statistics', 'data', 'chart', 'graph', 'percentage', 'percent',
        'risk level', 'risk score', 'distribution', 'breakdown', 'analysis',
        'compare', 'comparison', 'trend', 'trends', 'overview', 'dashboard',
        'metrics', 'numbers', 'quantify', 'how much', 'how many', 'what percent'
    ]
    
    # Chart types for different data
    CHART_TYPES = {
        'risk_distribution': 'pie',
        'case_strengths': 'radar',
        'timeline': 'line',
        'comparison': 'bar',
        'categories': 'doughnut',
        'trends': 'line'
    }
    
    def __init__(self):
        pass
    
    def detect_stats_request(self, prompt: str) -> bool:
        """Detect if user prompt is asking for statistical data or visualization"""
        prompt_lower = prompt.lower()
        
        # Check for direct stats keywords
        for keyword in self.STATS_KEYWORDS:
            if keyword in prompt_lower:
                return True
        
        # Check for question patterns that imply stats
        stats_patterns = [
            r'what is the.*level',
            r'how.*compare',
            r'show me.*data',
            r'what.*percentage',
            r'break.*down',
            r'analyze.*distribution',
            r'.*overview.*',
            r'dashboard.*'
        ]
        
        for pattern in stats_patterns:
            if re.search(pattern, prompt_lower):
                return True
        
        return False
    
    def generate_case_risk_chart(self, case_analysis: str) -> Dict[str, Any]:
        """Generate risk level pie chart from case analysis"""
        
        # Extract risk indicators from analysis text
        high_risk_indicators = len(re.findall(r'(high risk|dangerous|problematic|weak|vulnerability)', case_analysis.lower()))
        medium_risk_indicators = len(re.findall(r'(moderate|uncertain|unclear|potential)', case_analysis.lower()))
        low_risk_indicators = len(re.findall(r'(strong|advantage|favorable|solid)', case_analysis.lower()))
        
        # Calculate percentages
        total = max(high_risk_indicators + medium_risk_indicators + low_risk_indicators, 1)
        high_pct = round((high_risk_indicators / total) * 100)
        medium_pct = round((medium_risk_indicators / total) * 100)
        low_pct = 100 - high_pct - medium_pct
        
        return {
            "type": "pie",
            "title": "Case Risk Distribution",
            "data": {
                "labels": ["High Risk", "Medium Risk", "Low Risk"],
                "datasets": [{
                    "data": [high_pct, medium_pct, low_pct],
                    "backgroundColor": [
                        "#EF4444", # Red for high risk
                        "#F59E0B", # Orange for medium risk  
                        "#10B981"  # Green for low risk
                    ],
                    "borderWidth": 2,
                    "borderColor": "#ffffff"
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {
                        "position": "bottom"
                    },
                    "title": {
                        "display": True,
                        "text": "Case Risk Assessment"
                    }
                }
            }
        }
    
    def generate_strengths_weaknesses_chart(self, case_analysis: str) -> Dict[str, Any]:
        """Generate bar chart comparing case strengths vs weaknesses"""
        
        # Count strength and weakness indicators
        strength_count = len(re.findall(r'strength|strong|advantage|favorable|solid|good|positive', case_analysis.lower()))
        weakness_count = len(re.findall(r'weakness|weak|disadvantage|problematic|risk|negative|vulnerable', case_analysis.lower()))
        
        return {
            "type": "bar",
            "title": "Case Strengths vs Weaknesses",
            "data": {
                "labels": ["Strengths", "Weaknesses"],
                "datasets": [{
                    "label": "Count",
                    "data": [strength_count, weakness_count],
                    "backgroundColor": [
                        "#10B981", # Green for strengths
                        "#EF4444"  # Red for weaknesses
                    ],
                    "borderColor": [
                        "#059669",
                        "#DC2626"
                    ],
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "ticks": {
                            "stepSize": 1
                        }
                    }
                },
                "plugins": {
                    "legend": {
                        "display": False
                    },
                    "title": {
                        "display": True,
                        "text": "Case Analysis Overview"
                    }
                }
            }
        }
    
    def generate_contract_risk_radar(self, contract_analysis: str) -> Dict[str, Any]:
        """Generate radar chart for contract risk assessment"""
        
        # Risk categories for contracts
        categories = ["Legal Compliance", "Financial Risk", "Operational Risk", "Reputational Risk", "Regulatory Risk"]
        
        # Simple scoring based on text analysis (in real scenario, you'd use more sophisticated NLP)
        scores = []
        for category in categories:
            # Count risk indicators for each category
            category_risks = len(re.findall(rf'{category.lower()}|compliance|financial|operational|reputation|regulatory', contract_analysis.lower()))
            # Convert to 0-10 scale (inverse - more risks = lower score)
            score = max(0, 10 - min(category_risks * 2, 10))
            scores.append(score)
        
        return {
            "type": "radar",
            "title": "Contract Risk Assessment",
            "data": {
                "labels": categories,
                "datasets": [{
                    "label": "Risk Score (0-10)",
                    "data": scores,
                    "backgroundColor": "rgba(59, 130, 246, 0.2)",
                    "borderColor": "#3B82F6",
                    "borderWidth": 2,
                    "pointBackgroundColor": "#3B82F6",
                    "pointBorderColor": "#ffffff",
                    "pointBorderWidth": 2
                }]
            },
            "options": {
                "responsive": True,
                "scales": {
                    "r": {
                        "min": 0,
                        "max": 10,
                        "ticks": {
                            "stepSize": 2
                        }
                    }
                },
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Contract Risk Profile"
                    }
                }
            }
        }
    
    def generate_precedent_timeline(self, precedent_analysis: str) -> Dict[str, Any]:
        """Generate timeline chart for legal precedents"""
        
        # Extract years from precedent analysis (simplified)
        years = re.findall(r'\b(19|20)\d{2}\b', precedent_analysis)
        if not years:
            # Generate sample years if none found
            years = ['2018', '2019', '2020', '2021', '2022', '2023', '2024']
        
        # Count cases per year (simplified)
        year_counts = {}
        for year in years:
            year_counts[year] = year_counts.get(year, 0) + 1
        
        # Sort by year
        sorted_years = sorted(year_counts.items())
        labels = [year for year, _ in sorted_years]
        data = [count for _, count in sorted_years]
        
        return {
            "type": "line",
            "title": "Legal Precedent Timeline",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": "Related Cases",
                    "data": data,
                    "borderColor": "#8B5CF6",
                    "backgroundColor": "rgba(139, 92, 246, 0.1)",
                    "borderWidth": 3,
                    "fill": True,
                    "tension": 0.4
                }]
            },
            "options": {
                "responsive": True,
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "ticks": {
                            "stepSize": 1
                        }
                    }
                },
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Precedent Cases Over Time"
                    }
                }
            }
        }
    
    def generate_witness_credibility_chart(self, witness_analysis: str) -> Dict[str, Any]:
        """Generate credibility assessment chart for witnesses"""
        
        # Extract witness-related indicators
        credibility_indicators = {
            "High Credibility": len(re.findall(r'credible|reliable|trustworthy|consistent|honest', witness_analysis.lower())),
            "Medium Credibility": len(re.findall(r'uncertain|unclear|moderate|mixed', witness_analysis.lower())),
            "Low Credibility": len(re.findall(r'inconsistent|unreliable|questionable|problematic', witness_analysis.lower()))
        }
        
        labels = list(credibility_indicators.keys())
        data = list(credibility_indicators.values())
        
        return {
            "type": "doughnut",
            "title": "Witness Credibility Assessment",
            "data": {
                "labels": labels,
                "datasets": [{
                    "data": data,
                    "backgroundColor": [
                        "#10B981", # Green
                        "#F59E0B", # Orange
                        "#EF4444"  # Red
                    ],
                    "borderWidth": 3,
                    "borderColor": "#ffffff"
                }]
            },
            "options": {
                "responsive": True,
                "cutout": "60%",
                "plugins": {
                    "legend": {
                        "position": "bottom"
                    },
                    "title": {
                        "display": True,
                        "text": "Witness Analysis Results"
                    }
                }
            }
        }
    
    def generate_charts_for_model(self, model_type: str, analysis_text: str, prompt: str) -> List[Dict[str, Any]]:
        """Generate appropriate charts based on model type and analysis"""
        
        charts = []
        
        if not self.detect_stats_request(prompt):
            return charts  # No charts if user didn't ask for stats
        
        # Generate model-specific charts
        if model_type == "case-breaker":
            charts.append(self.generate_case_risk_chart(analysis_text))
            charts.append(self.generate_strengths_weaknesses_chart(analysis_text))
            
        elif model_type == "contract-xray":
            charts.append(self.generate_contract_risk_radar(analysis_text))
            
        elif model_type == "precedent-strategist":
            charts.append(self.generate_precedent_timeline(analysis_text))
            
        elif model_type == "deposition-strategist":
            charts.append(self.generate_witness_credibility_chart(analysis_text))
        
        return charts
    
    def generate_dashboard_charts(self, all_analyses: Dict[str, str]) -> List[Dict[str, Any]]:
        """Generate comprehensive dashboard charts from all model analyses"""
        
        dashboard_charts = []
        
        # Overall risk distribution across all models
        all_text = ' '.join(all_analyses.values())
        dashboard_charts.append(self.generate_case_risk_chart(all_text))
        
        # Model comparison chart
        model_scores = {}
        for model, analysis in all_analyses.items():
            # Calculate a simple confidence score based on analysis length and positive indicators
            positive_count = len(re.findall(r'strong|good|favorable|advantage|solid', analysis.lower()))
            negative_count = len(re.findall(r'weak|poor|problematic|risk|disadvantage', analysis.lower()))
            
            # Score from 0-100
            total_indicators = max(positive_count + negative_count, 1)
            confidence_score = round((positive_count / total_indicators) * 100)
            model_scores[model.replace('-', ' ').title()] = confidence_score
        
        dashboard_charts.append({
            "type": "bar",
            "title": "Model Analysis Confidence",
            "data": {
                "labels": list(model_scores.keys()),
                "datasets": [{
                    "label": "Confidence Score",
                    "data": list(model_scores.values()),
                    "backgroundColor": [
                        "#3B82F6", # Blue
                        "#10B981", # Green
                        "#F59E0B", # Orange
                        "#8B5CF6"  # Purple
                    ],
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "max": 100,
                        "ticks": {
                            "callback": "function(value) { return value + '%'; }"
                        }
                    }
                },
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Analysis Confidence by Model"
                    }
                }
            }
        })
        
        return dashboard_charts

# Global instance
chart_generator = ChartDataGenerator()
