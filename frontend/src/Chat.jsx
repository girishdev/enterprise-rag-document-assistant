import { useEffect, useState } from "react";
import {
	getConversations,
	getMessages,
} from "./api";

const API_URL = import.meta.env.VITE_API_URL;

export default function Chat({ token }) {
	const [message, setMessage] = useState("");
	const [reply, setReply] = useState("");
	const [conversationId, setConversationId] = useState(null);
	const [conversations, setConversations] = useState([]);
	const [messages, setMessages] = useState([]);
	const [sources, setSources] = useState([]);
	const [documents, setDocuments] = useState([]);
	const [selectedDocumentId, setSelectedDocumentId] = useState("");

	async function loadConversations() {
		try {
			const data = await getConversations(token);

			setConversations(
				Array.isArray(data) ? data : []
			);
		} catch (error) {
			console.error(error);
			setConversations([]);
		}
	}

	async function loadDocuments() {
		const response = await fetch(
			`${API_URL}/documents`,
			{
				headers: {
					Authorization: `Bearer ${token}`,
				},
			}
		);

		if (response.ok) {
			setDocuments(await response.json());
		}
	}

	useEffect(() => {
		loadConversations();
		loadDocuments();
	}, []);

	async function selectConversation(id) {
		setConversationId(id);

		const data = await getMessages(token, id);
		setMessages(data);
	}

	async function sendMessage() {
		setReply("");

		const response = await fetch(
			`${API_URL}/chat/stream`,
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					Authorization: `Bearer ${token}`,
				},
				body: JSON.stringify({
					message,
					conversation_id: conversationId,
					document_id: selectedDocumentId || null,
				}),
			}
		);

		const reader = response.body.getReader();
		const decoder = new TextDecoder();

		while (true) {
			const { value, done } = await reader.read();

			if (done) break;

			const text = decoder.decode(value);

			for (const line of text.split("\n")) {
				if (!line.startsWith("data: ")) continue;

				const data = line.replace("data: ", "");

				if (data.startsWith("[SOURCES:")) {
					const sourceData = data.slice(
						"[SOURCES:".length,
						-1
					);

					setSources(JSON.parse(sourceData));
					continue;
				}

				if (data.startsWith("[DONE:")) {
					const conversationId = data.slice(
						"[DONE:".length,
						-1
					);

					setConversationId(conversationId);
					continue;
				}

				// Only normal AI text should reach here
				setReply((prev) => prev + data);
			}
		}

		setMessage("");
	}

	return (
		<div>
			<h2>Enterprise RAG Document Assistant</h2>

			<hr />

			<h3>Conversations</h3>

			{conversations.map((conversation) => (
				<button
					key={conversation.id}
					onClick={() =>
						selectConversation(conversation.id)
					}
				>
					{conversation.title || "Conversation"}
				</button>
			))}

			<hr />

			<select
				value={selectedDocumentId}
				onChange={(e) =>
					setSelectedDocumentId(e.target.value)
				}
			>
				<option value="">
					All Documents
				</option>

				{documents.map((document) => (
					<option
						key={document.id}
						value={document.id}
					>
						{document.original_filename}
					</option>
				))}
			</select>

			<h3>Messages</h3>

			{messages.map((item) => (
				<p key={item.id}>
					<strong>{item.role}:</strong>{" "}
					{item.content}
				</p>
			))}

			{reply && (
				<p>
					<strong>assistant:</strong> {reply}
				</p>
			)}

			<input
				value={message}
				placeholder="Ask something..."
				onChange={(e) => setMessage(e.target.value)}
			/>

			<button
				onClick={sendMessage}
				disabled={!message.trim()}
			>
				Send
			</button>

			{sources.length > 0 && (
				<div>
					<strong>Sources:</strong>

					{sources.map((source, index) => (
						<div key={index}>
							{source.filename}

							{source.page_number
								? ` - Page ${source.page_number}`
								: ` - Chunk ${source.chunk_index}`
							}
						</div>
					))}
				</div>
			)}

		</div>
	);
}