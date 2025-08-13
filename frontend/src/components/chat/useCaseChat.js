import { useState, useRef, useEffect } from 'react';
import { apiJoin } from '../../config/api';

const generateCaseGuid = () => {
  const s4 = () => Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);
  return `case-guid-${s4()}${s4()}-${s4()}-${s4()}-${s4()}-${s4()}${s4()}${s4()}`;
};

export function useCaseChat() {
  const [selectedModule, setSelectedModule] = useState(null);
  const [caseTitle, setCaseTitle] = useState("");
  const [messages, setMessages] = useState([]); // {role, content}
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const analysisRef = useRef(null);

  useEffect(()=>{
    if (analysisRef.current) {
      analysisRef.current.scrollTop = analysisRef.current.scrollHeight;
    }
  }, [messages]);

  const modules = [
    { id: 'analysis', title: 'Case Breaker', icon: '📊' },
    { id: 'summarize', title: 'Contract X-Ray', icon: '📝' },
    { id: 'translate', title: 'Deposition Strategist', icon: '🌍' },
    { id: 'extract', title: 'Precedent Strategist', icon: '🔍' }
  ];

  const moduleEndpoints = {
    analysis: apiJoin('/analyze/case-breaker'),
    summarize: apiJoin('/analyze/contract-xray'),
    translate: apiJoin('/analyze/deposition-strategist'),
    extract: apiJoin('/analyze/precedent-strategist')
  };

  const ensureCase = () => {
    let active = caseTitle || localStorage.getItem('case_title');
    if (!active) {
      active = generateCaseGuid();
      setCaseTitle(active);
      localStorage.setItem('case_title', active);
    } else if (!caseTitle) {
      setCaseTitle(active);
    }
    return active;
  };

  const sendMessage = async () => {
    if (!input.trim() || !selectedModule) return;
    const userContent = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: userContent }]);
    setInput('');
    setLoading(true);
    setError(null);
    try {
      const activeCase = ensureCase();
      // Build FormData because backend expects Form(...) params
      const fd = new FormData();
      fd.append('user_prompt', userContent);
      fd.append('case_title', activeCase);
      // Optional fields per endpoint (backend has defaults). Customize if needed.
      if (selectedModule === 'summarize') fd.append('contract_type', 'general');
      if (selectedModule === 'translate') fd.append('case_context', 'General legal case');
      if (selectedModule === 'extract') fd.append('legal_issue', 'General legal analysis');
      fd.append('session_id', 'default_session');

      const res = await fetch(moduleEndpoints[selectedModule], {
        method: 'POST',
        body: fd
      });
      if (!res.ok) throw new Error('Request failed');
      const data = await res.json();
      // Prefer envelope style (if later implemented) else fallback to legacy fields
      const analysis = (data.data && (data.data.analysis_markdown || data.data.analysis)) || data.analysis || data.result || data.message || 'No content returned.';
      setMessages(prev => [...prev, { role: 'assistant', content: analysis }]);
    } catch (e) {
      setError('Request failed');
      setMessages(prev => [...prev, { role: 'assistant', content: '**Error:** Unable to process your request.' }]);
    } finally {
      setLoading(false);
    }
  };

  return { selectedModule, setSelectedModule, caseTitle, messages, input, setInput, loading, error, setError, analysisRef, modules, sendMessage };
}
