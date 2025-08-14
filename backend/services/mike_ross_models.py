"""
Mike Ross AI Engine - 4 Specialized Legal Models
=================================================

This module implements the 4 core Mike Ross specialized models:
1. Case Breaker - Analyzes case strengths/weaknesses, finds contradictions
2. Contract X-Ray - Deep contract analysis, risk assessment, clause extraction  
3. Deposition Strategist - Witness analysis, inconsistency detection, questioning strategy
4. Precedent Strategist - Legal precedent analysis, argument extraction, similarity mapping

Each model operates on the same RAG foundation but with specialized prompts and logic.
"""

import os
import json
from typing import Dict, List, Any, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from model.watsonx import get_chatwatsonx
from services.retrieval import hybrid_search
import re


class MikeRossModelBase:
    """Base class for all Mike Ross specialized models"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.chat = get_chatwatsonx()
        
    def _get_legal_context(self, query: str, k_cases: int = 5, k_law: int = 5) -> str:
        """Get relevant legal context for any model"""
        hits = hybrid_search(query, k_case_files=k_cases, k_case_law=k_law)
        context_blocks = []
        
        for group, docs in hits.items():
            for d in docs:
                meta = d['metadata']
                source = meta.get('source') or meta.get('filename') or meta.get('hash', '')
                score = d.get('score', 0)
                snippet = d['text'][:600]
                context_blocks.append(f"[{group}] score={score:.3f} source={source}\n{snippet}")
        
        return "\n\n".join(context_blocks) if context_blocks else "No relevant legal context found."


class CaseBreakerModel(MikeRossModelBase):
    """
    Case Breaker - Analyzes legal cases for strengths, weaknesses, and contradictions
    Specializes in: case analysis, strength assessment, weakness identification, contradiction detection
    """
    
    def __init__(self):
        super().__init__("Case Breaker")
        
    def analyze_case(self, case_text: str, case_type: str = "general") -> Dict[str, Any]:
        """Comprehensive case analysis for strengths, weaknesses, and strategy"""
        
        # Simple document metadata without enrichment
        doc_meta = {"case_type": case_type, "analysis_type": "case_breaker"}
        
        # Get relevant precedent
        context = self._get_legal_context(f"{case_type} case law precedent", k_cases=3, k_law=7)
        
        system_prompt = SystemMessage(content=f"""
You are Case Breaker, an elite legal strategist. Analyze cases using structured briefing methodology.

ANALYSIS FRAMEWORK:

1. **CASE BRIEF ELEMENTS**
   - Facts: Key legally relevant facts only
   - Issues: Substantive legal questions (law + key facts)
   - Holdings: Court's legal conclusions
   - Reasoning: Court's analysis and policy rationale

2. **STRATEGIC ASSESSMENT (PROFESSIONAL)**
   For each section below, provide:
   - A numbered list of points
   - A PRIORITY rating: ★★★★★ (critical) to ★☆☆☆☆ (minor)
   - Explicit references to facts, dates, or precedent supporting the point
   - A one-line tactical note on what to do about it

   **ADVANTAGEOUS POSITIONS**:
   - Identify the most compelling legal arguments and fact patterns
   - Highlight precedent that solidly supports these points
   - Explain why these positions are resilient against counter-arguments

   **VULNERABLE POSITIONS**:
   - Pinpoint arguments or facts that expose the case to significant risk
   - Identify evidentiary gaps, procedural missteps, or adverse precedent
   - Suggest targeted measures to reinforce or mitigate each vulnerability

   **CONTRADICTIONS**:
   - List factual, legal, or procedural inconsistencies within the case
   - Indicate potential exploitation angles for opposing counsel
   - Propose clarification or reframing strategies

   **PRECEDENT ANALYSIS**:
   - Explain alignment/deviation from controlling and persuasive precedent
   - Highlight unique aspects of the case that can be leveraged

3. **TACTICAL RECOMMENDATIONS**
   - Present a ranked action list to fortify the case before trial
   - Include pre-trial motions, targeted discovery, or witness preparation
   - Anticipate 2–3 likely moves from opposing counsel and counter them

Be concise but thorough. Prioritize actionable insights over academic discussion.
Be brutally honest—highlight even uncomfortable vulnerabilities.

RELEVANT LEGAL CONTEXT:
{context}
""")

        
        human_prompt = HumanMessage(content=f"""
CASE TYPE: {case_type}

EXTRACTED METADATA:
- Citations: {doc_meta.get('citations', [])}
- Key Acts: {doc_meta.get('acts', [])}  
- Parties: {doc_meta.get('parties', [])}
- Dates: {doc_meta.get('dates', [])}

