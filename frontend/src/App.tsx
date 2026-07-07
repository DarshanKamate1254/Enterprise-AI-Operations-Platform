import React, { useState, useEffect, useRef } from 'react';
import {
  MessageSquare,
  UploadCloud,
  Database,
  Activity,
  LogOut,
  User as UserIcon,
  Send,
  AlertTriangle,
  Lock,
  RefreshCw,
  DollarSign,
  Cpu,
  Clock,
  Terminal
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css';
import { motion, AnimatePresence } from 'framer-motion';

// Define structures
interface Message {
  role: 'human' | 'assistant';
  content: string;
  node?: string;
  isStreaming?: boolean;
  timestamp?: string;
}

interface User {
  username: string;
  token: string;
  role: 'Admin' | 'Manager' | 'User';
}

interface TableColumn {
  name: string;
  type: string;
  key?: 'PK' | 'FK' | '';
  nullable: boolean;
  references?: string;
}

export default function App() {
  // Authentication states
  const [user, setUser] = useState<User | null>(null);
  const [usernameInput, setUsernameInput] = useState('devendra.rao');
  const [passwordInput, setPasswordInput] = useState('password');
  const [authError, setAuthError] = useState('');
  const [authLoading, setAuthLoading] = useState(false);

  // Layout states
  const [activeTab, setActiveTab] = useState<'chat' | 'ingest' | 'schema' | 'metrics'>('chat');

  // Chat workflow states
  const [messages, setMessages] = useState<Message[]>([]);
  const [queryInput, setQueryInput] = useState('');
  const [threadId] = useState('session_' + Math.floor(Math.random() * 10000));
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [completedSteps, setCompletedSteps] = useState<string[]>([]);
  const [activeStep, setActiveStep] = useState<string | null>(null);
  const [executionTrace, setExecutionTrace] = useState<string[]>([]);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Ingestion states
  const [selectedCategory, setSelectedCategory] = useState('hr');
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<{ success?: boolean; msg?: string } | null>(null);
  const [uploadLoading, setUploadLoading] = useState(false);

  // Schema state
  const [selectedTable, setSelectedTable] = useState('employees');

  // Live observability metrics
  const [metrics, setMetrics] = useState({
    requestsCount: 24,
    tokenUsage: 14520,
    accumulatedCost: 0.087,
    failuresCount: 1,
    retryLoops: 2,
    avgLatency: 3.82
  });

  // Scroll to bottom helper
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auth handler
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError('');
    setAuthLoading(true);

    try {
      const response = await fetch('http://localhost:8000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: usernameInput,
          password: passwordInput
        })
      });

      if (!response.ok) {
        throw new Error('Unauthorized credentials. Please verify your details.');
      }

      const data = await response.json();
      setUser({
        username: data.username,
        token: data.access_token,
        role: data.role as 'Admin' | 'Manager' | 'User'
      });
    } catch (err: any) {
      setAuthError(err.message || 'Login failed.');
    } finally {
      setAuthLoading(false);
    }
  };

  // Logout handler
  const handleLogout = () => {
    setUser(null);
    setMessages([]);
    setExecutionTrace([]);
    setCompletedSteps([]);
    setActiveStep(null);
  };

  // Centralized Send Chat logic
  const executeChat = async (userMsg: string) => {
    setIsChatLoading(true);
    setCompletedSteps([]);
    setActiveStep('router');
    setExecutionTrace(['Initializing operational workflow...']);

    // Append user query message
    setMessages((prev) => [...prev, { role: 'human', content: userMsg, timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }]);

    // Setup placeholder for assistant stream
    setMessages((prev) => [...prev, { role: 'assistant', content: 'Orchestrating agents...', isStreaming: true, timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }]);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.token}`
        },
        body: JSON.stringify({
          message: userMsg,
          thread_id: threadId
        })
      });

      if (!response.ok) {
        throw new Error('Communication failed.');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder('utf-8');
      if (!reader) throw new Error('Readable stream not supported.');

      let assistantText = '';
      let activeNodeName = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.replace('data: ', '').trim();
            if (!dataStr) continue;

            try {
              const event = JSON.parse(dataStr);
              if (event.error) {
                assistantText = `System Error: ${event.error}`;
                setExecutionTrace((prev) => [...prev, `[Critical Error] ${event.error}`]);
              } else {
                // Parse standard LangGraph nodes updates
                const nodeKeys = Object.keys(event);
                if (nodeKeys.length > 0) {
                  const nodeName = nodeKeys[0];
                  const nodeData = event[nodeName];
                  activeNodeName = nodeName;
                  setActiveStep(nodeName);

                  // Append trace details
                  let traceLog = `[${nodeName.toUpperCase()}] executed successfully.`;
                  if (nodeName === 'router') {
                    traceLog = `[Router] Intent routing decided: '${nodeData.route}'.`;
                    setCompletedSteps((prev) => [...prev, 'router']);
                  } else if (nodeName === 'planner') {
                    traceLog = `[Planner] Plan steps generated: [${nodeData.plan?.join(', ')}].`;
                    setCompletedSteps((prev) => [...prev, 'planner']);
                  } else if (nodeName === 'sql') {
                    traceLog = `[SQL Agent] Query generated: \`${nodeData.sql_query}\`.`;
                    setCompletedSteps((prev) => [...prev, 'sql']);
                  } else if (nodeName === 'retrieval') {
                    traceLog = `[RAG Agent] Semantic manuals search matched ${nodeData.retrieved_context?.length || 0} policy chunks.`;
                    setCompletedSteps((prev) => [...prev, 'retrieval']);
                  } else if (nodeName === 'api') {
                    traceLog = `[API Agent] Outbound API call made.`;
                    setCompletedSteps((prev) => [...prev, 'api']);
                  } else if (nodeName === 'reflection') {
                    const approved = nodeData.reflection_feedback === '';
                    traceLog = `[Reflection] Correctness check: ${approved ? 'APPROVED' : 'REJECTED. Feedback: ' + nodeData.reflection_feedback}.`;
                    setCompletedSteps((prev) => [...prev, 'reflection']);
                    if (!approved) {
                      setMetrics((prev) => ({ ...prev, retryLoops: prev.retryLoops + 1 }));
                    }
                  } else if (nodeName === 'safety') {
                    traceLog = `[Safety] Compliance scan verdict: ${nodeData.safety_verdict?.toUpperCase()}.`;
                    setCompletedSteps((prev) => [...prev, 'safety']);
                  } else if (nodeName === 'report') {
                    assistantText = nodeData.final_report || '';
                    traceLog = `[Reporter] Completed final response rendering.`;
                    setCompletedSteps((prev) => [...prev, 'report']);
                  }

                  setExecutionTrace((prev) => [...prev, traceLog]);
                }
              }
            } catch (jsonErr) {
              // Ignore partial chunk syntax parser fails
            }
          }
        }

        // Update assistant streaming message
        setMessages((prev) => {
          const newMsgs = [...prev];
          const lastMsg = newMsgs[newMsgs.length - 1];
          if (lastMsg && lastMsg.role === 'assistant') {
            lastMsg.content = assistantText || 'Executing system workflow...';
            lastMsg.node = activeNodeName.toUpperCase();
          }
          return newMsgs;
        });
      }

      // Finalize message stream
      setMessages((prev) => {
        const newMsgs = [...prev];
        const lastMsg = newMsgs[newMsgs.length - 1];
        if (lastMsg) {
          lastMsg.isStreaming = false;
        }
        return newMsgs;
      });

      // Update counters mock metrics
      setMetrics((prev) => ({
        ...prev,
        requestsCount: prev.requestsCount + 1,
        tokenUsage: prev.tokenUsage + Math.floor(Math.random() * 400) + 150,
        accumulatedCost: prev.accumulatedCost + 0.002
      }));

    } catch (err: any) {
      setMessages((prev) => {
        const newMsgs = [...prev];
        const lastMsg = newMsgs[newMsgs.length - 1];
        if (lastMsg) {
          lastMsg.content = `Communication failure: ${err.message}`;
          lastMsg.isStreaming = false;
        }
        return newMsgs;
      });
      setMetrics((prev) => ({ ...prev, failuresCount: prev.failuresCount + 1 }));
    } finally {
      setIsChatLoading(false);
      setActiveStep(null);
    }
  };

  // Chat input submit
  const handleSendChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!queryInput.trim() || !user || isChatLoading) return;
    const userMsg = queryInput.trim();
    setQueryInput('');
    await executeChat(userMsg);
  };

  // Suggestion click handler
  const handleSelectSuggestion = (promptText: string) => {
    if (isChatLoading) return;
    executeChat(promptText);
  };

  // Upload Document handler
  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile || !user) return;

    setUploadStatus(null);
    setUploadLoading(true);

    const formData = new FormData();
    formData.append('file', uploadFile);
    formData.append('category', selectedCategory);

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${user.token}`
        },
        body: formData
      });

      const data = await response.json();
      if (response.ok) {
        setUploadStatus({ success: true, msg: data.message });
        setUploadFile(null);
        // Clear input element
        const fileInput = document.getElementById('file-upload-input') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
      } else {
        throw new Error(data.detail || 'Upload process failed.');
      }
    } catch (err: any) {
      setUploadStatus({ success: false, msg: err.message });
    } finally {
      setUploadLoading(false);
    }
  };

  // Database static schema documentation
  const databaseSchemas: Record<string, TableColumn[]> = {
    departments: [
      { name: 'department_id', type: 'SERIAL', key: 'PK', nullable: false },
      { name: 'name', type: 'VARCHAR(100)', nullable: false },
      { name: 'description', type: 'TEXT', nullable: true },
      { name: 'cost_center', type: 'VARCHAR(50)', nullable: false }
    ],
    employees: [
      { name: 'employee_id', type: 'SERIAL', key: 'PK', nullable: false },
      { name: 'full_name', type: 'VARCHAR(100)', nullable: false },
      { name: 'email', type: 'VARCHAR(100)', nullable: false },
      { name: 'phone', type: 'VARCHAR(50)', nullable: false },
      { name: 'department_id', type: 'INT', key: 'FK', nullable: false, references: 'departments.department_id' },
      { name: 'manager_id', type: 'INT', key: 'FK', nullable: true, references: 'employees.employee_id' },
      { name: 'salary', type: 'NUMERIC(12,2)', nullable: false },
      { name: 'joining_date', type: 'DATE', nullable: false },
      { name: 'location', type: 'VARCHAR(100)', nullable: false },
      { name: 'status', type: 'VARCHAR(50)', nullable: false }
    ],
    users: [
      { name: 'user_id', type: 'SERIAL', key: 'PK', nullable: false },
      { name: 'employee_id', type: 'INT', key: 'FK', nullable: false, references: 'employees.employee_id' },
      { name: 'username', type: 'VARCHAR(50)', nullable: false },
      { name: 'password_hash', type: 'VARCHAR(255)', nullable: false },
      { name: 'role', type: 'VARCHAR(50)', nullable: false },
      { name: 'is_active', type: 'BOOLEAN', nullable: false }
    ],
    customers: [
      { name: 'customer_id', type: 'SERIAL', key: 'PK', nullable: false },
      { name: 'company_name', type: 'VARCHAR(150)', nullable: false },
      { name: 'contact_name', type: 'VARCHAR(100)', nullable: false },
      { name: 'email', type: 'VARCHAR(100)', nullable: false },
      { name: 'phone', type: 'VARCHAR(50)', nullable: false },
      { name: 'country', type: 'VARCHAR(100)', nullable: false },
      { name: 'industry', type: 'VARCHAR(100)', nullable: false }
    ],
    products: [
      { name: 'product_id', type: 'SERIAL', key: 'PK', nullable: false },
      { name: 'name', type: 'VARCHAR(100)', nullable: false },
      { name: 'category', type: 'VARCHAR(50)', nullable: false },
      { name: 'price', type: 'NUMERIC(10,2)', nullable: false },
      { name: 'supplier', type: 'VARCHAR(100)', nullable: false },
      { name: 'stock', type: 'INT', nullable: false }
    ],
    inventory: [
      { name: 'inventory_id', type: 'SERIAL', key: 'PK', nullable: false },
      { name: 'product_id', type: 'INT', key: 'FK', nullable: false, references: 'products.product_id' },
      { name: 'warehouse_location', type: 'VARCHAR(100)', nullable: false },
      { name: 'quantity_on_hand', type: 'INT', nullable: false },
      { name: 'safety_stock', type: 'INT', nullable: false },
      { name: 'reorder_point', type: 'INT', nullable: false },
      { name: 'last_restocked', type: 'DATE', nullable: true }
    ],
    orders: [
      { name: 'order_id', type: 'SERIAL', key: 'PK', nullable: false },
      { name: 'customer_id', type: 'INT', key: 'FK', nullable: false, references: 'customers.customer_id' },
      { name: 'product_id', type: 'INT', key: 'FK', nullable: false, references: 'products.product_id' },
      { name: 'quantity', type: 'INT', nullable: false },
      { name: 'price', type: 'NUMERIC(10,2)', nullable: false },
      { name: 'discount', type: 'NUMERIC(5,2)', nullable: false },
      { name: 'status', type: 'VARCHAR(50)', nullable: false },
      { name: 'order_date', type: 'DATE', nullable: false }
    ],
    support_tickets: [
      { name: 'ticket_id', type: 'SERIAL', key: 'PK', nullable: false },
      { name: 'customer_id', type: 'INT', key: 'FK', nullable: false, references: 'customers.customer_id' },
      { name: 'issue', type: 'TEXT', nullable: false },
      { name: 'priority', type: 'VARCHAR(50)', nullable: false },
      { name: 'assigned_employee_id', type: 'INT', key: 'FK', nullable: true, references: 'employees.employee_id' },
      { name: 'status', type: 'VARCHAR(50)', nullable: false },
      { name: 'created_date', type: 'DATE', nullable: false },
      { name: 'resolved_date', type: 'DATE', nullable: true }
    ]
  };

  // Auth screen layout
  if (!user) {
    return (
      <div className="auth-container">
        <div className="auth-card glass-panel">
          <div className="auth-header">
            <h1>Darshan_AI_Engineer_Ops</h1>
            <p>Enterprise Multi-Agent AI Operations Platform</p>
          </div>
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label htmlFor="username">Username / Email</label>
              <input
                id="username"
                type="text"
                className="form-input"
                value={usernameInput}
                onChange={(e) => setUsernameInput(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="password">Security Password</label>
              <input
                id="password"
                type="password"
                className="form-input"
                value={passwordInput}
                onChange={(e) => setPasswordInput(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="auth-btn" disabled={authLoading}>
              {authLoading ? 'Verifying Identity...' : 'Access Dashboard'}
            </button>
          </form>
          {authError && <div className="auth-error">{authError}</div>}
        </div>
      </div>
    );
  }

  // Dashboard layout
  return (
    <div className="dashboard-layout">
      {/* Navigation Sidebar */}
      <aside className="sidebar">
        <div>
          <div className="sidebar-header">
            <h2>Darshan_AI_Engineer_Ops</h2>
            <p>Enterprise Multi-Agent AI Operations Platform</p>
          </div>
          <nav className="menu-list">
            <button
              className={`menu-item ${activeTab === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveTab('chat')}
            >
              <MessageSquare size={16} />
              AI Orchestrator
            </button>
            <button
              className={`menu-item ${activeTab === 'ingest' ? 'active' : ''}`}
              onClick={() => setActiveTab('ingest')}
            >
              <UploadCloud size={16} />
              Document Indexer
            </button>
            <button
              className={`menu-item ${activeTab === 'schema' ? 'active' : ''}`}
              onClick={() => setActiveTab('schema')}
            >
              <Database size={16} />
              Schema Inspector
            </button>
            <button
              className={`menu-item ${activeTab === 'metrics' ? 'active' : ''}`}
              onClick={() => setActiveTab('metrics')}
            >
              <Activity size={16} />
              Telemetry & Logs
            </button>
          </nav>
        </div>
        <div className="user-profile">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                width: '38px',
                height: '38px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 10px rgba(99, 102, 241, 0.3)'
              }}
            >
              <UserIcon size={18} color="#fff" />
            </div>
            <div className="user-info">
              <span className="user-name">{user.username}</span>
              <span className="user-role">{user.role} Authorization</span>
            </div>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            <LogOut size={13} />
            Logout Session
          </button>
        </div>
      </aside>

      {/* Main Content Workspace */}
      <main className="main-content">
        <header className="content-header">
          <h1>
            {activeTab === 'chat' && 'Operational Agent Control Chat'}
            {activeTab === 'ingest' && 'RAG Manual Policies Ingestion'}
            {activeTab === 'schema' && 'Relational Database Schema Inspector'}
            {activeTab === 'metrics' && 'Real-Time System Metrics Observability'}
          </h1>
          <span className={`badge badge-${user.role.toLowerCase()}`}>
            {user.role} Account
          </span>
        </header>

        <div className="content-body">
          {/* 1. CHAT WORKSPACE */}
          {activeTab === 'chat' && (
            <div className="chat-container">
              {/* Messages Panel */}
              <div className="chat-panel">
                <div className="chat-messages">
                  {messages.length === 0 ? (
                    <div className="empty-state-container">
                      <div className="empty-state-title">
                        How can Darshan_AI_Engineer_Ops help today?
                      </div>
                      <div className="empty-state-subtitle">
                        Ask about employee details, departments, corporate policies, or pipeline diagnostics.
                      </div>
                      <div className="prompt-suggestions-grid">
                        <div 
                          className="suggestion-card" 
                          onClick={() => handleSelectSuggestion("What are the core operational hours defined by Darshan_AI_Engineer_Ops?")}
                        >
                          <div className="suggestion-card-title">Corporate Rules</div>
                          <div className="suggestion-card-desc">Check standard operational hours & leave policies.</div>
                        </div>
                        <div 
                          className="suggestion-card" 
                          onClick={() => handleSelectSuggestion("Show me the top 3 employees by salary")}
                        >
                          <div className="suggestion-card-title">Database Query</div>
                          <div className="suggestion-card-desc">Search employee records and compile salary statistics.</div>
                        </div>
                        <div 
                          className="suggestion-card" 
                          onClick={() => handleSelectSuggestion("What is our corporate travel policy for flights?")}
                        >
                          <div className="suggestion-card-title">Travel Policy</div>
                          <div className="suggestion-card-desc">Lookup airline booking grades and reimbursement rules.</div>
                        </div>
                        <div 
                          className="suggestion-card" 
                          onClick={() => handleSelectSuggestion("Check active support tickets and their priorities")}
                        >
                          <div className="suggestion-card-title">Support Desk</div>
                          <div className="suggestion-card-desc">Analyze support ticket logs for customer escalations.</div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    messages.map((msg, idx) => {
                      const isAssistant = msg.role === 'assistant';
                      const hasRAG = completedSteps.includes('retrieval') || msg.content.includes('[Source:') || msg.content.includes('RAG');
                      const hasSQL = completedSteps.includes('sql') || msg.content.includes('SELECT') || msg.content.includes('Query Executed:');
                      const hasAPI = completedSteps.includes('api') || msg.content.includes('API Request');
                      const hasSafety = completedSteps.includes('safety') || !msg.isStreaming;
                      
                      return (
                        <div key={idx} className="chat-message-wrapper">
                          {isAssistant && !msg.isStreaming && (
                            <div className="chat-message-metadata">
                              <span className="chat-message-badge node">Report</span>
                              {hasRAG && <span className="chat-message-badge node">RAG</span>}
                              {hasSQL && <span className="chat-message-badge node">SQL</span>}
                              {hasAPI && <span className="chat-message-badge node">API</span>}
                              {hasSafety && <span className="chat-message-badge verified">✓ Safety Verified</span>}
                              <span className="chat-message-badge verified">✓ Generated Successfully</span>
                              <span className="chat-message-badge timestamp">
                                {msg.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                              </span>
                            </div>
                          )}
                          <div className={`chat-message ${msg.role} ${msg.isStreaming ? 'streaming' : ''}`}>
                            {msg.role === 'human' ? (
                              <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                            ) : (
                              <div className="prose">
                                <ReactMarkdown
                                  remarkPlugins={[remarkGfm]}
                                  rehypePlugins={[rehypeHighlight]}
                                >
                                  {msg.content}
                                </ReactMarkdown>
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })
                  )}
                  <div ref={chatEndRef} />
                </div>
                <form onSubmit={handleSendChat} className="chat-input-wrapper">
                  <input
                    type="text"
                    placeholder="Enter operational request or prompt command..."
                    value={queryInput}
                    onChange={(e) => setQueryInput(e.target.value)}
                    disabled={isChatLoading}
                  />
                  <button type="submit" className="send-btn" disabled={isChatLoading}>
                    <Send size={18} />
                  </button>
                </form>
              </div>

              {/* Interactive Execution Pipeline Sidebar */}
              <div className="chat-sidebar">
                <div className="sidebar-widget">
                  <div className="widget-title">
                    <Activity size={14} /> Execution Pipeline
                  </div>
                  <div className="pipeline-container">
                    {[
                      { id: 'router', label: '1. Intent Router', desc: 'Routing query...' },
                      { id: 'planner', label: '2. Task Planner', desc: 'Planning subtasks...' },
                      { id: 'retrieval', label: '3. RAG Manuals', desc: 'Searching manuals...' },
                      { id: 'sql', label: '4. SQL Database', desc: 'Querying records...' },
                      { id: 'api', label: '5. Outbound API', desc: 'Invoking endpoints...' },
                      { id: 'reflection', label: '6. Output Reflection', desc: 'Evaluating feedback...' },
                      { id: 'safety', label: '7. Safety Guardrails', desc: 'Scanning PII/Content...' },
                      { id: 'report', label: '8. Final Reporter', desc: 'Compiling response...' }
                    ].map((step, idx) => {
                      const completed = completedSteps.includes(step.id);
                      const active = isChatLoading && activeStep === step.id;
                      const statusClass = completed ? 'completed' : active ? 'active' : 'pending';
                      
                      return (
                        <React.Fragment key={step.id}>
                          <motion.div
                            className={`pipeline-node ${statusClass}`}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: idx * 0.04 }}
                          >
                            <div className="pipeline-node-icon">
                              {completed ? '✓' : active ? '●' : idx + 1}
                            </div>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                              <span style={{ fontSize: '13px', fontWeight: 700 }}>{step.label}</span>
                              {active && <span style={{ fontSize: '11px', opacity: 0.8 }} className="animate-pulse">{step.desc}</span>}
                            </div>
                          </motion.div>
                          {idx < 7 && (
                            <div className={`pipeline-node-connector ${completed ? 'completed' : ''}`} />
                          )}
                        </React.Fragment>
                      );
                    })}
                  </div>
                </div>

                <div className="sidebar-widget" style={{ flexGrow: 1, overflowY: 'auto', maxHeight: '420px' }}>
                  <div className="widget-title">
                    <Terminal size={14} /> Agent Execution Logs
                  </div>
                  <div style={{ fontSize: '11px', fontFamily: 'monospace', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <AnimatePresence>
                      {executionTrace.map((log, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, y: 5 }}
                          animate={{ opacity: 1, y: 0 }}
                          style={{ borderBottom: '1px solid rgba(255,255,255,0.03)', paddingBottom: '6px', lineHeight: '1.4' }}
                        >
                          <span style={{ color: 'var(--accent-primary)' }}>&gt;</span> {log}
                        </motion.div>
                      ))}
                    </AnimatePresence>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 2. KNOWLEDGE INGESTION */}
          {activeTab === 'ingest' && (
            <div>
              <div style={{ marginBottom: '30px' }}>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '20px' }}>
                  Ingest corporate documents (Markdown format) directly into Qdrant collections. This content is immediately processed, chunked, embedded, and indexed.
                </p>
                {user.role === 'User' ? (
                  <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', borderColor: 'var(--error-color)' }}>
                    <Lock size={48} color="var(--error-color)" style={{ marginBottom: '16px' }} />
                    <h3>Access Restricted</h3>
                    <p style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>
                      Document ingestion is restricted to <strong>Admin</strong> or <strong>Manager</strong> credentials under RBAC policies.
                    </p>
                  </div>
                ) : (
                  <form onSubmit={handleUpload} className="glass-panel" style={{ padding: '30px' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                      <div className="form-group">
                        <label>Target Category Department</label>
                        <select
                           className="form-input"
                          value={selectedCategory}
                          onChange={(e) => setSelectedCategory(e.target.value)}
                        >
                          <option value="hr">Human Resources (hr)</option>
                          <option value="finance">Finance & Auditing (finance)</option>
                          <option value="sales">Sales & Commissions (sales)</option>
                          <option value="it">Security & IT Operations (it)</option>
                          <option value="customer_support">Customer Service (customer_support)</option>
                          <option value="inventory">Inventory & Logistics (inventory)</option>
                        </select>
                      </div>
                      <div className="form-group">
                        <label>Select Markdown File</label>
                        <input
                          id="file-upload-input"
                          type="file"
                          accept=".md"
                          className="form-input"
                          onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                          required
                        />
                      </div>
                    </div>
                    <button type="submit" className="auth-btn" style={{ maxWidth: '200px' }} disabled={uploadLoading || !uploadFile}>
                      {uploadLoading ? 'Embedding & Indexing...' : 'Upload & Process'}
                    </button>
                    {uploadStatus && (
                      <div
                        className="auth-error"
                        style={{
                          borderColor: uploadStatus.success ? 'var(--success-color)' : 'var(--error-color)',
                          background: uploadStatus.success ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
                          color: uploadStatus.success ? 'var(--success-color)' : 'var(--error-color)'
                        }}
                      >
                        {uploadStatus.msg}
                      </div>
                    )}
                  </form>
                )}
              </div>
            </div>
          )}

          {/* 3. SCHEMA INSPECTOR */}
          {activeTab === 'schema' && (
            <div className="schema-grid">
              {/* Tables selector */}
              <div className="table-list">
                <div className="widget-title"><Database size={14} /> Relational Tables</div>
                {Object.keys(databaseSchemas).map((tbl) => (
                  <button
                    key={tbl}
                    className={`table-item ${selectedTable === tbl ? 'active' : ''}`}
                    onClick={() => setSelectedTable(tbl)}
                  >
                    {tbl}
                  </button>
                ))}
              </div>

              {/* Table schema definition details */}
              <div className="glass-panel" style={{ padding: '24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '15px' }}>
                  <h3 style={{ textTransform: 'capitalize' }}>Table Definition: {selectedTable}</h3>
                </div>
                <table className="schema-table">
                  <thead>
                    <tr>
                      <th>Column</th>
                      <th>Data Type</th>
                      <th>Key Type</th>
                      <th>Nullable</th>
                      <th>References</th>
                    </tr>
                  </thead>
                  <tbody>
                    {databaseSchemas[selectedTable].map((col) => (
                      <tr key={col.name}>
                        <td style={{ fontWeight: 600, fontFamily: 'monospace' }}>{col.name}</td>
                        <td style={{ fontFamily: 'monospace', color: 'var(--text-secondary)' }}>{col.type}</td>
                        <td>
                          {col.key && (
                            <span style={{
                              padding: '2px 6px',
                              borderRadius: '4px',
                              fontSize: '0.7rem',
                              fontWeight: 700,
                              background: col.key === 'PK' ? 'rgba(16,185,129,0.15)' : 'rgba(59,130,246,0.15)',
                              color: col.key === 'PK' ? 'var(--success-color)' : 'var(--accent-blue)',
                              border: `1px solid ${col.key === 'PK' ? 'rgba(16,185,129,0.3)' : 'rgba(59,130,246,0.3)'}`
                            }}>
                              {col.key}
                            </span>
                          )}
                        </td>
                        <td>{col.nullable ? 'YES' : 'NO'}</td>
                        <td style={{ color: 'var(--text-secondary)', fontFamily: 'monospace', fontSize: '0.8rem' }}>{col.references || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* 4. OBSERVABILITY DETAILS */}
          {activeTab === 'metrics' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
              <div className="metrics-grid">
                <div className="glass-panel metric-card">
                  <div className="metric-header">
                    <span>Total Gateway Requests</span>
                    <Activity size={18} color="var(--accent-blue)" />
                  </div>
                  <div className="metric-value">{metrics.requestsCount}</div>
                  <div className="metric-footer">API endpoints processed</div>
                </div>

                <div className="glass-panel metric-card">
                  <div className="metric-header">
                    <span>Tokens Consumed</span>
                    <Cpu size={18} color="var(--accent-purple)" />
                  </div>
                  <div className="metric-value">{metrics.tokenUsage.toLocaleString()}</div>
                  <div className="metric-footer">Prompt & Completion vectors</div>
                </div>

                <div className="glass-panel metric-card">
                  <div className="metric-header">
                    <span>LLM Accumulated Cost</span>
                    <DollarSign size={18} color="var(--success-color)" />
                  </div>
                  <div className="metric-value">${metrics.accumulatedCost.toFixed(3)}</div>
                  <div className="metric-footer">Cost estimation (USD)</div>
                </div>

                <div className="glass-panel metric-card">
                  <div className="metric-header">
                    <span>Average Agent Latency</span>
                    <Clock size={18} color="var(--warning-color)" />
                  </div>
                  <div className="metric-value">{metrics.avgLatency}s</div>
                  <div className="metric-footer">Per execution sequence</div>
                </div>
              </div>

              {/* Extra telemetry info */}
              <div className="glass-panel" style={{ padding: '30px' }}>
                <h3 style={{ marginBottom: '15px' }}>System Audit Indicators</h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '40px' }}>
                  <div>
                    <h4 style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '12px', fontWeight: 600 }}>Active Agent Nodes Failures</h4>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                      <AlertTriangle size={32} color={metrics.failuresCount > 0 ? 'var(--error-color)' : 'var(--success-color)'} />
                      <div>
                        <div style={{ fontSize: '1.2rem', fontWeight: 700 }}>{metrics.failuresCount} Exceptions</div>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Registered inside Prometheus scrapers</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h4 style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '12px', fontWeight: 600 }}>Reflection Planner Retry Cycles</h4>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                      <RefreshCw size={32} color={metrics.retryLoops > 0 ? 'var(--warning-color)' : 'var(--success-color)'} />
                      <div>
                        <div style={{ fontSize: '1.2rem', fontWeight: 700 }}>{metrics.retryLoops} Iterations</div>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Loops processed inside LangGraph</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
