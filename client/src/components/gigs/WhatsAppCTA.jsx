import { MessageCircle } from "lucide-react";

import { Button } from "../common/Button";
import { useToast } from "../../hooks/useToast";
import { trackCtaClick } from "../../utils/analytics";

export function WhatsAppCTA({
  gigTitle,
  posterName,
  phoneNumber,
  onAlternativeChat,
}) {
  const { toast } = useToast();

  const waUrl = phoneNumber
    ? `https://wa.me/${phoneNumber.replace(/\D/g, "")}?text=${encodeURIComponent(
        `Hi ${posterName}, I saw your listing for "${gigTitle}" on ComradePlug`
      )}`
    : "";

  return (
    <div className="flex flex-col gap-2">
      {waUrl && (
        <a
          href={waUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex animate-fade-in items-center justify-center gap-2 rounded-lg bg-[#25D366] px-4 py-3 text-fluid-sm font-medium text-white shadow-card hover:shadow-card-hover transition-shadow"
          onClick={() => trackCtaClick("whatsapp_cta")}
        >
          <MessageCircle className="h-4 w-4" aria-hidden="true" />
          Chat on WhatsApp
        </a>
      )}
      {onAlternativeChat && (
        <Button
          variant="secondary"
          onClick={() => {
            onAlternativeChat();
            toast({
              title: "In-app messaging",
              description: "Use the message thread below to reach out.",
            });
          }}
        >
          Message privately
        </Button>
      )}
    </div>
  );
}
