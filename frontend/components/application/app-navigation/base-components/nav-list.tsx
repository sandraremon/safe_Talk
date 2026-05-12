import { useState } from "react";
import { cx } from "../../../../utils/cx";
import { NavItemBase } from "./nav-item";
import type {ChatPreview} from "~/Model/ChatPreview";

export const NavList = ({chats, className}: {chats: ChatPreview[], className: string} ) => {

    return (
        <ul className={cx("flex flex-col px-4 pt-5" + className)}>
            {chats.map((item) => {
                if (chats.length) {
                    return (
                        <NavItemBase badge={null} icon={undefined} type="collapsible">
                            {item.username}
                        </NavItemBase>
                    );
                }
            })}
        </ul>
    );
};
