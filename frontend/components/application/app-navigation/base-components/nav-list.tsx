import { cx } from "../../../../utils/cx";
import { NavItemBase } from "./nav-item";
import type {ChatPreview} from "~/Model/ChatPreview";

interface NavListProps {
    chats: ChatPreview[];
    className: string;
    activeUsername?: string;
    onSelect?: (chat: ChatPreview) => void;
}

export const NavList = ({ chats, className, activeUsername, onSelect }: NavListProps) => {
    return (
        <ul className={cx("flex flex-col px-4 pt-5" + className)}>
            {chats.map((item) => (
                <NavItemBase
                    key={item.username}
                    badge={null}
                    icon={undefined}
                    type="collapsible"
                    current={item.username === activeUsername}
                    onClick={() => onSelect?.(item)}
                >
                    {item.username}
                </NavItemBase>
            ))}
        </ul>
    );
};
