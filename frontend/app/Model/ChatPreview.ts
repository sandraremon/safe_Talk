export class ChatPreview {

    recipient_name: string;
    recipient_id: bigint;

    constructor(recipient_name: string, recipient_id: bigint) {
        this.recipient_name = recipient_name;
        this.recipient_id = recipient_id;
    }
}