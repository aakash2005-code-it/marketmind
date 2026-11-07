import { useState, useRef, useEffect } from "react";
import axios from "axios";

export default function ChatBot({ stockContext }) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: "bot", text: "Hi! I'm the MarketMind assistant. Ask me how a verdict was reached, or any general finance question." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, open]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = input;
    setMessages((prev) => [...prev, { role: "user", text: userMsg }]);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post("http://127.0.0.1:8000/chat", {
        message: userMsg,
        stock_context: stockContext || null,
      });
      setMessages((prev) => [...prev, { role: "bot", text: res.data.reply }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "bot", text: "Sorry, something went wrong." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button className="chat-bubble" onClick={() => setOpen(!open)}>
        {open ? "×" : "💬"}
      </button>

      {open && (
        <div className="chat-window">
          <div className="chat-header">
            <span>MarketMind Assistant</span>
            {stockContext && <span className="chat-context-tag">Viewing: {stockContext.ticker}</span>}
          </div>

          <div className="chat-messages" ref={scrollRef}>
            {messages.map((m, idx) => (
              <div key={idx} className={`chat-msg chat-msg-${m.role}`}>
                {m.text}
              </div>
            ))}
            {loading && <div className="chat-msg chat-msg-bot chat-typing">Thinking…</div>}
          </div>

          <div className="chat-input-row">
            <input
              type="text"
              placeholder="Ask something…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            />
            <button onClick={sendMessage} disabled={loading}>Send</button>
          </div>
        </div>
      )}
    </>
  );
}