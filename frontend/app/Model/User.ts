export class User {

    id?: bigint;
    username: string;
    email: string;
    password?: string;

    // @ts-ignore
    constructor(id?: bigint, username: string, email: string, password?: string) {
        this.id = id;
        this.username = username;
        this.email = email;
        this.password = password;
    }
}