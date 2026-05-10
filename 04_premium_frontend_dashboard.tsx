/**
 * GeoMind AI - Premium Frontend Components
 * Perplexity/Palantir inspired design with futuristic, cinematic aesthetic
 * 
 * Build with: React 18+, TypeScript, Tailwind CSS, Framer Motion
 */

import React, { useState, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

// ============================================================================
// DESIGN TOKENS & CONFIGURATION
// ============================================================================

const DesignTokens = {
  colors: {
    // Primary: Deep space + neon accent
    primary: "#0a1428", // Deep navy
    primaryAlt: "#1a2f4f", // Slightly lighter navy
    accent: "#00d9ff", // Cyan
    accentSecondary: "#ff006e", // Magenta
    
    // Backgrounds
    bgDark: "#0d0f14",
    bgCard: "#1a1f2e",
    bgOverlay: "rgba(10, 20, 40, 0.8)",
    
    // Text
    textPrimary: "#e8eef5",
    textSecondary: "#a0afc2",
    textTertiary: "#6b7a92",
    
    // Status
    success: "#00d084",
    warning: "#ffa800",
    error: "#ff4757",
    
    // Borders
    border: "#2a3a52",
    borderLight: "#3a4a62",
  },
  
  typography: {
    // Display fonts (headings)
    displayFont: "'Space Mono', monospace",
    // Body font (content)
    bodyFont: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  },
  
  spacing: {
    xs: "0.25rem",
    sm: "0.5rem",
    md: "1rem",
    lg: "1.5rem",
    xl: "2rem",
    xxl: "3rem",
  },
  
  transitions: {
    fast: "150ms cubic-bezier(0.4, 0, 0.2, 1)",
    base: "300ms cubic-bezier(0.4, 0, 0.2, 1)",
    slow: "500ms cubic-bezier(0.4, 0, 0.2, 1)",
  },
};

// ============================================================================
// GLOBAL STYLES (Tailwind + Custom CSS)
// ============================================================================

const GlobalStyles = `
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  font-family: ${DesignTokens.typography.bodyFont};
  background-color: ${DesignTokens.colors.bgDark};
  color: ${DesignTokens.colors.textPrimary};
  overflow-x: hidden;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: ${DesignTokens.colors.bgDark};
}

::-webkit-scrollbar-thumb {
  background: ${DesignTokens.colors.border};
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: ${DesignTokens.colors.borderLight};
}

/* Glass morphism effect */
.glass {
  background: rgba(26, 31, 46, 0.4);
  backdrop-filter: blur(10px);
  border: 1px solid ${DesignTokens.colors.border};
}

/* Glow effect */
.glow-cyan {
  box-shadow: 0 0 20px rgba(0, 217, 255, 0.3);
}

.glow-magenta {
  box-shadow: 0 0 20px rgba(255, 0, 110, 0.3);
}

/* Text gradient */
.text-gradient {
  background: linear-gradient(135deg, ${DesignTokens.colors.accent}, ${DesignTokens.colors.accentSecondary});
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Smooth focus states */
button:focus, a:focus, input:focus {
  outline: 2px solid ${DesignTokens.colors.accent};
  outline-offset: 2px;
}
`;

// ============================================================================
// CORE UI COMPONENTS
// ============================================================================

/**
 * Navigation Bar with floating effect
 */
const NavBar: React.FC = () => {
  return (
    <motion.nav
      className="fixed top-0 left-0 right-0 z-50 glass"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ type: "spring", damping: 20 }}
      style={{
        borderBottomColor: DesignTokens.colors.border,
        background: `linear-gradient(to bottom, ${DesignTokens.colors.bgCard}, rgba(26, 31, 46, 0.2))`,
      }}
    >
      <div className="flex items-center justify-between px-8 py-4 max-w-7xl mx-auto">
        {/* Logo */}
        <motion.div
          className="flex items-center gap-3"
          whileHover={{ scale: 1.05 }}
        >
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-400 to-magenta-500 flex items-center justify-center font-bold text-black">
            G
          </div>
          <div>
            <h1
              className="font-bold text-lg tracking-tight"
              style={{ fontFamily: DesignTokens.typography.displayFont }}
            >
              GeoMind
            </h1>
            <p
              className="text-xs"
              style={{ color: DesignTokens.colors.textTertiary }}
            >
              AI Exploration
            </p>
          </div>
        </motion.div>

        {/* Nav Items */}
        <div className="flex items-center gap-8">
          {["Documents", "Chat", "Analysis", "Reports"].map((item, i) => (
            <motion.button
              key={item}
              className="relative text-sm font-medium transition-colors"
              style={{ color: DesignTokens.colors.textSecondary }}
              whileHover={{ color: DesignTokens.colors.accent }}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
            >
              {item}
              <motion.div
                className="absolute bottom-0 left-0 h-0.5 bg-gradient-to-r from-cyan-400 to-magenta-500"
                initial={{ width: 0 }}
                whileHover={{ width: "100%" }}
                transition={{ duration: 0.3 }}
              />
            </motion.button>
          ))}
        </div>

        {/* CTA Button */}
        <motion.button
          className="px-6 py-2 rounded-lg font-semibold text-sm transition-all"
          style={{
            background: `linear-gradient(135deg, ${DesignTokens.colors.accent}, ${DesignTokens.colors.accentSecondary})`,
            color: DesignTokens.colors.bgDark,
          }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Upload Documents
        </motion.button>
      </div>
    </motion.nav>
  );
};

