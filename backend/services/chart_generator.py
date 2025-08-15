"""
Dynamic Chart Data Generator for Mike Ross AI
============================================

Generates dynamic, data-driven visualizations based on actual Mike Ross model analyses.
Uses real data from model responses and responds intelligently to user prompts.

Features:
- Dynamic data extraction from Mike Ross model analyses
- Intelligent chart type selection based on data characteristics
- User prompt-aware chart generation
- Chart.js compatible JSON output
- Real-time risk assessment and visualization
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import random


class DynamicChartGenerator:
    """Generates dynamic Chart.js compatible data from real Mike Ross model analyses"""
    
    # Enhanced chart request keywords for explicit detection
    CHART_REQUEST_KEYWORDS = [
        'chart', 'graph', 'visualize', 'visualization', 'plot', 'diagram',
        'show chart', 'generate chart', 'create chart', 'display chart',
        'show graph', 'generate graph', 'pie chart', 'bar chart', 'radar chart'
    ]
    
    def __init__(self):
        pass
    
    def detect_chart_request(self, prompt: str, analysis_content: str = "") -> bool:
        """Restrictive detection - only show charts when user explicitly asks"""
        prompt_lower = prompt.lower()
        
        # Only trigger on EXPLICIT visualization requests
        explicit_chart_keywords = [
            'chart', 'graph', 'visualize', 'visualization', 'plot', 'diagram',
            'show chart', 'generate chart', 'create chart', 'display chart',
            'show graph', 'generate graph', 'create graph', 'display graph',
            'visual', 'dashboard', 'pie chart', 'bar chart', 'line chart',
            'radar chart', 'doughnut chart'
        ]
        
        # Check for explicit chart requests
        for keyword in explicit_chart_keywords:
            if keyword in prompt_lower:
                return True
        
        # Very specific patterns that clearly indicate chart requests
        explicit_patterns = [
            r'show.*chart',
            r'generate.*chart',
            r'create.*chart',
            r'display.*chart',
            r'show.*graph',
            r'generate.*graph',
            r'create.*graph',
            r'display.*graph',
            r'visualiz.*this',
            r'chart.*of',
            r'graph.*of',
            r'plot.*',
            r'dashboard.*view'
        ]
        
        for pattern in explicit_patterns:
            if re.search(pattern, prompt_lower):
                return True
        
        # Do NOT generate charts automatically based on content
        # Only when user explicitly requests visualization
        return False
    
    def extract_risk_data_from_analysis(self, analysis_text: str) -> Dict[str, int]:
        """Extract actual risk assessments from Mike Ross model analysis"""
        text_lower = analysis_text.lower()
        
        # Enhanced risk pattern detection
        high_risk_patterns = [
            r'high risk', r'critical risk', r'severe', r'dangerous', r'problematic',
            r'major concern', r'significant weakness', r'vulnerable', r'exposed',
            r'★☆☆☆☆', r'★★☆☆☆', r'poor', r'weak', r'unfavorable'
        ]
        
        medium_risk_patterns = [
            r'medium risk', r'moderate risk', r'uncertain', r'unclear', r'potential',
            r'mixed', r'variable', r'★★★☆☆', r'average', r'neutral'
        ]
        
        low_risk_patterns = [
            r'low risk', r'minimal risk', r'strong', r'advantage', r'favorable',
            r'solid', r'good', r'positive', r'★★★★★', r'★★★★☆', r'excellent'
        ]
        
        # Count patterns with weights
        high_score = 0
        medium_score = 0
        low_score = 0
        
        for pattern in high_risk_patterns:
            matches = len(re.findall(pattern, text_lower))
            high_score += matches * 3  # Higher weight
        
        for pattern in medium_risk_patterns:
            matches = len(re.findall(pattern, text_lower))
            medium_score += matches * 2
        
        for pattern in low_risk_patterns:
            matches = len(re.findall(pattern, text_lower))
            low_score += matches * 1
        
        # Ensure minimum distribution
        if high_score == 0 and medium_score == 0 and low_score == 0:
            # Default balanced distribution if no patterns found
            return {"high": 20, "medium": 50, "low": 30}
        
        # Convert to percentages
        total = high_score + medium_score + low_score
        return {
            "high": round((high_score / total) * 100) if total > 0 else 0,
            "medium": round((medium_score / total) * 100) if total > 0 else 0,
            "low": round((low_score / total) * 100) if total > 0 else 0
        }
    
    def determine_chart_type(self, data_characteristics: Dict[str, Any], prompt: str) -> str:
        """Intelligently determine chart type based on data and user intent"""
        prompt_lower = prompt.lower()
        
        # Explicit chart type requests
        if any(word in prompt_lower for word in ['pie', 'pie chart']):
            return 'pie'
        elif any(word in prompt_lower for word in ['bar', 'bar chart', 'column']):
            return 'bar'
        elif any(word in prompt_lower for word in ['line', 'line chart', 'trend', 'timeline']):
            return 'line'
        elif any(word in prompt_lower for word in ['radar', 'radar chart', 'spider']):
            return 'radar'
        elif any(word in prompt_lower for word in ['doughnut', 'donut']):
            return 'doughnut'
        
        # Data-driven chart type selection
        data_points = data_characteristics.get('data_points', 0)
        has_categories = data_characteristics.get('has_categories', False)
        has_time_series = data_characteristics.get('has_time_series', False)
        has_risk_levels = data_characteristics.get('has_risk_levels', False)
        
        # Chart type logic
        if has_time_series or any(word in prompt_lower for word in ['over time', 'timeline', 'trend']):
            return 'line'
        elif has_risk_levels and data_points <= 5:
            return 'doughnut'  # Better for risk visualization
        elif has_categories and data_points <= 6:
            return 'pie'
        elif data_points > 6:
            return 'bar'
        else:
            return 'bar'  # Default fallback
    
    
    def generate_dynamic_risk_chart(self, analysis_text: str, prompt: str) -> Dict[str, Any]:
        """Generate dynamic risk chart from actual analysis data"""
        risk_data = self.extract_risk_data_from_analysis(analysis_text)
        
        # Determine chart characteristics
        data_characteristics = {
            'data_points': 3,
            'has_categories': True,
            'has_risk_levels': True,
            'has_time_series': False
        }
        
        chart_type = self.determine_chart_type(data_characteristics, prompt)
        
        # Dynamic color scheme based on risk distribution
        if risk_data['high'] > 50:
            color_scheme = ["#DC2626", "#F59E0B", "#10B981"]  # Red dominant
        elif risk_data['low'] > 50:
            color_scheme = ["#EF4444", "#FBBF24", "#34D399"]  # Green dominant
        else:
            color_scheme = ["#EF4444", "#F59E0B", "#10B981"]  # Balanced
        
        return {
            "type": chart_type,
            "title": "Dynamic Risk Assessment",
            "data": {
                "labels": ["High Risk", "Medium Risk", "Low Risk"],
                "datasets": [{
                    "data": [risk_data['high'], risk_data['medium'], risk_data['low']],
                    "backgroundColor": color_scheme,
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
                        "text": f"Risk Analysis from Mike Ross Model"
                    }
                }
            }
        }
    
    def extract_numerical_data(self, analysis_text: str) -> List[Tuple[str, float]]:
        """Extract numerical data points from analysis text"""
        data_points = []
        
        # Look for percentage patterns
        percentage_matches = re.findall(r'(\w+(?:\s+\w+)*)\s*:?\s*(\d+(?:\.\d+)?)%', analysis_text)
        for label, value in percentage_matches:
            data_points.append((label.strip(), float(value)))
        
        # Look for score patterns
        score_matches = re.findall(r'(\w+(?:\s+\w+)*)\s*:?\s*(\d+(?:\.\d+)?)\s*/\s*(\d+)', analysis_text)
        for label, score, max_score in score_matches:
            percentage = (float(score) / float(max_score)) * 100
            data_points.append((label.strip(), percentage))
        
        # Look for rating patterns (stars)
        star_matches = re.findall(r'(\w+(?:\s+\w+)*)\s*:?\s*(★+)', analysis_text)
        for label, stars in star_matches:
            rating = len(stars)
            percentage = (rating / 5) * 100
            data_points.append((label.strip(), percentage))
        
        return data_points
    
    def generate_charts_for_model(self, model_type: str, analysis_text: str, prompt: str) -> List[Dict[str, Any]]:
        """Generate appropriate charts based on model type and analysis"""
        
        charts = []
        
        if not self.detect_chart_request(prompt, analysis_text):
            return charts  # No charts if user didn't explicitly ask
        
        # Extract numerical data from analysis
        numerical_data = self.extract_numerical_data(analysis_text)
        
        # Always generate dynamic risk chart
        charts.append(self.generate_dynamic_risk_chart(analysis_text, prompt))
        
        # Model-specific additional charts
        if model_type == "case-breaker":
            charts.extend(self.generate_case_breaker_charts(analysis_text, prompt))
        elif model_type == "contract-xray":
            charts.extend(self.generate_contract_charts(analysis_text, prompt))
        elif model_type == "precedent-strategist":
            charts.extend(self.generate_precedent_charts(analysis_text, prompt))
        elif model_type == "deposition-strategist":
            charts.extend(self.generate_deposition_charts(analysis_text, prompt))
        
        return charts
    
    def generate_case_breaker_charts(self, analysis_text: str, prompt: str) -> List[Dict[str, Any]]:
        """Generate Case Breaker specific charts"""
        charts = []
        
        # Strengths vs Weaknesses analysis
        strengths = len(re.findall(r'strength|strong|advantage|favorable|solid|★★★★|★★★★★', analysis_text.lower()))
        weaknesses = len(re.findall(r'weakness|weak|disadvantage|problematic|risk|★☆☆☆☆|★★☆☆☆', analysis_text.lower()))
        
        if strengths > 0 or weaknesses > 0:
            chart_type = self.determine_chart_type({
                'data_points': 2,
                'has_categories': True,
                'has_risk_levels': False
            }, prompt)
            
            charts.append({
                "type": chart_type,
                "title": "Case Strengths vs Weaknesses",
                "data": {
                    "labels": ["Strengths", "Weaknesses"],
                    "datasets": [{
                        "label": "Analysis Count",
                        "data": [strengths, weaknesses],
                        "backgroundColor": ["#10B981", "#EF4444"],
                        "borderColor": ["#059669", "#DC2626"],
                        "borderWidth": 1
                    }]
                },
                "options": {
                    "responsive": True,
                    "scales": {
                        "y": {
                            "beginAtZero": True,
                            "ticks": {"stepSize": 1}
                        }
                    },
                    "plugins": {
                        "title": {
                            "display": True,
                            "text": "Dynamic Case Analysis Overview"
                        }
                    }
                }
            })
        
        return charts
    
    def generate_contract_charts(self, analysis_text: str, prompt: str) -> List[Dict[str, Any]]:
        """Generate Contract X-Ray specific charts"""
        charts = []
        
        # Risk categories analysis
        risk_categories = {
            "Legal Compliance": len(re.findall(r'legal|compliance|regulation|statute', analysis_text.lower())),
            "Financial Risk": len(re.findall(r'financial|money|payment|cost|fee', analysis_text.lower())),
            "Operational Risk": len(re.findall(r'operational|process|delivery|performance', analysis_text.lower())),
            "Liability Risk": len(re.findall(r'liability|responsible|obligation|duty', analysis_text.lower()))
        }
        
        # Only create chart if we found risk data
        total_risks = sum(risk_categories.values())
        if total_risks > 0:
            chart_type = self.determine_chart_type({
                'data_points': len(risk_categories),
                'has_categories': True,
                'has_risk_levels': True
            }, prompt)
            
            charts.append({
                "type": chart_type,
                "title": "Contract Risk Categories",
                "data": {
                    "labels": list(risk_categories.keys()),
                    "datasets": [{
                        "label": "Risk Indicators",
                        "data": list(risk_categories.values()),
                        "backgroundColor": [
                            "#3B82F6", "#10B981", "#F59E0B", "#EF4444"
                        ],
                        "borderWidth": 2
                    }]
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {
                            "display": True,
                            "text": "Dynamic Contract Risk Analysis"
                        }
                    }
                }
            })
        
        return charts
    
    def generate_precedent_charts(self, analysis_text: str, prompt: str) -> List[Dict[str, Any]]:
        """Generate Precedent Strategist specific charts"""
        charts = []
        
        # Extract years from precedent analysis
        years = re.findall(r'\b(19|20)\d{2}\b', analysis_text)
        if years:
            year_counts = {}
            for year in years:
                year_counts[year] = year_counts.get(year, 0) + 1
            
            # Sort by year
            sorted_years = sorted(year_counts.items())
            if len(sorted_years) > 1:  # Only create timeline if multiple years
                chart_type = self.determine_chart_type({
                    'data_points': len(sorted_years),
                    'has_time_series': True,
                    'has_categories': False
                }, prompt)
                
                charts.append({
                    "type": chart_type,
                    "title": "Precedent Timeline",
                    "data": {
                        "labels": [year for year, _ in sorted_years],
                        "datasets": [{
                            "label": "Related Cases",
                            "data": [count for _, count in sorted_years],
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
                                "ticks": {"stepSize": 1}
                            }
                        },
                        "plugins": {
                            "title": {
                                "display": True,
                                "text": "Dynamic Precedent Case Timeline"
                            }
                        }
                    }
                })
        
        return charts
    
    def generate_deposition_charts(self, analysis_text: str, prompt: str) -> List[Dict[str, Any]]:
        """Generate Deposition Strategist specific charts"""
        charts = []
        
        # Credibility analysis
        credibility_data = {
            "High Credibility": len(re.findall(r'credible|reliable|trustworthy|consistent|honest', analysis_text.lower())),
            "Medium Credibility": len(re.findall(r'uncertain|unclear|moderate|mixed', analysis_text.lower())),
            "Low Credibility": len(re.findall(r'inconsistent|unreliable|questionable|problematic', analysis_text.lower()))
        }
        
        total_indicators = sum(credibility_data.values())
        if total_indicators > 0:
            chart_type = self.determine_chart_type({
                'data_points': 3,
                'has_categories': True,
                'has_risk_levels': True
            }, prompt)
            
            charts.append({
                "type": chart_type,
                "title": "Witness Credibility Assessment",
                "data": {
                    "labels": list(credibility_data.keys()),
                    "datasets": [{
                        "data": list(credibility_data.values()),
                        "backgroundColor": [
                            "#10B981", "#F59E0B", "#EF4444"
                        ],
                        "borderWidth": 3,
                        "borderColor": "#ffffff"
                    }]
                },
                "options": {
                    "responsive": True,
                    "cutout": "60%" if chart_type == "doughnut" else None,
                    "plugins": {
                        "legend": {"position": "bottom"},
                        "title": {
                            "display": True,
                            "text": "Dynamic Witness Analysis Results"
                        }
                    }
                }
            })
        
        return charts
    
    def generate_dashboard_charts(self, all_analyses: Dict[str, str]) -> List[Dict[str, Any]]:
        """Generate comprehensive dashboard charts from all model analyses"""
        dashboard_charts = []
        
        # Combined analysis text
        combined_text = ' '.join(all_analyses.values())
        
        # Overall risk distribution across all models
        overall_risk = self.extract_risk_data_from_analysis(combined_text)
        dashboard_charts.append({
            "type": "doughnut",
            "title": "Overall Risk Assessment",
            "data": {
                "labels": ["High Risk", "Medium Risk", "Low Risk"],
                "datasets": [{
                    "data": [overall_risk['high'], overall_risk['medium'], overall_risk['low']],
                    "backgroundColor": ["#EF4444", "#F59E0B", "#10B981"],
                    "borderWidth": 3,
                    "borderColor": "#ffffff"
                }]
            },
            "options": {
                "responsive": True,
                "cutout": "60%",
                "plugins": {
                    "legend": {"position": "bottom"},
                    "title": {
                        "display": True,
                        "text": "Combined Risk Analysis from All Models"
                    }
                }
            }
        })
        
        # Model confidence comparison
        model_scores = {}
        for model, analysis in all_analyses.items():
            positive_indicators = len(re.findall(r'strong|good|favorable|advantage|solid|★★★★|★★★★★', analysis.lower()))
            negative_indicators = len(re.findall(r'weak|poor|problematic|risk|disadvantage|★☆☆☆☆|★★☆☆☆', analysis.lower()))
            
            total_indicators = max(positive_indicators + negative_indicators, 1)
            confidence_score = round((positive_indicators / total_indicators) * 100)
            model_scores[model.replace('-', ' ').title()] = confidence_score
        
        if model_scores:
            dashboard_charts.append({
                "type": "bar",
                "title": "Model Analysis Confidence",
                "data": {
                    "labels": list(model_scores.keys()),
                    "datasets": [{
                        "label": "Confidence Score (%)",
                        "data": list(model_scores.values()),
                        "backgroundColor": [
                            "#3B82F6", "#10B981", "#F59E0B", "#8B5CF6"
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
                            "text": "Dynamic Analysis Confidence by Model"
                        }
                    }
                }
            })
        
        return dashboard_charts

# Global instance
chart_generator = DynamicChartGenerator()
