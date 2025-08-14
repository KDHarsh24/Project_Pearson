import { useState, useRef, useEffect } from 'react';
import { apiJoin } from '../../config/api';

const generateCaseGuid = () => {
  const s4 = () => Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);
  return `case-guid-${s4()}${s4()}-${s4()}-${s4()}-${s4()}-${s4()}${s4()}${s4()}`;
};

export function useCaseChat() {
  const [selectedModule, setSelectedModule] = useState(null);
  const [caseTitle, setCaseTitle] = useState("");
  const [sessionId, setSessionId] = useState("");
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
    { id: 'analysis', title: 'Case Analyzer', icon: '📊' },
    { id: 'summarize', title: 'Contract Scanner', icon: '📝' },
    { id: 'translate', title: 'Deposition Strategist', icon: '🌍' },
    { id: 'extract', title: 'Precedent Locator', icon: '🔍' }
  ];

  const moduleEndpoints = {
    analysis: apiJoin('/analyze/case-breaker'),
    summarize: apiJoin('/analyze/contract-xray'),
    translate: apiJoin('/analyze/deposition-strategist'),
    extract: apiJoin('/analyze/precedent-strategist')
  };

  const ensureCase = () => {
    let active = caseTitle || localStorage.getItem('session_id') || localStorage.getItem('case_title');
    let session_id = localStorage.getItem('session_id');
    if (!active) {
      active = generateCaseGuid();
      setCaseTitle(active);
      setSessionId(active);
      localStorage.setItem('case_title', active);
      localStorage.setItem('session_id', active);
    } else if (!caseTitle) {
      setCaseTitle(active);
    }
    if (!session_id) {
      session_id = active;
      localStorage.setItem('session_id', session_id);
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
      fd.append('session_id', activeCase);
      // Optional fields per endpoint (backend has defaults). Customize if needed.
      if (selectedModule === 'summarize') fd.append('contract_type', 'general');
      if (selectedModule === 'translate') fd.append('case_context', 'General legal case');
      if (selectedModule === 'extract') fd.append('legal_issue', 'General legal analysis');
      console.log(fd);
      const res = await fetch(moduleEndpoints[selectedModule], {
        method: 'POST',
        body: fd
      });
      if (!res.ok) throw new Error('Request failed');
      const data = await res.json();
      const structured = data?.structured_data || {};
      const analysisMarkdown = (data.data && (data.data.analysis_markdown || data.data.analysis))
        || data.analysis || '';
      const chartsFlag = !!(
        data?.has_charts || structured.has_charts ||
        (Array.isArray(structured.charts) && structured.charts.length) ||
        (Array.isArray(structured.visualizations) && structured.visualizations.length) ||
        (Array.isArray(data?.charts) && data.charts.length) ||
        (Array.isArray(data?.visualizations) && data.visualizations.length)
      );
      const hasStructured = chartsFlag || analysisMarkdown || data?.metadata || structured.metadata;

      // Build conversational quick reply
  let quickReply = data.reply || structured.reply || data.message || data.result || analysisMarkdown;
      if (!quickReply) quickReply = 'Analysis generated.';
      if (quickReply.length > 600) quickReply = quickReply.slice(0, 600) + '…';

      setMessages(prev => {
        const next = [...prev];
        if (hasStructured) {
          try {
            next.push({ role: 'assistant', content: JSON.stringify(data) });
          } catch {
            if (analysisMarkdown && analysisMarkdown !== quickReply) {
              next.push({ role: 'assistant', content: analysisMarkdown });
            }
          }
        }
        return next;
      });
    } catch (e) {
      setError('Request failed');
      setMessages(prev => [...prev, { role: 'assistant', content: '**Error:** Unable to process your request.' }]);
    } finally {
      setLoading(false);
    }
  };

  return { selectedModule, setSelectedModule, caseTitle, messages, input, setInput, loading, error, setError, analysisRef, modules, sendMessage };
}