FULL CASE TEXT:
{case_text}
Provide structured analysis following the framework. Prioritize critical vulnerabilities and strongest arguments.4200 tokens is limit
Execute full-spectrum analysis per partner-level standards. Prioritize actionable insights over academic discussion. Flag all 4-star+ vulnerabilities immediately.
""")
        
        response = self.chat.invoke([system_prompt, human_prompt])
        
        # Parse strengths and weaknesses from response
        content = response.content
        strengths = []
        weaknesses = []
        
        # Simple parsing logic - look for strength/weakness indicators
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['strength', 'strong', 'advantage']):
                current_section = 'strengths'
                if '1.' in line or '-' in line or '•' in line:
                    strengths.append(line)
            elif any(word in line.lower() for word in ['weakness', 'weak', 'vulnerable', 'risk']):
                current_section = 'weaknesses'
                if '1.' in line or '-' in line or '•' in line:
                    weaknesses.append(line)
            elif current_section == 'strengths' and (line.startswith('-') or line.startswith('•') or any(char.isdigit() for char in line[:3])):
                strengths.append(line)
            elif current_section == 'weaknesses' and (line.startswith('-') or line.startswith('•') or any(char.isdigit() for char in line[:3])):
                weaknesses.append(line)
        
        return {
            "model": self.model_name,
            "case_type": case_type,
            "analysis": response.content,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "metadata": doc_meta,
            "context_sources": len(context.split('\n\n')) if context else 0
        }
    
    def find_contradictions(self, document1: str, document2: str) -> Dict[str, Any]:
        """Find contradictions between two legal documents"""
        
        system_prompt = SystemMessage(content="""
You are Case Breaker's contradiction detection engine. Compare two legal documents and identify:
1. **FACTUAL CONTRADICTIONS**: Conflicting statements of fact
2. **LEGAL POSITION CONFLICTS**: Inconsistent legal arguments  
3. **TIMELINE DISCREPANCIES**: Date/sequence conflicts
4. **PARTY STATEMENT CONFLICTS**: Contradictory claims by same parties
5. **PROCEDURAL INCONSISTENCIES**: Conflicting procedural histories

Rate each contradiction: CRITICAL, MODERATE, or MINOR
Provide specific quotes and line references.
""")
        
        human_prompt = HumanMessage(content=f"""
DOCUMENT 1:
{document1}

DOCUMENT 2:  
{document2}

Identify and rate all contradictions between these documents.
""")
        
        response = self.chat.invoke([system_prompt, human_prompt])
        
        return {
            "model": self.model_name,
            "contradiction_analysis": response.content,
            "documents_compared": 2
        }


class ContractXRayModel(MikeRossModelBase):
    """
    Contract X-Ray - Deep contract analysis, risk assessment, clause extraction
    Specializes in: contract review, risk identification, clause analysis, redrafting suggestions
    """
    
    def __init__(self):
        super().__init__("Contract X-Ray")
        
    def analyze_contract(self, contract_text: str, contract_type: str = "general") -> Dict[str, Any]:
        """Comprehensive contract analysis and risk assessment"""
        
        # Get relevant contract law context
        context = self._get_legal_context(f"{contract_type} contract law clauses", k_cases=3, k_law=5)
        
        system_prompt = SystemMessage(content=f"""
You are Contract X-Ray, an expert contract analysis AI specializing in:
- Risk identification and assessment
- Clause-by-clause analysis  
- Legal loophole detection
- Redrafting recommendations
- Compliance verification

Analyze this contract with surgical precision:

1. **RISK ASSESSMENT**: Identify HIGH, MEDIUM, LOW risk clauses
2. **PROBLEMATIC CLAUSES**: Flag unfavorable, ambiguous, or legally questionable terms
3. **MISSING PROTECTIONS**: What standard protections are absent?
4. **COMPLIANCE ISSUES**: Any regulatory or legal compliance problems?
5. **REDRAFT RECOMMENDATIONS**: Specific language improvements for risky clauses
6. **NEGOTIATION POINTS**: Which terms should be renegotiated?

RELEVANT CONTRACT LAW CONTEXT:
{context}
""")
        
        human_prompt = HumanMessage(content=f"""
CONTRACT TYPE: {contract_type}

CONTRACT TEXT:
{contract_text}

Provide comprehensive Contract X-Ray analysis with risk ratings, problematic clauses, and specific redrafting recommendations.
""")
        
        response = self.chat.invoke([system_prompt, human_prompt])
        
        return {
            "model": self.model_name,
            "contract_type": contract_type,
            "analysis": response.content,
            "risk_assessment": "Detailed in analysis",
            "context_sources": len(context.split('\n\n')) if context else 0
        }
    
    def extract_key_clauses(self, contract_text: str) -> Dict[str, Any]:
        """Extract and categorize key contract clauses"""
        
        system_prompt = SystemMessage(content="""
