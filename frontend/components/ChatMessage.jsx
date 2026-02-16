import ReactMarkdown from "react-markdown";

export default function ChatMessage({ message }) {

    const isUser = message.role === "user";

    return (
        <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
            <div
                className={`max-w-xl p-4 rounded-xl
        ${isUser ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-100"}`}
            >
                <ReactMarkdown>
                    {message.content}
                </ReactMarkdown>
            </div>
        </div>
    );
}
