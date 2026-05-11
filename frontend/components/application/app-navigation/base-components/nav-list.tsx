import { useState } from "react";
import { cx } from "../../../../utils/cx";
import { NavItemBase } from "./nav-item";
import type {SidebarNavigationProps} from "../sidebar-navigation/sidebar-section-dividers";

export const NavList = ({activeChat, chats, className}: SidebarNavigationProps) => {
    const [open, setOpen] = useState(false);

    return (
        <ul className={cx("flex flex-col px-4 pt-5", className)}>
            {chats.map((item, index) => {

                if (chats.length) {
                    return (
                        <NavItemBase badge={null} icon={undefined} type="collapsible">
                            {item.recipient_name}
                        </NavItemBase>
                    );
                }
            })}
        </ul>
    );
};
