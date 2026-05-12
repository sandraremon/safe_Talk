import {NavAccountCard} from "../base-components/nav-account-card";
import {NavList} from "../base-components/nav-list";
import {type ChatPreview} from "~/Model/ChatPreview";
import {useEffect, useState, useRef} from "react";
import {User} from "~/Model/User";

export const SidebarNavigationSectionDividers = () => {

    let sock: WebSocket | null = null;

    const MAIN_SIDEBAR_WIDTH = 292;

    const [chats, setChats] = useState<ChatPreview[]>([]);
    const [userDetails, setUserDetails] = useState<User | null>(null);
    const [message, setMessage] = useState("");
    const [messages, setMessages] = useState<{text: string, fromMe: boolean}[]>([]);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    useEffect(() => {
        const fetchChats = async () => {
            const response = await fetch("http://localhost:8000/key/conversations", {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("token")}`,
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
                    Authorization: `Bearer ${localStorage.getItem("token")}`,
                    "Content-Type": "application/json",
                },
            });
            if (!response.ok) throw new Error("Failed to fetch user details");
            const data = await response.json();
            setUserDetails(data);
        };
        fetchUserDetails().catch(console.error);
    }, []);

    useEffect(() => {

        const token = localStorage.getItem("token");
        if (!token) return;

        const socket = new WebSocket(`ws://localhost:8000/ws?token=${token}`);

        socket.onopen = () => console.log("Connected to SafeTalk WebSocket");

        socket.onmessage = (event) => {
            const payload = JSON.parse(event.data);
            if (payload.type === "new_chat") {
                const newChat: ChatPreview = payload.data;
                setChats((prev) => {
                    const exists = prev.find(c => c.recipient_id === newChat.recipient_id);
                    if (exists) return prev;
                    return [newChat, ...prev];
                });
            }
            if (payload.type === "message") {
                setMessages(prev => [...prev, { text: payload.data.text, fromMe: false }]);
            }
        };

        socket.onclose = (e) => console.log("WebSocket closed", e.reason);
        socket.onerror = (err) => console.error("WebSocket error", err);

        sock = socket;

        return () => socket.close();
    }, []);

    const handleSend = () => {
        if (!message.trim()) return;
        setMessages(prev => [...prev, { text: message, fromMe: true }]);

        sock?.send(JSON.stringify({toUser: chats[0].recipient_id, plaintext: message}))

        setMessage("");
    };

    const sidebar = (
        <div className="flex h-full p-3">
            <aside
                style={{"--width": `${MAIN_SIDEBAR_WIDTH}px`} as React.CSSProperties}
                className="h-full flex w-full max-w-full flex-col self-center justify-center overflow-auto border-secondary bg-secondary pt-4 shadow-xs md:border-r lg:w-(--width) rounded-3xl lg:border lg:pt-5"
            >
                <NavList chats={chats} className="mt-0.5 flex rounded-4xl gap-2"/>
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
                    {/* Messages area */}
                    <div className="w-full pr-6 pl-6 h-full flex flex-col overflow-auto">
                        {messages.length === 0 && (
                            <div className="flex-1 flex items-center justify-center">
                                <p className="text-white/40 text-sm">No messages yet. Say hello!</p>
                            </div>
                        )}
                        {messages.map((msg, i) => (
                            <div key={i} className={`flex ${msg.fromMe ? "justify-end" : "justify-start"}`}>
                                <div
                                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl text-sm ${
                                        msg.fromMe
                                            ? "bg-white rounded-br-sm"
                                            : "bg-white/20 text-white rounded-bl-sm"
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
                                placeholder="Type a message..."
                                className="text-chat placeholder-purple-300 text-sm outline-none"
                            />

                            {/* Send button */}
                            <button
                                onClick={handleSend}
                                className="rounded-full bg-purple-500 flex items-center justify-center hover:bg-white/90 transition-colors" style={{height: "50px", width: "50px", padding: "12px", background: "var(--primary-color)"}}>
                                <img src="/images/assets/arrow.up.right@4x.png" width="20px" alt="Send"/>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};