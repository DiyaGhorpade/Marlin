import Navigation from "@/components/Navigation";
import ChatbotSection from "@/components/ChatbotSection";

const Chatbot = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="pt-16">
        <ChatbotSection />
      </div>
    </div>
  );
};

export default Chatbot;
