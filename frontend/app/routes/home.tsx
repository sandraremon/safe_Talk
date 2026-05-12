import type { Route } from "./+types/home";
import { Welcome } from "~/webpages/welcome";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "New React Router App" },
    { name: "description", content: "Welcome to React Router!" },
  ];
}
if (typeof window !== "undefined" && !localStorage.getItem("token")) {
  window.location.href = "/login";
}
export default function Home() {
  return <Welcome />;
}
