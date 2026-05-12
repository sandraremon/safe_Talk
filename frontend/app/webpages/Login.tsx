import React, {useState} from "react";
import {Alert, CloseButton, Spinner, Tabs} from "@heroui/react";
import {User} from "~/Model/User";

export default function Login() {

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [email, setEmail] = useState("");
    const [errorMessage, setErrorMessage] = useState(null as string | null);
    const [loading, setLoading] = useState(false);

    async function handleSignIn(event: React.FormEvent<HTMLFormElement>) {

        setErrorMessage(null);
        setLoading(true);

        event.preventDefault();
        const formData = new URLSearchParams();
        formData.append("username", username);
        formData.append("password", password);

        try {

            console.log("1");

            const response = await fetch("http://localhost:8000/login", {
                method: "POST",
                body: formData,
            });

            console.log("2");

            setLoading(false);

            console.log("3");

            if (!response.ok) {
                setErrorMessage(response.statusText);
                return
            }

            const data = await response.json();

            console.log(data);
            localStorage.setItem("token", data.access_token);

            window.location.href = "/";
        } catch (error) {
            console.error("Error during login:", error);
            setLoading(false);
            setErrorMessage(error.message || "An unexpected error occurred.");
        }
    }

        async function handleSignUp(event: React.FormEvent<HTMLFormElement>) {

            setErrorMessage(null);
            setLoading(true);

            event.preventDefault();
            const data = new FormData(event.currentTarget);
            data.append("email", email);
            data.append("username", username);
            data.append("password", password);

            try {

            const response = await fetch("http://localhost:8000/register", {
                method: "POST",
                headers: {
                    "content-type": "application/json"
                },
                body: JSON.stringify({
                    "email": email,
                    "username": username,
                    "password": password,
                }),
            });

            const data2 = await response.json();
            setLoading(false);

            if (!response.ok) {
                setLoading(false)
                setErrorMessage(data2.detail || "An unexpected error occurred.");
                return
            }

            console.log(data2);
            localStorage.setItem("token", data2.access_token);

            window.location.href = "/";
            } catch (error) {
                console.error("Error during registration:", error);
                setLoading(false);
                // setErrorMessage(error.message || "An unexpected error occurred.");
            }
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

            <div className="container">

                 {errorMessage && (
                    <>
                        <br/>
                        <Alert className="dark rounded-4xl" style={{background: "var(--container-secondary)"}} status="danger">
                            <Alert.Indicator>
                                <img src="/images/assets/exclamationmark.circle.fill@4x.png" alt="Logo" style={{width: "20px", height: "20px", aspectRatio: "1/1"}}/>
                            </Alert.Indicator>
                            <Alert.Content>
                                <Alert.Title>
                                    <p className="font-bold" style={{marginTop: "2.2px", color: "rgb(225, 66, 69)"}}>
                                        {errorMessage}
                                    </p>
                                </Alert.Title>
                            </Alert.Content>
                            <CloseButton style={{background: "var(--component-tertiary)", marginTop: "2.2px"}} onClick={() => setErrorMessage(null)} />
                        </Alert>
                    </>
                )}

                {!errorMessage && (
                    <>
                        <h1 className="font-bold text-3xl" style={{paddingTop: "25px"}}>Authenticate</h1>
                    </>
                )}

                <br/><br/>

            <Tabs className="full-width" style={{margin: "-20px"}} defaultSelectedKey={"student"}>
                    <Tabs.ListContainer>
                        <Tabs.List aria-label="selection control">
                            <Tabs.Tab id="sign-in">
                                Sign in
                                <Tabs.Indicator />
                            </Tabs.Tab>
                            <Tabs.Tab id="sign-up">
                                Sign up
                                <Tabs.Indicator />
                            </Tabs.Tab>
                        </Tabs.List>
                    </Tabs.ListContainer>

                    <br/>

                    <Tabs.Panel id="sign-in" style={{padding: 0}}>

                       <form onSubmit={handleSignIn}>

                            <label>Username:</label>
                            <input
                                id="username"
                                name="username"
                                className="text-sm"
                                type="text"
                                value={username}
                                placeholder="Craig@safeTalk.co"
                                onChange={(e) => setUsername(e.target.value)}
                                onInput={() => {setErrorMessage(null)}}
                                autoFocus={true}
                                // onKeyDownCapture={(e) => {if (e.key === 'Enter') { if (password.length > 0) {return handleLogin()} else { document.getElementById("password")?.focus() }}}}
                                required
                            />

                            <br/><br/>

                            <label>Password:</label>
                            <input
                                id="password"
                                className="text-sm"
                                type="password"
                                name="password"
                                value={password}
                                placeholder="Anything"
                                onChange={(e) => setPassword(e.target.value)}
                                onInput={() => {setErrorMessage(null)}}
                                // onKeyDownCapture={(e) => {if (e.key === 'Enter') { if (username.length > 0) {return handleForm(e)} else { document.getElementById("email")?.focus()} }}}
                                required
                            />

                            <br/>

                            { loading ? <Spinner size="lg" color="current" /> : <><br /> <input className="text-lg" type="submit" onKeyDownCapture={(e) => {if (e.key === 'Enter') {return handleSignIn}}} value="Sign in" /></>}

                            <br/><br/><br/>
                       </form>

                    </Tabs.Panel>

                    <Tabs.Panel id="sign-up" style={{padding: 0}}>

                       <form onSubmit={handleSignUp}>

                            <label>Username:</label>
                            <input
                                id="username"
                                name="username"
                                className="text-sm"
                                type="text"
                                value={username}
                                placeholder="Craig@safeTalk.co"
                                onChange={(e) => setUsername(e.target.value)}
                                onInput={() => {setErrorMessage(null)}}
                                autoFocus={true}
                                required
                            />

                            <br/><br/>

                            <label>Email:</label>
                            <input
                                id="email"
                                className="text-sm"
                                type="email"
                                name="email"
                                value={email}
                                placeholder="Anything"
                                onChange={(e) => setEmail(e.target.value)}
                                onInput={() => {setErrorMessage(null)}}
                                required/>

                            <br/><br/>

                           <label>Password:</label>
                            <input
                                id="password"
                                className="text-sm"
                                type="password"
                                name="password"
                                value={password}
                                placeholder="Anything"
                                onChange={(e) => setPassword(e.target.value)}
                                onInput={() => {setErrorMessage(null)}}
                                required/>

                            <br/><br/>

                            { loading ? <Spinner size="sm" color="current" /> : <><br /> <input className="text-lg" type="submit" value="Sign up" /></>}

                            <br/><br/><br/>
                       </form>

                    </Tabs.Panel>
                </Tabs>
            </div>
        </div>
    );
}
