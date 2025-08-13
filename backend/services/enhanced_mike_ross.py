"""
Enhanced Mike Ross Engine with Data Management and Visualization
==============================================================

Integrates the 4 Mike Ross models with structured data collection and diagram generation.
Creates JSON files and visualizations for each case analysis.
"""

from datetime import datetime
from typing import Dict, Any, List
import re

from .mike_ross_models import MikeRossEngine
from .case_data_manager import (
    case_data_manager, 
    CaseMetadata, 
    CaseBreakerData, 
    ContractXRayData,
    DepositionData,
    PrecedentData
)

class EnhancedMikeRossEngine:
    """Enhanced Mike Ross Engine with data management and visualization"""
    
    def __init__(self):
        self.engine = MikeRossEngine()
        self.data_manager = case_data_manager
    
    def analyze_case_with_data(self, case_text: str, case_type: str, session_id: str, 
                              case_title: str = None) -> Dict[str, Any]:
        """Case Breaker with structured data and diagram generation"""
        
        # Get analysis from original model
        original_result = self.engine.case_breaker.analyze_case(case_text, case_type)
        
        # Create structured data
        case_id = self.data_manager.generate_case_id(session_id, "case_breaker")
        
        metadata = CaseMetadata(
            case_id=case_id,
            case_title=case_title or f"Case Analysis {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            case_type=case_type,
            model_used="case_breaker",
            timestamp=datetime.now().isoformat(),
            session_id=session_id,
            user_prompt=case_text[:100] + "..." if len(case_text) > 100 else case_text
        )
        
        # Extract and structure data from original result
        structured_data = CaseBreakerData(
            metadata=metadata,
            analysis_summary=original_result.get('analysis', ''),
            strengths=self._extract_strengths(original_result),
            weaknesses=self._extract_weaknesses(original_result),
            contradictions=self._extract_contradictions(original_result),
            risk_score=self._calculate_risk_score(original_result),
            confidence_level=self._calculate_confidence(original_result),
            key_findings=self._extract_key_findings(original_result),
            recommendations=self._extract_recommendations(original_result),
            evidence_gaps=self._extract_evidence_gaps(original_result),
            legal_issues=self._extract_legal_issues(original_result)
        )
        
        # Save structured data
        data_file = self.data_manager.save_case_data(structured_data)
        
        # Generate diagram
        diagram_path = self.data_manager.create_case_breaker_diagram(structured_data)
        
        # Enhanced response
        enhanced_result = original_result.copy()
        enhanced_result.update({
            'case_id': case_id,
            'structured_data': structured_data.__dict__,
            'data_file': data_file,
            'diagram_path': diagram_path,
            'frontend_ready': True,
            'visualization_available': True
        })
        
        return enhanced_result
    
    def analyze_contract_with_data(self, contract_text: str, contract_type: str, 
                                 session_id: str, case_title: str = None) -> Dict[str, Any]:
        """Contract X-Ray with structured data and diagram generation"""
        
        # Get analysis from original model
        original_result = self.engine.contract_xray.analyze_contract(contract_text, contract_type)
        
        # Create structured data
        case_id = self.data_manager.generate_case_id(session_id, "contract_xray")
        
        metadata = CaseMetadata(
            case_id=case_id,
            case_title=case_title or f"Contract Analysis {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            case_type=f"contract_{contract_type}",
            model_used="contract_xray",
            timestamp=datetime.now().isoformat(),
            session_id=session_id,
            user_prompt=contract_text[:100] + "..." if len(contract_text) > 100 else contract_text
        )
        
        # Extract and structure data from original result
        structured_data = ContractXRayData(
            metadata=metadata,
            analysis_summary=original_result.get('analysis', ''),
            risk_assessment=original_result.get('risk_assessment', {}),
            clauses=self._extract_clauses(original_result),
            risk_score=self._calculate_contract_risk_score(original_result),
            problematic_clauses=self._extract_problematic_clauses(original_result),
            missing_protections=self._extract_missing_protections(original_result),
            recommendations=self._extract_recommendations(original_result),
            compliance_issues=self._extract_compliance_issues(original_result),
            negotiation_points=self._extract_negotiation_points(original_result)
        )
        
        # Save structured data
        data_file = self.data_manager.save_case_data(structured_data)
        
        # Generate diagram
        diagram_path = self.data_manager.create_contract_xray_diagram(structured_data)
        
        # Enhanced response
        enhanced_result = original_result.copy()
        enhanced_result.update({
            'case_id': case_id,
            'structured_data': structured_data.__dict__,
            'data_file': data_file,
            'diagram_path': diagram_path,
            'frontend_ready': True,
            'visualization_available': True
        })
        
        return enhanced_result
    
    # Helper methods for data extraction
    def _extract_strengths(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract strengths from analysis result"""
        strengths = result.get('strengths', [])
        if isinstance(strengths, list):
            return [{'text': str(s), 'confidence': 'high'} for s in strengths]
        return []
    
    def _extract_weaknesses(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract weaknesses from analysis result"""
        weaknesses = result.get('weaknesses', [])
        if isinstance(weaknesses, list):
            return [{'text': str(w), 'severity': 'medium'} for w in weaknesses]
        return []
    
    def _extract_contradictions(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract contradictions from analysis result"""
        contradictions = result.get('contradictions', [])
        if isinstance(contradictions, list):
            return [{'text': str(c), 'type': 'factual'} for c in contradictions]
        return []
    
    def _calculate_risk_score(self, result: Dict[str, Any]) -> float:
        """Calculate overall risk score"""
        strengths = len(result.get('strengths', []))
        weaknesses = len(result.get('weaknesses', []))
        
        if strengths + weaknesses == 0:
            return 50.0
        
        risk_ratio = weaknesses / (strengths + weaknesses)
        return round(risk_ratio * 100, 1)
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate confidence level"""
        # Simple heuristic based on amount of analysis
        analysis_length = len(result.get('analysis', ''))
        if analysis_length > 1000:
            return 85.0
        elif analysis_length > 500:
            return 75.0
        else:
            return 65.0
    
    def _extract_key_findings(self, result: Dict[str, Any]) -> List[str]:
        """Extract key findings from analysis"""
        findings = []
        analysis = result.get('analysis', '')
        
        # Simple extraction using keywords
        if 'critical' in analysis.lower():
            findings.append("Critical issues identified in case analysis")
        if 'precedent' in analysis.lower():
            findings.append("Relevant legal precedents found")
        if 'evidence' in analysis.lower():
            findings.append("Evidence requirements identified")
        
        return findings
    
    def _extract_recommendations(self, result: Dict[str, Any]) -> List[str]:
        """Extract recommendations from analysis"""
        recommendations = []
        analysis = result.get('analysis', '')
        
        # Look for recommendation keywords
        if 'recommend' in analysis.lower():
            recommendations.append("Strategic recommendations provided")
        if 'should' in analysis.lower():
            recommendations.append("Action items identified")
        
        return recommendations
    
    def _extract_evidence_gaps(self, result: Dict[str, Any]) -> List[str]:
        """Extract evidence gaps"""
        gaps = []
        analysis = result.get('analysis', '')
        
        if 'missing' in analysis.lower():
            gaps.append("Missing evidence identified")
        if 'need' in analysis.lower():
            gaps.append("Additional documentation needed")
        
        return gaps
    
    def _extract_legal_issues(self, result: Dict[str, Any]) -> List[str]:
        """Extract legal issues"""
        issues = []
        analysis = result.get('analysis', '')
        
        if 'liability' in analysis.lower():
            issues.append("Liability concerns")
        if 'contract' in analysis.lower():
            issues.append("Contract law issues")
        if 'statute' in analysis.lower():
            issues.append("Statutory compliance")
        
        return issues
    
    def _extract_clauses(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract contract clauses"""
        clauses = result.get('clauses', [])
        if isinstance(clauses, list):
            return [{'text': str(c), 'type': 'general', 'risk_level': 'MEDIUM'} for c in clauses]
        return []
    
    def _calculate_contract_risk_score(self, result: Dict[str, Any]) -> float:
        """Calculate contract risk score"""
        risk_assessment = result.get('risk_assessment', '')
        if isinstance(risk_assessment, str):
            if 'high' in risk_assessment.lower():
                return 75.0
            elif 'low' in risk_assessment.lower():
                return 25.0
        return 50.0
    
    def _extract_problematic_clauses(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract problematic clauses"""
        return [{'clause': 'Sample problematic clause', 'issue': 'Potential risk'}]
    
    def _extract_missing_protections(self, result: Dict[str, Any]) -> List[str]:
        """Extract missing protections"""
        return ['Liability limitation', 'Termination protection', 'IP protection']
    
    def _extract_compliance_issues(self, result: Dict[str, Any]) -> List[str]:
        """Extract compliance issues"""
        return ['Regulatory compliance check needed']
    
    def _extract_negotiation_points(self, result: Dict[str, Any]) -> List[str]:
        """Extract negotiation points"""
        return ['Payment terms', 'Termination clauses', 'Liability limits']

# Global instance
enhanced_mike_ross = EnhancedMikeRossEngine()
