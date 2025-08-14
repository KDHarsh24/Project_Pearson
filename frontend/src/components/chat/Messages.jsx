import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  RadialLinearScale,
} from 'chart.js';
import { Bar, Pie, Line, Doughnut, PolarArea, Radar } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  RadialLinearScale,
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

// Enhanced Chart component for rendering different chart types
const ChartComponent = ({ chartData, index }) => {
  const { type, data, options, title, description } = chartData;

  // Default options for better styling
  const defaultOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 20,
          usePointStyle: true,
        }
      },
      title: {
        display: !!title,
        text: title,
        font: {
          size: 14,
          weight: 'bold'
        },
        padding: {
          bottom: 20
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
      }
    }
  };

  // Merge default options with provided options
  const mergedOptions = {
    ...defaultOptions,
    ...options,
    plugins: {
      ...defaultOptions.plugins,
      ...options?.plugins
    }
  };

  // Chart type mapping
  const renderChart = () => {
    switch (type?.toLowerCase()) {
      case 'pie':
        return <Pie data={data} options={mergedOptions} />;
      case 'bar':
        return <Bar data={data} options={mergedOptions} />;
      case 'line':
        return <Line data={data} options={mergedOptions} />;
      case 'doughnut':
        return <Doughnut data={data} options={mergedOptions} />;
      case 'polararea':
        return <PolarArea data={data} options={mergedOptions} />;
      case 'radar':
        return <Radar data={data} options={mergedOptions} />;
      default:
        console.warn(`Unsupported chart type: ${type}`);
        return (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <div className="text-2xl mb-2">📊</div>
              <div className="text-sm">Unsupported chart type: {type}</div>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-4 transition-all hover:shadow-md">
      {title && (
        <div className="mb-3">
          <h3 className="text-sm font-semibold text-gray-900">{title}</h3>
          {description && (
            <p className="text-xs text-gray-600 mt-1">{description}</p>
          )}
        </div>
      )}
      <div className="h-64 w-full">
        {renderChart()}
      </div>
      {/* Chart metadata */}
      <div className="mt-3 pt-3 border-t border-gray-100">
        <div className="flex justify-between items-center text-xs text-gray-500">
          <span>Chart {index + 1}</span>
          <span className="capitalize bg-gray-100 px-2 py-1 rounded-full">
            {type} Chart
          </span>
        </div>
      </div>
    </div>
  );
};

// Function to render assistant messages with enhanced chart support
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

  // Unwrap structured_data if present
  const wrapper = parsedContent?.structured_data || parsedContent;
  // Check if response has charts (multiple possible keys for flexibility)
  const hasCharts = wrapper?.has_charts || (Array.isArray(wrapper?.charts) && wrapper.charts.length > 0) || (Array.isArray(wrapper?.visualizations) && wrapper.visualizations.length > 0);
  const charts = wrapper?.charts || wrapper?.visualizations || [];

  if (hasCharts && charts.length > 0) {
    return (
      <div className="space-y-4">
        
        {/* Analysis Content */}
    {wrapper.analysis && (
          <div className="bg-white/50 rounded-lg border border-gray-100 p-4">
            <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
      {wrapper.analysis}
            </ReactMarkdown>
          </div>
        )}

        {/* Summary if provided */}
    {wrapper.summary && (
          <div className="bg-amber-50/50 rounded-lg border border-amber-100 p-4">
            <h4 className="text-sm font-semibold text-amber-900 mb-2">Executive Summary</h4>
            <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
      {wrapper.summary}
            </ReactMarkdown>
          </div>
        )}

        {/* Charts Section */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-900">Visual Analysis</h3>
            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
              {charts.length} chart{charts.length !== 1 ? 's' : ''}
            </span>
          </div>
          
          {/* Responsive grid for charts */}
          <div className={`grid gap-3 ${
            charts.length === 1 
              ? 'grid-cols-1' 
              : charts.length === 2 
              ? 'grid-cols-1 lg:grid-cols-2' 
              : 'grid-cols-1 md:grid-cols-2 xl:grid-cols-3'
          }`}>
            {charts.map((chart, index) => (
              <ChartComponent key={index} chartData={chart} index={index} />
            ))}
          </div>
        </div>

        {/* Metadata Footer */}
        {wrapper.metadata && (
          <div className="bg-gray-50/50 rounded-lg border border-gray-100 p-3">
            <h4 className="text-xs font-medium text-gray-900 mb-2">Analysis Metadata</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
              {wrapper.metadata.confidence && (
                <div>
                  <span className="text-gray-500">Confidence:</span>
                  <span className={`ml-1 capitalize font-medium ${
                    wrapper.metadata.confidence === 'high' 
                      ? 'text-green-600' 
                      : wrapper.metadata.confidence === 'medium'
                      ? 'text-yellow-600'
                      : 'text-red-600'
                  }`}>
                    {wrapper.metadata.confidence}
                  </span>
                </div>
              )}
              {wrapper.metadata.analysis_type && (
                <div>
                  <span className="text-gray-500">Type:</span>
                  <span className="ml-1 font-medium">{wrapper.metadata.analysis_type}</span>
                </div>
              )}
              {(wrapper.metadata.chart_count || charts.length) && (
                <div>
                  <span className="text-gray-500">Charts:</span>
                  <span className="ml-1 font-medium">{wrapper.metadata.chart_count || charts.length}</span>
                </div>
              )}
              {wrapper.timestamp && (
                <div>
                  <span className="text-gray-500">Generated:</span>
                  <span className="ml-1 font-medium">
                    {new Date(wrapper.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Additional content sections */}
    {wrapper.recommendations && (
          <div className="bg-green-50/50 rounded-lg border border-green-100 p-4">
            <h4 className="text-sm font-semibold text-green-900 mb-2">Recommendations</h4>
            <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
      {wrapper.recommendations}
            </ReactMarkdown>
          </div>
        )}

    {wrapper.warnings && (
          <div className="bg-red-50/50 rounded-lg border border-red-100 p-4">
            <h4 className="text-sm font-semibold text-red-900 mb-2">Warnings</h4>
            <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
      {wrapper.warnings}
            </ReactMarkdown>
          </div>
        )}
      </div>
    );
  }

  // Regular JSON response without charts or plain text
  if (typeof parsedContent === 'object') {
    // Handle structured JSON without charts
    return (
      <div className="space-y-3">
        {Object.entries(parsedContent).map(([key, value]) => (
          <div key={key} className="bg-gray-50/50 rounded-lg border border-gray-100 p-3">
            <h4 className="text-xs font-medium text-gray-900 mb-1 capitalize">
              {key.replace(/_/g, ' ')}
            </h4>
            <div className="text-sm">
              {typeof value === 'string' ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
                  {value}
                </ReactMarkdown>
              ) : (
                <pre className="text-xs bg-white p-2 rounded border overflow-auto">
                  {JSON.stringify(value, null, 2)}
                </pre>
              )}
            </div>
          </div>
        ))}
      </div>
    );
  }

  // Fallback to regular markdown
  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
      {content}
    </ReactMarkdown>
  );
};

export function Messages({ messages, loading, analysisRef }) {
  const hasAssistant = messages.some(m => m.role === 'assistant');
  const endRef = useRef(null);
  
  const scrollToBottom = (smooth = true) => {
    const behavior = smooth ? 'smooth' : 'auto';
    if (endRef.current) {
      try { endRef.current.scrollIntoView({ behavior, block: 'end' }); } catch {}
    }
    if (analysisRef?.current) {
      try { analysisRef.current.scrollTop = analysisRef.current.scrollHeight; } catch {}
    }
  };

  // Scroll on every messages or loading change (primary)
  useEffect(() => {
    scrollToBottom(true);
    // Retry a couple times in case of images/charts sizing late
    const timeouts = [50, 150, 350].map(t => setTimeout(() => scrollToBottom(false), t));
    return () => timeouts.forEach(clearTimeout);
  }, [messages, loading]);

  // Initial mount safety
  useEffect(() => { scrollToBottom(false); }, []);

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
                <span className={`text-[10px] tracking-wide ${isUser ? 'text-blue-500' : 'text-blue-700 font-semibold'}`}>
                  {isUser ? 'You' : 'Mike Ross'}
                </span>
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
        {loading && (
          <div className="mt-6 flex flex-col items-start">
            <div className="flex items-center gap-2 mb-1">
              <img
                src={require('../../image/mikeross.webp')}
                alt="Mike Ross"
                className="h-5 w-5 rounded-full border border-blue-200 shadow"
              />
              <span className="text-[10px] text-blue-700 font-semibold">Mike Ross</span>
            </div>
            <div className="rounded-xl px-4 py-3 md:py-3.5 text-[13px] leading-[1.6] shadow-sm transition-colors max-w-[780px] w-fit bg-white/95 backdrop-blur border border-gray-200 flex items-center gap-2">
              <div className="animate-spin h-4 w-4 border-2 border-blue-300 border-t-blue-600 rounded-full mr-2"></div>
              <span className="animate-pulse text-blue-700 font-medium">Analyzing…</span>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>
    </div>
  );
}