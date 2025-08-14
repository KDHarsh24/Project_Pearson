import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

// Lightweight code block with copy button & nicer styling
function CodeBlock({ inline, className, children, ...props }) {
  const text = String(children).replace(/\n$/, '');
  if (inline) {
    return (
      <code className="px-1.5 py-0.5 rounded-md bg-gray-200 text-gray-800 text-[12px] font-mono border border-gray-300">
        {text}
      </code>
    );
  }
  const lang = /language-(\w+)/.exec(className || '')?.[1];
  const handleCopy = () => {
    navigator.clipboard?.writeText(text).catch(()=>{});
  };
  return (
    <div className="group relative my-4 first:mt-0 last:mb-0">
      <pre className="overflow-x-auto max-h-[480px] scrollbar-thin scrollbar-track-transparent scrollbar-thumb-gray-300 text-[13px] leading-relaxed font-mono rounded-lg border border-gray-300 bg-gradient-to-br from-gray-50 to-gray-100 p-4 shadow-sm">
        <code className={`block ${lang ? `language-${lang}` : ''}`}>{text}</code>
      </pre>
      <button onClick={handleCopy} type="button" className="opacity-0 group-hover:opacity-100 transition-opacity absolute top-2 right-2 text-[10px] tracking-wide px-2 py-1 rounded-md bg-white/80 backdrop-blur border border-gray-300 shadow hover:bg-white active:scale-[0.97]">
        Copy
      </button>
    </div>
  );
}

// Markdown component overrides to tighten spacing & polish look
const mdComponents = {
  p: ({ children }) => <p className="mb-2 last:mb-0 leading-[1.55] whitespace-pre-wrap">{children}</p>,
  ul: ({ children }) => <ul className="list-disc ml-5 mb-1 space-y-1 marker:text-gray-500">{children}</ul>,
  ol: ({ children }) => <ol className="list-decimal ml-5 mb-3 space-y-1 marker:text-gray-500">{children}</ol>,
  li: ({ children }) => <li className="pl-1">{children}</li>,
  blockquote: ({ children }) => (
    <blockquote className="border-l-4 border-blue-300/70 bg-blue-50/60 px-4 py-2 rounded-r-md shadow-sm text-[13px] italic mb-4 last:mb-0">{children}</blockquote>
  ),
  table: ({ children }) => (
    <div className="my-4 overflow-x-auto rounded-lg border border-gray-200 shadow-sm">{children}</div>
  ),
  thead: ({ children }) => <thead className="bg-gray-100 text-gray-700">{children}</thead>,
  th: ({ children }) => <th className="text-left text-[12px] font-semibold px-3 py-2 border-b border-gray-200">{children}</th>,
  td: ({ children }) => <td className="align-top text-[12px] px-3 py-2 border-b border-gray-100">{children}</td>,
  hr: () => <hr className="my-6 border-gray-200" />,
  h1: ({ children }) => <h1 className="mt-3 mb-3 text-lg font-semibold tracking-tight">{children}</h1>,
  h2: ({ children }) => <h2 className="mt-2 mb-3 text-[18px] font-semibold tracking-tight text-[#1d4ed8]">{children}</h2>,
  h3: ({ children }) => <h3 className="mt-6 mb-2 text-[14px] font-bold tracking-tight text-gray-700">{children}</h3>,
  a: ({ children, href }) => (
    <a href={href} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline decoration-[1.5px] underline-offset-2">{children}</a>
  ),
  code: CodeBlock
};

// Chart component for rendering different chart types
const ChartComponent = ({ chartData }) => {
  const { type, data, options, title } = chartData;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-4">
      <h3 className="text-sm font-semibold text-gray-900 mb-3">{title}</h3>
      <div className="h-64">
        {type === 'pie' && <Pie data={data} options={options} />}
        {type === 'bar' && <Bar data={data} options={options} />}
        {type === 'doughnut' && <Pie data={data} options={options} />}
      </div>
    </div>
  );
};

