"""
Mike Ross AI - Analytics API Endpoints
=====================================

FastAPI endpoints for legal analytics and data visualization:
- Dashboard data endpoints
- Chart generation APIs
- Report export functionality
- Real-time metrics streaming
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, List
import json
from services.legal_analytics import LegalAnalytics

# Create analytics router
analytics_router = APIRouter(prefix="/analytics", tags=["Legal Analytics"])

# Initialize analytics engine
analytics_engine = LegalAnalytics()

@analytics_router.get("/dashboard")
async def get_dashboard_data():
    """
    Get comprehensive dashboard data for legal analytics.
    
    Returns:
    - Vector store statistics
    - Case type distribution
    - Risk level metrics
    - Monthly trends
    """
    try:
        vector_stats = analytics_engine.get_vector_store_stats()
        case_data = analytics_engine.analyze_case_types()
        
        return {
            "status": "success",
            "data": {
                "vector_store": vector_stats,
                "case_analytics": case_data,
                "summary": {
                    "total_documents": vector_stats['total_documents'],
                    "total_cases": case_data['total_cases'],
                    "active_collections": len(vector_stats['collections'])
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")

@analytics_router.get("/charts/dashboard")
async def get_dashboard_chart():
    """
    Generate interactive dashboard chart.
    
    Returns HTML with embedded Plotly chart.
    """
    try:
        fig = analytics_engine.create_case_analytics_dashboard()
        html_content = fig.to_html(include_plotlyjs='cdn')
        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chart generation error: {str(e)}")

@analytics_router.get("/charts/risk-heatmap")
async def get_risk_heatmap():
    """
    Generate contract risk analysis heatmap.
    
    Returns HTML with embedded Plotly heatmap.
    """
    try:
        fig = analytics_engine.create_contract_risk_heatmap()
        html_content = fig.to_html(include_plotlyjs='cdn')
        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Heatmap generation error: {str(e)}")

@analytics_router.get("/charts/precedent-network")
async def get_precedent_network():
    """
    Generate legal precedent citation network visualization.
    
    Returns HTML with embedded Plotly network graph.
    """
    try:
        fig = analytics_engine.create_precedent_network()
        html_content = fig.to_html(include_plotlyjs='cdn')
        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Network chart error: {str(e)}")

@analytics_router.get("/charts/model-performance")
async def get_model_performance():
    """
    Generate Mike Ross model performance radar chart.
    
    Returns HTML with embedded Plotly radar chart.
    """
    try:
        fig = analytics_engine.create_model_performance_radar()
        html_content = fig.to_html(include_plotlyjs='cdn')
        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance chart error: {str(e)}")

@analytics_router.get("/metrics")
async def get_legal_metrics():
    """
    Get comprehensive legal metrics and KPIs.
    
    Returns:
    - Total cases and contracts processed
    - Average risk scores
    - Case type distribution
    - Precedent strength analysis
    """
    try:
        metrics = analytics_engine.generate_legal_metrics_report()
        
        return {
            "status": "success",
            "metrics": {
                "total_cases": metrics.total_cases,
                "total_contracts": metrics.total_contracts,
                "avg_risk_score": metrics.avg_risk_score,
                "high_risk_contracts": metrics.high_risk_contracts,
                "case_types": metrics.case_types,
                "monthly_trends": metrics.monthly_trends,
                "precedent_strength": metrics.precedent_strength
            },
            "generated_at": analytics_engine.db.execute("SELECT datetime('now')").scalar()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics error: {str(e)}")

@analytics_router.get("/reports/{format}")
async def export_analytics_report(
    format: str = Query(..., regex="^(html|json)$", description="Report format: html or json")
):
    """
    Export comprehensive analytics report.
    
    Parameters:
    - format: Either 'html' or 'json'
    
    Returns formatted report for download.
    """
    try:
        report_content = analytics_engine.export_analytics_report(format)
        
        if format == 'html':
            return HTMLResponse(
                content=report_content,
                headers={"Content-Disposition": "attachment; filename=legal_analytics_report.html"}
            )
        elif format == 'json':
            return JSONResponse(
                content=json.loads(report_content),
                headers={"Content-Disposition": "attachment; filename=legal_analytics_report.json"}
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report export error: {str(e)}")

@analytics_router.get("/vector-store/stats")
async def get_vector_store_statistics():
    """
    Get detailed vector store statistics.
    
    Returns:
    - Collection information
    - Document counts per collection
    - Storage status and health
    """
    try:
        stats = analytics_engine.get_vector_store_stats()
        return {
            "status": "success",
            "vector_store": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector store stats error: {str(e)}")

@analytics_router.get("/case-analysis/summary")
async def get_case_analysis_summary():
    """
    Get case analysis summary statistics.
    
    Returns:
    - Case type breakdown
    - Risk level distribution  
    - Processing trends
    """
    try:
        case_data = analytics_engine.analyze_case_types()
        return {
            "status": "success",
            "case_analysis": case_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Case analysis error: {str(e)}")

# Health check for analytics service
@analytics_router.get("/health")
async def analytics_health_check():
    """Health check for analytics service"""
    try:
        # Test database connection
        analytics_engine.db.execute("SELECT 1").scalar()
        
        # Test vector store access
        collections = analytics_engine.collections
        
        return {
            "status": "healthy",
            "database": "connected",
            "vector_store": "accessible",
            "collections_available": len(collections),
            "timestamp": analytics_engine.db.execute("SELECT datetime('now')").scalar()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": analytics_engine.db.execute("SELECT datetime('now')").scalar()
        }
