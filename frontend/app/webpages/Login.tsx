import React, {useState} from "react";
import {Alert, CloseButton, Spinner} from "@heroui/react";

export default function Login() {

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [errorMessage, setErrorMessage] = useState(null as string | null);
    const [loading, setLoading] = useState(false);

    async function handleForm(e: React.SubmitEvent) {
        e.preventDefault()

        await handleLogin()
    }

    async function handleLogin() {
        setErrorMessage(null);
        setLoading(true);

        const response = await fetch("http://localhost:8000/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "form-data": JSON.stringify({ email: username, password })
            },
        });

        setLoading(false);

        if (response.status !== 200) {
            setErrorMessage(response.statusText);
            return
        }

        const data = await response.json();

        console.log(data);
        localStorage.setItem("token", data.token);

        window.location.href = "/";
    }

    return (
        <div className="centered">
            <a href="/" style={{ borderRadius: "200px" }}>
                <img
                    src="/cryptalk-logo%201.png"
                    alt="Logo"
                    style={{ width: "100px", height: "100px" }}
                />
            </a>
            <br/>

            <form className="container" onSubmit={handleForm}>

                {errorMessage && (
                    <>
                        <br/>
                        <Alert className="dark rounded-4xl" style={{background: "var(--container-secondary)"}} status="danger">
                            <Alert.Indicator className="pr-0">
                                <img src="/images/assets/exclamationmark.circle.fill@4x.png" alt="Logo" style={{width: "20px", height: "20px"}}/>
                            </Alert.Indicator>
                            <Alert.Content>
                                <Alert.Title>
                                    <div className="flex center font-bold" style={{marginTop: "2.2px", color: "rgb(225, 66, 69)"}}>
                                        {errorMessage}
                                    </div>
                                </Alert.Title>
                            </Alert.Content>
                            <CloseButton style={{background: "var(--component-tertiary)", marginTop: "2.2px"}} onClick={() => setErrorMessage(null)} />
                        </Alert>
                        <br/>
                    </>
                )}

                {!errorMessage && (
                    <>
                        <h1 className="font-bold text-3xl m-2" style={{paddingTop: "12px"}}>Sign in</h1>
                    </>
                )}

                <label>Username:</label>
                <input
                    id="email"
                    className="text-sm"
                    type="text"
                    value={username}
                    placeholder="Craig@safeTalk.co"
                    onChange={(e) => setUsername(e.target.value)}
                    onInput={() => {setErrorMessage(null)}}
                    autoFocus={true}
                    onKeyDownCapture={(e) => {if (e.key === 'Enter') { if (password.length > 0) {return handleLogin()} else { document.getElementById("password")?.focus() }}}}
                    required
                />

                <br/><br/>

                <label>Password:</label>
                <input
                    id="password"
                    className="text-sm"
                    type="password"
                    value={password}
                    placeholder="Anything"
                    onChange={(e) => setPassword(e.target.value)}
                    onInput={() => {setErrorMessage(null)}}
                    onKeyDownCapture={(e) => {if (e.key === 'Enter') { if (username.length > 0) {return handleLogin()} else { document.getElementById("email")?.focus()} }}}
                    required
                />

                <br />

                { loading ? <Spinner size="lg" color="current" /> : <><br /> <input className="text-lg" type="submit" onKeyDownCapture={(e) => {if (e.key === 'Enter') {return handleLogin()}}} value="Log In" /></>}

                <br />

                <p style={{ fontSize: "14px" }}>
                    Need to sign up first?{" "}
                    <a href="/signup" style={{ color: "rgb(149 80 255)", fontWeight: 600 }}>
                        Sign up
                    </a>
                </p>
                <br/>
            </form>
        </div>
    );
}
