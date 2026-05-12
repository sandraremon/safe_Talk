import Loading from "~/webpages/fragments/Loading";
import {useNavigate} from "react-router";
import {useEffect} from "react";

export function loader() {}

export function HydrateFallback() {
    return <Loading/>;
}

export default function logout() {
    useEffect(() => {
        localStorage.removeItem("token");
        window.location.href = "/"
    }, []);
}