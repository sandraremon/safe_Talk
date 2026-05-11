export class User {

    id: bigint;
    username: string;
    email: string;

    constructor(id: bigint, username: string, email: string) {
        this.id = id;
        this.username = username;
        this.email = email;
    }
}