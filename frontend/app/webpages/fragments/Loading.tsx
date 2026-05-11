import {Spinner} from "@heroui/react";

export default function Loading() {
    return (
        <div className="centered">
            <Spinner className="size-27 accent-purple-400"></Spinner>
        </div>
    )
}