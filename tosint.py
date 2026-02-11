#!/usr/bin/env python3
import argparse
import json
import requests

TEXT_OUTPUT_ENABLED = True


def text_print(*args, **kwargs):
    if TEXT_OUTPUT_ENABLED:
        print(*args, **kwargs)


def format_output_value(value):
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return value


def print_field(data, key, label=None):
    if key not in data:
        return
    value = data[key]
    if value is None:
        return
    if isinstance(value, str) and not value.strip():
        return
    text_print(f"{label or key}: {format_output_value(value)}")


def normalize_single_line(value):
    return " ".join(str(value).split())


def print_section(title):
    text_print(f"\n[{title}]")


def print_chat_summary(chat):
    print_field(chat, "title", "Chat Title")
    print_field(chat, "type", "Chat Type")
    print_field(chat, "id", "Chat ID")
    print_field(chat, "username", "Chat Username")
    print_field(chat, "active_usernames", "Chat Active Usernames")
    if "description" in chat and chat["description"] is not None:
        text_print(f"Chat Description: {normalize_single_line(chat['description'])}")
    print_field(chat, "is_forum", "Chat Is Forum")
    print_field(chat, "is_direct_messages", "Chat Is Direct Messages")
    print_field(chat, "has_visible_history", "Chat Has Visible History")
    print_field(chat, "has_hidden_members", "Chat Has Hidden Members")
    print_field(chat, "has_protected_content", "Chat Has Protected Content")
    print_field(chat, "join_to_send_messages", "Join Required To Send")
    print_field(chat, "join_by_request", "Join Requires Admin Approval")
    print_field(chat, "slow_mode_delay", "Slow Mode Delay (s)")
    print_field(chat, "message_auto_delete_time", "Message Auto Delete Time (s)")
    print_field(chat, "linked_chat_id", "Linked Chat ID")
    if "location" in chat and chat["location"]:
        text_print(f"Chat Location: {format_output_value(chat['location'])}")

    if "permissions" in chat and chat["permissions"]:
        text_print(f"Default Chat Permissions: {format_output_value(chat['permissions'])}")

    if "pinned_message" in chat and chat["pinned_message"]:
        pinned = chat["pinned_message"]
        text_print("Pinned Message:")
        print_field(pinned, "message_id", "  Message ID")
        print_field(pinned, "date", "  Date (unix)")
        print_field(pinned, "author_signature", "  Author Signature")
        print_field(pinned, "text", "  Text")
        if "from" in pinned and pinned["from"]:
            text_print(f"  From: {pinned['from']}")
        if "sender_chat" in pinned and pinned["sender_chat"]:
            text_print(f"  Sender Chat: {pinned['sender_chat']}")


def print_linked_chat_summary(chat):
    text_print("Linked Chat Details:")
    print_field(chat, "title", "  Title")
    print_field(chat, "type", "  Type")
    print_field(chat, "id", "  ID")
    print_field(chat, "username", "  Username")
    print_field(chat, "active_usernames", "  Active Usernames")
    if "description" in chat and chat["description"] is not None:
        text_print(f"  Description: {normalize_single_line(chat['description'])}")


def format_admin_name(user):
    if not user:
        return "Unknown"
    first_name = user.get("first_name", "")
    last_name = user.get("last_name", "")
    full_name = f"{first_name} {last_name}".strip()
    if full_name:
        return full_name
    if user.get("username"):
        return user["username"]
    return str(user.get("id", "Unknown"))


def extract_admin_permissions(chat_member):
    permissions = {}
    for key, value in chat_member.items():
        if key.startswith("can_") and isinstance(value, bool):
            permissions[key] = value
    for key in ["is_anonymous", "can_manage_direct_messages"]:
        if key in chat_member and isinstance(chat_member[key], bool):
            permissions[key] = chat_member[key]
    return permissions


