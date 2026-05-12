export class ChatPreview {
    username: string;
    recipient_id: number;

    constructor(username: string, recipient_id: number) {
        this.username = username;
        this.recipient_id = recipient_id;
    }
}