// Function to render assistant messages with chart support
const renderAssistantMessage = (content) => {
  // Try to parse as JSON (structured response with charts)
  let parsedContent;
  try {
    parsedContent = JSON.parse(content);
  } catch {
    // If not JSON, treat as regular markdown
    return (
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
        {content}
      </ReactMarkdown>
    );
  }

  // If it's a structured response with charts
  if (parsedContent && parsedContent.has_charts && parsedContent.charts) {
    return (
      <div className="space-y-4">
        {/* Response Header */}
        <div className="bg-blue-50/50 rounded-lg border border-blue-100 p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-semibold text-gray-900">
              {parsedContent.case_title || 'Analysis Results'}
            </h2>
            {parsedContent.status && (
              <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                {parsedContent.status}
              </span>
            )}
          </div>
          {parsedContent.case_id && (
            <p className="text-xs text-gray-600 mb-1">
              <strong>Case ID:</strong> {parsedContent.case_id}
            </p>
          )}
          {parsedContent.model_type && (
            <p className="text-xs text-gray-600 mb-1">
              <strong>Model:</strong> {parsedContent.model_type}
            </p>
          )}
          {parsedContent.user_prompt && (
            <p className="text-xs text-gray-600">
              <strong>User Prompt:</strong> {parsedContent.user_prompt}
            </p>
          )}
        </div>

        {/* Analysis Content */}
        {parsedContent.analysis && (
          <div className="bg-white/50 rounded-lg border border-gray-100 p-4">
            <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
              {parsedContent.analysis}
            </ReactMarkdown>
          </div>
        )}

        {/* Charts Section */}
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-gray-900">Visual Analysis</h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            {parsedContent.charts.map((chart, index) => (
              <ChartComponent key={index} chartData={chart} />
            ))}
          </div>
        </div>

        {/* Metadata */}
        {parsedContent.metadata && (
          <div className="bg-gray-50/50 rounded-lg border border-gray-100 p-3">
            <h4 className="text-xs font-medium text-gray-900 mb-2">Analysis Metadata</h4>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <span className="text-gray-500">Confidence:</span>
                <span className="ml-1 capitalize font-medium">{parsedContent.metadata.confidence}</span>
              </div>
              <div>
                <span className="text-gray-500">Analysis Type:</span>
                <span className="ml-1 font-medium">{parsedContent.metadata.analysis_type}</span>
              </div>
              <div>
                <span className="text-gray-500">Charts Generated:</span>
                <span className="ml-1 font-medium">{parsedContent.metadata.chart_count}</span>
              </div>
              {parsedContent.timestamp && (
                <div>
                  <span className="text-gray-500">Timestamp:</span>
                  <span className="ml-1 font-medium">{new Date(parsedContent.timestamp).toLocaleString()}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    );
  }

  // Regular JSON response without charts
  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
      {content}
    </ReactMarkdown>
  );
};

export function Messages({ messages, loading, analysisRef }) {
  const hasAssistant = messages.some(m => m.role === 'assistant');
  const endRef = useRef(null);
  useEffect(() => {
    if (analysisRef?.current && analysisRef.current.scrollHeight > 0) {
      try { analysisRef.current.scrollTo({ top: analysisRef.current.scrollHeight, behavior: 'smooth' }); } catch { /* no-op */ }
    }
    if (endRef.current) {
      endRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [messages, loading, analysisRef]);
  if (!hasAssistant) return null;

  return (
    <div ref={analysisRef} className="mt-4 px-3 md:px-4 pb-2">
      <div className="flex flex-col max-w-4xl mx-auto">
        {messages.map((m, idx) => {
          const isUser = m.role === 'user';
          const prevRole = idx > 0 ? messages[idx - 1].role : null;
          const gapClass = prevRole === null ? 'mt-0' : prevRole === m.role ? 'mt-3' : 'mt-6';
          return (
            <div key={idx} className={`${gapClass} flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
              <div className="flex items-center gap-2 mb-1">
                {!isUser && (
                  <img
                    src={require('../../image/mikeross.webp')}
                    alt="Mike Ross"
                    className="h-5 w-5 rounded-full border border-blue-200 shadow"
                  />
                )}
                <span className={`text-[10px] tracking-wide ${isUser ? 'text-blue-500' : 'text-blue-700 font-semibold'}`}>{isUser ? 'You' : 'Mike Ross'}</span>
              </div>
              <div
                className={`group rounded-xl px-4 py-3 md:py-3.5 text-[13px] leading-[1.6] shadow-sm transition-colors max-w-[780px] w-fit ${
                  isUser
                    ? 'bg-gradient-to-tr from-blue-600 to-blue-500 text-white border border-blue-400/50'
                    : 'bg-white/95 backdrop-blur border border-gray-200'
                }`}
                style={isUser ? { borderTopRightRadius: 0, minWidth: '116px' } : { borderTopLeftRadius: 0 }}
              >
                {isUser ? (
                  <span className="whitespace-pre-wrap block">{m.content}</span>
                ) : (
                  renderAssistantMessage(m.content)
                )}
              </div>
            </div>
          );
        })}
        {loading && <p className="mt-4 text-xs text-gray-500 animate-pulse">Thinking...</p>}
        <div ref={endRef} />
      </div>
    </div>
  );
}
