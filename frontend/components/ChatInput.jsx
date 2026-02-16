"use client";

import { useState } from "react";

export default function ChatInput({ onSend }) {

    const [input, setInput] = useState("");

    const handleSend = () => {

        if (!input.trim()) return;

        onSend(input);

        setInput("");
    };

    return (
        <div className="p-4 border-t border-gray-700 flex gap-2">
            <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                className="flex-1 p-3 rounded bg-gray-800 text-white"
            />
            <button
                onClick={handleSend}
                className="bg-blue-600 px-4 rounded text-white"
            >
                Send
            </button>
        </div>
    );
}
