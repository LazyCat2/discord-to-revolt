import pyvolt
import json
import asyncio

TEMPLATE_IMPORT_STEPS = 5

"""
	Key    : ID in Discord template
	Value  : ID in Revolt API

	Example: IDs.roles[discordRoleID] == revoltRoleID
"""
IDs = {
	"roles": {},
	"channels": {}
}

cache = {
	"roles": {},
	"channels": {}
}

def d2r(type, id):
    return cache[type][IDs[type][id]]

def step(current, total=None, text="Something is wrong"):
    print(("\t" if total else ""), "[", current, "/", total or TEMPLATE_IMPORT_STEPS, "] ", text, sep='')

def convert_permission(permissions: int):
    """
| Name                                   | Discord | Revolt  |
| CREATE_INSTANT_INVITE                  | 1 << 0  | 1 << 25 |
| KICK_MEMBERS                           | 1 << 1  | 1 << 6  |
| BAN_MEMBERS                            | 1 << 2  | 1 << 7  |
| ADMINISTRATOR                          | 1 << 3  |         |
| MANAGE_CHANNELS                        | 1 << 4  | 1 << 0  |
| MANAGE_GUILD                           | 1 << 5  | 1 << 1  |
| ADD_REACTIONS                          | 1 << 6  | 1 << 29 |
| VIEW_AUDIT_LOG                         | 1 << 7  |         |
| PRIORITY_SPEAKER                       | 1 << 8  |         |
| STREAM                                 | 1 << 9  |         |
| VIEW_CHANNEL                           | 1 << 10 | 1 << 20 |
| SEND_MESSAGES                          | 1 << 11 | 1 << 22 |
| SEND_TTS_MESSAGES                      | 1 << 12 |         |
| MANAGE_MESSAGES                        | 1 << 13 | 1 << 23 |
| EMBED_LINKS                            | 1 << 14 | 1 << 26 |
| ATTACH_FILES                           | 1 << 15 | 1 << 27 |
| READ_MESSAGE_HISTORY                   | 1 << 16 | 1 << 21 |
| MENTION_EVERYONE                       | 1 << 17 |         |
| USE_EXTERNAL_EMOJIS                    | 1 << 18 |         |
| VIEW_GUILD_INSIGHTS                    | 1 << 19 |         |
| CONNECT                                | 1 << 20 | 1 << 30 |
| SPEAK                                  | 1 << 21 | 1 << 31 |
| MUTE_MEMBERS                           | 1 << 22 | 1 << 33 |
| DEAFEN_MEMBERS                         | 1 << 23 | 1 << 34 |
| MOVE_MEMBERS                           | 1 << 24 | 1 << 35 |
| USE_VAD                                | 1 << 25 |         |
| CHANGE_NICKNAME                        | 1 << 26 | 1 << 10 |
| MANAGE_NICKNAMES                       | 1 << 27 | 1 << 11 |
| MANAGE_ROLES                           | 1 << 28 | 1 << 3  |
| MANAGE_WEBHOOKS                        | 1 << 29 | 1 << 24 |
| MANAGE_GUILD_EXPRESSIONS               | 1 << 30 |         |
| USE_APPLICATION_COMMANDS               | 1 << 31 |         |
| REQUEST_TO_SPEAK                       | 1 << 32 |         |
| MANAGE_EVENTS                          | 1 << 33 |         |
| MANAGE_THREADS                         | 1 << 34 |         |
| CREATE_PUBLIC_THREADS                  | 1 << 35 |         |
| CREATE_PRIVATE_THREADS                 | 1 << 36 |         |
| USE_EXTERNAL_STICKERS                  | 1 << 37 |         |
| SEND_MESSAGES_IN_THREADS               | 1 << 38 |         |
| USE_EMBEDDED_ACTIVITIES                | 1 << 39 |         |
| MODERATE_MEMBERS                       | 1 << 40 | 1 << 8  |
| VIEW_CREATOR_MONETIZATION_ANALYTICS    | 1 << 41 |         |
| USE_SOUNDBOARD                         | 1 << 42 |         |
| CREATE_GUILD_EXPRESSIONS               | 1 << 43 | 1 << 4  |
| CREATE_EVENTS                          | 1 << 44 |         |
| USE_EXTERNAL_SOUNDS                    | 1 << 45 |         |
| SEND_VOICE_MESSAGES                    | 1 << 46 |         |
| SEND_POLLS                             | 1 << 49 |         |
| USE_EXTERNAL_APPS                      | 1 << 50 |         |

| ManagePermissions                      |         | 1 << 2  |
| AssignRoles                            |         | 1 << 9  |
| ChangeAvatar                           |         | 1 << 12 |
| RemoveAvatars                          |         | 1 << 13 |
| Masquerade                             |         | 1 << 28 |
    """

    d2r = {
        43: 4,
        40: 8,
        29: 24,
        28: 3,
        26: 10,
        27: 11,
        0 : 25,
        1 : 6,
        2 : 7,
        4 : 0,
        5 : 1,
        6 : 29,
        10: 20,
        11: 22,
        13: 23,
        14: 26,
        15: 27,
        16: 21,
        20: 30,
        21: 31,
        23: 34,
        22: 33,
        24: 35,
    }
    
    out = 0
    max_byte = max([item for pair in d2r.items() for item in pair]) +1

    if type(permissions) == str: permissions = int(permissions)
    
    for i in d2r:
        if permissions & (1 << i):
            out |= 1 << d2r[i]

    return pyvolt.Permissions(out)