You are Contract X-Ray's clause extraction engine. Extract and categorize ALL key clauses:

**CLAUSE CATEGORIES:**
- Payment Terms
- Termination Conditions  
- Liability Limitations
- Indemnification
- Intellectual Property
- Confidentiality
- Force Majeure
- Dispute Resolution
- Governing Law
- Performance Standards
- Warranties & Representations

For each clause found:
1. Quote the exact text
2. Categorize it
3. Rate risk level (HIGH/MEDIUM/LOW)
4. Note any concerning language
""")
        
        human_prompt = HumanMessage(content=f"""
CONTRACT TEXT:
{contract_text}

Extract and categorize all key clauses with risk ratings.
""")
        
        response = self.chat.invoke([system_prompt, human_prompt])
        
        return {
            "model": self.model_name,
            "clause_extraction": response.content,
            "extraction_type": "key_clauses"
        }


class DepositionStrategistModel(MikeRossModelBase):
    """
    Deposition Strategist - Witness analysis, inconsistency detection, questioning strategy
    Specializes in: witness preparation, deposition strategy, inconsistency detection, questioning tactics
    """
    
    def __init__(self):
        super().__init__("Deposition Strategist")
    
    def analyze_witness_statements(self, witness_statements: List[str], case_context: str = "") -> Dict[str, Any]:
        """Analyze witness statements for inconsistencies and strategic opportunities"""
        
        context = self._get_legal_context(f"witness testimony deposition {case_context}", k_cases=3, k_law=3)
        
        system_prompt = SystemMessage(content=f"""
You are Deposition Strategist, an expert in witness analysis and deposition tactics. Analyze witness statements for:

1. **INCONSISTENCIES**: Compare statements for contradictions
2. **CREDIBILITY GAPS**: Identify implausible or questionable claims  
3. **STRATEGIC VULNERABILITIES**: Where witnesses are most vulnerable to questioning
4. **KEY QUESTIONING AREAS**: Priority topics for deposition focus
5. **CORROBORATION NEEDS**: What needs additional verification
6. **IMPEACHMENT OPPORTUNITIES**: Ways to challenge witness credibility

RELEVANT LEGAL CONTEXT:
{context}
""")
        
        statements_text = "\n\n--- WITNESS STATEMENT ---\n".join(witness_statements)
        
        human_prompt = HumanMessage(content=f"""
CASE CONTEXT: {case_context}

WITNESS STATEMENTS:
{statements_text}

Provide strategic Deposition Strategist analysis focusing on inconsistencies, vulnerabilities, and questioning strategy.
""")
        
        response = self.chat.invoke([system_prompt, human_prompt])
        
        return {
            "model": self.model_name,
            "witnesses_analyzed": len(witness_statements),
            "case_context": case_context,
            "analysis": response.content,
            "context_sources": len(context.split('\n\n')) if context else 0
        }
    
    def generate_deposition_questions(self, witness_profile: str, case_facts: str, objectives: List[str]) -> Dict[str, Any]:
        """Generate strategic deposition questions based on witness profile and case objectives"""
        
        system_prompt = SystemMessage(content="""
You are Deposition Strategist's question generation engine. Create strategic deposition questions that:

1. **ESTABLISH FOUNDATION**: Basic witness credentials and knowledge
2. **LOCK IN TESTIMONY**: Get witness committed to key facts  
3. **EXPLORE VULNERABILITIES**: Probe areas of weakness or uncertainty
4. **IMPEACHMENT SETUP**: Questions that may reveal inconsistencies
5. **CASE OBJECTIVES**: Questions that advance specific legal goals

Format as numbered questions with strategic notes for each question explaining the purpose.
""")
        
        objectives_text = "; ".join(objectives)
        
        human_prompt = HumanMessage(content=f"""
WITNESS PROFILE:
{witness_profile}

CASE FACTS:
{case_facts}

DEPOSITION OBJECTIVES:
{objectives_text}

Generate strategic deposition questions with explanatory notes for each question's purpose.
""")
        
        response = self.chat.invoke([system_prompt, human_prompt])
        
        return {
            "model": self.model_name,
            "witness_profile": witness_profile,
            "objectives": objectives,
            "questions": response.content
        }


class PrecedentStrategistModel(MikeRossModelBase):
    """
    Precedent Strategist - Legal precedent analysis, argument extraction, similarity mapping
    Specializes in: precedent analysis, legal argument crafting, case law strategy, distinguishing cases
    """
    
    def __init__(self):
        super().__init__("Precedent Strategist")
        
    def analyze_precedent_strength(self, current_case: str, legal_issue: str) -> Dict[str, Any]:
        """Analyze precedent strength for a specific legal issue"""
        
        # Get extensive precedent context
        context = self._get_legal_context(legal_issue, k_cases=5, k_law=10)
        
        system_prompt = SystemMessage(content=f"""
