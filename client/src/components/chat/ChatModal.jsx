import { useState, useEffect } from "react";
import { MessageSquare, Send, User } from "lucide-react";
import { Modal } from "../common/Modal";
import { Button } from "../common/Button";
import { fieldClasses } from "../common/ErrorBanner";
import { fetchOpportunityThread, sendMessage } from "../../api/gigs";
import { useAuth } from "../../hooks/useAuth";

export function ChatModal({ open, onClose, opportunityId, otherUser, opportunityTitle }) {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [content, setContent] = useState("");
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(false);

  const loadMessages = async () => {
    if (!opportunityId || !otherUser) return;
    setLoading(true);
    try {
      const data = await fetchOpportunityThread(opportunityId, otherUser.id);
      setMessages(data || []);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open) {
      loadMessages();
    }
  }, [open, opportunityId, otherUser?.id]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!content.trim() || sending) return;
    setSending(true);
    try {
      const msg = await sendMessage({
        opportunityId,
        recipientId: otherUser.id,
        content: content.trim(),
      });
      setMessages((prev) => [...prev, msg]);
      setContent("");
    } catch (err) {
      alert(err.message || "Could not send message");
    } finally {
      setSending(false);
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={`Chat with ${otherUser?.name || "Participant"}`}
    >
      <div className="flex flex-col h-[400px]">
        <div className="bg-surface-raised border border-border p-2.5 rounded-lg mb-3 text-xs text-ink-muted">
          <p className="font-medium text-ink">Gig: {opportunityTitle || `#${opportunityId}`}</p>
          <p className="text-[11px] text-ink-muted">
            Keep communication on Comrade Plug to protect payment & review guarantees.
          </p>
        </div>

        {/* Message history */}
        <div className="flex-1 overflow-y-auto space-y-2 p-1">
          {loading && <p className="text-center text-xs text-ink-muted py-4">Loading messages...</p>}
          {!loading && messages.length === 0 && (
            <p className="text-center text-xs text-ink-muted py-8">
              No messages yet. Send a note to discuss deliverables or campus meeting place.
            </p>
          )}
          {messages.map((m) => {
            const isMe = m.sender_id === user?.id;
            return (
              <div
                key={m.id}
                className={`flex flex-col ${isMe ? "items-end" : "items-start"}`}
              >
                <div
                  className={`max-w-[80%] rounded-xl px-3 py-2 text-sm ${
                    isMe
                      ? "bg-accent text-accent-ink rounded-tr-none"
                      : "bg-surface-raised border border-border text-ink rounded-tl-none"
                  }`}
                >
                  <p className="text-xs font-semibold opacity-70 mb-0.5">
                    {isMe ? "You" : m.sender_name}
                  </p>
                  <p className="whitespace-pre-wrap">{m.content}</p>
                </div>
                <span className="text-[10px] text-ink-muted mt-0.5 px-1">
                  {new Date(m.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </span>
              </div>
            );
          })}
        </div>

        {/* Composer */}
        <form onSubmit={handleSend} className="mt-3 flex gap-2">
          <input
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Type your message..."
            className={`${fieldClasses(false)} flex-1 text-sm`}
          />
          <Button type="submit" loading={sending} icon={Send} disabled={!content.trim()}>
            Send
          </Button>
        </form>
      </div>
    </Modal>
  );
}
