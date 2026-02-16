export default function ChatSidebar({ executions, createExecution }) {
    return (
        <div className="w-64 bg-gray-800 p-4 border-r border-gray-700 text-white">
            <button
                onClick={createExecution}
                className="w-full bg-blue-600 p-2 rounded mb-4"
            >
                + New Chat
            </button>

            <div className="space-y-2">
                {executions.map((ex) => (
                    <div
                        key={ex.id}
                        className="p-2 bg-gray-700 rounded"
                    >
                        Chat {ex.id.slice(0, 6)}
                    </div>
                ))}
            </div>
        </div>
    );
}