You are Precedent Strategist, a master of legal precedent analysis. Evaluate precedent strength for the current case:

1. **BINDING PRECEDENT**: Identify controlling authorities that must be followed
2. **PERSUASIVE PRECEDENT**: Similar cases that support the position
3. **ADVERSE PRECEDENT**: Cases that could hurt the current position  
4. **DISTINGUISHING FACTORS**: How current case differs from adverse precedent
5. **ARGUMENT STRENGTH**: Rate overall precedent support (STRONG/MODERATE/WEAK)
6. **STRATEGIC APPROACH**: Best way to frame legal arguments given precedent landscape

EXTENSIVE LEGAL PRECEDENT CONTEXT:
{context}
""")
        
        human_prompt = HumanMessage(content=f"""
LEGAL ISSUE: {legal_issue}

CURRENT CASE:
{current_case}

Analyze precedent strength and provide strategic recommendations for legal arguments.
""")
        
        response = self.chat.invoke([system_prompt, human_prompt])
        
        return {
            "model": self.model_name,
            "legal_issue": legal_issue,
            "precedent_analysis": response.content,
            "context_sources": len(context.split('\n\n')) if context else 0
        }
    
    def craft_legal_arguments(self, case_facts: str, desired_outcome: str, legal_theories: List[str]) -> Dict[str, Any]:
        """Craft persuasive legal arguments based on precedent and case facts"""
        
        # Get context for each legal theory
        theory_contexts = []
        for theory in legal_theories:
            ctx = self._get_legal_context(theory, k_cases=2, k_law=3)
            theory_contexts.append(f"=== {theory.upper()} PRECEDENT ===\n{ctx}")
        
        combined_context = "\n\n".join(theory_contexts)
        
        system_prompt = SystemMessage(content=f"""
You are Precedent Strategist's argument crafting engine. Create compelling legal arguments that:

1. **INTEGRATE PRECEDENT**: Weave case law seamlessly into factual narrative
2. **ADDRESS COUNTERARGUMENTS**: Anticipate and refute opposing positions
3. **BUILD LOGICAL PROGRESSION**: Structure arguments for maximum persuasive impact  
4. **CITE AUTHORITY**: Reference specific cases and legal principles
5. **CONNECT FACTS TO LAW**: Show how case facts satisfy legal requirements

RELEVANT PRECEDENT BY LEGAL THEORY:
{combined_context}
""")
        
        theories_text = "; ".join(legal_theories)
        
        human_prompt = HumanMessage(content=f"""
CASE FACTS:
{case_facts}

DESIRED OUTCOME:
{desired_outcome}

LEGAL THEORIES TO PURSUE:
{theories_text}

Craft comprehensive legal arguments integrating precedent analysis with case facts.
""")
        
        response = self.chat.invoke([system_prompt, human_prompt])
        
        return {
            "model": self.model_name,
            "desired_outcome": desired_outcome,
            "legal_theories": legal_theories,
            "arguments": response.content,
            "precedent_sources": len(combined_context.split('\n\n')) if combined_context else 0
        }


# Factory class to manage all Mike Ross models
class MikeRossEngine:
    """
    Central engine managing all 4 Mike Ross specialized models
    """
    
    def __init__(self):
        self.case_breaker = CaseBreakerModel()
        self.contract_xray = ContractXRayModel()  
        self.deposition_strategist = DepositionStrategistModel()
        self.precedent_strategist = PrecedentStrategistModel()
        
    def get_model(self, model_name: str):
        """Get specific Mike Ross model by name"""
        models = {
            "case_breaker": self.case_breaker,
            "contract_xray": self.contract_xray,
            "deposition_strategist": self.deposition_strategist,
            "precedent_strategist": self.precedent_strategist
        }
        return models.get(model_name.lower())
    
    def available_models(self) -> List[str]:
        """List all available Mike Ross models"""
        return ["case_breaker", "contract_xray", "deposition_strategist", "precedent_strategist"]
    
    def model_capabilities(self) -> Dict[str, str]:
        """Describe capabilities of each model"""
        return {
            "case_breaker": "Case analysis, strength/weakness assessment, contradiction detection",
            "contract_xray": "Contract analysis, risk assessment, clause extraction, redrafting",
            "deposition_strategist": "Witness analysis, deposition strategy, questioning tactics",
            "precedent_strategist": "Precedent analysis, legal argument crafting, case law strategy"
        }