import {NavAccountCard} from "../base-components/nav-account-card";
import {NavList} from "../base-components/nav-list";
import {type ChatPreview} from "~/Model/ChatPreview";
import {useEffect, useState, useRef} from "react";
import {User} from "~/Model/User";

const decodeHex = (hex: string) => {
    if (!hex) return "";
    try {
        const bytes = new Uint8Array(hex.match(/.{1,2}/g)!.map(byte => parseInt(byte, 16)));
        return new TextDecoder().decode(bytes);
    } catch {
        return hex; // Fallback if not valid hex
    }
};

export const SidebarNavigationSectionDividers = () => {

    // ── Fix #4: store the WebSocket in a ref so handleSend always sees the live socket ──
    const sockRef = useRef<WebSocket | null>(null);

    const MAIN_SIDEBAR_WIDTH = 292;

    const [chats, setChats] = useState<ChatPreview[]>([]);
    const [userDetails, setUserDetails] = useState<User | null>(null);
    const [message, setMessage] = useState("");
    const [messages, setMessages] = useState<{text: string, fromMe: boolean}[]>([]);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // ── Fix #5: track which conversation is currently open ──
    const [activeChat, setActiveChat] = useState<ChatPreview | null>(null);

    // ── Search State ──
    const [searchQuery, setSearchQuery] = useState("");
    const [searchResults, setSearchResults] = useState<{username: string}[]>([]);

    // Auto-scroll to the newest message
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    // ── Load conversation list + own user details on mount ──
    useEffect(() => {
        const token = localStorage.getItem("token");

        const fetchChats = async () => {
            const response = await fetch("http://localhost:8000/key/conversations", {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
            });
            if (!response.ok) throw new Error("Failed to fetch chats");
            const data: ChatPreview[] = await response.json();
            setChats(data);
        };
        fetchChats().catch(console.error);

        const fetchUserDetails = async () => {
            const response = await fetch("http://localhost:8000/key/mydetails", {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
            });
            if (!response.ok) throw new Error("Failed to fetch user details");
            const data = await response.json();
            setUserDetails(data);
        };
        fetchUserDetails().catch(console.error);
    }, []);

    // ── Open WebSocket once on mount ──
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) return;

        const socket = new WebSocket(`ws://localhost:8000/ws?token=${token}`);

        socket.onopen = () => console.log("Connected to SafeTalk WebSocket");

        // ── Fix #3: read `payload.ciphertext` — that is what the server actually sends ──
        socket.onmessage = (event) => {
            const payload = JSON.parse(event.data);

            if (payload.type === "new_chat") {
                const newChat: ChatPreview = payload.data;
                setChats((prev) => {
                    const exists = prev.find(c => c.username === newChat.username);
                    if (exists) return prev;
                    return [newChat, ...prev];
                });
            }

            if (payload.type === "message") {
                setMessages(prev => [...prev, { text: decodeHex(payload.ciphertext), fromMe: false }]);
            }
        };

        socket.onclose = (e) => console.log("WebSocket closed", e.reason);
        socket.onerror = (err) => console.error("WebSocket error", err);

        // ── Fix #4: assign to ref, not a plain let variable ──
        sockRef.current = socket;

        return () => {
            socket.close();
            sockRef.current = null;
        };
    }, []);

    // ── Fix #6: load message history whenever the active chat changes ──
    useEffect(() => {
        if (!activeChat) return;

        // Clear old messages while the new ones load
        setMessages([]);

        const token = localStorage.getItem("token");
        fetch(`http://localhost:8000/key/messages/${activeChat.username}`, {
            headers: { Authorization: `Bearer ${token}` },
        })
            .then(r => r.json())
            .then((history: { from: string; ciphertext: string; timestamp: string }[]) => {
                const myUsername = userDetails?.username ?? "";
                setMessages(
                    history.map(m => ({
                        text: decodeHex(m.ciphertext),
                        fromMe: m.from === myUsername,
                    }))
                );
            })
            .catch(console.error);
    }, [activeChat, userDetails?.username]);

    // ── Search Effect ──
    useEffect(() => {
        if (!searchQuery.trim()) {
            setSearchResults([]);
            return;
        }
        const delayDebounceFn = setTimeout(() => {
            const token = localStorage.getItem("token");
            fetch(`http://localhost:8000/key/users/search?user=${encodeURIComponent(searchQuery)}`, {
                headers: { Authorization: `Bearer ${token}` }
            })
                .then(r => r.json())
                .then(data => setSearchResults(data))
                .catch(console.error);
        }, 300);
        return () => clearTimeout(delayDebounceFn);
    }, [searchQuery]);

    // ── Start new chat from search ──
    const handleStartChat = (username: string) => {
        const existingChat = chats.find(c => c.username === username);
        if (existingChat) {
            setActiveChat(existingChat);
        } else {
            // Add as a new chat with a placeholder id (backend only needs username to send)
            const newChat = { username, recipient_id: -1 };
            setChats(prev => [newChat, ...prev]);
            setActiveChat(newChat);
        }
        setSearchQuery("");
        setSearchResults([]);
    };

    // ── Fix #2 + #5: send to the correct recipient using the correct field names ──
    const handleSend = () => {
        if (!message.trim()) return;

        // Fix #5: guard if no conversation is selected yet
        if (!activeChat) {
            console.warn("No active chat selected");
            return;
        }

        // Encode the plaintext as a hex string (backend stores bytes via fromhex)
        const encoded = Array.from(new TextEncoder().encode(message))
            .map(b => b.toString(16).padStart(2, "0"))
            .join("");

        // Fix #2: correct field name is `to` (string username), not `toUser` (numeric id)
        sockRef.current?.send(JSON.stringify({ to: activeChat.username, ciphertext: encoded }));

        setMessages(prev => [...prev, { text: message, fromMe: true }]);
        setMessage("");
    };

    const sidebar = (
        <div className="flex h-full p-3">
            <aside
                style={{"--width": `${MAIN_SIDEBAR_WIDTH}px`} as React.CSSProperties}
                className="h-full flex w-full max-w-full flex-col self-center justify-center overflow-auto border-secondary bg-secondary pt-4 shadow-xs md:border-r lg:w-(--width) rounded-3xl lg:border lg:pt-5"
            >
                {/* ── Search Bar UI ── */}
                <div className="px-4 pb-2 relative z-20">
                    <input
                        type="text"
                        placeholder="Search users..."
                        className="w-full bg-black/20 text-white rounded-xl px-4 py-2 text-sm outline-none placeholder-white/40"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                    {searchResults.length > 0 && (
                        <div className="absolute top-full left-4 right-4 mt-1 bg-gray-800 rounded-xl overflow-hidden max-h-40 overflow-y-auto shadow-lg border border-white/10">
                            {searchResults.map(u => (
                                <button
                                    key={u.username}
                                    className="w-full text-left px-4 py-2 text-sm text-white hover:bg-white/10 transition-colors"
                                    onClick={() => handleStartChat(u.username)}
                                >
                                    {u.username}
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                {/* Fix #5: pass activeUsername + onSelect so clicking a chat works */}
                <NavList
                    chats={chats}
                    className="mt-0.5 flex rounded-4xl gap-2"
                    activeUsername={activeChat?.username}
                    onSelect={(chat) => setActiveChat(chat)}
                />
                    <div className="mt-auto flex rounded-4xl flex-col gap-5 px-2 py-4 lg:gap-6 lg:px-4 lg:py-4">
                        <NavAccountCard user={userDetails as User}/>
                    </div>
            </aside>
        </div>
    );

    return (
        <div className="flex h-screen w-screen overflow-hidden">

            {/* Sidebar */}
            <div className="lg:fixed lg:inset-y-0 lg:left-0 z-10">
                {sidebar}
            </div>

            {/* Main chat area */}
            <div className="flex fixed flex-col self-center justify-center overflow-auto border-secondary bg-secondary pt-4 shadow-xs md:border-r rounded-3xl lg:border mr-6"
                style={{
                    marginLeft: MAIN_SIDEBAR_WIDTH + 40,
                    background: "var(--form-background-color)",
                    height: "calc(100vh - 20px)",
                    width: "calc(100vw - 292px - 50px)",
                }}>

                <div className="flex h-full w-full flex-col overflow-hidden rounded-3xl">

                    {/* Chat header — shows active conversation name */}
                    {activeChat && (
                        <div className="px-6 py-4 border-b border-white/20 flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center text-white text-sm font-bold">
                                {activeChat.username[0].toUpperCase()}
                            </div>
                            <span className="text-white font-semibold">{activeChat.username}</span>
                        </div>
                    )}

                    {/* Messages area */}
                    <div className="w-full pr-6 pl-6 h-full flex flex-col overflow-auto">
                        {!activeChat && (
                            <div className="flex-1 flex items-center justify-center">
                                <p className="text-white/40 text-sm">Select a conversation or search for a user to start chatting.</p>
                            </div>
                        )}
                        {activeChat && messages.length === 0 && (
                            <div className="flex-1 flex items-center justify-center">
                                <p className="text-white/40 text-sm">No messages yet. Say hello to {activeChat.username}!</p>
                            </div>
                        )}
                        {messages.map((msg, i) => (
                            <div key={i} className={`flex ${msg.fromMe ? "justify-end" : "justify-start"}`}>
                                <div
                                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl text-sm mt-2 mb-2 ${
                                        msg.fromMe
                                            ? "bg-white text-black rounded-br-sm"
                                            : "bg-white/20 text-black rounded-bl-sm"
                                    }`}
                                >
                                    {msg.text}
                                </div>
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Message input bar */}
                    <div className="px-4 py-4 bg-white/10 backdrop-blur-sm border-t border-white/20">
                        <div className="flex p-20 items-center gap-3 rounded-full px-4 py-2">
                            <input
                                type="text"
                                value={message}
                                onChange={(e) => setMessage(e.target.value)}
                                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                                placeholder={activeChat ? `Message ${activeChat.username}…` : "Select a chat first…"}
                                disabled={!activeChat}
                                className="text-chat placeholder-purple-300 text-sm outline-none"
                            />

                            {/* Send button */}
                            <button
                                onClick={handleSend}
                                disabled={!activeChat}
                                className="rounded-full bg-purple-500 flex items-center justify-center hover:bg-white/90 transition-colors disabled:opacity-50" style={{height: "50px", width: "50px", padding: "12px", background: "var(--primary-color)"}}>
                                <img src="/images/assets/arrow.up.right@4x.png" width="20px" alt="Send"/>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
