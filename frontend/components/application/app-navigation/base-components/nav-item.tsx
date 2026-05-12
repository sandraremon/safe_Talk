import type { FC, HTMLAttributes, MouseEventHandler, ReactNode } from "react";
import { ChevronDown, Share04 } from "@untitledui/icons";
import { Link as AriaLink } from "react-aria-components";
import { Badge } from "../../../base/badges/badges";
import { cx, sortCx } from "../../../../utils/cx";

const styles = sortCx({
    root: "group relative flex max-h-9 w-full cursor-pointer items-center rounded-md bg-primary outline-focus-ring transition duration-100 ease-linear select-none hover:bg-primary_hover focus-visible:z-10 focus-visible:outline-2 focus-visible:outline-offset-2",
    rootSelected: "bg-secondary hover:bg-secondary_hover",
});

interface NavItemBaseProps {
    /** Whether the nav item shows only an icon. */
    iconOnly?: boolean;
    /** Whether the collapsible nav item is open. */
    open?: boolean;
    /** Type of the nav item. */
    type: "link" | "collapsible" | "collapsible-child";
    /** Icon component to display. */
    icon?: FC<HTMLAttributes<HTMLOrSVGElement>>;
    /** Badge to display. */
    badge?: ReactNode;
    /** Whether the nav item is currently active. */
    current?: boolean;
    /** Whether to truncate the label text. */
    truncate?: boolean;
    /** Handler for click events. */
    onClick?: MouseEventHandler;
    /** Content to display. */
    children?: ReactNode;
}

export const NavItemBase = ({ current, type, badge, icon: Icon, children, truncate = true, onClick }: NavItemBaseProps) => {
    const iconElement = Icon && (
        <Icon
            aria-hidden="true"
            className={cx(
                "mr-2 size-5 shrink-0 rounded-4xl",
                current && "text-fg-quaternary_hover",
            )}
        />
    );

    const badgeElement =
        badge && (typeof badge === "string" || typeof badge === "number") ? (
            <Badge className="ml-3" color="gray" type="pill-color" size="sm">
                {badge}
            </Badge>
        ) : (
            badge
        );

    const labelElement = (
        <span
            className={cx(
                "flex-1 p-3 rounded-4xl font-semibold text-secondary transition-inherit-all group-hover/item:text-secondary_hover",
                truncate && "truncate",
                current && "text-secondary_hover",
            )}
        >
            {children}
        </span>
    );

    if (type === "collapsible") {
        return (
            <summary className={cx("p-2 rounded-4xl", styles.root, current && styles.rootSelected)} style={{borderRadius: "20px"}} onClick={onClick}>

                {labelElement}
            </summary>
        );
    }

    if (type === "collapsible-child") {
        return (
            <AriaLink
                rel="noopener noreferrer"
                className={cx("py-2 pr-3 pl-10 rounded-4xl", styles.root, current && styles.rootSelected)}
                onClick={onClick}
                aria-current={current ? "page" : undefined}
            >
                {labelElement}
                {badgeElement}
            </AriaLink>
        );
    }

    return (
        <AriaLink
            rel="noopener noreferrer"
            className={cx("group/item p-2 rounded-4xl", styles.root, current && styles.rootSelected)}
            onClick={onClick}
            aria-current={current ? "page" : undefined}
        >
            {iconElement}
            {labelElement}
            {badgeElement}
        </AriaLink>
    );
};