/**
 * Floating Chat Panel - Main interaction interface
 */
interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Array<{ document: string; page: number }>;
  loading?: boolean;
}

const ChatPanel: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      role: "assistant",
      content:
        "Welcome to GeoMind AI. Upload geological documents and ask me anything about your exploration project.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = useCallback(async () => {
    if (!input.trim()) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    // Simulate API call
    setTimeout(() => {
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `Based on the geological data in your documents, I can provide analysis on your query: "${input}". 
        
The Sumayau nickel-copper project shows promising mineralization with copper grades up to 54% in the massive sulfide zones. The laterite cap shows nickel enrichment to 2.1% Ni.

**Key findings:**
- Primary mineralization: 100-150m depth
- Main ore type: Massive sulfide (MSLF)
- Cu grade: 0.74-54% depending on zone
- Ni grade: 0.3-2.3% Ni

I recommend additional drilling to define the resource model further.`,
        sources: [
          { document: "Sumayau Drill Log SYD25-0001", page: 3 },
          { document: "Addison Mining Services MRE Apr 2026", page: 12 },
        ],
      };

      setMessages((prev) => [...prev, aiMessage]);
      setIsLoading(false);
    }, 1500);
  }, [input]);

  return (
    <motion.div
      className="fixed bottom-8 right-8 w-96 rounded-2xl overflow-hidden shadow-2xl"
      style={{ background: DesignTokens.colors.bgCard }}
      initial={{ opacity: 0, y: 100 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: "spring", damping: 15 }}
    >
      {/* Header */}
      <div
        className="p-4 border-b"
        style={{ borderColor: DesignTokens.colors.border }}
      >
        <div className="flex items-center justify-between">
          <h3
            className="font-semibold"
            style={{ fontFamily: DesignTokens.typography.displayFont }}
          >
            GeoMind Chat
          </h3>
          <div className="flex gap-2">
            {isLoading && (
              <motion.div
                className="w-2 h-2 rounded-full"
                style={{ background: DesignTokens.colors.accent }}
                animate={{ scale: [1, 1.5, 1] }}
                transition={{ duration: 1, repeat: Infinity }}
              />
            )}
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="h-96 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <motion.div
            key={msg.id}
            className="flex gap-3"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
          >
            {msg.role === "assistant" && (
              <div
                className="w-8 h-8 rounded-lg flex-shrink-0 flex items-center justify-center text-xs font-bold"
                style={{
                  background: `linear-gradient(135deg, ${DesignTokens.colors.accent}, ${DesignTokens.colors.accentSecondary})`,
                  color: DesignTokens.colors.bgDark,
                }}
              >
                GM
              </div>
            )}

            <div
              className={`flex-1 rounded-lg p-3 ${
                msg.role === "user"
                  ? "rounded-br-none"
                  : "rounded-bl-none"
              }`}
              style={{
                background:
                  msg.role === "user"
                    ? DesignTokens.colors.primaryAlt
                    : DesignTokens.colors.bgDark,
                borderColor: DesignTokens.colors.border,
                borderWidth: msg.role === "assistant" ? "1px" : "0",
              }}
            >
              <p
                className="text-sm leading-relaxed"
                style={{
                  color:
                    msg.role === "user"
                      ? DesignTokens.colors.textPrimary
                      : DesignTokens.colors.textSecondary,
                }}
              >
                {msg.content}
              </p>

              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-2 pt-2 border-t" style={{ borderColor: DesignTokens.colors.border }}>
                  <p
                    className="text-xs font-semibold mb-1"
                    style={{ color: DesignTokens.colors.accent }}
                  >
                    Sources:
                  </p>
                  {msg.sources.map((src, i) => (
                    <p key={i} className="text-xs" style={{ color: DesignTokens.colors.textTertiary }}>
                      • {src.document} (p. {src.page})
                    </p>
                  ))}
                </div>
              )}
            </div>

            {msg.role === "user" && (
              <div
                className="w-8 h-8 rounded-lg flex-shrink-0 flex items-center justify-center text-xs font-bold"
                style={{
                  background: DesignTokens.colors.primaryAlt,
                  color: DesignTokens.colors.accent,
                  border: `1px solid ${DesignTokens.colors.border}`,
                }}
              >
                U
              </div>
            )}
          </motion.div>
        ))}
        {isLoading && (
          <motion.div
            className="flex gap-2"
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            <div
              className="h-2 w-2 rounded-full"
              style={{ background: DesignTokens.colors.accent }}
            />
            <div
              className="h-2 w-2 rounded-full"
              style={{ background: DesignTokens.colors.accent }}
            />
            <div
              className="h-2 w-2 rounded-full"
              style={{ background: DesignTokens.colors.accent }}
            />
          </motion.div>
        )}
      </div>

      {/* Input */}
      <div
        className="p-4 border-t flex gap-2"
        style={{ borderColor: DesignTokens.colors.border }}
      >
        <input
          type="text"
          placeholder="Ask about your geological data..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              handleSendMessage();
            }
          }}
          className="flex-1 px-3 py-2 rounded-lg text-sm border transition-colors"
          style={{
            background: DesignTokens.colors.bgDark,
            borderColor: DesignTokens.colors.border,
            color: DesignTokens.colors.textPrimary,
          }}
        />
        <motion.button
          onClick={handleSendMessage}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="p-2 rounded-lg font-semibold transition-colors"
          style={{
            background: `linear-gradient(135deg, ${DesignTokens.colors.accent}, ${DesignTokens.colors.accentSecondary})`,
            color: DesignTokens.colors.bgDark,
          }}
        >
          →
        </motion.button>
      </div>
    </motion.div>
  );
};

