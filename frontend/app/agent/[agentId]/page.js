"use client";

import { useState, use } from "react";
import api from "@/lib/api";
import ChatSidebar from "@/components/ChatSidebar";
import ChatMessage from "@/components/ChatMessage";
import ChatInput from "@/components/ChatInput";

export default function AgentChat({ params }) {

    const resolvedParams = use(params);
    const agentId = resolvedParams.agentId;

    const [messages, setMessages] = useState([]);

    const sendMessage = async (input) => {

        const userMessage = {
            role: "user",
            content: input
        };

        setMessages(prev => [...prev, userMessage]);

        const res = await api.post("/execute", {
            text: input
        });

        const assistantMessage = {
            role: "assistant",
            content:
                res.data.output?.ollama?.response ||
                JSON.stringify(res.data)
        };

        setMessages(prev => [...prev, assistantMessage]);
    };

    return (
        <div className="flex h-screen">

            <ChatSidebar executions={[]} createExecution={() => { }} />

            <div className="flex flex-col flex-1">

                <div className="flex-1 p-6 space-y-4">

                    {messages.map((msg, i) => (
                        <ChatMessage key={i} message={msg} />
                    ))}

                </div>

                <ChatInput onSend={sendMessage} />

            </div>

        </div>
    );
}
