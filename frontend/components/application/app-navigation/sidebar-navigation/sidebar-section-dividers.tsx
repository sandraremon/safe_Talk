import {MobileNavigationHeader} from "../base-components/mobile-header";
import {NavAccountCard} from "../base-components/nav-account-card";
import {NavList} from "../base-components/nav-list";
import  {type ChatPreview} from "~/Model/ChatPreview";
import {useEffect, useState} from "react";
import {User} from "~/Model/User";


export interface SidebarNavigationProps {
    /** URL of the currently active item. */
    activeChat: bigint,
    /** List of items to display. */
    chats: ChatPreview[],

    className?: string
}

export const SidebarNavigationSectionDividers = () => {

    const MAIN_SIDEBAR_WIDTH = 292;

    const [chats, setChats] = useState<ChatPreview[]>([]);
    const [userDetails, setUserDetails] = useState<User | null>(null);

    useEffect(() => {
      const fetchChats = async () => {
        const response = await fetch("http://localhost:8000/conversations", {
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
          const response = await fetch("http://localhost:8080/mydetails", {
              method: "GET",
              headers: {
                  Authorization: `Bearer ${localStorage.getItem("token")}`,
                  "Content-Type": "application/json",
              },
          })

          if (!response.ok) {
              console.error(response.statusText, response.status, response.headers, response.body);
              throw new Error("Failed to fetch user details");
          }

          const data = await response.json();
          setUserDetails(data);
      }

    }, []);

    const content = (
        <div className="flex h-full p-3">
            <aside
                style={{"--width": `${MAIN_SIDEBAR_WIDTH}px`,} as React.CSSProperties}
                className="h-full flex w-full max-w-full flex-col self-center justify-center overflow-auto border-secondary bg-secondary pt-4 shadow-xs md:border-r lg:w-(--width) rounded-3xl lg:border lg:pt-5"
            >
                <NavList activeChat={chats[0]?.recipient_id} chats={chats} className="mt-0.5 rounded-4xl"/>

                <div className="mt-auto fle rounded-4xl flex-col gap-5 px-2 py-4 lg:gap-6 lg:px-4 lg:py-4">
                    <NavAccountCard/>
                </div>
            </aside>
        </div>
    );

    return (
        <>
            {/* Desktop sidebar navigation */}
            <div className="lg:fixed lg:inset-y-0">{content}</div>

            {/* Placeholder to take up physical space because the real sidebar has `fixed` position. */}
            <div style={{paddingLeft: MAIN_SIDEBAR_WIDTH + 40}} className=" lg:sticky lg:top-0 lg:bottom-0 lg:left-0 lg:block">
                <button>You had me at Hello</button>
            </div>
        </>
    );
};