def print_admin_details(chat_member, index):
    user = chat_member.get("user", {})
    text_print(f"- #{index}")
    print_field(user, "first_name", "  First Name")
    print_field(user, "last_name", "  Last Name")
    print_field(user, "id", "  User ID")
    print_field(user, "username", "  Username")
    print_field(user, "is_bot", "  Is Bot")
    print_field(chat_member, "status", "  Status")
    print_field(chat_member, "custom_title", "  Custom Title")
    permissions = extract_admin_permissions(chat_member)
    if permissions:
        text_print(f"  Permissions: {format_output_value(permissions)}")


def telegram_api_get(token, method, params=None):
    url = f"https://api.telegram.org/bot{token}/{method}"
    response = requests.get(url, params=params)
    return response.json()


def get_bot_info(token):
    return telegram_api_get(token, "getMe")


def get_bot_description(token):
    return telegram_api_get(token, "getMyDescription")


def get_bot_short_description(token):
    return telegram_api_get(token, "getMyShortDescription")


def get_default_admin_rights(token, for_channels=False):
    params = {"for_channels": "true"} if for_channels else None
    return telegram_api_get(token, "getMyDefaultAdministratorRights", params=params)


def get_bot_chat_member(token, chat_id, user_id):
    params = {"chat_id": chat_id, "user_id": user_id}
    return telegram_api_get(token, "getChatMember", params=params)


def get_chat_info(token, chat_id):
    params = {"chat_id": chat_id}
    return telegram_api_get(token, "getChat", params=params)


def export_chat_invite_link(token, chat_id):
    params = {"chat_id": chat_id}
    return telegram_api_get(token, "exportChatInviteLink", params=params)


def create_chat_invite_link(token, chat_id):
    params = {"chat_id": chat_id}
    return telegram_api_get(token, "createChatInviteLink", params=params)


def get_chat_member_count(token, chat_id):
    params = {"chat_id": chat_id}
    return telegram_api_get(token, "getChatMemberCount", params=params)


def get_chat_administrators(token, chat_id):
    params = {"chat_id": chat_id}
    return telegram_api_get(token, "getChatAdministrators", params=params)


def print_invite_links(chat_invite_link, exported_invite_link, created_invite_link):
    if not chat_invite_link and not exported_invite_link and not created_invite_link:
        text_print("Invite Links: None")
        return
    text_print("Invite Links:")
    text_print(f"  Chat Invite Link: {chat_invite_link}")
    text_print(f"  Chat Invite Link (exported): {exported_invite_link}")
    text_print(f"  Chat Invite Link (created): {created_invite_link}")


def build_admin_json(chat_member, index):
    user = chat_member.get("user", {})
    return {
        "index": index,
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "user_id": user.get("id"),
        "username": user.get("username"),
        "is_bot": user.get("is_bot"),
        "status": chat_member.get("status"),
        "custom_title": chat_member.get("custom_title"),
        "permissions": extract_admin_permissions(chat_member),
    }


def emit_json_report(report, print_json, json_file):
    if not print_json and not json_file:
        return
    report_payload = json.dumps(report, indent=2, ensure_ascii=False)
    if print_json:
        print(report_payload)
    if json_file:
        try:
            with open(json_file, "w", encoding="utf-8") as file_obj:
                file_obj.write(report_payload)
                file_obj.write("\n")
            text_print(f"\nJSON report saved to: {json_file}")
        except OSError as error:
            text_print(f"\nATTENTION Unable to save JSON report to '{json_file}': {error}")


