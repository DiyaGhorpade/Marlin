import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Send, Bot, User } from "lucide-react";

interface Message {
  id: number;
  text: string;
  sender: "user" | "bot";
}

const ChatbotSection = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Hello! I'm your marine data assistant. Ask me anything about oceanographic data, fisheries, or marine biodiversity.",
      sender: "bot",
    },
  ]);
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;

    const newMessage: Message = {
      id: messages.length + 1,
      text: input,
      sender: "user",
    };

    setMessages([...messages, newMessage]);
    setInput("");

    setTimeout(() => {
      const botResponse: Message = {
        id: messages.length + 2,
        text: "I'm analyzing your query about marine data. This is a demo interface - connect to Lovable Cloud to enable real AI responses!",
        sender: "bot",
      };
      setMessages((prev) => [...prev, botResponse]);
    }, 1000);
  };

  return (
    <section id="chatbot" className="py-24 bg-gradient-to-b from-background to-teal-light/10">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4">
              <span className="bg-gradient-ocean bg-clip-text text-transparent">
                AI Marine Assistant
              </span>
            </h2>
            <p className="text-muted-foreground text-lg">
              Get instant insights powered by advanced language models
            </p>
          </div>

          <Card className="shadow-ocean overflow-hidden">
            <div className="h-[500px] flex flex-col">
              <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-card to-teal-light/5">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex items-start gap-3 ${
                      message.sender === "user" ? "flex-row-reverse" : ""
                    }`}
                  >
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                        message.sender === "user"
                          ? "bg-gradient-ocean"
                          : "bg-gradient-teal"
                      }`}
                    >
                      {message.sender === "user" ? (
                        <User className="w-5 h-5 text-primary-foreground" />
                      ) : (
                        <Bot className="w-5 h-5 text-primary-foreground" />
                      )}
                    </div>
                    <div
                      className={`max-w-[75%] rounded-2xl p-4 ${
                        message.sender === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-card border border-border shadow-sm"
                      }`}
                    >
                      <p className="text-sm leading-relaxed">{message.text}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="p-4 border-t border-border bg-card">
                <div className="flex gap-2">
                  <Input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && handleSend()}
                    placeholder="Ask about marine data, fisheries, biodiversity..."
                    className="flex-1"
                  />
                  <Button
                    onClick={handleSend}
                    className="bg-gradient-ocean hover:opacity-90"
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </section>
  );
};

export default ChatbotSection;
