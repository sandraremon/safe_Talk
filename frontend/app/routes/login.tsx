import type { Route } from "./+types/login";
import Login from "~/webpages/Login";
import Loading from "~/webpages/fragments/Loading";

export function loader() {
    return {};
}

export function HydrateFallback() {
    return <Loading/>;
}

export default function login({loaderData}: Route.ComponentProps) {
    return <Login/>;
}