def main():
    global TEXT_OUTPUT_ENABLED
    # Initialize the argument parser for command-line parameters
    parser = argparse.ArgumentParser(description='OSINT analysis for Telegram bots.')

    # Add options for token and chat ID
    parser.add_argument('-t', '--token', type=str, help='Telegram Token (bot1xxx)', required=False)
    parser.add_argument('-c', '--chat_id', type=str, help='Telegram Chat ID (-100xxx)', required=False)
    parser.add_argument('--json', action='store_true', help='Print analysis report in JSON format')
    parser.add_argument('--json-file', type=str, help='Save analysis report as JSON file')

    # Parse the command-line arguments
    args = parser.parse_args()
    TEXT_OUTPUT_ENABLED = not args.json

    # If the token is not provided via command line, prompt the user for input
    if args.token:
        telegram_token = args.token.strip()
    else:
        telegram_token = input('Telegram Token (bot1xxx): ').strip()

    # If the chat ID is not provided via command line, prompt the user for input
    if args.chat_id:
        telegram_chat_id = args.chat_id.strip()
    else:
        telegram_chat_id = input('Telegram Chat ID (-100xxx): ').strip()

    # Remove the 'bot' prefix from the token if it exists
    if telegram_token.startswith('bot'):
        telegram_token = telegram_token[3:]

    report = {
        "input": {
            "token": telegram_token,
            "chat_id": telegram_chat_id,
        },
        "bot": {},
        "chat": {},
        "invite_links": {},
        "admins": [],
        "errors": [],
    }

    text_print(f"\nAnalysis of token: {telegram_token} and chat id: {telegram_chat_id}\n")

    # Get Bot Info
    telegram_get_me_response = get_bot_info(telegram_token)
    telegram_get_me = telegram_get_me_response.get("result")

    # If the response contains bot information, print the relevant details
    if telegram_get_me:
        print_section("BOT")
        last_error_description = None
        text_print(f"Bot First Name: {telegram_get_me['first_name']}")
        text_print(f"Bot Username: {telegram_get_me['username']}")
        text_print(f"Bot User ID: {telegram_get_me['id']}")
        text_print(f"Bot Can Read Group Messages: {format_output_value(telegram_get_me['can_read_all_group_messages'])}")
        report["bot"]["first_name"] = telegram_get_me.get("first_name")
        report["bot"]["username"] = telegram_get_me.get("username")
        report["bot"]["user_id"] = telegram_get_me.get("id")
        report["bot"]["can_read_all_group_messages"] = telegram_get_me.get("can_read_all_group_messages")

        # Get Bot Description
        bot_description_response = get_bot_description(telegram_token)
        bot_description = bot_description_response.get("result")
        if bot_description:
            if "description" in bot_description and bot_description["description"] is not None:
                desc = normalize_single_line(bot_description["description"])
                if desc:
                    text_print(f"Bot Description: {desc}")
                    report["bot"]["description"] = desc

        # Get Bot Short Description
        bot_short_description_response = get_bot_short_description(telegram_token)
        bot_short_description = bot_short_description_response.get("result")
        if bot_short_description:
            if "short_description" in bot_short_description and bot_short_description["short_description"] is not None:
                short_desc = normalize_single_line(bot_short_description["short_description"])
                if short_desc:
                    text_print(f"Bot Short Description: {short_desc}")
                    report["bot"]["short_description"] = short_desc

        # Get Bot Default Admin Rights (groups/supergroups)
        default_admin_rights_response = get_default_admin_rights(telegram_token, for_channels=False)
        default_admin_rights = default_admin_rights_response.get("result")
        if default_admin_rights:
            text_print(f"Bot Default Administrator Rights (groups): {format_output_value(default_admin_rights)}")
            report["bot"]["default_admin_rights_groups"] = default_admin_rights

        # Get Bot Default Admin Rights (channels)
        default_admin_rights_channels_response = get_default_admin_rights(telegram_token, for_channels=True)
        default_admin_rights_channels = default_admin_rights_channels_response.get("result")
        if default_admin_rights_channels:
            text_print(f"Bot Default Administrator Rights (channels): {format_output_value(default_admin_rights_channels)}")
            report["bot"]["default_admin_rights_channels"] = default_admin_rights_channels

        # Get Bot Status - Member or Admin

        bot_chat_member_response = get_bot_chat_member(telegram_token, telegram_chat_id, telegram_get_me['id'])
        if bot_chat_member_response.get('result'):
            telegram_get_chat_member = bot_chat_member_response.get('result')
            text_print(f"Bot In The Chat Is An: {telegram_get_chat_member['status']}")
            report["bot"]["status_in_chat"] = telegram_get_chat_member.get("status")
        elif bot_chat_member_response.get('description'):
            error_description = bot_chat_member_response.get('description')
            if bot_chat_member_response.get('parameters') and 'migrate_to_chat_id' in bot_chat_member_response.get('parameters'):
                text_print(f"ATTENTION {error_description} - Migrated to: {bot_chat_member_response.get('parameters')['migrate_to_chat_id']}")
            else:
                text_print(f"ATTENTION {error_description}")
            last_error_description = error_description
            report["errors"].append(error_description)

        # Get Chat Info

        get_chat_response = get_chat_info(telegram_token, telegram_chat_id)
        telegram_get_chat = get_chat_response.get('result')

        if not telegram_get_chat:
            if get_chat_response.get('description'):
                error_description = get_chat_response.get('description')
                if error_description != last_error_description:
                    text_print(f"ATTENTION {error_description}")
                report["errors"].append(error_description)
            else:
                text_print("ATTENTION Chat ID is invalid, inaccessible, or no longer available.")
                report["errors"].append("Chat ID is invalid, inaccessible, or no longer available.")
            emit_json_report(report, args.json, args.json_file)
            return

        print_section("CHAT")
        print_chat_summary(telegram_get_chat)
        report["chat"] = dict(telegram_get_chat)
        if report["chat"].get("description"):
            report["chat"]["description"] = normalize_single_line(report["chat"]["description"])
        if "linked_chat_id" in telegram_get_chat and telegram_get_chat["linked_chat_id"]:
            linked_chat_id = telegram_get_chat["linked_chat_id"]
            linked_chat_response = get_chat_info(telegram_token, linked_chat_id)
            linked_chat = linked_chat_response.get('result')
            if linked_chat:
                print_linked_chat_summary(linked_chat)
                report["chat"]["linked_chat"] = linked_chat
            elif linked_chat_response.get('description'):
                text_print(f"ATTENTION linked_chat_id getChat error: {linked_chat_response.get('description')}")
                report["errors"].append(f"linked_chat_id getChat error: {linked_chat_response.get('description')}")


        # Export Chat Invite Link

        export_invite_response = export_chat_invite_link(telegram_token, telegram_chat_id)
        exported_invite_link = export_invite_response.get("result")

        # Create Chat Invite Link

        create_invite_response = create_chat_invite_link(telegram_token, telegram_chat_id)
        created_invite_link_result = create_invite_response.get('result')
        created_invite_link = None
        if created_invite_link_result and "invite_link" in created_invite_link_result:
            created_invite_link = created_invite_link_result["invite_link"]

        print_invite_links(telegram_get_chat.get('invite_link'), exported_invite_link, created_invite_link)
        report["invite_links"] = {
            "chat_invite_link": telegram_get_chat.get("invite_link"),
            "exported": exported_invite_link,
            "created": created_invite_link,
        }

        # Get Chat Member Count

        chat_member_count_response = get_chat_member_count(telegram_token, telegram_chat_id)
        telegram_chat_members_count = chat_member_count_response.get('result')

        text_print(f"Number of users in the chat: {telegram_chat_members_count}")
        report["chat"]["member_count"] = telegram_chat_members_count

        # Get Administrators in chat

        chat_administrators_response = get_chat_administrators(telegram_token, telegram_chat_id)
        telegram_get_chat_administrators = chat_administrators_response.get('result')

        if telegram_get_chat_administrators:
            print_section("ADMINS")
            text_print(f"Administrators in the chat:")
            for index, chat_member in enumerate(telegram_get_chat_administrators, start=1):
                print_admin_details(chat_member, index)
                report["admins"].append(build_admin_json(chat_member, index))
        emit_json_report(report, args.json, args.json_file)
    else:
        text_print('Telegram token is invalid or revoked.')
        report["errors"].append("Telegram token is invalid or revoked.")
        emit_json_report(report, args.json, args.json_file)


if __name__ == '__main__':
    main()