# print(convert_permission(1 << 50))
# print(convert_permission(1 << 43), 1 << 4)
# print(convert_permission((1 << 43) | (1 << 49)), 1 << 4)
# print(convert_permission((1 << 43) | (1 << 49) | (1 << 21)), (1 << 4) | (1 << 31))
# print(convert_permission((1 << 43) | (1 << 21)), (1 << 4) | (1 << 31))
# 
# exit()
async def main():
    template_url = None
    template = None
    while not template:
        template_url = input("Template URL: ").split("/")[-1]
        if template_url == "":
            template = json.load(open("demo_template.json"))["serialized_source_guild"]
            break
        try:
            template = requests.get(f"https://discord.com/api/v9/guilds/templates/{template_url}").json()["serialized_source_guild"]
        except Exception as error: 
            print(error)
            template_url = None
            template = None

    print(f"""A new server called "{template["name"]}" will be created.
{len(template["channels"])} channels and {len(template["roles"])} roles will be added to the server.""")
    if input("type Y to continue, anything else to cancel: ").lower()[0] != "y": return
    
    client = None
    server = None
    while not server:
        client = pyvolt.Client(token=input("Revolt token: "), bot=False)
        try:
            server = await client.create_server(
                name = template["name"],
                description = template["description"]
            )
        except Exception as error: 
            print(error)
            client = None

    step(1, text="Delete default channels")

    deleted = 0
    total = len(server.channels)
    for channel in server.channels:
        step(deleted+1, total, channel.name)
        await channel.close()
        deleted += 1


    step(2, text="Create channels")

    # 0 - Text channel
    # 2 - Voice channel
    # 4 - Category

    channels = template["channels"]

    # Get only text channels
    # Convert forums to text channels
    textChannels = list(filter(lambda channel: channel["type"] not in [2, 4], channels))
    voiceChannels = list(filter(lambda channel: channel["type"] == 2, channels))
    categories = list(filter(lambda channel: channel["type"] == 4, channels))

    total = len(textChannels) + len(voiceChannels)
    created = 0
    for channel in textChannels + voiceChannels:
        step(created + 1, total, channel["name"])
        
        rChannel = await server.create_channel(
            name = channel["name"],
            description = channel["topic"], 
            nsfw = channel["nsfw"],
            type = (
                pyvolt.ChannelType.voice 
                if channel["type"] == 2 else 
                pyvolt.ChannelType.text
            )
        )

        IDs["channels"][channel["id"]] = rChannel.id
        cache["channels"][rChannel.id] = rChannel
        created += 1


    step(3, text="Setup categories")

    await server.edit(
        categories=[
            pyvolt.Category(
                id = str(category["id"]),
                title = category["name"],
                channels = [
                    IDs["channels"][channel["id"]]
                    for channel in textChannels + voiceChannels
                    if channel["parent_id"] == category["id"] 
                ]
            )

            for category in categories
        ]
    )


    step(4, text="Create and setup roles")
    
    total = len(template["roles"])
    created = 0
    for role in template["roles"]:
        step(created + 1, total, role["name"])
        if role["id"] == 0:
            await server.set_default_permissions(
                convert_permission(role["permissions"])
            )
            created += 1
            continue
        
        rRole = await server.create_role(
            name = role["name"],
            rank = role["id"]
        )
        
        IDs["roles"][role["id"]] = rRole.id
        cache["roles"][rRole.id] = rRole
        
        await rRole.edit(
            color = "#" + hex(role["color"])[2:],
            hoist = role["hoist"]
        )
        await server.set_role_permissions(
            rRole,
            allow = convert_permission(
                role["permissions"]
            ),
            deny = pyvolt.Permissions(0)
        )
        created += 1


    step(5, text="Set permissions for channels")

    channels_to_handle = [
        channel
        for channel in textChannels + voiceChannels
        if channel["permission_overwrites"]
    ]
    total = len(channels_to_handle)
    handled = 0
    for channel in channels_to_handle:
        step(handled + 1, total, channel["name"])
        rChannel = d2r("channels", channel["id"])

        for overwrite in channel["permission_overwrites"]:
            ow = {
                "allow": convert_permission(overwrite["allow"]),
                "deny": convert_permission(overwrite["deny"]),
            }

            if overwrite["id"] == 0:
                await rChannel.set_default_permissions(
                    pyvolt.PermissionOverride(**ow)
                )
            else:
                await rChannel.set_role_permissions(
                    d2r("roles", overwrite["id"]),
                    **ow
                )
        
        handled += 1

asyncio.run(main())