/**
 * Document Viewer Component
 */
const DocumentViewer: React.FC<{ documentName: string }> = ({
  documentName,
}) => {
  return (
    <motion.div
      className="fixed left-8 top-24 w-96 rounded-2xl overflow-hidden h-96"
      style={{ background: DesignTokens.colors.bgCard }}
      initial={{ opacity: 0, x: -100 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ type: "spring", damping: 15 }}
    >
      {/* Header */}
      <div
        className="p-4 border-b"
        style={{ borderColor: DesignTokens.colors.border }}
      >
        <h3
          className="font-semibold text-sm"
          style={{ fontFamily: DesignTokens.typography.displayFont }}
        >
          {documentName}
        </h3>
        <p style={{ color: DesignTokens.colors.textTertiary }} className="text-xs mt-1">
          Page 1 of 28
        </p>
      </div>

      {/* Content */}
      <div className="p-4 space-y-3 h-80 overflow-y-auto">
        <motion.div
          className="p-3 rounded-lg"
          style={{
            background: DesignTokens.colors.bgDark,
            border: `1px solid ${DesignTokens.colors.border}`,
          }}
          whileHover={{ borderColor: DesignTokens.colors.accent }}
        >
          <p
            className="text-xs font-mono"
            style={{ color: DesignTokens.colors.textSecondary }}
          >
            <span style={{ color: DesignTokens.colors.accent }}>Location:</span>{" "}
            5.2345°N, 118.1234°E
          </p>
          <p
            className="text-xs font-mono mt-2"
            style={{ color: DesignTokens.colors.textSecondary }}
          >
            <span style={{ color: DesignTokens.colors.accent }}>Depth:</span> 0-200m
          </p>
        </motion.div>

        <motion.div
          className="p-3 rounded-lg"
          style={{
            background: DesignTokens.colors.bgDark,
            border: `1px solid ${DesignTokens.colors.border}`,
          }}
          whileHover={{ borderColor: DesignTokens.colors.accentSecondary }}
        >
          <p
            className="text-xs font-bold mb-2"
            style={{ color: DesignTokens.colors.accentSecondary }}
          >
            MINERALIZATION SUMMARY
          </p>
          <p className="text-xs leading-relaxed" style={{ color: DesignTokens.colors.textSecondary }}>
            • Massive sulfide zone: 54% Cu
          </p>
          <p className="text-xs leading-relaxed" style={{ color: DesignTokens.colors.textSecondary }}>
            • Laterite cap: 2.1% Ni
          </p>
        </motion.div>
      </div>
    </motion.div>
  );
};

