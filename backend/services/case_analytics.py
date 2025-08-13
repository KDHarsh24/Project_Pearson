"""
Case Analytics and JSON Data Management
=====================================

Creates structured JSON files with case statistics and generates relevant diagrams
for each Mike Ross model analysis. Provides frontend-ready data.
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import uuid

# Ensure directories exist
CASE_DATA_DIR = Path("case_data")
DIAGRAMS_DIR = Path("diagrams") 
CASE_DATA_DIR.mkdir(exist_ok=True)
DIAGRAMS_DIR.mkdir(exist_ok=True)

class CaseAnalytics:
    """Manages case data analytics, JSON storage, and diagram generation"""
    
    def __init__(self):
        self.case_data_dir = CASE_DATA_DIR
        self.diagrams_dir = DIAGRAMS_DIR
    
    def create_case_data(self, model_name: str, user_prompt: str, result: Dict[str, Any], 
                        session_id: str, file_info: Optional[Dict] = None) -> str:
        """Creates structured JSON file with all case analytics data"""
        
        case_id = f"{model_name}_{session_id}_{int(datetime.now().timestamp())}"
        
        # Extract key metrics based on model type
        metrics = self._extract_metrics(model_name, result)
        
        # Create comprehensive case data
        case_data = {
            "case_id": case_id,
            "model_used": model_name,
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "user_prompt": user_prompt,
            "uploaded_file": file_info,
            
            # Analysis Results
            "analysis_summary": result.get('analysis', ''),
            "full_result": result,
            
            # Statistical Data
            "metrics": metrics,
            "confidence_score": self._calculate_confidence(result),
            "complexity_score": self._calculate_complexity(user_prompt),
            "risk_indicators": self._extract_risk_indicators(result),
            
            # Key Highlights
            "key_findings": self._extract_key_findings(result),
            "recommendations": self._extract_recommendations(result),
            "important_sections": self._extract_important_sections(result),
            
            # Metadata for Frontend
            "frontend_display": {
                "title": f"{model_name.replace('_', ' ').title()} Analysis",
                "status": "completed",
                "priority": self._determine_priority(metrics),
                "tags": self._generate_tags(model_name, result)
            }
        }
        
        # Save JSON file
        json_path = self.case_data_dir / f"{case_id}.json"
        with open(json_path, 'w') as f:
            json.dump(case_data, f, indent=2)
        
        # Generate diagram
        diagram_path = self._create_diagram(model_name, case_data)
        case_data["diagram_path"] = str(diagram_path)
        
        # Update JSON with diagram path
        with open(json_path, 'w') as f:
            json.dump(case_data, f, indent=2)
        
        return str(json_path)
    
    def _extract_metrics(self, model_name: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract model-specific metrics"""
        
        if model_name == "case_breaker":
            return {
                "strengths_count": len(result.get('strengths', [])),
                "weaknesses_count": len(result.get('weaknesses', [])),
                "contradictions_found": len(result.get('contradictions', [])),
                "evidence_gaps": len(result.get('evidence_gaps', [])),
                "legal_issues": len(result.get('legal_issues', []))
            }
        
        elif model_name == "contract_xray":
            return {
                "clauses_analyzed": len(result.get('clauses', [])),
                "risk_level": result.get('risk_level', 'medium'),
                "problematic_clauses": len([c for c in result.get('clauses', []) if c.get('risk', '') == 'high']),
                "recommendations_count": len(result.get('recommendations', []))
            }
        
        elif model_name == "deposition_strategist":
            return {
                "witnesses_analyzed": len(result.get('witnesses', [])),
                "inconsistencies_found": len(result.get('inconsistencies', [])),
                "key_questions": len(result.get('key_questions', [])),
                "strategy_points": len(result.get('strategy_points', []))
            }
        
        elif model_name == "precedent_strategist":
            return {
                "precedents_found": len(result.get('precedents', [])),
                "citations_count": len(result.get('citations', [])),
                "legal_theories": len(result.get('legal_theories', [])),
                "argument_strength": result.get('argument_strength', 'medium')
            }
        
        return {}
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate confidence score based on result quality"""
        score = 0.5  # base score
        
        # Increase confidence based on content richness
        if result.get('analysis') and len(result['analysis']) > 100:
            score += 0.2
        
        if result.get('context_sources'):
            score += 0.1 * min(len(result['context_sources']), 3)
        
        # Model-specific confidence factors
        if 'strengths' in result and 'weaknesses' in result:
            score += 0.1
        
        if 'precedents' in result and len(result['precedents']) > 0:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_complexity(self, user_prompt: str) -> float:
        """Calculate complexity score based on prompt analysis"""
        words = len(user_prompt.split())
        legal_terms = sum(1 for word in user_prompt.lower().split() 
                         if word in ['contract', 'clause', 'liability', 'breach', 'damages', 'precedent'])
        
        complexity = min((words / 100) + (legal_terms / 10), 1.0)
        return complexity
    
    def _extract_risk_indicators(self, result: Dict[str, Any]) -> List[str]:
        """Extract risk indicators from analysis"""
        risks = []
        
        if 'weaknesses' in result:
            risks.extend([w.get('description', str(w))[:100] for w in result['weaknesses'][:3]])
        
        if 'risk_assessment' in result:
            risks.append(f"Risk Level: {result['risk_assessment']}")
        
        if 'contradictions' in result and len(result['contradictions']) > 0:
            risks.append(f"Contradictions found: {len(result['contradictions'])}")
        
        return risks
    
    def _extract_key_findings(self, result: Dict[str, Any]) -> List[str]:
        """Extract key findings for frontend display"""
        findings = []
        
        if 'strengths' in result:
            findings.extend([s.get('description', str(s))[:100] for s in result['strengths'][:2]])
        
        if 'key_points' in result:
            findings.extend(result['key_points'][:3])
        
        if 'precedents' in result and len(result['precedents']) > 0:
            findings.append(f"Found {len(result['precedents'])} relevant precedents")
        
        return findings
    
    def _extract_recommendations(self, result: Dict[str, Any]) -> List[str]:
        """Extract actionable recommendations"""
        recommendations = []
        
        if 'recommendations' in result:
            recommendations.extend(result['recommendations'][:3])
        
        if 'next_steps' in result:
            recommendations.extend(result['next_steps'][:2])
        
        if 'strategy' in result:
            recommendations.append(f"Strategy: {result['strategy'][:100]}")
        
        return recommendations
    
    def _extract_important_sections(self, result: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract important text sections with labels"""
        sections = []
        
        if 'analysis' in result and len(result['analysis']) > 200:
            sections.append({
                "label": "Main Analysis",
                "content": result['analysis'][:300] + "..." if len(result['analysis']) > 300 else result['analysis']
            })
        
        if 'legal_strategy' in result:
            sections.append({
                "label": "Legal Strategy", 
                "content": result['legal_strategy'][:200] + "..." if len(result['legal_strategy']) > 200 else result['legal_strategy']
            })
        
        return sections
    
    def _determine_priority(self, metrics: Dict[str, Any]) -> str:
        """Determine case priority based on metrics"""
        risk_factors = 0
        
        if metrics.get('contradictions_found', 0) > 2:
            risk_factors += 2
        if metrics.get('weaknesses_count', 0) > 3:
            risk_factors += 1
        if metrics.get('problematic_clauses', 0) > 1:
            risk_factors += 2
        
        if risk_factors >= 3:
            return "high"
        elif risk_factors >= 1:
            return "medium"
        else:
            return "low"
    
    def _generate_tags(self, model_name: str, result: Dict[str, Any]) -> List[str]:
        """Generate relevant tags for categorization"""
        tags = [model_name.replace('_', '-')]
        
        if 'contract' in str(result).lower():
            tags.append('contract')
        if 'employment' in str(result).lower():
            tags.append('employment')
        if 'liability' in str(result).lower():
            tags.append('liability')
        if 'precedent' in str(result).lower():
            tags.append('precedent')
        
        return tags
    
    def _create_diagram(self, model_name: str, case_data: Dict[str, Any]) -> Path:
        """Create relevant diagram based on model type"""
        
        case_id = case_data['case_id']
        metrics = case_data['metrics']
        
        if model_name == "case_breaker":
            return self._create_case_analysis_chart(case_id, metrics)
        elif model_name == "contract_xray":
            return self._create_risk_assessment_chart(case_id, metrics)
        elif model_name == "deposition_strategist":
            return self._create_witness_analysis_chart(case_id, metrics)
        elif model_name == "precedent_strategist":
            return self._create_precedent_network_chart(case_id, metrics)
        
        return self._create_generic_chart(case_id, metrics)
    
    def _create_case_analysis_chart(self, case_id: str, metrics: Dict[str, Any]) -> Path:
        """Create case strengths vs weaknesses chart"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Strengths vs Weaknesses
        categories = ['Strengths', 'Weaknesses', 'Contradictions', 'Evidence Gaps']
        values = [
            metrics.get('strengths_count', 0),
            metrics.get('weaknesses_count', 0), 
            metrics.get('contradictions_found', 0),
            metrics.get('evidence_gaps', 0)
        ]
        
        colors = ['green', 'red', 'orange', 'purple']
        ax1.bar(categories, values, color=colors, alpha=0.7)
        ax1.set_title('Case Analysis Breakdown')
        ax1.set_ylabel('Count')
        
        # Risk pie chart
        risk_data = [max(1, v) for v in values]  # Avoid zero values
        ax2.pie(risk_data, labels=categories, colors=colors, autopct='%1.1f%%')
        ax2.set_title('Risk Distribution')
        
        plt.tight_layout()
        diagram_path = self.diagrams_dir / f"{case_id}_case_analysis.png"
        plt.savefig(diagram_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return diagram_path
    
    def _create_risk_assessment_chart(self, case_id: str, metrics: Dict[str, Any]) -> Path:
        """Create contract risk assessment visualization"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Risk levels
        risk_categories = ['Low Risk', 'Medium Risk', 'High Risk']
        total_clauses = metrics.get('clauses_analyzed', 1)
        problematic = metrics.get('problematic_clauses', 0)
        
        low_risk = max(0, total_clauses - problematic * 2)
        medium_risk = max(0, total_clauses - problematic - low_risk)
        high_risk = problematic
        
        values = [low_risk, medium_risk, high_risk]
        colors = ['green', 'yellow', 'red']
        
        bars = ax.bar(risk_categories, values, color=colors, alpha=0.7)
        ax.set_title('Contract Risk Assessment')
        ax.set_ylabel('Number of Clauses')
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value}', ha='center', va='bottom')
        
        plt.tight_layout()
        diagram_path = self.diagrams_dir / f"{case_id}_risk_assessment.png"
        plt.savefig(diagram_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return diagram_path
    
    def _create_witness_analysis_chart(self, case_id: str, metrics: Dict[str, Any]) -> Path:
        """Create witness analysis chart"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        categories = ['Witnesses', 'Inconsistencies', 'Key Questions', 'Strategy Points']
        values = [
            metrics.get('witnesses_analyzed', 0),
            metrics.get('inconsistencies_found', 0),
            metrics.get('key_questions', 0),
            metrics.get('strategy_points', 0)
        ]
        
        x = np.arange(len(categories))
        bars = ax.bar(x, values, color=['blue', 'red', 'green', 'purple'], alpha=0.7)
        
        ax.set_xlabel('Analysis Categories')
        ax.set_ylabel('Count')
        ax.set_title('Witness Analysis Summary')
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45)
        
        # Add value labels
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value}', ha='center', va='bottom')
        
        plt.tight_layout()
        diagram_path = self.diagrams_dir / f"{case_id}_witness_analysis.png"
        plt.savefig(diagram_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return diagram_path
    
    def _create_precedent_network_chart(self, case_id: str, metrics: Dict[str, Any]) -> Path:
        """Create precedent analysis chart"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Precedent strength
        precedents = metrics.get('precedents_found', 0)
        citations = metrics.get('citations_count', 0)
        theories = metrics.get('legal_theories', 0)
        
        categories = ['Precedents', 'Citations', 'Legal Theories']
        values = [precedents, citations, theories]
        
        ax1.bar(categories, values, color=['blue', 'green', 'orange'], alpha=0.7)
        ax1.set_title('Precedent Analysis')
        ax1.set_ylabel('Count')
        
        # Argument strength gauge
        strength_map = {'weak': 1, 'medium': 2, 'strong': 3}
        strength = strength_map.get(metrics.get('argument_strength', 'medium'), 2)
        
        # Create a simple gauge chart
        angles = np.linspace(0, np.pi, 100)
        x = np.cos(angles)
        y = np.sin(angles)
        
        ax2.plot(x, y, 'k-', linewidth=2)
        ax2.fill_between(x[:int(strength*33)], y[:int(strength*33)], alpha=0.3, 
                        color=['red', 'yellow', 'green'][strength-1])
        ax2.set_xlim(-1.1, 1.1)
        ax2.set_ylim(0, 1.1)
        ax2.set_title('Argument Strength')
        ax2.axis('equal')
        ax2.axis('off')
        
        plt.tight_layout()
        diagram_path = self.diagrams_dir / f"{case_id}_precedent_analysis.png"
        plt.savefig(diagram_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return diagram_path
    
    def _create_generic_chart(self, case_id: str, metrics: Dict[str, Any]) -> Path:
        """Create generic analysis chart"""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        if metrics:
            categories = list(metrics.keys())[:5]  # Limit to 5 items
            values = [metrics[cat] if isinstance(metrics[cat], (int, float)) else len(str(metrics[cat])) 
                     for cat in categories]
            
            ax.bar(categories, values, color='skyblue', alpha=0.7)
            ax.set_title('Analysis Summary')
            ax.set_ylabel('Values')
            
            # Rotate labels if needed
            if len(max(categories, key=len)) > 10:
                plt.xticks(rotation=45)
        else:
            ax.text(0.5, 0.5, 'Analysis Complete\nNo Metrics Available', 
                   ha='center', va='center', fontsize=16)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        
        plt.tight_layout()
        diagram_path = self.diagrams_dir / f"{case_id}_analysis.png"
        plt.savefig(diagram_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return diagram_path
    
    def get_case_data(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve case data by ID"""
        json_path = self.case_data_dir / f"{case_id}.json"
        if json_path.exists():
            with open(json_path, 'r') as f:
                return json.load(f)
        return None
    
    def list_recent_cases(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent cases with summary info"""
        case_files = sorted(self.case_data_dir.glob("*.json"), 
                           key=lambda x: x.stat().st_mtime, reverse=True)
        
        cases = []
        for file_path in case_files[:limit]:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    cases.append({
                        'case_id': data['case_id'],
                        'model_used': data['model_used'],
                        'timestamp': data['timestamp'],
                        'confidence_score': data['confidence_score'],
                        'priority': data['frontend_display']['priority']
                    })
            except:
                continue
        
        return cases

# Global instance
case_analytics = CaseAnalytics()
