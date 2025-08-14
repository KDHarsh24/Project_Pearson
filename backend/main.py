from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, Dict, List
import json
import os
import time
from datetime import datetime

# Import the real Mike Ross models
try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from services.mike_ross_models import MikeRossEngine
    from services.chart_generator import chart_generator
    from services.session_manager import session_manager
    REAL_MODELS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import real models: {e}")
    REAL_MODELS_AVAILABLE = False

app = FastAPI(
    title="Mike Ross AI - RAG Paralegal Assistant",
    description="Production-level RAG Paralegal Chatbot with 4 Specialized Legal AI Models",
    version="3.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Mike Ross Engine
if REAL_MODELS_AVAILABLE:
    mike_ross = MikeRossEngine()
else:
    mike_ross = None

# Document storage for uploaded files
uploaded_documents = {}
case_analyses = {}

@app.get("/")
async def root():
    """Welcome endpoint with system information"""
    return {
        "message": "🏛️ Mike Ross AI - RAG Paralegal Assistant",
        "version": "3.0.0",
        "status": "online",
        "real_models": REAL_MODELS_AVAILABLE,
        "features": [
            "📊 Intelligent Chart Generation",
            "📈 Statistical Data Visualization", 
            "🎯 Chart.js Compatible JSON Output",
            "📋 Comprehensive Dashboard Analysis"
        ],
        "models": [
            "Case Breaker - Analyze case strengths & weaknesses",
            "Contract X-Ray - Deep contract analysis",
            "Deposition Strategist - Witness analysis & strategy",
            "Precedent Strategist - Legal precedent research",
            "Dashboard - Run ALL models with statistics"
        ],
        "endpoints": [
            "/upload-document",
            "/models/available", 
            "/analyze/case-breaker",
            "/analyze/contract-xray",
            "/analyze/deposition-strategist",
            "/analyze/precedent-strategist",
            "/analyze/dashboard"
        ],
        "chart_support": {
            "enabled": True,
            "formats": ["pie", "bar", "radar", "line", "doughnut"],
            "framework": "Chart.js compatible",
            "triggers": "Automatic detection when user asks for stats/data"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mike_ross_models": "operational" if REAL_MODELS_AVAILABLE else "mock_mode",
        "message": "RAG Paralegal Assistant is ready!",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    case_title: str = Form(""),
    case_type: str = Form("General Legal"),
    session_id: str = Form("default_session")
):
    """Upload legal document for analysis - now session-based"""
    try:
        # Read file content
        content = await file.read()
        
        # Add document to session with vector storage
        doc_metadata = session_manager.add_document_to_session(
            session_id=session_id,
            file_content=content,
            filename=file.filename,
            case_title=case_title,
            case_type=case_type
        )
        
        return {
            "message": "Document uploaded successfully",
            "document_id": doc_metadata["doc_id"],
            "filename": file.filename,
            "case_title": case_title,
            "case_type": case_type,
            "session_id": session_id,
            "status": "ready",
            "vector_storage": doc_metadata["vector_status"],
            "chunks_created": doc_metadata.get("chunks_count", 0),
            "file_size": doc_metadata["file_size"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/models/available")
async def get_available_models():
    """Get list of available Mike Ross models"""
    return {
        "models": [
            {
                "id": "case-breaker",
                "name": "Case Breaker",
                "description": "Analyze case strengths, weaknesses, and contradictions",
                "best_for": "Case strategy and risk assessment",
                "endpoint": "/analyze/case-breaker",
                "supports_charts": True
            },
            {
                "id": "contract-xray",
                "name": "Contract X-Ray", 
                "description": "Deep contract analysis and risk assessment",
                "best_for": "Contract review and clause analysis",
                "endpoint": "/analyze/contract-xray",
                "supports_charts": True
            },
            {
                "id": "deposition-strategist",
                "name": "Deposition Strategist",
                "description": "Witness analysis and questioning strategy",
                "best_for": "Deposition preparation and witness strategy",
                "endpoint": "/analyze/deposition-strategist",
                "supports_charts": True
            },
            {
                "id": "precedent-strategist",
                "name": "Precedent Strategist",
                "description": "Legal precedent research and argument crafting",
                "best_for": "Legal research and precedent analysis",
                "endpoint": "/analyze/precedent-strategist",
                "supports_charts": True
            },
            {
                "id": "dashboard",
                "name": "Comprehensive Dashboard",
                "description": "Run ALL 4 models and generate statistical dashboard",
                "best_for": "Complete case overview with data visualization",
                "endpoint": "/analyze/dashboard",
                "supports_charts": True,
                "dashboard_mode": True,
                "models_included": ["Case Breaker", "Contract X-Ray", "Deposition Strategist", "Precedent Strategist"]
            }
        ]
    }

def get_session_document_content(session_id: str) -> Optional[str]:
    """Get the most recent document content for a session"""
    documents = session_manager.get_session_documents(session_id)
    if not documents:
        return None
    
    # Get the most recent document
    latest_doc = max(documents, key=lambda x: x['uploaded_at'])
    return session_manager.get_document_content(session_id, latest_doc['doc_id'])

def get_session_document_metadata(session_id: str) -> Optional[Dict]:
    """Get the most recent document metadata for a session"""
    documents = session_manager.get_session_documents(session_id)
    if not documents:
        return None
    
    # Get the most recent document
    return max(documents, key=lambda x: x['uploaded_at'])

def create_case_data_simple(model_type: str, user_prompt: str, analysis: str, 
                          session_id: str, case_title: str = None) -> dict:
    """Create structured case data with session management"""
    case_id = f"case_{int(time.time())}"
    
    # Generate charts if user prompt requests statistical data
    charts = chart_generator.generate_charts_for_model(model_type, analysis, user_prompt)
    has_charts = len(charts) > 0
    
    case_data = {
        "case_id": case_id,
        "session_id": session_id,
        "model_type": model_type,
        "case_title": case_title or f"Case Analysis - {model_type}",
        "user_prompt": user_prompt,
        "analysis": analysis,
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "has_charts": has_charts,
        "charts": charts,
        "metadata": {
            "model": model_type.replace("-", " ").title(),
            "analysis_type": "AI-generated",
            "confidence": "high",
            "chart_count": len(charts)
        }
    }
    
    # Add to session chat history
    session_manager.add_chat_message(
        session_id=session_id,
        message_type="user_prompt",
        content=user_prompt,
        metadata={"model_requested": model_type}
    )
    
    session_manager.add_chat_message(
        session_id=session_id,
        message_type="ai_response",
        content=analysis,
        model_used=model_type,
        metadata={
            "case_id": case_id,
            "has_charts": has_charts,
            "chart_count": len(charts)
        }
    )
    
    # Save to mock storage
    case_analyses[case_id] = case_data
    
    # Save to JSON file
    json_file = f"case_data_{case_id}.json"
    try:
        with open(json_file, 'w') as f:
            json.dump(case_data, f, indent=2)
        case_data["json_file"] = json_file
    except Exception as e:
        print(f"Could not save JSON file: {e}")
        case_data["json_file"] = None
    
    return case_data

@app.post("/analyze/case-breaker")
async def analyze_with_case_breaker(
    user_prompt: str = Form(...),
    case_title: Optional[str] = Form(None),
    session_id: str = Form("default_session")
):
    """Analyze case using Case Breaker model"""
    try:
        # Get document from session
        document_content = get_session_document_content(session_id)
        if not document_content:
            raise HTTPException(status_code=400, detail=f"No document found for session {session_id}. Please upload a document first.")
        
        document_metadata = get_session_document_metadata(session_id)
        case_type = document_metadata.get('case_type', 'general')
        
        # Get session context for better analysis
        session_context = session_manager.get_session_context(session_id)
        
        if REAL_MODELS_AVAILABLE and mike_ross:
            # Use real Mike Ross Case Breaker model with session context
            full_context = f"SESSION CONTEXT:\n{session_context}\n\nUSER QUESTION: {user_prompt}\n\nDOCUMENT CONTENT:\n{document_content}"
            result = mike_ross.case_breaker.analyze_case(
                case_text=full_context,
                case_type=case_type
            )
            analysis = result.get('analysis', 'No analysis available')
        else:
            # Fallback mock analysis
            filename = document_metadata.get('filename', 'document')
            analysis = f"""
**CASE ANALYSIS - CASE BREAKER**

**Document:** {filename}
**User Query:** {user_prompt}
**Session:** {session_id}

**DOCUMENT-SPECIFIC ANALYSIS:**
Based on the uploaded document "{filename}", this appears to be a {case_type} case.

**STRENGTHS:**
• Document provides clear factual foundation
• Legal claims are well-documented in the uploaded file
• Evidence chain appears intact based on document review
• Case type ({case_type}) has favorable precedent patterns
• Session history provides additional context

**WEAKNESSES:**
• Further document discovery may reveal additional complexities
• Opposing counsel may challenge document authenticity
• Timeline constraints may affect case preparation
• Settlement vs litigation cost-benefit needs evaluation

**STRATEGIC RECOMMENDATIONS:**
1. Conduct thorough analysis of the uploaded document for key evidence
2. Cross-reference document facts with legal precedents
3. Prepare for potential document challenges
4. Consider early case evaluation based on document strength
5. Review session history for consistent strategy

**DOCUMENT INSIGHTS:**
The uploaded {case_type} document contains approximately {len(document_content)} characters of legal content that forms the foundation for this analysis.
            """
        
        # Create structured data with session
        case_data = create_case_data_simple("case-breaker", user_prompt, analysis, session_id, case_title)
        
        return {
            "model": "Case Breaker",
            "analysis": analysis,
            "case_id": case_data["case_id"],
            "session_id": session_id,
            "json_file": case_data.get("json_file"),
            "structured_data": case_data,
            "document_analyzed": document_metadata.get('filename', 'N/A'),
            "document_type": case_type,
            "real_model_used": REAL_MODELS_AVAILABLE,
            "has_charts": case_data["has_charts"],
            "charts": case_data["charts"],
            "chart_count": len(case_data["charts"]),
            "diagram_available": case_data["has_charts"],
            "diagram_path": None,
            "frontend_ready": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Case Breaker analysis failed: {str(e)}")

# New session-based endpoints
@app.get("/sessions/list")
async def list_sessions():
    """Get list of all sessions"""
    sessions = session_manager.list_sessions()
    return {
        "sessions": sessions,
        "total": len(sessions),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/sessions/{session_id}")
async def get_session_info(session_id: str):
    """Get session information and documents"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    documents = session_manager.get_session_documents(session_id)
    chat_history = session_manager.get_chat_history(session_id, limit=20)
    
    return {
        "session": session,
        "documents": documents,
        "recent_chat_history": chat_history,
        "summary": {
            "documents_count": len(documents),
            "total_conversations": len(chat_history),
            "last_activity": session.get("last_accessed")
        }
    }

@app.get("/sessions/{session_id}/documents")
async def get_session_documents(session_id: str):
    """Get all documents for a session"""
    documents = session_manager.get_session_documents(session_id)
    if not documents:
        raise HTTPException(status_code=404, detail=f"No documents found for session {session_id}")
    
    return {
        "session_id": session_id,
        "documents": documents,
        "count": len(documents)
    }

@app.get("/sessions/{session_id}/chat-history")
async def get_session_chat_history(session_id: str, limit: int = 50):
    """Get chat history for a session"""
    chat_history = session_manager.get_chat_history(session_id, limit=limit)
    return {
        "session_id": session_id,
        "chat_history": chat_history,
        "count": len(chat_history)
    }

@app.post("/sessions/{session_id}/search")
async def search_session_documents(session_id: str, query: str = Form(...), k: int = Form(5)):
    """Search documents within a session"""
    results = session_manager.search_session_documents(session_id, query, k)
    return {
        "session_id": session_id,
        "query": query,
        "results": results,
        "count": len(results)
    }

@app.post("/analyze/contract-xray")
async def analyze_with_contract_xray(
    user_prompt: str = Form(...),
    contract_type: str = Form("general"),
    case_title: Optional[str] = Form(None),
    session_id: str = Form("default_session")
):
    """Analyze contract using Contract X-Ray model"""
    try:
        # Get document from session
        document_content = get_session_document_content(session_id)
        if not document_content:
            raise HTTPException(status_code=400, detail=f"No document found for session {session_id}. Please upload a document first.")
        
        document_metadata = get_session_document_metadata(session_id)
        session_context = session_manager.get_session_context(session_id)
        
        if REAL_MODELS_AVAILABLE and mike_ross:
            # Use real Mike Ross Contract X-Ray model
            full_context = f"SESSION CONTEXT:\n{session_context}\n\nUSER QUESTION: {user_prompt}\n\nCONTRACT CONTENT:\n{document_content}"
            result = mike_ross.contract_xray.analyze_contract(
                contract_text=full_context,
                contract_type=contract_type
            )
            analysis = result.get('analysis', 'No analysis available')
        else:
            # Fallback mock analysis
            filename = document_metadata.get('filename', 'document')
            analysis = f"""
**CONTRACT ANALYSIS - CONTRACT X-RAY**

**Document:** {filename}
**User Query:** {user_prompt}
**Contract Type:** {contract_type}
**Session:** {session_id}

**DOCUMENT-SPECIFIC ANALYSIS:**
Analyzing the uploaded contract "{filename}" for risk assessment and clause evaluation.

**KEY FINDINGS:**
• Contract length: {len(document_content)} characters suggests comprehensive agreement
• Document type appears to be {contract_type} contract
• User-specific query: "{user_prompt}" requires focused analysis
• Session context provides additional legal background

**RISK FACTORS:**
1. **DOCUMENT-BASED RISKS:** Analysis based on uploaded contract content
2. **CLAUSE COMPLEXITY:** Contract length indicates detailed terms requiring review
3. **USER-SPECIFIC CONCERNS:** Query suggests particular areas of concern
4. **SESSION HISTORY:** Previous analyses inform current risk assessment

**RECOMMENDATIONS:**
• Review the uploaded contract for the specific issues raised in: "{user_prompt}"
• Consider legal counsel for complex clauses identified in document
• Ensure all contractual obligations in uploaded document are clearly understood
• Document any amendments or modifications to original contract
• Reference session history for consistent legal strategy

**CONTRACT INSIGHTS:**
The uploaded contract provides the foundation for this analysis, with particular attention to the user's question about: "{user_prompt}"
            """
        
        case_data = create_case_data_simple("contract-xray", user_prompt, analysis, session_id, case_title)
        
        return {
            "model": "Contract X-Ray",
            "analysis": analysis,
            "case_id": case_data["case_id"],
            "session_id": session_id,
            "json_file": case_data.get("json_file"),
            "structured_data": case_data,
            "document_analyzed": document_metadata.get('filename', 'N/A'),
            "contract_type": contract_type,
            "real_model_used": REAL_MODELS_AVAILABLE,
            "has_charts": case_data["has_charts"],
            "charts": case_data["charts"],
            "chart_count": len(case_data["charts"]),
            "diagram_available": case_data["has_charts"],
            "diagram_path": None,
            "frontend_ready": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Contract X-Ray analysis failed: {str(e)}")

@app.post("/analyze/deposition-strategist")
async def analyze_with_deposition_strategist(
    user_prompt: str = Form(...),
    case_context: Optional[str] = Form("General legal case"),
    case_title: Optional[str] = Form(None),
    session_id: str = Form("default_session")
):
    """Analyze witness statements using Deposition Strategist model"""
    try:
        # Get document from session
        document_content = get_session_document_content(session_id)
        if not document_content:
            raise HTTPException(status_code=400, detail=f"No document found for session {session_id}. Please upload a document first.")
        
        document_metadata = get_session_document_metadata(session_id)
        session_context = session_manager.get_session_context(session_id)
        
        if REAL_MODELS_AVAILABLE and mike_ross:
            # Use real Mike Ross Deposition Strategist model
            full_context = f"SESSION CONTEXT:\n{session_context}\n\nUSER QUESTION: {user_prompt}\n\nDOCUMENT CONTENT:\n{document_content}"
            result = mike_ross.deposition_strategist.analyze_witness_statements(
                witness_statements=[f"USER QUESTION: {user_prompt}\n\nDOCUMENT CONTENT:\n{document_content}"],
                case_context=case_context
            )
            analysis = result.get('analysis', 'No analysis available')
        else:
            # Fallback mock analysis
            filename = document_metadata.get('filename', 'document')
            analysis = f"""
**DEPOSITION STRATEGY - DEPOSITION STRATEGIST**

**Document:** {filename}
**User Query:** {user_prompt}
**Case Context:** {case_context}
**Session:** {session_id}

**DOCUMENT-BASED WITNESS ANALYSIS:**
Analyzing the uploaded document for witness-related information and deposition strategy.

**WITNESS IDENTIFICATION:**
• Document review reveals potential witnesses mentioned in {filename}
• Case context: {case_context}
• User focus: "{user_prompt}"
• Session history informs witness credibility assessment

**QUESTIONING STRATEGY:**
1. **Document Foundation:** Use uploaded document as basis for witness questioning
2. **Key Topics:** Focus on elements raised in user query
3. **Verification Points:** Cross-reference witness statements with document content
4. **Impeachment Material:** Look for inconsistencies between document and testimony
5. **Session Context:** Use previous analyses for consistent questioning approach

**STRATEGIC OBJECTIVES:**
✓ Establish facts documented in uploaded file
✓ Address specific concerns: "{user_prompt}"
✓ Maintain consistency with case context: {case_context}
✓ Identify additional discovery needs from witness testimony
✓ Leverage session history for strategic advantage

**DOCUMENT INSIGHTS:**
The uploaded document provides the factual foundation for deposition strategy, particularly relevant to the user's inquiry about: "{user_prompt}"
            """
        
        case_data = create_case_data_simple("deposition-strategist", user_prompt, analysis, session_id, case_title)
        
        return {
            "model": "Deposition Strategist",
            "analysis": analysis,
            "case_id": case_data["case_id"],
            "session_id": session_id,
            "json_file": case_data.get("json_file"),
            "structured_data": case_data,
            "document_analyzed": document_metadata.get('filename', 'N/A'),
            "case_context": case_context,
            "real_model_used": REAL_MODELS_AVAILABLE,
            "has_charts": case_data["has_charts"],
            "charts": case_data["charts"],
            "chart_count": len(case_data["charts"]),
            "diagram_available": case_data["has_charts"],
            "diagram_path": None,
            "frontend_ready": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deposition Strategist analysis failed: {str(e)}")

@app.post("/analyze/precedent-strategist")
async def analyze_with_precedent_strategist(
    user_prompt: str = Form(...),
    legal_issue: Optional[str] = Form("General legal analysis"),
    case_title: Optional[str] = Form(None),
    session_id: str = Form("default_session")
):
    """Analyze legal precedents using Precedent Strategist model"""
    try:
        # Get the session document
        document = get_session_document_metadata(session_id)
        if not document:
            raise HTTPException(status_code=400, detail="No document uploaded. Please upload a document first.")
        
        document_content = get_session_document_content(session_id)
        
        if REAL_MODELS_AVAILABLE and mike_ross:
            # Use real Mike Ross Precedent Strategist model
            result = mike_ross.precedent_strategist.analyze_precedent_strength(
                current_case=f"USER QUESTION: {user_prompt}\n\nDOCUMENT CONTENT:\n{document_content}",
                legal_issue=legal_issue
            )
            analysis = result.get('precedent_analysis', 'No analysis available')
        else:
            # Fallback mock analysis
            analysis = f"""
**PRECEDENT RESEARCH - PRECEDENT STRATEGIST**

**Document:** {document['filename']}
**User Query:** {user_prompt}
**Legal Issue:** {legal_issue}

**DOCUMENT-BASED PRECEDENT ANALYSIS:**
Analyzing legal precedents relevant to the uploaded document and specific legal issue.

**RELEVANT CASE LAW:**
1. **Document Type Precedents:** Cases similar to the uploaded {document['filename']}
2. **Issue-Specific Cases:** Precedents addressing: {legal_issue}
3. **User Query Precedents:** Case law relevant to: "{user_prompt}"

**LEGAL ARGUMENTS:**
**Primary Argument:** Based on document content and legal issue framework
**Secondary Argument:** Alternative theories supported by precedent
**Distinguishing Factors:** How current case differs from adverse precedent

**STRATEGIC RECOMMENDATIONS:**
1. Leverage document content to support precedent arguments
2. Address legal issue through established case law framework
3. Prepare responses to user's specific concerns: "{user_prompt}"
4. Consider jurisdictional variations in precedent application

**PRECEDENT STRENGTH ASSESSMENT:**
• Document provides factual foundation for precedent application
• Legal issue context: {legal_issue}
• User-specific analysis focus strengthens targeted argument development

**ESTIMATED SUCCESS RATE:** Moderate to High based on document content and precedent alignment
            """
        
        case_data = create_case_data_simple("precedent-strategist", user_prompt, analysis, session_id, case_title)
        
        return {
            "model": "Precedent Strategist",
            "analysis": analysis,
            "case_id": case_data["case_id"],
            "json_file": case_data["json_file"],
            "structured_data": case_data,
            "document_analyzed": document['filename'],
            "legal_issue": legal_issue,
            "real_model_used": REAL_MODELS_AVAILABLE,
            "has_charts": case_data["has_charts"],
            "charts": case_data["charts"],
            "chart_count": len(case_data["charts"]),
            "diagram_available": case_data["has_charts"],
            "diagram_path": None,
            "frontend_ready": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Precedent Strategist analysis failed: {str(e)}")

@app.post("/analyze/dashboard")
async def analyze_dashboard_all_models(
    user_prompt: str = Form(...),
    case_title: Optional[str] = Form(None),
    session_id: str = Form("default_session")
):
    """
    Comprehensive dashboard analysis using ALL 4 Mike Ross models.
    Returns aggregated statistical data and charts for complete case overview.
    """
    try:
        # Get the session document
        document = get_session_document_metadata(session_id)
        if not document:
            raise HTTPException(status_code=400, detail="No document uploaded. Please upload a document first.")
        
        document_content = get_session_document_content(session_id)
        case_type = document.get('case_type', 'general')
        
        if not REAL_MODELS_AVAILABLE or not mike_ross:
            raise HTTPException(status_code=503, detail="Real Mike Ross models not available for dashboard analysis")
        
        # Run all 4 models
        all_analyses = {}
        model_results = {}
        
        print(f"🔍 Dashboard Analysis: Running all 4 models for prompt: {user_prompt[:100]}...")
        
        # 1. Case Breaker Analysis
        try:
            case_result = mike_ross.case_breaker.analyze_case(
                case_text=f"USER QUESTION: {user_prompt}\n\nDOCUMENT CONTENT:\n{document_content}",
                case_type=case_type
            )
            all_analyses["case-breaker"] = case_result.get('analysis', 'No analysis available')
            model_results["case_breaker"] = case_result
        except Exception as e:
            all_analyses["case-breaker"] = f"Case Breaker analysis failed: {str(e)}"
            model_results["case_breaker"] = {"error": str(e)}
        
        # 2. Contract X-Ray Analysis
        try:
            contract_result = mike_ross.contract_xray.analyze_contract(
                contract_text=f"USER QUESTION: {user_prompt}\n\nCONTRACT CONTENT:\n{document_content}",
                contract_type=case_type
            )
            all_analyses["contract-xray"] = contract_result.get('analysis', 'No analysis available')
            model_results["contract_xray"] = contract_result
        except Exception as e:
            all_analyses["contract-xray"] = f"Contract X-Ray analysis failed: {str(e)}"
            model_results["contract_xray"] = {"error": str(e)}
        
        # 3. Deposition Strategist Analysis
        try:
            deposition_result = mike_ross.deposition_strategist.analyze_witness_statements(
                witness_statements=[f"USER QUESTION: {user_prompt}\n\nDOCUMENT CONTENT:\n{document_content}"],
                case_context=case_type
            )
            all_analyses["deposition-strategist"] = deposition_result.get('analysis', 'No analysis available')
            model_results["deposition_strategist"] = deposition_result
        except Exception as e:
            all_analyses["deposition-strategist"] = f"Deposition Strategist analysis failed: {str(e)}"
            model_results["deposition_strategist"] = {"error": str(e)}
        
        # 4. Precedent Strategist Analysis
        try:
            precedent_result = mike_ross.precedent_strategist.analyze_precedent_strength(
                current_case=f"USER QUESTION: {user_prompt}\n\nDOCUMENT CONTENT:\n{document_content}",
                legal_issue=case_type
            )
            all_analyses["precedent-strategist"] = precedent_result.get('precedent_analysis', 'No analysis available')
            model_results["precedent_strategist"] = precedent_result
        except Exception as e:
            all_analyses["precedent-strategist"] = f"Precedent Strategist analysis failed: {str(e)}"
            model_results["precedent_strategist"] = {"error": str(e)}
        
        # Generate comprehensive dashboard charts
        dashboard_charts = chart_generator.generate_dashboard_charts(all_analyses)
        
        # Create comprehensive case data
        dashboard_case_id = f"dashboard_{int(time.time())}"
        
        # Aggregate analysis text
        combined_analysis = f"""
# COMPREHENSIVE LEGAL DASHBOARD ANALYSIS

## Document Analyzed: {document['filename']}
## User Query: {user_prompt}
## Case Type: {case_type}

---

## 🔍 CASE BREAKER ANALYSIS
{all_analyses.get('case-breaker', 'Analysis unavailable')}

---

## 📋 CONTRACT X-RAY ANALYSIS  
{all_analyses.get('contract-xray', 'Analysis unavailable')}

---

## 👥 DEPOSITION STRATEGIST ANALYSIS
{all_analyses.get('deposition-strategist', 'Analysis unavailable')}

---

## ⚖️ PRECEDENT STRATEGIST ANALYSIS
{all_analyses.get('precedent-strategist', 'Analysis unavailable')}

---

## 📊 DASHBOARD SUMMARY

This comprehensive analysis combines insights from all 4 Mike Ross AI models to provide a complete legal perspective on your case. The statistical charts above visualize key metrics and risk assessments across all analytical dimensions.
        """
        
        dashboard_data = {
            "dashboard_id": dashboard_case_id,
            "case_title": case_title or f"Comprehensive Analysis - {document['filename']}",
            "user_prompt": user_prompt,
            "combined_analysis": combined_analysis,
            "individual_analyses": all_analyses,
            "model_results": model_results,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "has_charts": len(dashboard_charts) > 0,
            "charts": dashboard_charts,
            "metadata": {
                "models_used": list(all_analyses.keys()),
                "document_analyzed": document['filename'],
                "case_type": case_type,
                "chart_count": len(dashboard_charts),
                "analysis_type": "comprehensive_dashboard"
            }
        }
        
        # Save dashboard data
        case_analyses[dashboard_case_id] = dashboard_data
        
        # Save to JSON file
        json_file = f"dashboard_analysis_{dashboard_case_id}.json"
        try:
            with open(json_file, 'w') as f:
                json.dump(dashboard_data, f, indent=2)
            dashboard_data["json_file"] = json_file
        except Exception as e:
            print(f"Could not save dashboard JSON file: {e}")
            dashboard_data["json_file"] = None
        
        return {
            "model": "All Mike Ross Models (Dashboard)",
            "analysis": combined_analysis,
            "dashboard_id": dashboard_case_id,
            "json_file": dashboard_data["json_file"],
            "structured_data": dashboard_data,
            "individual_analyses": all_analyses,
            "model_results": model_results,
            "document_analyzed": document['filename'],
            "case_type": case_type,
            "models_used": ["Case Breaker", "Contract X-Ray", "Deposition Strategist", "Precedent Strategist"],
            "real_model_used": True,
            "has_charts": len(dashboard_charts) > 0,
            "charts": dashboard_charts,
            "chart_count": len(dashboard_charts),
            "diagram_available": len(dashboard_charts) > 0,
            "dashboard_analysis": True,
            "frontend_ready": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard analysis failed: {str(e)}")

@app.get("/cases/list")
async def list_cases():
    """Get list of all analyzed cases"""
    return {
        "cases": list(case_analyses.values()),
        "total": len(case_analyses),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/cases/{case_id}")
async def get_case(case_id: str):
    """Get specific case details"""
    if case_id not in case_analyses:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return case_analyses[case_id]

@app.get("/documents/current")
async def get_current_document(session_id: str = "default_session"):
    """Get the most recently uploaded document info for a session"""
    document = get_session_document_metadata(session_id)
    if not document:
        raise HTTPException(status_code=404, detail="No document uploaded for this session")
    
    document_content = get_session_document_content(session_id)
    
    return {
        "filename": document['filename'],
        "case_title": document['case_title'],
        "case_type": document['case_type'],
        "upload_time": document['uploaded_at'],
        "size": document['file_size'],
        "content_preview": document_content[:500] + "..." if len(document_content) > 500 else document_content
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