/**
 * Main Dashboard Layout
 */
const Dashboard: React.FC = () => {
  return (
    <div style={{ background: DesignTokens.colors.bgDark, minHeight: "100vh" }}>
      {/* Global Styles */}
      <style>{GlobalStyles}</style>

      <NavBar />

      {/* Hero Section */}
      <motion.section
        className="pt-32 pb-20 px-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <div className="max-w-5xl mx-auto">
          <motion.h2
            className="text-5xl font-bold mb-6 leading-tight"
            style={{ fontFamily: DesignTokens.typography.displayFont }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <span className="text-gradient">Geological Intelligence</span>
            <br />
            Powered by AI
          </motion.h2>

          <motion.p
            className="text-lg mb-8 max-w-2xl"
            style={{ color: DesignTokens.colors.textSecondary }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            Upload your geological reports, drill logs, and exploration data.
            Ask complex questions. Get instant, sourced answers powered by
            advanced RAG and multi-agent AI.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            className="flex gap-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <motion.button
              className="px-8 py-3 rounded-lg font-semibold transition-all"
              style={{
                background: `linear-gradient(135deg, ${DesignTokens.colors.accent}, ${DesignTokens.colors.accentSecondary})`,
                color: DesignTokens.colors.bgDark,
              }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Get Started
            </motion.button>

            <motion.button
              className="px-8 py-3 rounded-lg font-semibold border transition-all"
              style={{
                borderColor: DesignTokens.colors.border,
                color: DesignTokens.colors.textPrimary,
              }}
              whileHover={{
                borderColor: DesignTokens.colors.accent,
                color: DesignTokens.colors.accent,
              }}
              whileTap={{ scale: 0.95 }}
            >
              View Demo
            </motion.button>
          </motion.div>
        </div>
      </motion.section>

      {/* Interactive Demo Area */}
      <div className="relative">
        <DocumentViewer documentName="Sumayau_Drill_Log_SYD25-0001.pdf" />
        <ChatPanel />

        {/* Background Effects */}
        <motion.div
          className="absolute top-1/4 right-1/4 w-96 h-96 rounded-full blur-3xl opacity-10 pointer-events-none"
          style={{ background: DesignTokens.colors.accent }}
          animate={{ x: [0, 30, 0], y: [0, 30, 0] }}
          transition={{ duration: 8, repeat: Infinity }}
        />
      </div>

      {/* Features Section */}
      <motion.section className="py-20 px-8 mt-20">
        <div className="max-w-6xl mx-auto">
          <h3
            className="text-3xl font-bold mb-16 text-center"
            style={{ fontFamily: DesignTokens.typography.displayFont }}
          >
            Powered by Advanced AI Systems
          </h3>

          <div className="grid grid-cols-3 gap-6">
            {[
              {
                title: "Hybrid RAG",
                description:
                  "Semantic + keyword search with reranking for precision retrieval",
                icon: "⚡",
              },
              {
                title: "Multi-Agent AI",
                description:
                  "Specialized agents for geology, economics, ESG, and risk",
                icon: "🧠",
              },
              {
                title: "Real-time Citations",
                description:
                  "Every answer sourced with document references and page numbers",
                icon: "📍",
              },
            ].map((feature, i) => (
              <motion.div
                key={i}
                className="p-6 rounded-xl border transition-all"
                style={{
                  background: DesignTokens.colors.bgCard,
                  borderColor: DesignTokens.colors.border,
                }}
                whileHover={{
                  borderColor: DesignTokens.colors.accent,
                  boxShadow: `0 0 20px rgba(0, 217, 255, 0.2)`,
                }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
              >
                <div className="text-3xl mb-4">{feature.icon}</div>
                <h4 className="font-semibold mb-2">{feature.title}</h4>
                <p style={{ color: DesignTokens.colors.textSecondary }} className="text-sm">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.section>

      {/* Footer */}
      <footer
        className="border-t py-8 px-8 mt-20"
        style={{ borderColor: DesignTokens.colors.border }}
      >
        <div className="max-w-6xl mx-auto text-center">
          <p style={{ color: DesignTokens.colors.textTertiary }} className="text-sm">
            GeoMind AI © 2024. Powered by Claude API, LangChain, and LlamaIndex.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Dashboard;
