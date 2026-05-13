import type { FC, HTMLAttributes } from "react";
import { useCallback, useEffect, useRef } from "react";
import type { Placement } from "@react-types/overlays";
import { LogOut01 } from "@untitledui/icons";
import { useFocusManager } from "react-aria";
import type { DialogProps as AriaDialogProps } from "react-aria-components";
import { Dialog as AriaDialog} from "react-aria-components";
import { useBreakpoint } from "../../../../hooks/use-breakpoint";
import { cx } from "../../../../utils/cx";
import {Button} from "@heroui/react";
import type {User} from "~/Model/User";

export type NavAccountType = {
    /** Unique identifier for the nav item. */
    id: string;
    /** Name of the account holder. */
    name: string;
    /** Email address of the account holder. */
    email: string;
    /** Avatar image URL. */
    avatar: string;
    /** Online status of the account holder. This is used to display the online status indicator. */
    status: "online" | "offline";
};

export const AccountManager = ({className, selectedAccountId = "olivia", ...dialogProps}: AriaDialogProps & { className?: string; accounts?: NavAccountType[]; selectedAccountId?: string }) => {

    const focusManager = useFocusManager();
    const dialogRef = useRef<HTMLDivElement>(null);

    const onKeyDown = useCallback(
        (e: KeyboardEvent) => {
            switch (e.key) {
                case "ArrowDown":
                    focusManager?.focusNext({ tabbable: true, wrap: true });
                    break;
                case "ArrowUp":
                    focusManager?.focusPrevious({ tabbable: true, wrap: true });
                    break;
            }
        },
        [focusManager],
    );

    useEffect(() => {
        const element = dialogRef.current;
        if (element) {
            element.addEventListener("keydown", onKeyDown);
        }

        return () => {
            if (element) {
                element.removeEventListener("keydown", onKeyDown);
            }
        };
    }, [onKeyDown]);

    return (
        <AriaDialog
            {...dialogProps}
            ref={dialogRef}
            className={cx("w-66 rounded-xl bg-secondary_alt shadow-lg ring ring-secondary_alt outline-hidden", className)}
        >

            <div className="pt-1 pb-1.5">
                <NavAccountCardMenuItem label="Sign out" icon={LogOut01} />
            </div>
        </AriaDialog>
    );
};

const NavAccountCardMenuItem = ({
    icon: Icon,
    label,
    shortcut,
    ...buttonProps
}: {
    icon?: FC<{ className?: string }>;
    label: string;
    shortcut?: string;
} & HTMLAttributes<HTMLButtonElement>) => {
    return (
        <button {...buttonProps} className={cx("group/item w-full cursor-pointer px-1.5 focus:outline-hidden", buttonProps.className)}>
            <div
                className={cx(
                    "flex w-full items-center justify-between gap-3 rounded-md p-2 group-hover/item:bg-primary_hover",
                    // Focus styles.
                    "outline-focus-ring group-focus-visible/item:outline-2 group-focus-visible/item:outline-offset-2",
                )}
            >
                <div className="flex gap-2 text-sm font-semibold text-secondary group-hover/item:text-secondary_hover">
                    {Icon && <Icon className="size-5 text-fg-quaternary group-hover/item:text-fg-quaternary_hover" />} {label}
                </div>

                {shortcut && (
                    <kbd className="flex rounded px-1 py-px font-body text-xs font-medium text-tertiary ring-1 ring-secondary ring-inset">{shortcut}</kbd>
                )}
            </div>
        </button>
    );
};

export const NavAccountCard = ({user}: {user: User}) => {
    const triggerRef = useRef<HTMLDivElement>(null);
    const isDesktop = useBreakpoint("lg");

    return (
        <div ref={triggerRef} className="relative rounded-3xl flex items-center justify-between gap-3 p-3 bg-primary shadow-2xs">
            <div className="flex items-center gap-3">
                <img src="/cryptalk-logo%201.png" alt="logo" className={cx("size-10 rounded-full")} />

                <div className="flex flex-col gap-x-0.5 text-sm">
                    <p className="font-bold">{user?.username || "Unknown"}</p>
                    <p className="text-xs font-semibold">{user?.email || "Unknown"}</p>
                </div>
            </div>
            <div>
                <Button
                    variant="danger-soft"
                    className="rounded-4xl"
                    isIconOnly
                    onPress={() => {
                        localStorage.clear(); // This deletes the token
                        window.location.href = "/login"; // This sends them to the login screen
                    }}
                >
                    <img src="/images/assets/door.left.hand.open@4x.png" alt="Logout" className="w-3.5"/>
                </Button>
            </div>
        </div>
    );
};
